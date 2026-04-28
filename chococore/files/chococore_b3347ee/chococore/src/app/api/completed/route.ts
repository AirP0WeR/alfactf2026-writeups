import { cookies } from 'next/headers';
import { type NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { getFlag } from '@/lib/flag';

interface OrderRow {
  id: number;
  session_id: string;
  items: string;
  total: number;
  created_at: number;
}

export async function GET(request: NextRequest) {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get('session_id')?.value;

  if (!sessionId) {
    return NextResponse.json({ error: 'No session' }, { status: 401 });
  }

  const db = getDb();

  const currentTime = Math.floor(Date.now() / 1000);
  const fiveMinutesAgo = currentTime - 300;

  const recentOrder = db
    .prepare(
      'SELECT * FROM orders WHERE session_id = ? AND created_at > ? ORDER BY created_at DESC LIMIT 1'
    )
    .get(sessionId, fiveMinutesAgo) as OrderRow | undefined;

  if (!recentOrder) {
    return NextResponse.json({ error: 'No recent order found' }, { status: 403 });
  }

  let message = `Спасибо за покупку! Ваш заказ #${recentOrder.id} на ${recentOrder.total} ₽ оформлен. Ваш шоколад уже в пути!`;

  const items = JSON.parse(recentOrder.items) as { id: string; name: string; quantity: number }[];

  if (items.some((item) => item.id === 'flag' && item.quantity >= 1)) {
    message += ` Для нас большая честь наградить вас, как премиального покупателя, специальным секретным купоном на нашу эксклюзивную дегустацию: ${await getFlag(request)}`;
  }

  return NextResponse.json({
    success: true,
    message,
    orderId: recentOrder.id,
    total: recentOrder.total,
  });
}
