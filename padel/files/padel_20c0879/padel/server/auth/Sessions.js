import { randomBytes, createHash } from 'crypto';
import Redis from 'ioredis';

const SESSION_COOKIE = 'padel_sid';
const SESSION_TTL_SECONDS = 86400;
const USER_KEY_PREFIX = 'user:';
const SESSION_KEY_PREFIX = 'session:';
const LOGOUT_CHANNEL = 'sessions:logout';
const HOSTROOM_CLAIM_PREFIX = 'hostroom:';
const OFFICIAL_KEY_PREFIX = 'official:';

const HOSTROOM_ADJECTIVES = [
  'Золотой', 'Серебряный', 'Северный', 'Южный', 'Королевский',
  'Чемпионский', 'Морской', 'Лазурный', 'Алмазный', 'Гранитный',
  'Солнечный', 'Звёздный', 'Изумрудный', 'Рубиновый', 'Снежный',
  'Огненный', 'Стальной', 'Восточный', 'Западный', 'Бронзовый',
];

const HOSTROOM_NOUNS = [
  'корт', 'матч', 'турнир', 'клуб', 'арена',
  'кубок', 'сет', 'финал', 'стадион', 'центр',
];

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function hashPassword(password, salt) {
  return createHash('sha256').update(salt + ':' + password).digest('hex');
}

function genSalt() {
  return randomBytes(8).toString('hex');
}

export class SessionStore {
  constructor({ url, redis } = {}) {
    if (redis) {
      this.redis = redis;
      this._ownsRedis = false;
    } else {
      if (!url) throw new Error('SessionStore: either url or redis client is required');
      this.redis = new Redis(url, { lazyConnect: true, maxRetriesPerRequest: 3 });
      this._ownsRedis = true;
    }
    
    this.sub = url
      ? new Redis(url, { lazyConnect: true, maxRetriesPerRequest: 3 })
      : this.redis.duplicate();
    this.logoutListeners = new Set();
  }

  async connect() {
    if (this._ownsRedis && this.redis.status !== 'ready') {
      await this.redis.connect();
    }
    if (this.sub.status === 'wait' || this.sub.status === 'end') {
      await this.sub.connect();
    }
    await this.sub.subscribe(LOGOUT_CHANNEL);
    this.sub.on('message', (channel, message) => {
      if (channel !== LOGOUT_CHANNEL) return;
      for (const cb of this.logoutListeners) {
        try { cb(message); } catch (e) {  }
      }
    });
  }

  async disconnect() {
    try { await this.sub.quit(); } catch {}
    if (this._ownsRedis) {
      try { await this.redis.quit(); } catch {}
    }
  }

  onLogout(callback) {
    this.logoutListeners.add(callback);
    return () => this.logoutListeners.delete(callback);
  }

  async registerUser(username, password) {
    if (!username || typeof username !== 'string') return { ok: false, error: 'invalid_username' };
    if (!password || typeof password !== 'string' || password.length < 9) {
      return { ok: false, error: 'invalid_password' };
    }
    const uname = username.trim();
    if (uname.length < 9 || uname.length > 32) return { ok: false, error: 'invalid_username' };
    if (!/^[a-zA-Z0-9_]+$/.test(uname)) return { ok: false, error: 'invalid_username' };

    const salt = genSalt();
    const payload = JSON.stringify({
      username: uname,
      salt,
      password: hashPassword(password, salt),
      createdAt: Date.now(),
    });
    
    const ok = await this.redis.set(USER_KEY_PREFIX + uname, payload, 'NX');
    if (!ok) return { ok: false, error: 'already_exists' };
    return { ok: true, username: uname };
  }

  async getUser(username) {
    const uname = (username || '').trim();
    if (!uname) return null;
    const raw = await this.redis.get(USER_KEY_PREFIX + uname);
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
  }

  async getOfficialGamesSpec(username) {
    const uname = (username || '').trim();
    if (!uname) return null;
    const raw = await this.redis.get(OFFICIAL_KEY_PREFIX + uname);
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
  }

  async setOfficialGamesSpec(username, specs) {
    const uname = (username || '').trim();
    if (!uname) return false;
    await this.redis.set(OFFICIAL_KEY_PREFIX + uname, JSON.stringify(specs));
    return true;
  }

