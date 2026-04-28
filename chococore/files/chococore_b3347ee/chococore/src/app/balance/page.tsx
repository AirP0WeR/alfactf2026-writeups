'use client';

import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import type { CartItem } from '@/lib/session';
import './page.css';

interface Session {
  id: string;
  balance: number;
  used_coupons: string[];
  cart: CartItem[];
}

export default function BalancePage() {
  const [session, setSession] = useState<Session | null>(null);
  const [promoCode, setPromoCode] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const loadSession = async () => {
      const res = await fetch('/api/session');
      const data = await res.json();
      setSession(data);
    };
    loadSession();
  }, []);

  const applyPromoCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    if (!promoCode.trim()) {
      setMessage({ type: 'error', text: 'Введите промокод' });
      return;
    }

    const res = await fetch('/api/promocode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: promoCode }),
    });

    const data = await res.json();

    if (res.ok) {
      setMessage({
        type: 'success',
        text: `Промокод активирован! Добавлено ${data.amount} ₽ на баланс.`,
      });
      setPromoCode('');
      // Refresh session
      const sessionRes = await fetch('/api/session');
      setSession(await sessionRes.json());
    } else {
      setMessage({
        type: 'error',
        text:
          data.error === 'Invalid promocode'
            ? 'Неверный промокод'
            : data.error === 'Promocode already used'
              ? 'Промокод уже использован'
              : data.error,
      });
    }
  };

  return (
    <>
      <Header balance={session?.balance} cartCount={session?.cart.length} />

      <div className="container">
        <h2 className="balance-title">Ваш шоколёк</h2>

        <div className="balance-info">
          <div className="balance-card">
            <h3>Шоколёк — это кошелёк для оплаты нашего шоколада</h3>
            <div className="balance-amount">{session?.balance || 0} ₽</div>
            <p className="balance-hint">
              Вы можете использовать эти средства для оплаты заказов в нашем магазине. Деньги на
              шокольке не сгорают.
            </p>
          </div>
        </div>

        {message && <div className={`message ${message.type}`}>{message.text}</div>}

        <div className="promo-section">
          <h2>Активировать промокод</h2>
          <p className="promo-description">
            Принимайте участие в наших акциях и получайте промокоды для пополнения шоколька.
          </p>
          <form onSubmit={applyPromoCode} className="promo-form">
            <input
              type="text"
              value={promoCode}
              onChange={(e) => setPromoCode(e.target.value)}
              placeholder="Введите промокод"
            />
            <button type="submit" className="btn activate-btn">
              Активировать
            </button>
          </form>
        </div>

        {session && session.used_coupons.length > 0 && (
          <div className="used-coupons">
            <h3>Использованные промокоды</h3>
            <ul>
              {session.used_coupons.map((coupon) => (
                <li key={coupon}>{coupon}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </>
  );
}
