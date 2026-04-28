'use server';

import type { NextRequest } from 'next/server';

export async function getFlag(request: NextRequest): Promise<string> {
  return 'alfa{xxxxxxxxxxxxxxxxxxxxxxxxx}';
}
