import { v4 as uuidv4 } from 'uuid';
import { getDb } from './db';

export interface Session {
  id: string;
  balance: number;
  used_coupons: string[];
  cart: CartItem[];
}

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

interface SessionRow {
  id: string;
  balance: number;
  used_coupons: string;
  cart: string;
}

export function getOrCreateSession(sessionId?: string): Session {
  const db = getDb();

  if (sessionId) {
    const row = db.prepare('SELECT * FROM sessions WHERE id = ?').get(sessionId) as
      | SessionRow
      | undefined;
    if (row) {
      return {
        id: row.id,
        balance: row.balance,
        used_coupons: JSON.parse(row.used_coupons),
        cart: JSON.parse(row.cart),
      };
    }
  }

  const newSessionId = uuidv4();
  db.prepare('INSERT INTO sessions (id) VALUES (?)').run(newSessionId);

  return {
    id: newSessionId,
    balance: 0,
    used_coupons: [],
    cart: [],
  };
}

export function updateSessionBalance(sessionId: string, balance: number) {
  const db = getDb();
  db.prepare('UPDATE sessions SET balance = ? WHERE id = ?').run(balance, sessionId);
}

export function addUsedCoupon(sessionId: string, coupon: string) {
  const db = getDb();
  const session = getOrCreateSession(sessionId);
  const usedCoupons = [...session.used_coupons, coupon];
  db.prepare('UPDATE sessions SET used_coupons = ? WHERE id = ?').run(
    JSON.stringify(usedCoupons),
    sessionId
  );
}

export function updateCart(sessionId: string, cart: CartItem[]) {
  const db = getDb();
  db.prepare('UPDATE sessions SET cart = ? WHERE id = ?').run(JSON.stringify(cart), sessionId);
}

export function createOrder(sessionId: string, items: CartItem[], total: number) {
  const db = getDb();
  db.prepare('INSERT INTO orders (session_id, items, total) VALUES (?, ?, ?)').run(
    sessionId,
    JSON.stringify(items),
    total
  );
  // Clear cart after order
  updateCart(sessionId, []);
}
