import { createServer } from 'http';
import { readFile } from 'fs/promises';
import { join, extname } from 'path';
import { fileURLToPath } from 'url';
import { URL } from 'url';
import { WebSocketServer } from 'ws';
import { GameServer } from './GameServer.js';
import { RedisRoomRegistry } from './distributed/RedisRoomRegistry.js';
import { MatchHistory } from './distributed/MatchHistory.js';
import {
  SessionStore, parseCookies, cookieHeader, SESSION_COOKIE,
} from './auth/Sessions.js';
import { ensureOfficialGamesSpec } from './OfficialGames.js';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const ROOT = join(__dirname, '..');
const PORT = parseInt(process.env.PORT || '3000', 10);
const NODE_ID = process.env.NODE_ID || `node-${process.pid}`;
const REDIS_URL = process.env.REDIS_URL || null;

if (!REDIS_URL) {
  console.error(`[${NODE_ID}] REDIS_URL is required — session and user storage lives in Redis.`);
  console.error(`[${NODE_ID}] set REDIS_URL=redis://host:port and restart.`);
  process.exit(1);
}

const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const PUBLIC_PREFIXES = ['/client/css/', '/client/assets/', '/shared/'];
const PUBLIC_PATHS = new Set([
  '/login', '/register', '/logout',
  '/client/js/auth.js',
  '/client/login.html',
  '/favicon.ico', '/health',
]);

function isPublicPath(pathname) {
  if (PUBLIC_PATHS.has(pathname)) return true;
  return PUBLIC_PREFIXES.some((p) => pathname.startsWith(p));
}

function readRequestBody(req, limit = 4096) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => {
      data += chunk;
      if (data.length > limit) {
        reject(new Error('payload_too_large'));
        req.destroy();
      }
    });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

function parseForm(body, contentType = '') {
  if (contentType.includes('application/json')) {
    try { return JSON.parse(body || '{}'); } catch { return {}; }
  }
  
  const out = {};
  for (const part of (body || '').split('&')) {
    if (!part) continue;
    const idx = part.indexOf('=');
    const k = decodeURIComponent((idx < 0 ? part : part.slice(0, idx)).replace(/\+/g, ' '));
    const v = idx < 0 ? '' : decodeURIComponent(part.slice(idx + 1).replace(/\+/g, ' '));
    out[k] = v;
  }
  return out;
}

async function sessionFromRequest(req) {
  const cookies = parseCookies(req.headers.cookie || '');
  const sid = cookies[SESSION_COOKIE];
  const session = await sessionStore.getSession(sid);
  return { sid, session };
}

let registry = null;
let matchHistory = null;
let sessionStore = null;
try {
  registry = new RedisRoomRegistry({ url: REDIS_URL, nodeId: NODE_ID });
  await registry.connect();
  matchHistory = new MatchHistory(registry.redis);
  sessionStore = new SessionStore({ url: REDIS_URL, redis: registry.redis });
  await sessionStore.connect();
} catch (err) {
  console.error(`[${NODE_ID}] failed to connect to Redis at ${REDIS_URL}:`, err.message);
  process.exit(1);
}

const gameServer = new GameServer({ nodeId: NODE_ID, registry, matchHistory, sessionStore });

