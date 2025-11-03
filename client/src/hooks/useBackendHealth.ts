/**
 * useBackendHealth hook - Check backend health status with TanStack Query
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { MathRagAPI } from '@/lib/api';

const api = new MathRagAPI('http://localhost:8000');

export function useBackendHealth() {
  return useQuery({
    queryKey: ['backend-health'],
    queryFn: () => api.health(),
    refetchInterval: 30000, // Check every 30s
    retry: 3,
    staleTime: 10000
  });
}
