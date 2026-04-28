import { randomUUID } from 'crypto';
import { Room } from './Room.js';
import { MessageHandler } from './network/MessageHandler.js';
import * as Protocol from '../shared/Protocol.js';
import {
  ensureOfficialGamesSpec,
  specToMeta,
  isOfficialRoomId,
} from './OfficialGames.js';
import { GAME_STATES } from '../shared/constants.js';

export class GameServer {
  constructor({ nodeId, registry, matchHistory, sessionStore } = {}) {
    this.nodeId = nodeId || 'node0';
    this.registry = registry || null;
    this.matchHistory = matchHistory || null;
    this.sessionStore = sessionStore || null;

    this.rooms = new Map();
    this.playerRooms = new Map();
    this.playerSockets = new Map();
    this.playerUsernames = new Map();
    this.messageHandler = new MessageHandler(this);

    if (this.registry) {
      this.registry.onChange(() => this.broadcastRoomList());
    }
  }

  _mintPlayerId() {
    return randomUUID();
  }

  async onConnection(ws, { requestedRoomId } = {}) {
    
    const playerId = ws.sessionSid || this._mintPlayerId();
    ws.playerId = playerId;

    const prevWs = this.playerSockets.get(playerId);
    if (prevWs && prevWs !== ws) {
      try { prevWs.close(4003, 'replaced_by_reconnect'); } catch {}
    }
    this.playerSockets.set(playerId, ws);
    if (ws.username) this.playerUsernames.set(playerId, ws.username);

    if (this.registry) this.registry.incrStat('connections_total');

    ws.on('message', (data) => {
      this.messageHandler.handle(playerId, data.toString());
    });

    ws.on('close', () => {
      
      if (this.playerSockets.get(playerId) !== ws) return;
      this.handleDisconnect(playerId);
    });

    ws.on('error', (err) => {
      console.error(`WebSocket error for ${playerId}:`, err.message);
    });

    const existingRoomId = this.playerRooms.get(playerId);
    if (existingRoomId && this.rooms.has(existingRoomId)) {
      const room = this.rooms.get(existingRoomId);
      const player = room.players.get(playerId);
      if (player) {
        player.ws = ws;
        this.send(ws, {
          type: Protocol.S_WELCOME,
          playerId,
          roomId: room.id,
          nodeId: this.nodeId,
          hostId: room.hostId,
          config: {
            name: room.name,
            maxPlayers: room.maxPlayers,
            gamesPerSet: room.gamesPerSet,
            setsToWin: room.setsToWin,
          },
        });
        
        const st = room.gameState.state;
        if (st !== GAME_STATES.WAITING && st !== GAME_STATES.READY_CHECK) {
          const teams = { team1: [], team2: [] };
          const allPlayers = [];
          for (const p of room.players.values()) {
            (p.team === 0 ? teams.team1 : teams.team2).push({ id: p.id, name: p.name });
            allPlayers.push({ id: p.id, team: p.team, x: p.x, y: p.y, name: p.name });
          }
          this.send(ws, {
            type: Protocol.S_MATCH_START,
            teams,
            players: allPlayers,
            servingTeam: 0,
            servingPlayerIndex: 0,
            resume: true,
          });
        }
        
        if (room.isOfficial && room.hostId === playerId) {
          room._replayChatHistoryTo(ws);
        }
        room.broadcastRoomState();
        return;
      }
    }

    const targetRoomId = requestedRoomId || ws.currentRoomId || null;
    if (targetRoomId) {
      let ownerNode = null;
      if (!isOfficialRoomId(targetRoomId)) {
        if (this.registry) {
          ownerNode = await this.registry.getRoomNode(targetRoomId);
        }
        if (!ownerNode) {
          ownerNode = ws.currentRoomNode || null;
        }
      }
      if (!ownerNode && !isOfficialRoomId(targetRoomId)) {
        const idx = targetRoomId.indexOf('_');
        if (idx > 0) ownerNode = targetRoomId.slice(0, idx);
      }
      if (ownerNode && ownerNode !== this.nodeId) {
        this.send(ws, {
          type: Protocol.S_REDIRECT,
          nodeId: ownerNode,
          roomId: targetRoomId,
          reason: 'resume_on_owner_node',
        });
        return;
      }

      if (!this.rooms.has(targetRoomId) && isOfficialRoomId(targetRoomId)) {
        const ownerUsername = this.playerUsernames.get(playerId) || ws.username;
        if (ownerUsername) {
          try {
            const specs = await ensureOfficialGamesSpec(this.sessionStore, ownerUsername);
            const spec = specs.find((s) => s.id === targetRoomId);
            if (spec) {
              const room = await this._createOfficialRoomFromSpec(spec);
              if (room && this.playerSockets.get(playerId) === ws) {
                const joinName = (ws.username || 'Player').slice(0, 12);
                if (!room.players.has(playerId)) {
                  room.addPlayer(playerId, ws, joinName);
                } else {
                  room.players.get(playerId).ws = ws;
                }
                this.playerRooms.set(playerId, room.id);
                await this._rememberSessionRoom(ws, room.id);
                this.send(ws, {
                  type: Protocol.S_WELCOME,
                  playerId,
                  roomId: room.id,
                  nodeId: this.nodeId,
                  hostId: room.hostId,
                  config: {
                    name: room.name,
                    maxPlayers: room.maxPlayers,
                    gamesPerSet: room.gamesPerSet,
                    setsToWin: room.setsToWin,
                  },
                });
                room.broadcastRoomState();
                return;
              }
            }
          } catch (err) {
            console.error('official room resume failed:', err.message);
          }
        }
      }
    }

    this.sendRoomList(ws);
    this._pushOfficialList(ws, playerId).catch((err) =>
      console.error('_pushOfficialList failed:', err.message),
    );
  }

