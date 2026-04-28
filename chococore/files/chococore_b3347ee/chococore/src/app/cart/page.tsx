'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
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

export default function CartPage() {
  const [session, setSession] = useState<Session | null>(null);

  const loadSession = useCallback(async () => {
    const res = await fetch('/api/session');
    setSession(await res.json());
  }, []);

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  const updateQuantity = async (itemId: string, delta: number) => {
    if (!session) return;

    await fetch('/api/cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chocolateId: itemId, quantity: delta }),
    });

    loadSession();
  };

  const removeItem = (itemId: string) => {
    const item = session?.cart.find((i) => i.id === itemId);
    if (!item) return;
    updateQuantity(itemId, -item.quantity);
  };

  const total = session?.cart.reduce((sum, item) => sum + item.price * item.quantity, 0) || 0;

  return (
    <>
      <Header balance={session?.balance} cartCount={session?.cart.length} />

      <div className="container">
        <h2 className="cart-title">Корзина</h2>

        {!session?.cart.length ? (
          <div className="empty-state">
            <h2>Корзина пуста</h2>
            <p>Выбирайте самый вкусный шоколад в нашем каталоге!</p>
            <Link href="/">
              <button type="button" className="btn empty-btn">
                В каталог
              </button>
            </Link>
          </div>
        ) : (
          <>
            <div className="cart-items">
              {session.cart.map((item) => (
                <div key={item.id} className="cart-item">
                  <div className="cart-item-info">
                    <h3>{item.name}</h3>
                    <p>{item.price} ₽ за штуку</p>
                  </div>
                  <div className="cart-item-controls">
                    <div className="quantity-control">
                      <button type="button" onClick={() => updateQuantity(item.id, -1)}>
                        −
                      </button>
                      <span>{item.quantity}</span>
                      <button type="button" onClick={() => updateQuantity(item.id, 1)}>
                        +
                      </button>
                    </div>
                    <button
                      type="button"
                      className="btn remove-btn"
                      onClick={() => removeItem(item.id)}
                    >
                      Удалить
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="cart-summary">
              <div className="summary-row total">
                <span>Итого:</span>
                <span>{total} ₽</span>
              </div>
              <Link href="/checkout">
                <button type="button" className="btn checkout-btn">
                  Оплатить
                </button>
              </Link>
            </div>
          </>
        )}
      </div>
    </>
  );
}
