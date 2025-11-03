/**
 * useStream hook - Custom hook for SSE streaming with TanStack Query
 */

'use client';

import { useMutation } from '@tanstack/react-query';
import { streamSSE } from '@/lib/sse';
import type { StreamOptions } from '@/types';

export function useStream() {
  return useMutation({
    mutationFn: async ({ url, ...options }: StreamOptions & { url: string }) => {
      await streamSSE(url, options);
    },
    onError: (error) => {
      console.error('❌ Stream error:', error);
    }
  });
}
