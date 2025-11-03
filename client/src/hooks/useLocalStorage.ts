/**
 * useLocalStorage hook - Persistent state management with localStorage
 */

'use client';

import { useState, useEffect } from 'react';
import { saveToLocalStorage, loadFromLocalStorage } from '@/lib/utils';

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(initialValue);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load from localStorage on mount (client-side only)
  useEffect(() => {
    const stored = loadFromLocalStorage<T>(key, initialValue);
    setValue(stored);
    setIsInitialized(true);
  }, [key, initialValue]);

  // Save to localStorage when value changes
  useEffect(() => {
    if (isInitialized) {
      saveToLocalStorage(key, value);
    }
  }, [key, value, isInitialized]);

  return [value, setValue] as const;
}
