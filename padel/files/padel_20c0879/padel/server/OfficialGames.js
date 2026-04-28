import { randomUUID } from 'crypto';

const BOT_NAMES = [
  'Павел', 'Артём', 'Ольга', 'Дмитрий', 'Анна', 'Сергей', 'София', 'Максим',
  'Елена', 'Роман', 'Вера', 'Никита', 'Дарья', 'Михаил', 'Ирина', 'Андрей',
  'Полина', 'Егор', 'Марина', 'Виктор', 'Лариса', 'Алексей', 'Наталья', 'Иван',
];

const ROOM_NAMES = [
  'Центральный корт',
  'Падел-клуб «Олимп»',
  'Арена «Москва»',
  'Крытый корт «Спартак»',
  'Клуб «Динамо»',
  'Корт «Северный»',
  'Падел «Чемпион»',
  'Клуб «Восток»',
];

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function pickUniqueNames(pool, n) {
  const copy = [...pool];
  const out = [];
  for (let i = 0; i < n && copy.length > 0; i++) {
    const idx = Math.floor(Math.random() * copy.length);
    out.push(copy.splice(idx, 1)[0]);
  }
  return out;
}

export function mintOfficialRoomId() {
  return `official_${randomUUID()}`;
}

export function isOfficialRoomId(id) {
  return typeof id === 'string' && id.startsWith('official_');
}

function generateSpecs(username, count) {
  const roomPool = [...ROOM_NAMES];
  const specs = [];
  for (let i = 0; i < count; i++) {
    const nameIdx = roomPool.length > 0
      ? Math.floor(Math.random() * roomPool.length)
      : -1;
    const name = nameIdx >= 0 ? roomPool.splice(nameIdx, 1)[0] : pick(ROOM_NAMES);
    specs.push({
      id: mintOfficialRoomId(),
      name,
      maxPlayers: 4,
      gamesPerSet: 6,
      setsToWin: 2,
      ownerUsername: username,
      botNames: pickUniqueNames(BOT_NAMES, 3),
    });
  }
  return specs;
}

export async function ensureOfficialGamesSpec(sessionStore, username, { count = 3 } = {}) {
  if (!sessionStore || !username) return [];
  const existing = await sessionStore.getOfficialGamesSpec(username);
  if (Array.isArray(existing) && existing.length >= count) return existing;
  const specs = generateSpecs(username, count);
  await sessionStore.setOfficialGamesSpec(username, specs);
  return specs;
}

export function specToMeta(spec) {
  return {
    id: spec.id,
    name: spec.name,
    players: (spec.botNames || []).length,
    maxPlayers: spec.maxPlayers,
    status: 'waiting',
    nodeId: null,
    config: { gamesPerSet: spec.gamesPerSet, setsToWin: spec.setsToWin },
  };
}
