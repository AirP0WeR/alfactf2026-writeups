import { cookies } from 'next/headers';
import { type NextRequest, NextResponse } from 'next/server';
import { CHOCOLATES } from '@/lib/chocolates';
import { getOrCreateSession, updateCart } from '@/lib/session';

export async function POST(request: NextRequest) {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get('session_id')?.value;

  if (!sessionId) {
    return NextResponse.json({ error: 'No session' }, { status: 400 });
  }

  const body = await request.json();
  const { chocolateId, quantity } = body;

  const chocolate = CHOCOLATES.find((c) => c.id === chocolateId);
  if (!chocolate) {
    return NextResponse.json({ error: 'Invalid chocolate' }, { status: 400 });
  }

  if (typeof quantity !== 'number') {
    return NextResponse.json({ error: 'Invalid quantity' }, { status: 400 });
  }

  const quantityInt = Math.floor(quantity);

  const session = getOrCreateSession(sessionId);
  const cart = [...session.cart];

  const existingIndex = cart.findIndex((item) => item.id === chocolateId);
  if (existingIndex >= 0) {
    const newQuantity = Math.max(cart[existingIndex].quantity + quantityInt, 0);
    if (newQuantity === 0) {
      cart.splice(existingIndex, 1);
    } else {
      cart[existingIndex].quantity = Math.max(cart[existingIndex].quantity + quantityInt, 0);
    }
  } else {
    cart.push({
      id: chocolate.id,
      name: chocolate.name,
      price: chocolate.price,
      quantity: Math.max(quantityInt, 0),
    });
  }

  updateCart(sessionId, cart);

  return NextResponse.json({ success: true, cart });
}
