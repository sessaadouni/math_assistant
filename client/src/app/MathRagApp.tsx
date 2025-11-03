/**
 * MathRagApp - Main application component (New modular version)
 */

'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import type { PanelType } from '@/types';
import { useLocalStorage } from '@/hooks';
import {
  Header,
  PanelSelector,
  ChatPanel,
  SheetPanel,
  ReviewPanel,
  FormulaPanel,
  ExamPanel,
  CoursePanel,
  GradePanel,
} from '@/components/features';

export default function MathRagApp() {
  const [activePanel, setActivePanel] = useLocalStorage<PanelType>('active_panel', 'chat');

  const renderPanel = () => {
    switch (activePanel) {
      case 'chat':
        return <ChatPanel />;
      case 'sheet':
        return <SheetPanel />;
      case 'review':
        return <ReviewPanel />;
      case 'formula':
        return <FormulaPanel />;
      case 'exam':
        return <ExamPanel />;
      case 'course':
        return <CoursePanel />;
      case 'grade':
        return <GradePanel />;
      default:
        return <ChatPanel />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-900 to-pink-900">
      <Header />
      <PanelSelector activePanel={activePanel} onPanelChange={setActivePanel} />
      
      <main className="max-w-7xl mx-auto px-8 py-8">
        <AnimatePresence mode="wait">
          {renderPanel()}
        </AnimatePresence>
      </main>
    </div>
  );
}
