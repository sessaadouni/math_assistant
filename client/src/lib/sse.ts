/**
 * SSE (Server-Sent Events) streaming utilities
 */

import type { StreamOptions } from '@/types';

export async function streamSSE(url: string, options: StreamOptions): Promise<void> {
  const { 
    method = 'GET', 
    body, 
    headers = {}, 
    signal, 
    onToken, 
    onError,
    timeout = 120000 
  } = options;

  const timeoutId = setTimeout(() => {
    signal?.dispatchEvent(new Event('abort'));
    onError?.('Timeout - La requête a pris trop de temps');
  }, timeout);

  try {
    const response = await fetch(url, {
      method,
      headers: {
        'Accept': 'text/event-stream',
        ...(body ? { 'Content-Type': 'application/json' } : {}),
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
      signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('ReadableStream non supporté');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages
      let newlineIndex;
      while ((newlineIndex = buffer.indexOf('\n\n')) !== -1) {
        const chunk = buffer.slice(0, newlineIndex);
        buffer = buffer.slice(newlineIndex + 2);

        const lines = chunk.split('\n');
        for (const line of lines) {
          const match = /^data:\s?(.*)$/.exec(line);
          if (match && match[1]) {
            onToken(match[1]);
          }
        }
      }
    }

    // Process remaining buffer
    if (buffer.trim()) {
      const lines = buffer.split('\n');
      for (const line of lines) {
        const match = /^data:\s?(.*)$/.exec(line);
        if (match && match[1]) {
          onToken(match[1]);
        }
      }
    }
  } catch (error: any) {
    if (error?.name !== 'AbortError') {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onError?.(errorMessage);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
