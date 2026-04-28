import { Game } from './Game.js';
import { Connection } from './network/Connection.js';
import * as Protocol from '../../shared/Protocol.js';

const canvas = document.getElementById('game-canvas');
const lobby = document.getElementById('lobby');
const hud = document.getElementById('hud');
const chatContainer = document.getElementById('chat-container');

let game = null;
let connection = null;
let currentRoomId = null;
let isHost = false;
let myPlayerId = null;
let inWaitingRoom = false;
let pendingJoin = null;
let myUsername = null;

function getPlayerName() {
  return (myUsername || 'Игрок').slice(0, 12);
}

function showNotice(title, message) {
  const overlay = document.getElementById('notice-overlay');
  document.getElementById('notice-title').textContent = title || 'Уведомление';
  document.getElementById('notice-message').textContent = message || '';
  overlay.classList.remove('hidden');
}

function hideNotice() {
  document.getElementById('notice-overlay').classList.add('hidden');
}

document.getElementById('notice-ok').addEventListener('click', hideNotice);
document.getElementById('notice-overlay').addEventListener('click', (e) => {
  if (e.target === document.getElementById('notice-overlay')) hideNotice();
});

let _passwordResolve = null;

function showPasswordPrompt(errorMsg) {
  return new Promise((resolve) => {
    _passwordResolve = resolve;
    const overlay = document.getElementById('password-overlay');
    const input = document.getElementById('password-prompt-input');
    const errorEl = document.getElementById('password-error');
    input.value = '';
    if (errorMsg) {
      errorEl.textContent = errorMsg;
      errorEl.classList.remove('hidden');
    } else {
      errorEl.textContent = '';
      errorEl.classList.add('hidden');
    }
    overlay.classList.remove('hidden');
    input.focus();
  });
}

function hidePasswordPrompt(value) {
  document.getElementById('password-overlay').classList.add('hidden');
  if (_passwordResolve) {
    _passwordResolve(value);
    _passwordResolve = null;
  }
}

document.getElementById('password-prompt-ok').addEventListener('click', () => {
  const pw = document.getElementById('password-prompt-input').value;
  hidePasswordPrompt(pw || '');
});
document.getElementById('password-prompt-cancel').addEventListener('click', () => {
  hidePasswordPrompt(null);
});
document.getElementById('password-overlay').addEventListener('click', (e) => {
  if (e.target === document.getElementById('password-overlay')) hidePasswordPrompt(null);
});
document.getElementById('password-prompt-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    const pw = document.getElementById('password-prompt-input').value;
    hidePasswordPrompt(pw || '');
  }
});

function startLocalGame() {
  lobby.classList.add('hidden');
  hud.classList.remove('hidden');
  canvas.classList.remove('hidden');
  
  game = new Game(canvas);
  game.startLocal();
}

