'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Header from '@/components/Header';
import type { CartItem } from '@/lib/session';
import './page.css';

interface Session {
  id: string;
  balance: number;
  used_coupons: string[];
  cart: CartItem[];
}

export default function CompletedPage() {
  const [session, setSession] = useState<Session | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch session data
    fetch('/api/session')
      .then((res) => res.json())
      .then(setSession);

    // Fetch server-generated completion message
    // This is only available after verified purchase
    fetch('/api/completed')
      .then((res) => {
        if (!res.ok) {
          throw new Error('No valid order found');
        }
        return res.json();
      })
      .then((data) => {
        setMessage(data.message);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <>
        <Header balance={session?.balance} cartCount={session?.cart.length} />
        <div className="container">
          <div className="success-page">
            <p>Загрузка...</p>
          </div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Header balance={session?.balance} cartCount={session?.cart.length} />
        <div className="container">
          <div className="success-page">
            <div className="success-icon">❌</div>
            <h1>Доступ запрещён</h1>
            <p>Вам необходимо совершить покупку.</p>
            <Link href="/">
              <button type="button" className="btn continue-shopping-btn">
                Вернуться в каталог
              </button>
            </Link>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header balance={session?.balance} cartCount={session?.cart.length} />

      <div className="container">
        <div className="success-page">
          <div className="success-icon">✅</div>
          <h1>Заказ размещён!</h1>
          <p>{message}</p>
          <Link href="/">
            <button type="button" className="btn continue-shopping-btn">
              Купить ещё
            </button>
          </Link>
        </div>
      </div>
    </>
  );
}
