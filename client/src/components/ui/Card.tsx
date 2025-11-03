/**
 * Card component with glass morphism effect
 */

import type { HTMLAttributes, ReactNode } from 'react';
import { classNames } from '@/lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  variant?: 'default' | 'gradient';
}

export default function Card({
  title,
  subtitle,
  children,
  variant = 'default',
  className,
  ...props
}: CardProps) {
  const baseStyles = 'backdrop-blur-md rounded-2xl border p-6 transition-all duration-300';
  
  const variantStyles = {
    default: 'bg-white/5 border-white/10 hover:bg-white/10',
    gradient: 'bg-gradient-to-br from-white/10 to-white/5 border-white/20 hover:border-white/30'
  };

  return (
    <div
      className={classNames(baseStyles, variantStyles[variant], className)}
      {...props}
    >
      {(title || subtitle) && (
        <div className="mb-4">
          {title && (
            <h3 className="text-xl font-semibold text-white mb-1">{title}</h3>
          )}
          {subtitle && (
            <p className="text-sm text-white/60">{subtitle}</p>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
