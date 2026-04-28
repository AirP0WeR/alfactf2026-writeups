'use client';

import { useEffect, useRef } from 'react';
import type { Chocolate } from '@/lib/chocolates';
import QuantityControl from '@/components/QuantityControl';
import './ChocolateModal.css';

interface ChocolateModalProps {
  chocolate: Chocolate;
  isOpen: boolean;
  onClose: () => void;
  cartQuantity?: number;
  onUpdateQuantity: (chocolateId: string, delta: number) => Promise<void>;
}

export default function ChocolateModal({
  chocolate,
  isOpen,
  onClose,
  cartQuantity = 0,
  onUpdateQuantity,
}: ChocolateModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    // biome-ignore lint/a11y: modal backdrop styling
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-content" ref={modalRef}>
        <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
          ✕
        </button>

        <div className="modal-grid">
          <div className="modal-image">
            {/* biome-ignore lint/performance/noImgElement: using standard img for CTF assets */}
            <img src={`/assets/pictures/${chocolate.id}.jpg`} alt={chocolate.name} />
          </div>

          <div className="modal-info">
            <h2 className="modal-title">{chocolate.name}</h2>
            <p className="modal-subtitle">{chocolate.subtitle}</p>
            <p className="modal-description">{chocolate.description}</p>
            <div className="modal-price">{chocolate.price} ₽</div>
            <QuantityControl
              quantity={cartQuantity}
              onChange={(delta) => onUpdateQuantity(chocolate.id, delta)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