const httpServer = createServer(async (req, res) => {
  const pathname = req.url.split('?')[0];

  if (pathname === '/health') {
    const load = gameServer.snapshotLoad();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', ...load, uptime: process.uptime() }));
    return;
  }

  if (pathname === '/status') {
    const load = gameServer.snapshotLoad();
    const stats = registry ? await registry.getStats() : null;
    const allRooms = registry ? registry.getAllRooms().length : gameServer.rooms.size;
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      node: load,
      cluster: { totalRooms: allRooms, stats },
    }));
    return;
  }

  if (pathname === '/register' && req.method === 'POST') {
    try {
      const body = await readRequestBody(req);
      const fields = parseForm(body, req.headers['content-type'] || '');
      const result = await sessionStore.registerUser(fields.username, fields.password);
      if (!result.ok) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: result.error }));
        return;
      }
      
      try {
        await ensureOfficialGamesSpec(sessionStore, result.username);
      } catch (e) {
        console.error('ensureOfficialGamesSpec at register failed:', e.message);
      }
      const sid = await sessionStore.createSession(result.username);
      res.writeHead(200, {
        'Content-Type': 'application/json',
        'Set-Cookie': cookieHeader(sid),
      });
      res.end(JSON.stringify({
        ok: true,
        username: result.username,
      }));
    } catch (err) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: false, error: 'bad_request' }));
    }
    return;
  }

  if (pathname === '/login' && req.method === 'POST') {
    try {
      const body = await readRequestBody(req);
      const fields = parseForm(body, req.headers['content-type'] || '');
      const user = await sessionStore.authenticate(fields.username, fields.password);
      if (!user) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: 'invalid_credentials' }));
        return;
      }
      const sid = await sessionStore.createSession(user.username);
      res.writeHead(200, {
        'Content-Type': 'application/json',
        'Set-Cookie': cookieHeader(sid),
      });
      res.end(JSON.stringify({ ok: true, username: user.username }));
    } catch (err) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: false, error: 'bad_request' }));
    }
    return;
  }

  if (pathname === '/logout' && req.method === 'POST') {
    const { sid } = await sessionFromRequest(req);
    if (sid) {
      
      await sessionStore.destroySession(sid);
    }
    res.writeHead(200, {
      'Content-Type': 'application/json',
      'Set-Cookie': cookieHeader(null, { clear: true }),
    });
    res.end(JSON.stringify({ ok: true }));
    return;
  }

  if (pathname === '/whoami') {
    const { session } = await sessionFromRequest(req);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      authenticated: !!session,
      username: session ? session.username : null,
      hostingRoomName: session ? session.hostingRoomName || null : null,
      currentRoomId: session ? session.currentRoomId || null : null,
      currentRoomNode: session ? session.currentRoomNode || null : null,
    }));
    return;
  }

  if (pathname === '/' || pathname === '/client/index.html') {
    const { session } = await sessionFromRequest(req);
    if (!session) {
      res.writeHead(302, { 'Location': '/client/login.html' });
      res.end();
      return;
    }
  }

  let filePath = pathname === '/' ? '/client/index.html' : pathname;
  if (filePath.includes('..')) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  const fullPath = join(ROOT, filePath);
  const ext = extname(fullPath);
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  try {
    const data = await readFile(fullPath);
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  } catch (err) {
    if (err.code === 'ENOENT') {
      res.writeHead(404);
      res.end('Not found');
    } else {
      res.writeHead(500);
      res.end('Internal server error');
    }
  }
});

const wss = new WebSocketServer({ noServer: true });

sessionStore.onLogout((sid) => {
  try { gameServer.handleLogout(sid); } catch (e) {
    console.error('handleLogout failed:', e.message);
  }
  for (const client of wss.clients) {
    if (client.sessionSid === sid) {
      try { client.close(4010, 'logout'); } catch {}
    }
  }
});

httpServer.on('upgrade', async (req, socket, head) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = url.pathname;
  if (!pathname.startsWith('/ws')) {
    socket.destroy();
    return;
  }

  let sid, session;
  try {
    ({ sid, session } = await sessionFromRequest(req));
  } catch (e) {
    session = null;
  }
  if (!session) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
    return;
  }

  const requestedRoomId = url.searchParams.get('room') || null;
  
  let userRecord = null;
  try { userRecord = await sessionStore.getUser(session.username); } catch {}
  wss.handleUpgrade(req, socket, head, (ws) => {
    ws.sessionSid = sid;
    ws.username = session.username;
    ws.hostingRoomName = session.hostingRoomName || null;
    ws.currentRoomId = session.currentRoomId || null;
    ws.currentRoomNode = session.currentRoomNode || null;
    gameServer.onConnection(ws, { requestedRoomId });
  });
});

httpServer.listen(PORT, () => {
  console.log(`[${NODE_ID}] Padel server listening on :${PORT}`);
  if (registry) console.log(`[${NODE_ID}] clustered mode via Redis`);
});

async function shutdown(signal) {
  console.log(`[${NODE_ID}] ${signal} received, shutting down...`);
  httpServer.close();
  for (const client of wss.clients) {
    try { client.close(1001, 'server shutdown'); } catch {}
  }
  try { if (sessionStore) await sessionStore.disconnect(); } catch {}
  try { if (registry) await registry.disconnect(); } catch {}
  setTimeout(() => process.exit(0), 500);
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
