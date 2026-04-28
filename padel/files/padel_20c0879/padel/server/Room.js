import { randomUUID } from 'crypto';
import { Player } from './game/Player.js';
import { BotController } from './game/BotController.js';
import { GameState } from './GameState.js';
import { PhysicsEngine } from './physics/PhysicsEngine.js';
import { InputBuffer } from './network/InputBuffer.js';
import * as Protocol from '../shared/Protocol.js';
import {
  SERVER_TICK_RATE, GAME_STATES, BALL_STATES
} from '../shared/constants.js';
import { STARTING_POSITIONS } from '../shared/CourtLayout.js';

const OFFICIAL_CHAT_PRELUDE = [
  { minutesAgo: 12, text: 'Ты видел новенького?' },
  { minutesAgo: 11, text: 'Да, аххахаха, он как будто первый раз держит ракетку в руках' },
  { minutesAgo: 10, text: 'Он никогда не сможет выиграть у нас и получить этот флаг: alfa{XXXXXXXXX_CENSORED_XXXXXXXXX}' },
  { minutesAgo: 9, text: 'И не говори! Ой, кажется он идет сюда' },
];

const OFFICIAL_CHAT_POST_JOIN_VARIANTS = [
  [
    { delayMs: 600, text: 'всё, тихо, флаг не повторяйте' },
    { delayMs: 1800, text: 'давайте уже играть' },
  ],
  [
    { delayMs: 700, text: 'тссс, он зашёл' },
    { delayMs: 2000, text: 'ладно, разминаемся' },
  ],
  [
    { delayMs: 500, text: 'пришёл... тсс' },
    { delayMs: 1900, text: 'о, привет новичок 👋' },
  ],
  [
    { delayMs: 650, text: 'так, молчим про флаг' },
    { delayMs: 2100, text: 'погнали уже' },
  ],
  [
    { delayMs: 800, text: 'ставлю на то что он сольёт 6:0' },
    { delayMs: 2200, text: 'не, не все так плохо, хотя бы 6:1' },
  ],
  [
    { delayMs: 550, text: 'кто с ним в паре играть будет?' },
    { delayMs: 1700, text: 'да какая разница, ему не поможет' },
  ],
  [
    { delayMs: 900, text: 'эй, ракетку правильной стороной держи)' },
    { delayMs: 2300, text: 'да ладно тебе, пусть сам попробует. флаг не палим' },
  ],
  [
    { delayMs: 600, text: 'тихо, флаг не повторяйте' },
    { delayMs: 1900, text: 'надеюсь разминку ты уже сделал' },
  ],
];

export class Room {
  constructor(id, config = {}, deps = {}) {
    this.id = id;
    this.players = new Map();
    this.bots = new Map();
    this.spectators = [];
    this.gameState = new GameState();
    this.physics = new PhysicsEngine();
    this.inputBuffer = new InputBuffer();
    this.tickInterval = null;
    this.dt = 1 / SERVER_TICK_RATE;
    this.readyPlayers = new Set();

    this.name = config.name || 'Padel Match';
    this.maxPlayers = config.maxPlayers || 4;
    this.gamesPerSet = config.gamesPerSet || 6;
    this.setsToWin = config.setsToWin || 2;
    this.password = config.password || null;
    this.hostId = null;
    this.chatMessages = [];

    this.isOfficial = !!config.isOfficial;
    this.ownerUsername = config.ownerUsername || null;

    this.nodeId = deps.nodeId || null;
    this.matchHistory = deps.matchHistory || null;
    this.onStateChange = deps.onStateChange || null;

    this.matchStartedAt = null;
    this.matchPersisted = false;
    this.roomStateBroadcastTick = 0;
  }

  addBot(name) {
    if (this.players.size >= this.maxPlayers) return null;

    const teamCounts = [0, 0];
    for (const p of this.players.values()) teamCounts[p.team]++;
    const team = teamCounts[0] <= teamCounts[1] ? 0 : 1;
    const posIndex = teamCounts[team];
    const positions = team === 0 ? STARTING_POSITIONS.team1 : STARTING_POSITIONS.team2;
    const pos = positions[posIndex] || positions[0];

    const id = randomUUID();
    const bot = new Player(id, team, pos.x, pos.y, name);
    bot.ws = null;
    bot.isBot = true;
    this.players.set(id, bot);
    this.bots.set(id, new BotController(bot));

    this.readyPlayers.add(id);

    if (!this.hostId) this.hostId = id;
    return bot;
  }

