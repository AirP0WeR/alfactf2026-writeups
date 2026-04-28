import * as Protocol from '../../../shared/Protocol.js';

export class Connection {
  constructor() {
    this.ws = null;
    this.connected = false;
    this.playerId = null;
    this.roomId = null;
    this.nodeId = null;
    this.baseUrl = null;
    this.lastTarget = null;
    this.handlers = new Map();
    this.rtt = 0;
    this.pingInterval = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  buildUrl(baseUrl, { nodeId, roomId } = {}) {
    let path = '/ws';
    if (nodeId) path += `/${encodeURIComponent(nodeId)}`;
    const qs = roomId ? `?room=${encodeURIComponent(roomId)}` : '';
    return `${baseUrl}${path}${qs}`;
  }

  connect(baseUrl, target = {}) {
    this.baseUrl = baseUrl.replace(/\/ws.*$/, '');
    this.lastTarget = target;
    const url = this.buildUrl(this.baseUrl, target);

    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.connected = true;
        this.reconnectAttempts = 0;
        console.log('Connected to server');

        this.pingInterval = setInterval(() => this.ping(), 2000);

        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onclose = (event) => {
        this.connected = false;
        if (this.pingInterval) clearInterval(this.pingInterval);
        console.log('Disconnected from server', event && event.code);

        const code = event && event.code;
        if (code === 4003 || code === 4010 || code === 4002) return;

        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          const delay = Math.min(1000 * this.reconnectAttempts, 5000);
          console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);
          setTimeout(() => this.connect(this.baseUrl, this.lastTarget).catch(() => {}), delay);
        }
      };

      this.ws.onerror = (err) => {
        console.error('WebSocket error');
        reject(err);
      };
    });
  }

  handleMessage(data) {
    const msg = Protocol.decode(data);

    if (msg.type === Protocol.S_WELCOME) {
      this.playerId = msg.playerId;
      this.roomId = msg.roomId;
      if (msg.nodeId) this.nodeId = msg.nodeId;
    }

    if (msg.type === Protocol.S_PONG) {
      this.rtt = Date.now() - msg.t;
    }

    const handler = this.handlers.get(msg.type);
    if (handler) {
      handler(msg);
    }
  }

  on(type, handler) {
    this.handlers.set(type, handler);
  }

  send(msg) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(Protocol.encode(msg));
    }
  }

  sendInput(input) {
    this.send({
      type: Protocol.C_INPUT,
      ...input
    });
  }

  sendJoin(name, roomId, password) {
    const msg = { type: Protocol.C_JOIN, name, roomId };
    if (password) msg.password = password;
    this.send(msg);
  }

  sendReady() {
    this.send({ type: Protocol.C_READY });
  }

  sendUnready() {
    this.send({ type: Protocol.C_UNREADY });
  }

  sendShot(shotModifier, aimAngle) {
    this.send({
      type: Protocol.C_SHOT,
      shotModifier,
      aimAngle: aimAngle != null ? Math.round(aimAngle * 100) / 100 : null
    });
  }

  sendCreateRoom(config) {
    this.send({
      type: Protocol.C_CREATE_ROOM,
      ...config
    });
  }

  sendListRooms() {
    this.send({ type: Protocol.C_LIST_ROOMS });
  }

  sendChat(text) {
    this.send({
      type: Protocol.C_CHAT,
      text
    });
  }

  sendStartGame() {
    this.send({ type: Protocol.C_START_GAME });
  }

  sendServeToss() {
    this.send({ type: Protocol.C_SERVE_TOSS });
  }

  sendServeHit(aimAngle) {
    this.send({
      type: Protocol.C_SERVE_HIT,
      aimAngle: aimAngle != null ? Math.round(aimAngle * 100) / 100 : null
    });
  }

  ping() {
    this.send({
      type: Protocol.C_PING,
      t: Date.now(),
      rtt: this.rtt,
    });
  }

  disconnect() {
    this.maxReconnectAttempts = 0;
    if (this.pingInterval) clearInterval(this.pingInterval);
    if (this.ws) this.ws.close();
  }

  async reconnectTo({ nodeId, roomId }) {
    if (this.pingInterval) clearInterval(this.pingInterval);
    if (this.ws) {
      const old = this.ws;
      this.ws = null;
      
      old.onopen = null;
      old.onmessage = null;
      old.onclose = null;
      old.onerror = null;
      try { old.close(); } catch {}
    }
    this.connected = false;
    this.reconnectAttempts = 0;
    await this.connect(this.baseUrl, { nodeId, roomId });
  }

  sendListMatches() {
    this.send({ type: Protocol.C_LIST_MATCHES });
  }

  sendListOfficial() {
    this.send({ type: Protocol.C_LIST_OFFICIAL });
  }

  sendLeaveRoom() {
    this.send({ type: Protocol.C_LEAVE_ROOM });
  }

  sendRequestHostingName() {
    this.send({ type: Protocol.C_REQUEST_HOSTING_NAME });
  }

  sendUserKick(targetId) {
    this.send({ type: Protocol.C_USER_KICK, targetId });
  }

  sendAdminUpdateSettings(settings) {
    this.send({ type: Protocol.C_ADMIN_UPDATE_SETTINGS, settings });
  }

  sendAdminCloseRoom() {
    this.send({ type: Protocol.C_ADMIN_CLOSE_ROOM });
  }
}
