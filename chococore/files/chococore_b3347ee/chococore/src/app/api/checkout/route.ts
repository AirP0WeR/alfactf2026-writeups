import { cookies } from 'next/headers';
import { type NextRequest, NextResponse } from 'next/server';
import { createOrder, getOrCreateSession, updateSessionBalance } from '@/lib/session';

export async function POST(_request: NextRequest) {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get('session_id')?.value;

  if (!sessionId) {
    return NextResponse.json({ error: 'No session' }, { status: 400 });
  }

  const session = getOrCreateSession(sessionId);

  if (session.cart.length === 0) {
    return NextResponse.json({ error: 'Cart is empty' }, { status: 400 });
  }

  if (
    session.cart.some(
      (item) =>
        typeof item.quantity !== 'number' ||
        item.quantity <= 0 ||
        typeof item.price !== 'number' ||
        item.price <= 0
    )
  ) {
    return NextResponse.json({ error: 'Invalid cart items' }, { status: 400 });
  }

  const total = session.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  if (session.balance < total) {
    return NextResponse.json({ error: 'Insufficient balance' }, { status: 400 });
  }

  const newBalance = session.balance - total;
  updateSessionBalance(sessionId, newBalance);
  createOrder(sessionId, session.cart, total);

  return NextResponse.json({
    success: true,
    total,
    balance: newBalance,
  });
}