  _notifyStateChange() {
    if (this.onStateChange) {
      try { this.onStateChange(); } catch (e) {  }
    }
  }

  addPlayer(id, ws, name) {
    if (this.players.size >= this.maxPlayers) return false;

    const teamCounts = [0, 0];
    for (const p of this.players.values()) {
      teamCounts[p.team]++;
    }
    const team = teamCounts[0] <= teamCounts[1] ? 0 : 1;
    const posIndex = teamCounts[team];
    const positions = team === 0 ? STARTING_POSITIONS.team1 : STARTING_POSITIONS.team2;
    const pos = positions[posIndex] || positions[0];

    const player = new Player(id, team, pos.x, pos.y, name);
    player.ws = ws;
    this.players.set(id, player);
    this.inputBuffer.addPlayer(id);

    if (!this.hostId) {
      this.hostId = id;
    }

    this.send(ws, {
      type: Protocol.S_WELCOME,
      playerId: id,
      roomId: this.id,
      nodeId: this.nodeId,
      hostId: this.hostId,
      config: { name: this.name, maxPlayers: this.maxPlayers, gamesPerSet: this.gamesPerSet, setsToWin: this.setsToWin }
    });

    const otherRealPlayers = [...this.players.values()]
      .filter((p) => !p.isBot && p.id !== id).length;

    if (
      this.isOfficial && !player.isBot && otherRealPlayers === 0 &&
      this.gameState.state !== GAME_STATES.WAITING
    ) {
      this.stopTicking();
      this.gameState.reset();
      this.matchStartedAt = null;
      this.matchPersisted = false;
      this.readyPlayers.clear();
      for (const botId of this.bots.keys()) {
        this.readyPlayers.add(botId);
      }
    }

    if (
      this.isOfficial && !player.isBot && otherRealPlayers === 0 &&
      this.gameState.state === GAME_STATES.WAITING
    ) {
      this.gameState.state = GAME_STATES.READY_CHECK;
    }

    if (this.isOfficial && !player.isBot && otherRealPlayers === 0) {
      this._scheduleOfficialPostJoinChat();
    }

    this.broadcastRoomState();
    this._notifyStateChange();
    return true;
  }

  removePlayer(id) {
    const leavingPlayer = this.players.get(id);
    const leavingTeam = leavingPlayer ? leavingPlayer.team : null;
    const wasRealPlayer = leavingPlayer && !leavingPlayer.isBot;

    this.players.delete(id);
    this.bots.delete(id);
    this.inputBuffer.removePlayer(id);
    this.readyPlayers.delete(id);

    if (this.isOfficial && wasRealPlayer) {
      const realPlayersLeft = [...this.players.values()].some((p) => !p.isBot);
      if (!realPlayersLeft) {
        this.stopTicking();
        this.gameState.reset();
        this.matchStartedAt = null;
        this.matchPersisted = false;
        this.readyPlayers.clear();
        for (const botId of this.bots.keys()) {
          this.readyPlayers.add(botId);
        }
        
        this._postJoinChatPosted = false;
        this.hostId = this.players.size ? this.players.keys().next().value : null;
        this._notifyStateChange();
        return;
      }
    }

    if (this.hostId === id && this.players.size > 0) {
      this.hostId = this.players.keys().next().value;

      const newHost = this.players.get(this.hostId);
      this.broadcast({
        type: Protocol.S_CHAT,
        name: 'Система',
        text: `${newHost ? newHost.name : 'Кто-то'} теперь хост`,
        time: Date.now()
      });
      
      if (this.isOfficial && newHost && !newHost.isBot && newHost.ws) {
        this._replayChatHistoryTo(newHost.ws);
      }
    }

    if (this.players.size === 0) {
      this.stopTicking();
      return;
    }

    if (leavingTeam !== null && this.gameState.state !== GAME_STATES.WAITING) {
      const teamStillHasPlayers = [...this.players.values()].some(p => p.team === leavingTeam);
      if (!teamStillHasPlayers) {
        
        const winningTeam = leavingTeam === 0 ? 1 : 0;
        this.gameState.state = GAME_STATES.MATCH_ENDED;
        this.gameState.scoring.winner = winningTeam;
        this.broadcast({
          type: Protocol.S_MATCH_END,
          winner: winningTeam,
          reason: 'forfeit',
          finalScore: this.gameState.scoring.serialize()
        });
        this._persistMatch(winningTeam, 'forfeit');
        this.stopTicking();
      }
    }

    this.broadcastRoomState();
    this._notifyStateChange();
  }

