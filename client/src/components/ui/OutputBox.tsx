/**
 * OutputBox component - Container for streaming output with loading and error states
 */

import type { ReactNode } from 'react';
import { classNames } from '@/lib/utils';

interface OutputBoxProps {
  isLoading?: boolean;
  error?: string | null;
  children: ReactNode;
  className?: string;
}

export default function OutputBox({
  isLoading = false,
  error = null,
  children,
  className
}: OutputBoxProps) {
  return (
    <div className={classNames('relative', className)}>
      {/* Loading Indicator */}
      {isLoading && (
        <div className="absolute top-4 right-4 z-10">
          <div className="flex items-center gap-2 bg-blue-600/90 backdrop-blur-sm px-3 py-2 rounded-full shadow-lg">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white"></div>
            <span className="text-sm font-medium text-white">Streaming...</span>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
          <div className="flex items-start gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <h4 className="font-semibold text-red-400 mb-1">Erreur</h4>
              <p className="text-sm text-red-300">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      {children}
    </div>
  );
}
