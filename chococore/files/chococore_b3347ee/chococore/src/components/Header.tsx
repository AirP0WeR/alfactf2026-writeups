'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import './Header.css';

interface HeaderProps {
  balance?: number;
  cartCount?: number;
}

function Logo() {
  return (
    <svg
      className="header-logo-icon"
      width="34"
      height="34"
      viewBox="0 0 34 34"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M17 1.5L31.5 9.25V24.75L17 32.5L2.5 24.75V9.25L17 1.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <path
        d="M8 22L13.5 12L17 17L20.5 12L26 22"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="17" cy="25.5" r="1.5" fill="currentColor" opacity="0.5" />
    </svg>
  );
}

export default function Header({ balance = 0, cartCount = 0 }: HeaderProps) {
  const pathname = usePathname();

  return (
    <div className="header">
      <div className="header-content">
        <Link href="/" className="header-logo">
          <Logo />
          <span className="header-logo-text">CHOCOCORE</span>
        </Link>
        <div className="header-nav">
          <Link href="/balance" className={`balance ${pathname === '/balance' ? 'active' : ''}`}>
            Шоколёк: {balance} ₽
          </Link>
          <Link href="/" className={pathname === '/' ? 'active' : ''}>
            Каталог
          </Link>
          <Link
            href="/cart"
            className={pathname === '/cart' || pathname === '/checkout' ? 'active' : ''}
          >
            Корзина ({cartCount})
          </Link>
        </div>
      </div>
    </div>
  );
}
