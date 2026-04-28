import { existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import Database from 'better-sqlite3';

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (db) return db;

  const dataDir = join(process.cwd(), 'data');
  const dbPath = join(dataDir, 'chococore.db');

  if (!existsSync(dataDir)) {
    mkdirSync(dataDir, { recursive: true });
  }

  db = new Database(dbPath);

  db.exec(`
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY,
      balance REAL DEFAULT 0,
      used_coupons TEXT DEFAULT '[]',
      cart TEXT DEFAULT '[]',
      created_at INTEGER DEFAULT (strftime('%s', 'now'))
    );

    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT,
      items TEXT,
      total REAL,
      created_at INTEGER DEFAULT (strftime('%s', 'now'))
    );
  `);

  return db;
}