  async _claimUniqueHostingRoomName() {
    
    for (let attempt = 0; attempt < 12; attempt++) {
      const adj = pickRandom(HOSTROOM_ADJECTIVES);
      const noun = pickRandom(HOSTROOM_NOUNS);
      const tag = Math.floor(100 + Math.random() * 900);
      const candidate = `${adj} ${noun} #${tag}`;
      const ok = await this.redis.set(HOSTROOM_CLAIM_PREFIX + candidate, '1', 'NX');
      if (ok) return candidate;
    }
    
    return `Корт ${Date.now().toString(36)}`;
  }

  async claimSessionHostingRoomName(sid) {
    if (!sid) return null;
    const raw = await this.redis.get(SESSION_KEY_PREFIX + sid);
    if (!raw) return null;
    const data = parseSessionValue(raw);
    if (!data) return null;
    if (data.hostingRoomName) return data.hostingRoomName;

    const name = await this._claimUniqueHostingRoomName();
    data.hostingRoomName = name;
    await this._writeSession(sid, data);
    return name;
  }

  async updateSession(sid, patch) {
    if (!sid || !patch) return false;
    const raw = await this.redis.get(SESSION_KEY_PREFIX + sid);
    if (!raw) return false;
    const data = parseSessionValue(raw) || {};
    Object.assign(data, patch);
    await this._writeSession(sid, data);
    return true;
  }

  async _writeSession(sid, data) {
    const payload = JSON.stringify(data);
    try {
      await this.redis.set(SESSION_KEY_PREFIX + sid, payload, 'KEEPTTL');
    } catch {
      await this.redis.set(SESSION_KEY_PREFIX + sid, payload, 'EX', SESSION_TTL_SECONDS);
    }
  }

  async authenticate(username, password) {
    const uname = (username || '').trim();
    if (!uname) return null;
    const raw = await this.redis.get(USER_KEY_PREFIX + uname);
    if (!raw) return null;
    let user;
    try { user = JSON.parse(raw); } catch { return null; }
    if (!user || user.password !== hashPassword(password, user.salt || '')) return null;
    return { username: user.username };
  }

  async createSession(username) {
    const sid = randomBytes(24).toString('hex');
    const payload = JSON.stringify({ username });
    await this.redis.set(SESSION_KEY_PREFIX + sid, payload, 'EX', SESSION_TTL_SECONDS);
    return sid;
  }

  async getSession(sid) {
    if (!sid) return null;
    const raw = await this.redis.get(SESSION_KEY_PREFIX + sid);
    if (!raw) return null;
    const data = parseSessionValue(raw);
    if (!data) return null;
    return {
      username: data.username,
      hostingRoomName: data.hostingRoomName || null,
      currentRoomId: data.currentRoomId || null,
      currentRoomNode: data.currentRoomNode || null,
    };
  }

  async destroySession(sid) {
    if (!sid) return false;
    
    const raw = await this.redis.get(SESSION_KEY_PREFIX + sid);
    const data = raw ? parseSessionValue(raw) : null;
    const removed = await this.redis.del(SESSION_KEY_PREFIX + sid);
    if (data && data.hostingRoomName) {
      await this.redis
        .del(HOSTROOM_CLAIM_PREFIX + data.hostingRoomName)
        .catch(() => {});
    }
    if (removed) {
      
      await this.redis.publish(LOGOUT_CHANNEL, sid);
    }
    return removed > 0;
  }
}

function parseSessionValue(raw) {
  if (!raw) return null;
  
  if (raw.startsWith('{')) {
    try { return JSON.parse(raw); } catch { return null; }
  }
  return { username: raw };
}

export { SESSION_COOKIE };

export function parseCookies(header) {
  const out = {};
  if (!header) return out;
  for (const part of header.split(';')) {
    const idx = part.indexOf('=');
    if (idx < 0) continue;
    const key = part.slice(0, idx).trim();
    const val = part.slice(idx + 1).trim();
    out[key] = decodeURIComponent(val);
  }
  return out;
}

export function cookieHeader(sid, { clear } = {}) {
  if (clear) {
    return `${SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0`;
  }
  return `${SESSION_COOKIE}=${sid}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${SESSION_TTL_SECONDS}`;
}