function getBaseUrl() {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}`;
}

async function ensureConnection(pinnedTarget) {
  if (connection && connection.connected) return connection;

  connection = new Connection();
  
  registerConnectionHandlers(connection);
  let target;
  if (pinnedTarget !== undefined) {
    target = pinnedTarget;
  } else {
    const res = await fetch('/whoami', { credentials: 'same-origin' });
    const data = await res.json();
    if (!data || !data.authenticated) {
      throw new Error('unauthorized');
    }
    target = (data.currentRoomNode && data.currentRoomId)
      ? { nodeId: data.currentRoomNode, roomId: data.currentRoomId }
      : {};
  }
  await connection.connect(getBaseUrl(), target);
  return connection;
}

function registerConnectionHandlers(conn) {
  
  conn.on(Protocol.S_ROOM_LIST, (msg) => {
    renderRoomList(msg.rooms || []);
  });

  conn.on(Protocol.S_OFFICIAL_LIST, (msg) => {
    renderOfficialList(msg.games || []);
  });

  conn.on(Protocol.S_HOSTING_NAME, (msg) => {
    const roomNameInput = document.getElementById('room-name-input');
    if (roomNameInput && msg.name) {
      roomNameInput.value = msg.name;
      roomNameInput.placeholder = '';
      roomNameInput.title = 'Это уникальное имя вашей комнаты';
    }
  });

  conn.on(Protocol.S_CHAT, (msg) => {
    appendChatMessage(msg.name, msg.text);
  });

  conn.on(Protocol.S_WELCOME, (msg) => {
    myPlayerId = msg.playerId;
    isHost = msg.hostId === msg.playerId;
    currentRoomId = msg.roomId;
    pendingJoin = null;
    if (!inWaitingRoom && !game) {
      setupGameHandlers();
    }
  });

  conn.on(Protocol.S_KICKED, (msg) => {
    showNotice('Вы исключены', msg.message || 'Вы были исключены хостом');
    returnToLobby();
  });

  conn.on(Protocol.S_ERROR, async (msg) => {
    if (pendingJoin) {
      const join = pendingJoin;
      pendingJoin = null;
      if (msg.message === 'Неверный пароль') {
        returnToLobby();
        const errorText = join.password ? 'Неверный пароль. Попробуйте ещё раз.' : null;
        const pw = await showPasswordPrompt(errorText);
        if (pw != null) {
          joinRoom(join.roomId, pw);
        }
      } else {
        showNotice('Ошибка', msg.message || 'Не удалось войти в комнату');
        returnToLobby();
      }
      return;
    }
    const statusEl = document.getElementById('admin-status');
    if (statusEl && inWaitingRoom) {
      statusEl.textContent = msg.message || 'Ошибка';
      statusEl.style.color = '#e63946';
    }
  });

  conn.on(Protocol.S_REDIRECT, async (msg) => {
    console.log(`[cluster] redirect to node=${msg.nodeId} for room=${msg.roomId}`);
    try {
      await conn.reconnectTo({ nodeId: msg.nodeId, roomId: msg.roomId });
      
      if (pendingJoin) {
        conn.sendJoin(pendingJoin.name, pendingJoin.roomId, pendingJoin.password);
      }
    } catch (err) {
      console.error('redirect failed:', err);
    }
  });
}

function renderRoomList(rooms) {
  const body = document.getElementById('room-list-body');
  if (!rooms || rooms.length === 0) {
    body.innerHTML = '<div class="room-list-empty">Нет доступных игр. Создайте свою!</div>';
    return;
  }

  body.innerHTML = rooms.map(r => {
    const canJoin = r.status === 'waiting' && r.players < r.maxPlayers;
    const statusClass = r.status === 'waiting' ? 'waiting' : 'playing';
    const lockIcon = r.hasPassword ? ' &#128274;' : '';
    return `
      <div class="room-list-item">
        <div class="room-list-info">
          <div class="room-list-name">${escapeHtml(r.name)}${lockIcon}</div>
          <div class="room-list-meta">Хост: ${escapeHtml(r.hostName)} &middot; ${r.players}/${r.maxPlayers} &middot; ${r.config.gamesPerSet}Г/${r.config.setsToWin}С</div>
        </div>
        <span class="room-list-status ${statusClass}">${r.status === 'waiting' ? 'ожидание' : 'в игре'}</span>
        <button class="room-list-join" data-room="${r.id}" ${r.hasPassword ? 'data-locked="1"' : ''} ${canJoin ? '' : 'disabled'}>Войти</button>
      </div>
    `;
  }).join('');

  body.querySelectorAll('.room-list-join').forEach(btn => {
    btn.addEventListener('click', async () => {
      const roomId = btn.dataset.room;
      if (btn.dataset.locked) {
        const pw = await showPasswordPrompt();
        if (pw == null) return;
        joinRoom(roomId, pw);
      } else {
        joinRoom(roomId);
      }
    });
  });
}

function renderInGameAdmin(msg) {
  const panel = document.getElementById('admin-panel');
  const ingame = document.getElementById('admin-ingame-players');
  if (!panel || !ingame) return;

  if (!isHost) {
    panel.classList.add('hidden');
    ingame.classList.remove('visible');
    return;
  }

  panel.classList.remove('hidden');
  document.getElementById('admin-lobby-controls').classList.add('hidden');
  ingame.classList.add('visible');

  const rows = msg.players.map((p) => {
    const isMe = p.id === myPlayerId;
    const botTag = p.isBot ? ' <span style="color:#666">[бот]</span>' : '';
    const pingClass = p.isBot
      ? 'bot'
      : (p.rtt > 200 ? 'bad' : p.rtt > 100 ? 'high' : '');
    const pingText = p.isBot ? '—' : `${p.rtt || 0} мс`;
    const kickBtn = (isMe || p.isBot)
      ? ''
      : `<button class="kick-btn" data-kick="${escapeHtml(p.id)}">Выгнать</button>`;
    return `
      <div class="admin-player-row">
        <span class="admin-player-name">${escapeHtml(p.name)}${botTag}</span>
        <span class="admin-player-ping ${pingClass}">${pingText}</span>
        ${kickBtn}
      </div>
    `;
  }).join('');
  ingame.innerHTML = rows;

  ingame.querySelectorAll('.kick-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.kick;
      if (targetId && connection && connection.connected) {
        connection.sendUserKick(targetId);
      }
    });
  });
}

function renderOfficialList(games) {
  const body = document.getElementById('official-list-body');
  if (!games || games.length === 0) {
    body.innerHTML = '<div class="room-list-empty">Нет официальных игр.</div>';
    return;
  }

  body.innerHTML = games.map((g) => {
    const statusLabel = g.status === 'waiting' || g.status === 'ready_check'
      ? 'ожидание'
      : 'в игре';
    const statusClass = g.status === 'playing' || g.status === 'serving'
      ? 'playing'
      : 'waiting';
    return `
      <div class="room-list-item official">
        <div class="room-list-info">
          <div class="room-list-name">${escapeHtml(g.name)}</div>
          <div class="room-list-meta">${g.players}/${g.maxPlayers} &middot; ${g.config.gamesPerSet}Г/${g.config.setsToWin}С</div>
        </div>
        <span class="room-list-status ${statusClass}">${statusLabel}</span>
        <button class="room-list-join" data-official="${g.id}" data-node="${g.nodeId || ''}">Войти</button>
      </div>
    `;
  }).join('');

  body.querySelectorAll('.room-list-join').forEach((btn) => {
    btn.addEventListener('click', () => {
      const roomId = btn.dataset.official;
      joinRoom(roomId);
    });
  });
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

document.getElementById('btn-create').addEventListener('click', async () => {
  document.getElementById('create-room-dialog').classList.remove('hidden');
  document.getElementById('room-actions').classList.add('hidden');
  document.getElementById('room-list').classList.add('hidden');
  document.getElementById('official-list').classList.add('hidden');
  
  try {
    await ensureConnection();
    connection.sendRequestHostingName();
  } catch {
    
  }
});

document.getElementById('btn-create-cancel').addEventListener('click', () => {
  document.getElementById('create-room-dialog').classList.add('hidden');
  document.getElementById('room-actions').classList.remove('hidden');
  document.getElementById('room-list').classList.remove('hidden');
  document.getElementById('official-list').classList.remove('hidden');
});

document.getElementById('btn-create-confirm').addEventListener('click', async () => {
  try {
    await ensureConnection();
  } catch {
    console.warn('No server found, starting local mode');
    startLocalGame();
    return;
  }

  const password = document.getElementById('room-password-input').value.trim();
  const config = {
    playerName: getPlayerName(),
    name: document.getElementById('room-name-input').value.trim() || 'Матч падел',
    maxPlayers: parseInt(document.getElementById('room-max-players').value),
    gamesPerSet: parseInt(document.getElementById('room-games-per-set').value),
    setsToWin: parseInt(document.getElementById('room-sets-to-win').value),
    password: password || undefined
  };

  connection.sendCreateRoom(config);

  setupGameHandlers();
});

async function joinRoom(roomId, password) {
  try {
    await ensureConnection();
  } catch {
    console.warn('No server found, starting local mode');
    startLocalGame();
    return;
  }

  const name = getPlayerName();
  pendingJoin = { roomId, name, password };
  connection.sendJoin(name, roomId, password);
  setupGameHandlers();
}

document.getElementById('btn-quick-join').addEventListener('click', async () => {
  try {
    await ensureConnection();
  } catch {
    console.warn('No server found, starting local mode');
    startLocalGame();
    return;
  }

  const name = getPlayerName();
  pendingJoin = { roomId: null, name };
  connection.sendJoin(name, null);
  setupGameHandlers();
});

function returnToLobby() {
  inWaitingRoom = false;
  currentRoomId = null;
  isHost = false;
  if (game) {
    try { game.stop(); } catch {}
    game = null;
  }
  
  try {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  } catch {}
  canvas.classList.add('hidden');
  document.getElementById('room-view').classList.add('hidden');
  document.getElementById('admin-panel').classList.add('hidden');
  document.getElementById('admin-lobby-controls').classList.remove('hidden');
  const ingame = document.getElementById('admin-ingame-players');
  if (ingame) {
    ingame.classList.remove('visible');
    ingame.innerHTML = '';
  }
  document.getElementById('room-actions').classList.remove('hidden');
  document.getElementById('room-list').classList.remove('hidden');
  document.getElementById('official-list').classList.remove('hidden');
  chatContainer.classList.add('hidden');
  hud.classList.add('hidden');
  lobby.classList.remove('hidden');
  if (connection && connection.connected) {
    connection.sendLeaveRoom();
    connection.sendListRooms();
    connection.sendListOfficial();
  }
}

document.getElementById('btn-exit-game').addEventListener('click', () => {
  returnToLobby();
});

document.getElementById('btn-leave-room').addEventListener('click', () => {
  returnToLobby();
});

function showWaitingRoom() {
  inWaitingRoom = true;

  document.getElementById('room-actions').classList.add('hidden');
  document.getElementById('room-list').classList.add('hidden');
  document.getElementById('official-list').classList.add('hidden');
  document.getElementById('create-room-dialog').classList.add('hidden');
  document.getElementById('room-view').classList.remove('hidden');
  chatContainer.classList.remove('hidden');

  document.getElementById('chat-messages').innerHTML = '';
}

function updateWaitingRoom(msg) {
  if (!inWaitingRoom) {
    
    isHost = msg.hostId === myPlayerId;
    renderInGameAdmin(msg);
    return;
  }

  document.getElementById('room-id').textContent = msg.roomName || msg.roomId;

  const configInfo = document.getElementById('room-config-info');
  if (msg.config) {
    configInfo.textContent = `${msg.maxPlayers} игроков | ${msg.config.gamesPerSet} геймов | До ${msg.config.setsToWin} побед в сетах`;
  }

  isHost = msg.hostId === myPlayerId;

  const slotsEl = document.getElementById('player-slots');
  let slotsHtml = '';
  for (let i = 0; i < msg.maxPlayers; i++) {
    const p = msg.players[i];
    if (p) {
      const teamClass = p.team === 0 ? 'team1' : 'team2';
      const hostBadge = p.id === msg.hostId ? ' (Хост)' : '';
      const readyBadge = (msg.status === 'ready_check' && p.ready) ? ' <span style="color:#2ecc71">&#10003;</span>' : '';
      const canKick = isHost && p.id !== myPlayerId && msg.status === 'waiting';
      const kickBtn = canKick
        ? `<button class="kick-btn" data-kick="${escapeHtml(p.id)}">Выгнать</button>`
        : '';
      slotsHtml += `<div class="player-slot filled ${teamClass}"><div class="player-slot-row"><span>${escapeHtml(p.name)}${hostBadge}${readyBadge}</span>${kickBtn}</div></div>`;
    } else {
      slotsHtml += `<div class="player-slot">Ожидание...</div>`;
    }
  }
  slotsEl.innerHTML = slotsHtml;

  slotsEl.querySelectorAll('.kick-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.kick;
      if (targetId && connection && connection.connected) {
        connection.sendUserKick(targetId);
      }
    });
  });

  const adminPanel = document.getElementById('admin-panel');
  const showAdmin = isHost && msg.status === 'waiting';
  adminPanel.classList.toggle('hidden', !showAdmin);
  if (showAdmin && !adminPanel.dataset.editing) {
    document.getElementById('admin-room-name').value = msg.roomName || '';
    document.getElementById('admin-max-players').value = String(msg.maxPlayers);
    if (msg.config) {
      document.getElementById('admin-games-per-set').value = String(msg.config.gamesPerSet);
      document.getElementById('admin-sets-to-win').value = String(msg.config.setsToWin);
    }
  }

  const btnReady = document.getElementById('btn-ready');
  const btnAdminStart = document.getElementById('btn-admin-start');
  const btnAdminCloseRoom = document.getElementById('btn-admin-close-room');
  btnAdminCloseRoom.classList.toggle('hidden', !!msg.isOfficial);
  const statusEl = document.getElementById('room-status');
  const isReadyCheck = msg.status === 'ready_check';
  const myReady = msg.players.find(p => p.id === myPlayerId);
  const amReady = myReady && myReady.ready;
  const readyCount = msg.players.filter(p => p.ready).length;

  if (isReadyCheck) {

    btnAdminStart.classList.add('hidden');
    if (amReady) {
      btnReady.textContent = 'Не готов';
      btnReady.dataset.action = 'unready';
      btnReady.disabled = false;
    } else {
      btnReady.textContent = 'Готов';
      btnReady.dataset.action = 'ready';
      btnReady.disabled = false;
    }
    btnReady.classList.remove('hidden');
    statusEl.textContent = `${readyCount}/${msg.players.length} игроков готовы`;
  } else {
    
    btnReady.classList.add('hidden');
    if (isHost) {
      btnAdminStart.classList.remove('hidden');
      if (msg.players.length < 2) {
        btnAdminStart.disabled = true;
        statusEl.textContent = 'Нужно минимум 2 игрока для старта';
      } else {
        btnAdminStart.disabled = false;
        statusEl.textContent = `${msg.players.length}/${msg.maxPlayers} игроков присоединились`;
      }
    } else {
      btnAdminStart.classList.add('hidden');
      statusEl.textContent = `Ожидание старта от хоста... (${msg.players.length}/${msg.maxPlayers})`;
    }
  }
}

function setupGameHandlers() {
  showWaitingRoom();

  connection.on(Protocol.S_ROOM_STATE, (msg) => {
    if (inWaitingRoom) {
      updateWaitingRoom(msg);
    } else {
      
      isHost = msg.hostId === myPlayerId;
      renderInGameAdmin(msg);
    }
    if (game) {
      game.handleRoomState(msg);
    }
  });

  connection.on(Protocol.S_MATCH_START, (msg) => {
    
    inWaitingRoom = false;
    document.getElementById('room-view').classList.add('hidden');
    
    document.getElementById('admin-lobby-controls').classList.add('hidden');
    lobby.classList.add('hidden');
    hud.classList.remove('hidden');
    canvas.classList.remove('hidden');

    game = new Game(canvas);
    game.connection = connection;

    connection.on(Protocol.S_SNAPSHOT, (snap) => game.handleSnapshot(snap));
    connection.on(Protocol.S_POINT_SCORED, (p) => game.handlePointScored(p));
    connection.on(Protocol.S_MATCH_END, (m) => game.handleMatchEnd(m));

    game.handleMatchStart(msg);
    game.startOnline(connection);
  });
}

document.getElementById('btn-ready').addEventListener('click', () => {
  if (!connection || !connection.connected) return;
  const btn = document.getElementById('btn-ready');
  if (btn.dataset.action === 'ready') {
    connection.sendReady();
  } else if (btn.dataset.action === 'unready') {
    connection.sendUnready();
  }
});

document.getElementById('btn-admin-start').addEventListener('click', () => {
  if (!connection || !connection.connected) return;
  connection.sendStartGame();
});

document.getElementById('btn-admin-close-room').addEventListener('click', () => {
  if (!connection || !connection.connected) return;
  connection.sendAdminCloseRoom();
});

document.getElementById('btn-admin-save').addEventListener('click', () => {
  if (!connection || !connection.connected) return;
  const settings = {
    name: document.getElementById('admin-room-name').value.trim(),
    maxPlayers: parseInt(document.getElementById('admin-max-players').value, 10),
    gamesPerSet: parseInt(document.getElementById('admin-games-per-set').value, 10),
    setsToWin: parseInt(document.getElementById('admin-sets-to-win').value, 10)
  };
  connection.sendAdminUpdateSettings(settings);
  const statusEl = document.getElementById('admin-status');
  statusEl.textContent = 'Настройки отправлены...';
  statusEl.style.color = '#888';
  setTimeout(() => { statusEl.textContent = ''; }, 2000);
});

['admin-room-name', 'admin-max-players', 'admin-games-per-set', 'admin-sets-to-win'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('focus', () => {
    document.getElementById('admin-panel').dataset.editing = '1';
  });
  el.addEventListener('blur', () => {
    delete document.getElementById('admin-panel').dataset.editing;
  });
});

const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');

function sendChatMessage() {
  const text = chatInput.value.trim();
  if (!text || !connection || !connection.connected) return;
  connection.sendChat(text);
  chatInput.value = '';
}

chatSend.addEventListener('click', sendChatMessage);

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    sendChatMessage();
    e.preventDefault();
  }
  
  e.stopPropagation();
});

chatInput.addEventListener('keyup', (e) => e.stopPropagation());

function appendChatMessage(name, text) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-msg';
  div.innerHTML = `<span class="chat-name">${escapeHtml(name)}:</span><span class="chat-text">${escapeHtml(text)}</span>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