  async _pushOfficialList(ws, playerId) {
    if (!ws) return;
    const username = this.playerUsernames.get(playerId) || ws.username;
    if (!username) {
      this.send(ws, { type: Protocol.S_OFFICIAL_LIST, games: [] });
      return;
    }
    let specs = [];
    try {
      specs = await ensureOfficialGamesSpec(this.sessionStore, username);
    } catch (err) {
      console.error('ensureOfficialGamesSpec failed:', err.message);
    }
    if (!ws || ws.readyState !== 1) return;
    const games = specs.map((spec) => {
      const room = this.rooms.get(spec.id);
      if (room) {
        return {
          id: room.id,
          name: room.name,
          players: room.playerCount,
          maxPlayers: room.maxPlayers,
          status: room.gameState.state,
          nodeId: this.nodeId,
          config: { gamesPerSet: room.gamesPerSet, setsToWin: room.setsToWin },
        };
      }
      return specToMeta(spec);
    });
    this.send(ws, { type: Protocol.S_OFFICIAL_LIST, games });
  }

  async handleCreateRoom(playerId, msg) {
    const ws = this.playerSockets.get(playerId);
    if (!ws) return;

    if (!ws.hostingRoomName && this.sessionStore && ws.sessionSid) {
      try {
        const name = await this.sessionStore.claimSessionHostingRoomName(ws.sessionSid);
        if (name) ws.hostingRoomName = name;
      } catch (err) {
        console.error('claimSessionHostingRoomName failed:', err.message);
      }
    }
    
    if (!this.playerSockets.has(playerId)) return;

    const roomName = (ws.hostingRoomName || msg.name || 'Padel Match').slice(0, 32);
    const password = msg.password ? String(msg.password).slice(0, 20) : null;
    const config = {
      name: roomName,
      maxPlayers: [2, 4].includes(msg.maxPlayers) ? msg.maxPlayers : 4,
      gamesPerSet: Math.max(1, Math.min(6, msg.gamesPerSet || 6)),
      setsToWin: Math.max(1, Math.min(3, msg.setsToWin || 2)),
      password
    };

    const roomId = this.createRoom(config);
    const name = (msg.playerName || 'Player').slice(0, 12);

    const room = this.rooms.get(roomId);
    room.addPlayer(playerId, ws, name);
    this.playerRooms.set(playerId, roomId);
    
    await this._rememberSessionRoom(ws, roomId);

    console.log(`[${this.nodeId}] ${name} (${playerId}) created room "${config.name}" [${roomId}]`);

    if (this.registry) {
      this.registry.incrStat('rooms_created');
      this._publishRoom(room);
    }
    this.broadcastRoomList();
  }

  _rememberSessionRoom(ws, roomId) {
    if (ws) {
      ws.currentRoomId = roomId;
      ws.currentRoomNode = this.nodeId;
    }
    if (!this.sessionStore || !ws || !ws.sessionSid) return Promise.resolve();
    return this.sessionStore
      .updateSession(ws.sessionSid, { currentRoomId: roomId, currentRoomNode: this.nodeId })
      .catch((err) => console.error('updateSession(currentRoomId) failed:', err.message));
  }

