'use client';

import { useCallback, useEffect, useState } from 'react';
import Header from '@/components/Header';
import WelcomePopup from '@/components/WelcomePopup';
import ChocolateModal from '@/components/ChocolateModal';
import QuantityControl from '@/components/QuantityControl';
import { CHOCOLATES, type Chocolate } from '@/lib/chocolates';
import type { CartItem } from '@/lib/session';
import './page.css';

interface Session {
  id: string;
  balance: number;
  used_coupons: string[];
  cart: CartItem[];
}

export default function Home() {
  const [session, setSession] = useState<Session | null>(null);
  const [selectedChocolate, setSelectedChocolate] = useState<Chocolate | null>(null);

  const loadSession = useCallback(async () => {
    const sessionRes = await fetch('/api/session');
    setSession(await sessionRes.json());
  }, []);

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  const updateQuantity = async (chocolateId: string, delta: number) => {
    const res = await fetch('/api/cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chocolateId, quantity: delta }),
    });

    if (res.ok) {
      await loadSession();
    }
  };

  const getCartQuantity = (chocolateId: string): number => {
    const cartItem = session?.cart.find((item) => item.id === chocolateId);
    return cartItem?.quantity || 0;
  };

  return (
    <>
      <WelcomePopup />
      <Header balance={session?.balance} cartCount={session?.cart.length} />

      <div className="container">
        <h2 className="catalogue-title">Наша коллекция</h2>
        <div className="catalogue">
          {CHOCOLATES.map((chocolate, idx) => (
            // biome-ignore lint/a11y/useSemanticElements: div needed for card layout styling
            <div
              key={chocolate.id}
              className="chocolate-card"
              onClick={() => setSelectedChocolate(chocolate)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSelectedChocolate(chocolate);
                }
              }}
              role="button"
              tabIndex={idx}
            >
              <div className="chocolate-image">
                {/* biome-ignore lint/performance/noImgElement: no vercel, img is fine */}
                <img src={`/assets/pictures/${chocolate.id}.jpg`} alt={chocolate.name} />
              </div>
              <div className="chocolate-card-body">
                <h3>{chocolate.name}</h3>
                <p>{chocolate.subtitle}</p>
                <div className="price">{chocolate.price} ₽</div>
                <QuantityControl
                  quantity={getCartQuantity(chocolate.id)}
                  onChange={(delta) => updateQuantity(chocolate.id, delta)}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedChocolate && (
        <ChocolateModal
          chocolate={selectedChocolate}
          isOpen={!!selectedChocolate}
          onClose={() => setSelectedChocolate(null)}
          cartQuantity={getCartQuantity(selectedChocolate.id)}
          onUpdateQuantity={updateQuantity}
        />
      )}
    </>
  );
}
