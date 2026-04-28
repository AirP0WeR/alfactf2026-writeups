import * as Protocol from '../../shared/Protocol.js';

export class MessageHandler {
  constructor(gameServer) {
    this.gameServer = gameServer;
  }

  handle(playerId, data) {
    let msg;
    try {
      msg = Protocol.decode(data);
    } catch (e) {
      console.error(`Invalid message from ${playerId}:`, e.message);
      return;
    }

    switch (msg.type) {
      case Protocol.C_JOIN:
        this.gameServer.handleJoin(playerId, msg);
        break;
      case Protocol.C_READY:
        this.gameServer.handleReady(playerId);
        break;
      case Protocol.C_UNREADY:
        this.gameServer.handleUnready(playerId);
        break;
      case Protocol.C_INPUT:
        this.gameServer.handleInput(playerId, msg);
        break;
      case Protocol.C_SHOT:
        this.gameServer.handleShot(playerId, msg);
        break;
      case Protocol.C_PING:
        this.gameServer.handlePing(playerId, msg);
        break;
      case Protocol.C_CREATE_ROOM:
        this.gameServer.handleCreateRoom(playerId, msg);
        break;
      case Protocol.C_LIST_ROOMS:
        this.gameServer.handleListRooms(playerId);
        break;
      case Protocol.C_CHAT:
        this.gameServer.handleChat(playerId, msg);
        break;
      case Protocol.C_START_GAME:
        this.gameServer.handleStartGame(playerId);
        break;
      case Protocol.C_SERVE_TOSS:
        this.gameServer.handleServeToss(playerId);
        break;
      case Protocol.C_SERVE_HIT:
        this.gameServer.handleServeHit(playerId, msg);
        break;
      case Protocol.C_LIST_MATCHES:
        this.gameServer.handleListMatches(playerId);
        break;
      case Protocol.C_LIST_OFFICIAL:
        this.gameServer.handleListOfficial(playerId);
        break;
      case Protocol.C_LEAVE_ROOM:
        this.gameServer.handleLeaveRoom(playerId, msg);
        break;
      case Protocol.C_REQUEST_HOSTING_NAME:
        this.gameServer.handleRequestHostingName(playerId);
        break;
      case Protocol.C_USER_KICK:
        this.gameServer.handleUserKick(playerId, msg);
        break;
      case Protocol.C_ADMIN_UPDATE_SETTINGS:
        this.gameServer.handleAdminUpdateSettings(playerId, msg);
        break;
      case Protocol.C_ADMIN_CLOSE_ROOM:
        this.gameServer.handleAdminCloseRoom(playerId);
        break;
      default:
        console.warn(`Unknown message type: ${msg.type}`);
    }
  }
}