  _forgetSessionRoom(ws) {
    if (ws) {
      ws.currentRoomId = null;
      ws.currentRoomNode = null;
    }
    if (!this.sessionStore || !ws || !ws.sessionSid) return Promise.resolve();
    return this.sessionStore
      .updateSession(ws.sessionSid, { currentRoomId: null, currentRoomNode: null })
      .catch((err) => console.error('updateSession(clear room) failed:', err.message));
  }

  handleListRooms(playerId) {
    const ws = this.playerSockets.get(playerId);
    if (ws) this.sendRoomList(ws);
  }

  async handleRequestHostingName(playerId) {
    const ws = this.playerSockets.get(playerId);
    if (!ws) return;
    
    if (!ws.hostingRoomName && this.sessionStore && ws.sessionSid) {
      try {
        const name = await this.sessionStore.claimSessionHostingRoomName(ws.sessionSid);
        if (name) ws.hostingRoomName = name;
      } catch (err) {
        console.error('claimSessionHostingRoomName failed:', err.message);
      }
    }
    if (!this.playerSockets.has(playerId)) return;
    this.send(ws, {
      type: Protocol.S_HOSTING_NAME,
      name: ws.hostingRoomName || null,
    });
  }

  async handleListOfficial(playerId) {
    const ws = this.playerSockets.get(playerId);
    if (!ws) return;
    await this._pushOfficialList(ws, playerId);
  }

  handleListMatches(playerId) {
    const ws = this.playerSockets.get(playerId);
    if (!ws || !this.matchHistory) return;
    this.matchHistory.getRecentMatches(10).then((matches) => {
      this.send(ws, { type: Protocol.S_RECENT_MATCHES, matches });
    }).catch((err) => console.error('getRecentMatches error:', err.message));
  }

  handleStartGame(playerId) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;

