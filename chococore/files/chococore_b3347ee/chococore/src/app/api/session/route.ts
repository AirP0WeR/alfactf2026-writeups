import { cookies } from 'next/headers';
import { type NextRequest, NextResponse } from 'next/server';
import { getOrCreateSession } from '@/lib/session';

export async function GET(_request: NextRequest) {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get('session_id')?.value;

  const session = getOrCreateSession(sessionId);

  const response = NextResponse.json(session);

  // Set session cookie if new
  if (!sessionId || sessionId !== session.id) {
    response.cookies.set('session_id', session.id, {
      httpOnly: true,
      maxAge: 60 * 60 * 24 * 30, // 30 days
      path: '/',
    });
  }

  return response;
}
