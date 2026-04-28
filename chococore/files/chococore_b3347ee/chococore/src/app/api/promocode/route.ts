import { cookies } from 'next/headers';
import { type NextRequest, NextResponse } from 'next/server';
import { COUPONS, type PromoCode } from '@/lib/promocodes';
import { addUsedCoupon, getOrCreateSession, updateSessionBalance } from '@/lib/session';

export async function POST(request: NextRequest) {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get('session_id')?.value;

  if (!sessionId) {
    return NextResponse.json({ error: 'No session' }, { status: 400 });
  }

  const session = getOrCreateSession(sessionId);

  const body = await request.json();
  const { code } = body;

  let promo: PromoCode;
  try {
    const decoded = Buffer.from(code, 'base64').toString('utf-8');
    promo = JSON.parse(decoded) as PromoCode;
  } catch (_error) {
    return NextResponse.json({ error: 'Invalid promocode' }, { status: 400 });
  }

  if (!Object.hasOwn(promo, 'amount')) {
    return NextResponse.json({ error: 'Invalid promocode' }, { status: 400 });
  }

  session.balance += promo.amount;

  try {
    if (typeof promo.amount !== 'number' || typeof promo.coupon !== 'string') {
      throw new Error('Invalid promocode');
    }

    if (COUPONS[promo.coupon] !== promo.amount) {
      throw new Error('Invalid promocode');
    }

    if (session.used_coupons.includes(promo.coupon)) {
      throw new Error('Promocode already used');
    }
  } catch (error) {
    session.balance -= promo.amount;
    return NextResponse.json({ error: (error as Error).message }, { status: 400 });
  } finally {
    updateSessionBalance(sessionId, session.balance);
  }

  addUsedCoupon(sessionId, promo.coupon);

  return NextResponse.json({
    success: true,
    balance: session.balance,
    amount: promo.amount,
  });
}