    if (room.hostStartGame(playerId)) {
      console.log(`[${this.nodeId}] host ${playerId} started game in room ${roomId}`);
      this._publishRoom(room);
      this.broadcastRoomList();
    } else {
      const ws = this.playerSockets.get(playerId);
      if (ws) this.send(ws, { type: Protocol.S_ERROR, message: 'Cannot start game' });
    }
  }

  handleServeToss(playerId) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;
    const servingTeam = room.gameState.serveManager.servingTeam;
    const servingPlayer = room.getServingPlayer(servingTeam);
    if (!servingPlayer || servingPlayer.id !== playerId) return;
    room.gameState.serveToss();
  }

  handleServeHit(playerId, msg) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;
    const servingTeam = room.gameState.serveManager.servingTeam;
    const servingPlayer = room.getServingPlayer(servingTeam);
    if (!servingPlayer || servingPlayer.id !== playerId) return;
    room.gameState.serveHit(servingPlayer, msg.aimAngle);
  }

  handleChat(playerId, msg) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;
    const text = (msg.text || '').slice(0, 200);
    if (text.length === 0) return;
    room.addChatMessage(playerId, text);
  }

  async handleJoin(playerId, msg) {
    const ws = this.playerSockets.get(playerId);
    if (!ws) return;

    const name = (msg.name || 'Player').slice(0, 12);
    let roomId = msg.roomId;

    if (!roomId) {
      roomId = this.findAvailableLocalRoom();
      if (!roomId) {
        
        if (this.registry) {
          const globalRooms = this.registry.getAllRooms();
          const available = globalRooms.find(
            (r) => r.status === 'waiting' && r.players < r.maxPlayers,
          );
          if (available && available.nodeId !== this.nodeId) {
            this.send(ws, {
              type: Protocol.S_REDIRECT,
              nodeId: available.nodeId,
              roomId: available.id,
              reason: 'quick_join_remote',
            });
            return;
          }
          if (available) {
            roomId = available.id;
          }
        }
      }
      if (!roomId) {
        roomId = this.createRoom();
      }
    } else if (isOfficialRoomId(roomId)) {
      
      if (!this.rooms.has(roomId)) {
        const username = this.playerUsernames.get(playerId) || ws.username;
        if (username) {
          try {
            const specs = await ensureOfficialGamesSpec(this.sessionStore, username);
            const spec = specs.find((s) => s.id === roomId);
            if (spec) await this._createOfficialRoomFromSpec(spec);
          } catch (err) {
            console.error('materialize official room failed:', err.message);
          }
        }
      }
      if (!this.playerSockets.has(playerId)) return;
    } else {
      
      if (!this.rooms.has(roomId)) {
        let ownerNode = this.registry ? await this.registry.getRoomNode(roomId) : null;
        if (!ownerNode) {
          const idx = roomId.indexOf('_');
          if (idx > 0) ownerNode = roomId.slice(0, idx);
        }
        if (ownerNode && ownerNode !== this.nodeId) {
          this.send(ws, {
            type: Protocol.S_REDIRECT,
            nodeId: ownerNode,
            roomId,
            reason: 'room_on_other_node',
          });
          return;
        }
      }
    }

    const room = this.rooms.get(roomId);
    if (!room) {
      this.send(ws, { type: Protocol.S_ERROR, message: 'Room not found' });
      return;
    }

    if (room.isFull) {
      this.send(ws, { type: Protocol.S_ERROR, message: 'Room is full' });
      return;
    }

    if (room.password && room.password !== msg.password) {
      this.send(ws, { type: Protocol.S_ERROR, message: 'Неверный пароль' });
      return;
    }

    const joiningUsername = this.playerUsernames.get(playerId);
    if (joiningUsername) {
      for (const p of room.players.values()) {
        if (p.id === playerId) continue;
        const otherName = this.playerUsernames.get(p.id);
        if (otherName && otherName === joiningUsername) {
          this.send(ws, {
            type: Protocol.S_ERROR,
            message: 'Вы уже находитесь в этой игре',
          });
          return;
        }
      }
    }

    const currentRoomId = this.playerRooms.get(playerId);
    if (currentRoomId) {
      const currentRoom = this.rooms.get(currentRoomId);
      if (currentRoom) {
        currentRoom.removePlayer(playerId);
        if (currentRoom.isEmpty) {
          this.rooms.delete(currentRoomId);
          if (this.registry) this.registry.removeRoom(currentRoomId).catch(() => {});
        } else {
          this._publishRoom(currentRoom);
        }
      }
    }

    room.addPlayer(playerId, ws, name);
    this.playerRooms.set(playerId, roomId);
    
    await this._rememberSessionRoom(ws, roomId);

    console.log(`[${this.nodeId}] ${name} (${playerId}) joined room ${roomId} [${room.playerCount}/${room.maxPlayers}]`);

    this._publishRoom(room);
    this.broadcastRoomList();
  }

  handleReady(playerId) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;
    room.setReady(playerId);
    this._publishRoom(room);
  }

  handleUnready(playerId) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;
    room.setUnready(playerId);
    this._publishRoom(room);
  }

  handleInput(playerId, msg) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;
    room.inputBuffer.pushInput(playerId, msg);
  }

  handleShot(playerId, msg) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;

    const player = room.players.get(playerId);
    if (!player) return;

    room.physics.tryShot(player, room.gameState.ball, msg.shotModifier || 'flat', msg.aimAngle, room.gameState.rallyTime);
  }

  handlePing(playerId, msg) {
    const ws = this.playerSockets.get(playerId);
    if (!ws) return;
    
    if (typeof msg.rtt === 'number' && Number.isFinite(msg.rtt)) {
      const roomId = this.playerRooms.get(playerId);
      if (roomId) {
        const room = this.rooms.get(roomId);
        if (room) {
          const player = room.players.get(playerId);
          if (player) player.rtt = Math.max(0, Math.min(9999, Math.round(msg.rtt)));
        }
      }
    }
    this.send(ws, {
      type: Protocol.S_PONG,
      t: msg.t,
      serverT: Date.now()
    });
  }

  handleUserKick(playerId, msg) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;

    if (room.hostId !== playerId) {
      const ws = this.playerSockets.get(playerId);
      if (ws) this.send(ws, { type: Protocol.S_ERROR, message: 'Only the host can kick players' });
      return;
    }

    const targetId = msg && msg.targetId;
    if (!targetId || targetId === playerId) return;
    if (!room.players.has(targetId)) return;

    const targetWs = this.playerSockets.get(targetId);
    if (targetWs) {
      this.send(targetWs, { type: Protocol.S_KICKED, message: 'You were kicked' });
    }

    room.removePlayer(targetId);
    this.playerRooms.delete(targetId);

    console.log(`[${this.nodeId}] ${playerId} kicked ${targetId} from room ${roomId}`);

    if (room.isEmpty) {
      room.stopTicking();
      this.rooms.delete(roomId);
      if (this.registry) this.registry.removeRoom(roomId).catch(() => {});
    } else {
      this._publishRoom(room);
    }

    if (targetWs && targetWs.readyState === 1) {
      try { targetWs.close(4001, 'kicked'); } catch (e) {}
    }

    this.broadcastRoomList();
  }

  handleAdminUpdateSettings(playerId, msg) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;
    if (room.hostId !== playerId) {
      const ws = this.playerSockets.get(playerId);
      if (ws) this.send(ws, { type: Protocol.S_ERROR, message: 'Only the host can change settings' });
      return;
    }
    if (room.updateSettings(msg.settings || {})) {
      this._publishRoom(room);
      this.broadcastRoomList();
    } else {
      const ws = this.playerSockets.get(playerId);
      if (ws) this.send(ws, { type: Protocol.S_ERROR, message: 'Settings can only be changed in lobby' });
    }
  }

  handleAdminCloseRoom(playerId) {
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) return;
    const room = this.rooms.get(roomId);
    if (!room) return;
    if (room.isOfficial) {
      const ws = this.playerSockets.get(playerId);
      if (ws) this.send(ws, { type: Protocol.S_ERROR, message: 'Официальные комнаты удалять нельзя' });
      return;
    }
    if (room.hostId !== playerId) {
      const ws = this.playerSockets.get(playerId);
      if (ws) this.send(ws, { type: Protocol.S_ERROR, message: 'Only the host can close the room' });
      return;
    }

    const occupants = [];
    for (const p of room.players.values()) {
      if (!p.isBot) occupants.push(p.id);
    }

    for (const pid of occupants) {
      const targetWs = this.playerSockets.get(pid);
      if (targetWs) {
        this.send(targetWs, { type: Protocol.S_KICKED, message: 'Комната закрыта хостом' });
        this._forgetSessionRoom(targetWs);
      }
      this.playerRooms.delete(pid);
    }

    room.stopTicking();
    this.rooms.delete(roomId);
    if (this.registry) this.registry.removeRoom(roomId).catch(() => {});
    console.log(`[${this.nodeId}] room ${roomId} closed by host ${playerId}`);

    this.broadcastRoomList();
  }

  handleLeaveRoom(playerId, msg) {
    const ws = this.playerSockets.get(playerId);
    const roomId = this.playerRooms.get(playerId);
    if (!roomId) {
      this._forgetSessionRoom(ws);
      return;
    }
    const room = this.rooms.get(roomId);
    if (!room) {
      this.playerRooms.delete(playerId);
      this._forgetSessionRoom(ws);
      return;
    }
    const { playerId: leavingId } = { playerId, ...msg };
    if (!room.players.has(leavingId)) return;

    room.removePlayer(leavingId);
    this.playerRooms.delete(leavingId);

    if (leavingId === playerId) {
      this._forgetSessionRoom(ws);
    } else {
      const victimWs = this.playerSockets.get(leavingId);
      if (victimWs) {
        this.send(victimWs, { type: Protocol.S_KICKED, message: 'Вы покинули комнату' });
        this._forgetSessionRoom(victimWs);
        if (victimWs.readyState === 1) {
          try { victimWs.close(4001, 'left'); } catch (e) {}
        }
      }
    }

    if (room.isEmpty) {
      room.stopTicking();
      this.rooms.delete(roomId);
      if (this.registry) this.registry.removeRoom(roomId).catch(() => {});
      console.log(`[${this.nodeId}] room ${roomId} closed (empty after leave)`);
    } else {
      this._publishRoom(room);
    }
    this.broadcastRoomList();
    if (leavingId === playerId && ws) this.sendRoomList(ws);
  }

  handleDisconnect(playerId) {
    
    this.playerSockets.delete(playerId);
    console.log(`[${this.nodeId}] player ${playerId} socket closed (room seat preserved)`);
  }

  handleLogout(sid) {
    const playerId = sid;
    const roomId = this.playerRooms.get(playerId);
    if (roomId) {
      const room = this.rooms.get(roomId);
      if (room) {
        room.removePlayer(playerId);
        if (room.isEmpty) {
          room.stopTicking();
          this.rooms.delete(roomId);
          if (this.registry) this.registry.removeRoom(roomId).catch(() => {});
          console.log(`[${this.nodeId}] room ${roomId} closed (logout)`);
        } else {
          this._publishRoom(room);
        }
      }
      this.playerRooms.delete(playerId);
    }
    this.playerSockets.delete(playerId);
    this.playerUsernames.delete(playerId);
    this.broadcastRoomList();
  }

  createRoom(config = {}) {
    const id = randomUUID();
    const room = new Room(id, config, {
      nodeId: this.nodeId,
      matchHistory: this.matchHistory,
      onStateChange: () => {
        if (!room.isOfficial) this._publishRoom(room);
      },
    });
    this.rooms.set(id, room);
    if (!room.isOfficial) {
      console.log(`[${this.nodeId}] room ${id} created`);
      if (this.registry) this._publishRoom(room);
    }
    return id;
  }

  async _createOfficialRoomFromSpec(spec) {
    if (!spec || !spec.id) return null;
    const existing = this.rooms.get(spec.id);
    if (existing) return existing;
    const room = new Room(spec.id, {
      name: spec.name,
      maxPlayers: spec.maxPlayers,
      gamesPerSet: spec.gamesPerSet,
      setsToWin: spec.setsToWin,
      isOfficial: true,
      ownerUsername: spec.ownerUsername,
    }, {
      nodeId: this.nodeId,
      matchHistory: this.matchHistory,
      onStateChange: () => {  },
    });
    this.rooms.set(spec.id, room);
    for (const botName of spec.botNames || []) {
      try { room.addBot(botName); } catch (e) {  }
    }
    
    room.seedOfficialChatHistory();
    return room;
  }

  findAvailableLocalRoom() {
    for (const [id, room] of this.rooms) {
      if (room.isOfficial) continue;
      if (!room.isFull && room.gameState.state === 'waiting') {
        return id;
      }
    }
    return null;
  }

  _roomMeta(room) {
    const host = room.players.get(room.hostId);
    return {
      id: room.id,
      name: room.name,
      hostName: host ? host.name : '—',
      players: room.playerCount,
      maxPlayers: room.maxPlayers,
      status: room.gameState.state,
      gamesPerSet: room.gamesPerSet,
      setsToWin: room.setsToWin,
      hasPassword: !!room.password,
    };
  }

  _publishRoom(room) {
    if (!this.registry || !room) return;
    if (room.isOfficial) return;
    this.registry.upsertRoom(this._roomMeta(room)).catch((err) => {
      console.error('registry upsert error:', err.message);
    });
  }

  _allRooms() {
    if (this.registry) {
      
      return this.registry.getAllRooms().map((r) => ({
        id: r.id,
        name: r.name,
        hostName: r.hostName,
        players: r.players,
        maxPlayers: r.maxPlayers,
        status: r.status,
        nodeId: r.nodeId,
        config: { gamesPerSet: r.gamesPerSet, setsToWin: r.setsToWin },
        hasPassword: !!r.hasPassword,
      }));
    }
    
    const rooms = [];
    for (const [id, room] of this.rooms) {
      if (room.isOfficial) continue;
      const meta = this._roomMeta(room);
      rooms.push({
        id,
        name: meta.name,
        hostName: meta.hostName,
        players: meta.players,
        maxPlayers: meta.maxPlayers,
        status: meta.status,
        nodeId: this.nodeId,
        config: { gamesPerSet: meta.gamesPerSet, setsToWin: meta.setsToWin },
        hasPassword: meta.hasPassword,
      });
    }
    return rooms;
  }

  sendRoomList(ws) {
    this.send(ws, { type: Protocol.S_ROOM_LIST, rooms: this._allRooms() });
  }

  broadcastRoomList() {
    const rooms = this._allRooms();
    const msg = Protocol.encode({ type: Protocol.S_ROOM_LIST, rooms });
    for (const [pid, ws] of this.playerSockets) {
      
      if (!this.playerRooms.has(pid) && ws.readyState === 1) {
        ws.send(msg);
      }
    }
  }

  send(ws, msg) {
    if (ws && ws.readyState === 1) {
      ws.send(Protocol.encode(msg));
    }
  }

  snapshotLoad() {
    return {
      nodeId: this.nodeId,
      connections: this.playerSockets.size,
      rooms: this.rooms.size,
      activeMatches: [...this.rooms.values()].filter(
        (r) => r.gameState.state === 'playing' || r.gameState.state === 'serving',
      ).length,
    };
  }
}
