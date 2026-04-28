import Redis from 'ioredis';

const HEARTBEAT_INTERVAL_MS = 2000;
const HEARTBEAT_TTL_SEC = 6;

export class RedisRoomRegistry {
  constructor({ url, nodeId }) {
    this.nodeId = nodeId;
    this.url = url;
    
    this.redis = new Redis(url, { lazyConnect: true, maxRetriesPerRequest: 3 });
    this.sub = new Redis(url, { lazyConnect: true, maxRetriesPerRequest: 3 });

    this.localCache = new Map();
    this.changeListeners = new Set();
    this.heartbeatTimer = null;
  }

  async connect() {
    await this.redis.connect();
    await this.sub.connect();

    await this.redis.sadd('nodes', this.nodeId);
    await this._refreshHeartbeat();

    await this._cleanupNodeRooms(this.nodeId);

    await this.sub.subscribe('rooms:changes');
    this.sub.on('message', (channel, msg) => {
      if (channel !== 'rooms:changes') return;
      try {
        const payload = JSON.parse(msg);
        this._handleRemoteChange(payload).catch((err) =>
          console.error('registry change handler error:', err.message),
        );
      } catch (e) {
        console.error('bad rooms:changes payload:', e.message);
      }
    });

    await this._loadAllRooms();

    this.heartbeatTimer = setInterval(() => {
      this._refreshHeartbeat().catch((err) =>
        console.error('heartbeat error:', err.message),
      );
      this._pruneDeadNodes().catch((err) =>
        console.error('prune dead nodes error:', err.message),
      );
    }, HEARTBEAT_INTERVAL_MS);

    console.log(`[registry] connected as node ${this.nodeId}`);
  }

  async disconnect() {
    if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
    try {
      await this._cleanupNodeRooms(this.nodeId);
      await this.redis.srem('nodes', this.nodeId);
      await this.redis.del(`node:${this.nodeId}:alive`);
    } catch (e) {
      
    }
    try { await this.sub.quit(); } catch {}
    try { await this.redis.quit(); } catch {}
  }

  async _refreshHeartbeat() {
    await this.redis.set(`node:${this.nodeId}:alive`, '1', 'EX', HEARTBEAT_TTL_SEC);
  }

  async _pruneDeadNodes() {
    const nodes = await this.redis.smembers('nodes');
    for (const nid of nodes) {
      if (nid === this.nodeId) continue;
      const alive = await this.redis.exists(`node:${nid}:alive`);
      if (!alive) {
        
        const gotLock = await this.redis.set(
          `cleanup:${nid}`, this.nodeId, 'NX', 'EX', 10,
        );
        if (gotLock) {
          console.log(`[registry] pruning dead node ${nid}`);
          await this._cleanupNodeRooms(nid);
          await this.redis.srem('nodes', nid);
        }
      }
    }
  }

  async _cleanupNodeRooms(nodeId) {
    const key = `node:${nodeId}:rooms`;
    const rooms = await this.redis.smembers(key);
    if (rooms.length === 0) {
      await this.redis.del(key);
      return;
    }
    const pipe = this.redis.pipeline();
    for (const roomId of rooms) {
      pipe.del(`room:${roomId}`);
      pipe.srem('rooms:index', roomId);
    }
    pipe.del(key);
    await pipe.exec();
    
    for (const roomId of rooms) {
      await this.redis.publish('rooms:changes', JSON.stringify({ type: 'remove', roomId }));
    }
  }

  async _loadAllRooms() {
    const ids = await this.redis.smembers('rooms:index');
    for (const roomId of ids) {
      const data = await this.redis.hgetall(`room:${roomId}`);
      if (data && data.nodeId) this.localCache.set(roomId, this._deserializeRoom(data));
    }
  }

  async _handleRemoteChange({ type, roomId }) {
    if (type === 'remove') {
      this.localCache.delete(roomId);
    } else if (type === 'upsert') {
      const data = await this.redis.hgetall(`room:${roomId}`);
      if (data && data.nodeId) {
        this.localCache.set(roomId, this._deserializeRoom(data));
      }
    }
    this._emitChange();
  }

  _deserializeRoom(data) {
    return {
      id: data.id,
      nodeId: data.nodeId,
      name: data.name,
      hostName: data.hostName,
      players: parseInt(data.players || '0', 10),
      maxPlayers: parseInt(data.maxPlayers || '4', 10),
      status: data.status,
      gamesPerSet: parseInt(data.gamesPerSet || '6', 10),
      setsToWin: parseInt(data.setsToWin || '2', 10),
      updatedAt: parseInt(data.updatedAt || '0', 10),
    };
  }

  async upsertRoom(room) {
    const key = `room:${room.id}`;
    const payload = {
      id: room.id,
      nodeId: this.nodeId,
      name: room.name || 'Padel Match',
      hostName: room.hostName || '—',
      players: String(room.players ?? 0),
      maxPlayers: String(room.maxPlayers ?? 4),
      status: room.status || 'waiting',
      gamesPerSet: String(room.gamesPerSet ?? 6),
      setsToWin: String(room.setsToWin ?? 2),
      updatedAt: String(Date.now()),
    };
    const pipe = this.redis.pipeline();
    pipe.hset(key, payload);
    pipe.sadd('rooms:index', room.id);
    pipe.sadd(`node:${this.nodeId}:rooms`, room.id);
    await pipe.exec();
    this.localCache.set(room.id, this._deserializeRoom(payload));
    await this.redis.publish('rooms:changes', JSON.stringify({ type: 'upsert', roomId: room.id }));
    this._emitChange();
  }

  async removeRoom(roomId) {
    const pipe = this.redis.pipeline();
    pipe.del(`room:${roomId}`);
    pipe.srem('rooms:index', roomId);
    pipe.srem(`node:${this.nodeId}:rooms`, roomId);
    await pipe.exec();
    this.localCache.delete(roomId);
    await this.redis.publish('rooms:changes', JSON.stringify({ type: 'remove', roomId }));
    this._emitChange();
  }

  getAllRooms() {
    return [...this.localCache.values()].sort((a, b) => b.updatedAt - a.updatedAt);
  }

  async getRoomNode(roomId) {
    const room = this.localCache.get(roomId);
    if (room) return room.nodeId;
    const data = await this.redis.hgetall(`room:${roomId}`);
    if (!data || !data.nodeId) return null;
    const hydrated = this._deserializeRoom(data);
    this.localCache.set(roomId, hydrated);
    return hydrated.nodeId;
  }

  onChange(callback) {
    this.changeListeners.add(callback);
    return () => this.changeListeners.delete(callback);
  }

  _emitChange() {
    for (const cb of this.changeListeners) {
      try { cb(); } catch (e) { console.error('onChange listener error:', e.message); }
    }
  }

  async incrStat(name, by = 1) {
    try {
      await this.redis.incrby(`stats:${name}`, by);
    } catch (e) {
      
    }
  }

  async getStats() {
    const keys = ['stats:connections_total', 'stats:rooms_created', 'stats:matches_played', 'stats:points_scored'];
    const values = await this.redis.mget(keys);
    return {
      connectionsTotal: parseInt(values[0] || '0', 10),
      roomsCreated: parseInt(values[1] || '0', 10),
      matchesPlayed: parseInt(values[2] || '0', 10),
      pointsScored: parseInt(values[3] || '0', 10),
    };
  }
}