  _persistMatch(winner, reason) {
    if (this.matchPersisted || !this.matchHistory) return;
    this.matchPersisted = true;
    const team1 = [];
    const team2 = [];
    for (const p of this.players.values()) {
      (p.team === 0 ? team1 : team2).push({ id: p.id, name: p.name });
    }
    this.matchHistory.saveMatch({
      roomId: this.id,
      roomName: this.name,
      winner,
      score: this.gameState.scoring.serialize(),
      team1,
      team2,
      startedAt: this.matchStartedAt || Date.now(),
      endedAt: Date.now(),
      reason,
    }).catch((err) => console.error('saveMatch error:', err.message));
  }

  seedOfficialChatHistory() {
    if (!this.isOfficial) return;
    if (this._chatSeeded) return;
    this._chatSeeded = true;

    const botNames = [...this.players.values()]
      .filter((p) => p.isBot)
      .map((p) => p.name);
    if (botNames.length === 0) {
      console.warn(`[Room ${this.id}] seedOfficialChatHistory: no bots present, skipping prelude`);
      return;
    }

    const now = Date.now();
    for (let i = 0; i < OFFICIAL_CHAT_PRELUDE.length; i++) {
      const line = OFFICIAL_CHAT_PRELUDE[i];
      this.chatMessages.push({
        name: botNames[i % botNames.length],
        text: line.text,
        time: now - line.minutesAgo * 60_000,
      });
    }
  }

  _scheduleOfficialPostJoinChat() {
    if (!this.isOfficial) return;
    if (this._postJoinChatPosted) return;
    this._postJoinChatPosted = true;

    const botNames = [...this.players.values()]
      .filter((p) => p.isBot)
      .map((p) => p.name);
    if (botNames.length === 0) return;

    const variant = OFFICIAL_CHAT_POST_JOIN_VARIANTS[
      Math.floor(Math.random() * OFFICIAL_CHAT_POST_JOIN_VARIANTS.length)
    ];
    for (let i = 0; i < variant.length; i++) {
      const line = variant[i];
      const name = botNames[(OFFICIAL_CHAT_PRELUDE.length + i) % botNames.length];
      setTimeout(() => {
        const msg = { name, text: line.text, time: Date.now() };
        this.chatMessages.push(msg);
        if (this.chatMessages.length > 100) this.chatMessages.shift();
        this.broadcast({
          type: Protocol.S_CHAT,
          name: msg.name,
          text: msg.text,
          time: msg.time,
        });
      }, line.delayMs);
    }
  }

  _replayChatHistoryTo(ws) {
    if (!ws || ws.readyState !== 1) return;
    for (const msg of this.chatMessages) {
      this.send(ws, {
        type: Protocol.S_CHAT,
        name: msg.name,
        text: msg.text,
        time: msg.time,
      });
    }
  }

  addChatMessage(playerId, text) {
    const player = this.players.get(playerId);
    const name = player ? player.name : 'Unknown';
    const msg = { name, text, time: Date.now() };
    this.chatMessages.push(msg);
    
    if (this.chatMessages.length > 100) this.chatMessages.shift();
    
    this.broadcast({
      type: Protocol.S_CHAT,
      name,
      text,
      time: msg.time
    });
  }

  setReady(id) {
    if (this.gameState.state !== GAME_STATES.READY_CHECK) return;
    this.readyPlayers.add(id);
    this.broadcastRoomState();

    if (this.readyPlayers.size === this.players.size) {
      this.startMatch();
    }
  }

