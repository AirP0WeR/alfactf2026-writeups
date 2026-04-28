'use client';

import { useState } from 'react';
import './QuantityControl.css';
import { TailSpin } from 'react-loader-spinner';

interface QuantityControlProps {
  quantity: number;
  onChange: (delta: number) => Promise<void>;
}

type ButtonProps = Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onClick' | 'type'> & {
  action: () => Promise<void>;
};

function Button({ action, ...props }: ButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();

    if (props.disabled) return;

    setLoading(true);
    try {
      await action();
    } finally {
      setLoading(false);
    }
  };

  return (
    <button type="button" {...props} onClick={handleClick} disabled={loading || props.disabled}>
      {loading ? (
        <TailSpin width={18} height={18} color="#000" wrapperClass="qty-spinner" strokeWidth={5} />
      ) : (
        props.children
      )}
    </button>
  );
}

export default function QuantityControl({ quantity, onChange }: QuantityControlProps) {
  if (quantity === 0) {
    return (
      <Button
        className="quantity-control-btn quantity-control-btn-simple btn"
        action={() => onChange(1)}
      >
        Добавить в корзину
      </Button>
    );
  }

  return (
    <button type="button" className="quantity-control-btn btn" onClick={(e) => e.stopPropagation()}>
      <Button className="qty" action={() => onChange(-1)}>
        −
      </Button>
      <span className="qty-value">{quantity}</span>
      <Button className="qty" action={() => onChange(1)}>
        +
      </Button>
    </button>
  );
}
