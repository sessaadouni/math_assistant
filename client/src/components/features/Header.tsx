/**
 * Header component - App logo, status indicator, and controls
 */

'use client';

import { useBackendHealth } from '@/hooks';

export default function Header() {
  const { data: health, isLoading } = useBackendHealth();

  return (
    <header className="backdrop-blur-md bg-white/5 border-b border-white/10 px-8 py-6">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-4xl">📚</div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Math RAG Assistant
            </h1>
            <p className="text-white/60 text-sm mt-1">
              Assistant intelligent pour l'apprentissage des mathématiques
            </p>
          </div>
        </div>

        {/* Backend Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-lg border border-white/20">
            {isLoading ? (
              <>
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-white/70">Vérification...</span>
              </>
            ) : health?.ok ? (
              <>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-white/90">Backend OK</span>
                {health.model && (
                  <span className="text-xs text-white/50 ml-2">({health.model})</span>
                )}
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span className="text-sm text-red-400">Backend hors ligne</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