  setUnready(id) {
    if (this.gameState.state !== GAME_STATES.READY_CHECK) return;
    this.readyPlayers.delete(id);
    this.broadcastRoomState();
  }

  updateSettings(settings) {
    if (this.gameState.state !== GAME_STATES.WAITING) return false;
    if (typeof settings !== 'object' || settings === null) return false;

    if (settings.name != null) {
      this.name = String(settings.name).slice(0, 24) || this.name;
    }
    if (settings.maxPlayers != null) {
      const mp = Number(settings.maxPlayers);
      if ([2, 4].includes(mp) && mp >= this.players.size) {
        this.maxPlayers = mp;
      }
    }
    if (settings.gamesPerSet != null) {
      const g = Math.max(1, Math.min(9, Math.floor(Number(settings.gamesPerSet))));
      if (Number.isFinite(g)) this.gamesPerSet = g;
    }
    if (settings.setsToWin != null) {
      const s = Math.max(1, Math.min(5, Math.floor(Number(settings.setsToWin))));
      if (Number.isFinite(s)) this.setsToWin = s;
    }

    this.broadcastRoomState();
    this._notifyStateChange();
    return true;
  }

  hostStartGame(hostId) {
    if (hostId !== this.hostId) return false;
    if (this.players.size < 2) return false;
    if (this.gameState.state !== GAME_STATES.WAITING) return false;

    this.gameState.state = GAME_STATES.READY_CHECK;
    this.readyPlayers.clear();
    this.readyPlayers.add(hostId);
    this.broadcastRoomState();
    this._notifyStateChange();

    this.broadcast({
      type: Protocol.S_CHAT,
      name: 'Система',
      text: 'Хост начал игру. Нажмите «Готов»!',
      time: Date.now()
    });

    if (this.readyPlayers.size === this.players.size) {
      this.startMatch();
    }
    return true;
  }

  startMatch() {
    this.gameState.startMatch();
    this.matchStartedAt = Date.now();
    this.matchPersisted = false;

    const teams = { team1: [], team2: [] };
    const allPlayers = [];
    for (const p of this.players.values()) {
      const list = p.team === 0 ? teams.team1 : teams.team2;
      list.push({ id: p.id, name: p.name });
      allPlayers.push({ id: p.id, team: p.team, x: p.x, y: p.y, name: p.name });
    }

    this.broadcast({
      type: Protocol.S_MATCH_START,
      teams,
      players: allPlayers,
      servingTeam: 0,
      servingPlayerIndex: 0
    });

    this._notifyStateChange();
    this.startTicking();
  }

  startTicking() {
    if (this.tickInterval) return;
    this.tickInterval = setInterval(() => this.tick(), 1000 / SERVER_TICK_RATE);
  }

  stopTicking() {
    if (this.tickInterval) {
      clearInterval(this.tickInterval);
      this.tickInterval = null;
    }
  }

