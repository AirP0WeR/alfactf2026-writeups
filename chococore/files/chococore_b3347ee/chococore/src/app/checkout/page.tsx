'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import './page.css';

interface Session {
  id: string;
  balance: number;
  cart: CartItem[];
}

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

export default function CheckoutPage() {
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const loadSession = async () => {
      const res = await fetch('/api/session');
      const data = await res.json();
      setSession(data);

      if (!data.cart.length) {
        router.push('/cart');
      }
    };
    loadSession();
  }, [router]);

  const completeOrder = async () => {
    setMessage(null);

    const res = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    const data = await res.json();

    if (res.ok) {
      router.push('/completed');
    } else {
      setMessage({ type: 'error', text: data.error });
    }
  };

  const total = session?.cart.reduce((sum, item) => sum + item.price * item.quantity, 0) || 0;
  const canCheckout = session && session.balance >= total;

  return (
    <>
      <Header balance={session?.balance} cartCount={session?.cart.length} />

      <div className="container">
        <h2 className="checkout-title">Оплата заказа</h2>

        {message && <div className={`message ${message.type}`}>{message.text}</div>}

        <div className="cart-items">
          <h2 className="order-summary-title">Состав заказа</h2>
          {session?.cart.map((item) => (
            <div key={item.id} className="cart-item">
              <div className="cart-item-info">
                <h3>{item.name}</h3>
                <p>
                  {item.price} ₽ × {item.quantity}
                </p>
              </div>
              <div className="cart-item-total">{item.price * item.quantity} ₽</div>
            </div>
          ))}
        </div>

        <div className="cart-summary">
          <h2>Оплата</h2>
          <div className="summary-row">
            <span>Сумма заказа:</span>
            <span>{total} ₽</span>
          </div>
          <div className="summary-row">
            <span>Шоколёк:</span>
            <span>{session?.balance || 0} ₽</span>
          </div>
          <div className="summary-row total">
            <span>К оплате:</span>
            <span>{total} ₽</span>
          </div>

          {!canCheckout && (
            <div className="message error insufficient-funds">
              Недостаточно средств. Пополните{' '}
              <Link href="/balance" className="error-link">
                ваш шоколёк
              </Link>
              .
            </div>
          )}

          <button
            type="button"
            className="btn checkout-button"
            onClick={completeOrder}
            disabled={!canCheckout}
          >
            Оформить заказ
          </button>
        </div>
      </div>
    </>
  );
}
