/**
 * PanelSelector component - Tab navigation for different panels
 */

'use client';

import { motion } from 'framer-motion';
import type { PanelType } from '@/types';
import { classNames } from '@/lib/utils';

interface PanelSelectorProps {
  activePanel: PanelType;
  onPanelChange: (panel: PanelType) => void;
}

const PANELS: { id: PanelType; label: string; icon: string }[] = [
  { id: 'chat', label: 'Chat', icon: '💬' },
  { id: 'sheet', label: 'Fiche', icon: '📝' },
  { id: 'review', label: 'Révision', icon: '✅' },
  { id: 'formula', label: 'Formule', icon: '🧮' },
  { id: 'exam', label: 'Examen', icon: '📋' },
  { id: 'course', label: 'Cours', icon: '📖' },
  { id: 'grade', label: 'Note', icon: '🎯' }
];

export default function PanelSelector({ activePanel, onPanelChange }: PanelSelectorProps) {
  return (
    <div className="backdrop-blur-md bg-white/5 border-b border-white/10 px-8 py-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex gap-2 overflow-x-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent pb-2">
          {PANELS.map((panel) => {
            const isActive = activePanel === panel.id;
            return (
              <motion.button
                key={panel.id}
                onClick={() => onPanelChange(panel.id)}
                className={classNames(
                  'relative px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2',
                  isActive
                    ? 'text-white'
                    : 'text-white/60 hover:text-white/90 hover:bg-white/5'
                )}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg"
                    transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <span className="relative z-10">{panel.icon}</span>
                <span className="relative z-10">{panel.label}</span>
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