  tick() {
    const dt = this.dt;
    this.gameState.tick++;

    for (const [playerId, player] of this.players) {
      if (player.isBot) continue;
      const inputs = this.inputBuffer.getInputs(playerId);
      if (inputs && inputs.length > 0) {
        player.lastInput = inputs[inputs.length - 1];
      }
      if (player.lastInput) {
        player.applyInput(player.lastInput, dt);
      }
    }

    if (this.bots.size > 0) {
      const servingPlayerId = this.gameState.state === GAME_STATES.SERVING
        ? this.getServingPlayer(this.gameState.serveManager.servingTeam)?.id
        : null;
      for (const [botId, controller] of this.bots) {
        controller._isServingPlayer = servingPlayerId === botId;
        controller.tick(
          this.gameState,
          this.gameState.ball,
          this.physics,
          this.gameState.rallyTime,
          dt,
          this.players,
        );
      }
    }

    if (this.gameState.state === GAME_STATES.SERVING) {
      const servingTeam = this.gameState.serveManager.servingTeam;
      const servingPlayer = this.getServingPlayer(servingTeam);
      if (servingPlayer) {
        const result = this.gameState.updateServe(servingPlayer, dt);
        if (result === 'drop_fault') {
          const faultResult = this.gameState.serveManager.recordFault();
          if (faultResult === 'double_fault') {
            const scoringTeam = servingTeam === 0 ? 1 : 0;
            const scoreResult = this.gameState.handlePointScored(scoringTeam);
            this.broadcast({
              type: Protocol.S_POINT_SCORED,
              team: scoringTeam,
              reason: 'Двойная ошибка',
              byPlayerId: servingPlayer.id,
              scoreResult,
            });
          } else {
            this.broadcast({ type: Protocol.S_CHAT, name: 'Система', text: 'Ошибка подачи!', time: Date.now() });
            this.gameState.setupServe();
          }
        }
      }
    }

    if (this.gameState.state === GAME_STATES.PLAYING) {
      
      if (this.gameState.ball.state === BALL_STATES.IN_PLAY && !this.gameState.ball.isServe) {
        this.gameState.rallyTime += dt;
      }
      this.physics.update(this.gameState.ball, [...this.players.values()], dt);

      const result = this.gameState.rules.evaluate(
        this.gameState.ball,
        [...this.players.values()],
        this.gameState
      );

      if (result) {
        const lastHitterId = this.gameState.ball.lastHitBy;
        const scoreResult = this.gameState.handlePointScored(result.team);
        this.broadcast({
          type: Protocol.S_POINT_SCORED,
          team: result.team,
          reason: result.reason,
          byPlayerId: lastHitterId,
          scoreResult
        });
      }
    }

    if (this.gameState.state === GAME_STATES.POINT_SCORED) {
      this.gameState.updatePointPause(dt);
    }

    if (this.gameState.state === GAME_STATES.MATCH_ENDED) {
      this.broadcast({
        type: Protocol.S_MATCH_END,
        winner: this.gameState.scoring.winner,
        finalScore: this.gameState.scoring.serialize()
      });
      this._persistMatch(this.gameState.scoring.winner, 'match_end');
      this.stopTicking();
      this._notifyStateChange();
      return;
    }

    this.broadcastSnapshot();

    this.roomStateBroadcastTick++;
    if (this.roomStateBroadcastTick >= SERVER_TICK_RATE * 2) {
      this.roomStateBroadcastTick = 0;
      this.broadcastRoomState();
    }
  }

  getServingPlayer(team) {
    for (const p of this.players.values()) {
      if (p.team === team) return p;
    }
    return null;
  }

  broadcastSnapshot() {
    const snapshot = {
      type: Protocol.S_SNAPSHOT,
      ...this.gameState.serialize(),
      players: [...this.players.values()].map(p => p.serialize())
    };

    for (const [playerId, player] of this.players) {
      if (player.ws && player.ws.readyState === 1) {
        const msg = {
          ...snapshot,
          ack: this.inputBuffer.getLastProcessedSeq(playerId)
        };
        this.send(player.ws, msg);
      }
    }
  }

  broadcastRoomState() {
    const playerList = [...this.players.values()].map(p => ({
      id: p.id,
      name: p.name,
      team: p.team,
      ready: this.readyPlayers.has(p.id),
      isBot: !!p.isBot,
      rtt: p.isBot ? 0 : (p.rtt || 0),
    }));

    this.broadcast({
      type: Protocol.S_ROOM_STATE,
      roomId: this.id,
      roomName: this.name,
      hostId: this.hostId,
      players: playerList,
      status: this.gameState.state,
      maxPlayers: this.maxPlayers,
      isOfficial: !!this.isOfficial,
      config: { gamesPerSet: this.gamesPerSet, setsToWin: this.setsToWin }
    });
  }

  broadcast(msg) {
    const data = Protocol.encode(msg);
    for (const player of this.players.values()) {
      if (player.ws && player.ws.readyState === 1) {
        player.ws.send(data);
      }
    }
  }

  send(ws, msg) {
    if (ws && ws.readyState === 1) {
      ws.send(Protocol.encode(msg));
    }
  }

  get playerCount() {
    return this.players.size;
  }

  get isFull() {
    return this.players.size >= this.maxPlayers;
  }

  get isEmpty() {
    return this.players.size === 0;
  }
}
