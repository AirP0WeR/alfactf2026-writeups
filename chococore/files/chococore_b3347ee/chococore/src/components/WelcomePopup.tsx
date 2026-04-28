'use client';

import { generatePromocode } from '@/lib/promocodes';
import { useEffect, useState } from 'react';

export default function WelcomePopup() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const accepted = document.cookie
      .split('; ')
      .find((row) => row.startsWith('welcome_accepted='));
    if (!accepted || accepted.split('=')[1] !== 'true') {
      setShow(true);
    }
  }, []);

  const handleAccept = () => {
    const expires = new Date(Date.now() + 31536000 * 1000).toUTCString();
    document.cookie = `welcome_accepted=true; expires=${expires}; path=/`;
    setShow(false);
  };

  if (!show) return null;

  return (
    <div className="popup-overlay">
      <div className="popup">
        <h2>Добро пожаловать в ChocoCore! 🍫</h2>
        <p>ChocoCore — коллекция премиум-шоколада ручной работы с натуральными добавками.</p>
        <p>
          Впервые у нас? Воспользуйтесь промокодом <code style={{ wordBreak: 'break-all', fontWeight: 'bold' }}>{generatePromocode('TREAT5000')}</code> на
          первую покупку.
        </p>
        <div className="popup-actions">
          <button type="button" className="btn" onClick={handleAccept}>
            В каталог
          </button>
        </div>
      </div>
    </div>
  );
}
