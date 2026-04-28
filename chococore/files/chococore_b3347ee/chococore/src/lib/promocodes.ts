export const COUPONS: Record<string, number> = {
  TREAT5000: 5000,
};

export interface PromoCode {
  amount: number;
  coupon: string;
}

export function generatePromocode(coupon: string): string {
  return Buffer.from(JSON.stringify({ amount: COUPONS[coupon], coupon })).toString('base64');
}