document.getElementById('btn-refresh').addEventListener('click', async () => {
  try {
    await ensureConnection();
    connection.sendListRooms();
  } catch {
    
  }
});

document.getElementById('btn-rules').addEventListener('click', () => {
  document.getElementById('rules-overlay').classList.remove('hidden');
});
document.getElementById('rules-close').addEventListener('click', () => {
  document.getElementById('rules-overlay').classList.add('hidden');
});
document.getElementById('rules-overlay').addEventListener('click', (e) => {
  if (e.target === document.getElementById('rules-overlay')) {
    document.getElementById('rules-overlay').classList.add('hidden');
  }
});

document.getElementById('btn-local').addEventListener('click', () => {
  startLocalGame();
});

(async () => {
  try {
    const res = await fetch('/whoami', { credentials: 'same-origin' });
    const data = await res.json();
    if (!data || !data.authenticated) {
      window.location.href = '/client/login.html';
      return;
    }
    myUsername = data.username;
    document.getElementById('lobby-username').textContent = data.username;
    const roomNameInput = document.getElementById('room-name-input');
    if (roomNameInput) {
      
      roomNameInput.setAttribute('readonly', 'readonly');
      if (data.hostingRoomName) {
        roomNameInput.value = data.hostingRoomName;
        roomNameInput.title = 'Это уникальное имя вашей комнаты';
      } else {
        roomNameInput.value = '';
        roomNameInput.placeholder = 'Будет сгенерировано при создании';
        roomNameInput.title = 'Имя комнаты присваивается автоматически';
      }
    }
    const pinned = (data.currentRoomNode && data.currentRoomId)
      ? { nodeId: data.currentRoomNode, roomId: data.currentRoomId }
      : {};
    await ensureConnection(pinned);
    connection.sendListOfficial();
  } catch {
    
  }
})();

document.getElementById('btn-logout').addEventListener('click', async () => {
  try {
    await fetch('/logout', { method: 'POST', credentials: 'same-origin' });
  } catch {}
  window.location.href = '/client/login.html';
});
