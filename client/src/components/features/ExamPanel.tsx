/**
 * ExamPanel component - Generate exam with multiple chapters
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button, Input, Select, Card, MarkdownMath, OutputBox } from '@/components/ui';
import { useStream, useLocalStorage } from '@/hooks';
import { MathRagAPI } from '@/lib/api';
import type { ExamFormData } from '@/types';

const api = new MathRagAPI('http://localhost:8000');

const LEVEL_OPTIONS = [
  { value: 'facile', label: '😊 Facile' },
  { value: 'moyen', label: '🤔 Moyen' },
  { value: 'difficile', label: '😰 Difficile' }
];

export default function ExamPanel() {
  const [formData, setFormData] = useLocalStorage<ExamFormData>('exam_form', {
    chapters: '',
    duration: '2h',
    level: 'moyen',
    k: 10
  });
  const [response, setResponse] = useState('');
  const [error, setError] = useState<string | null>(null);

  const streamMutation = useStream();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 Exam - handleSubmit called', formData);

    if (!formData.chapters.trim()) {
      setError('Veuillez indiquer les chapitres');
      return;
    }

    setResponse('');
    setError(null);

    const url = api.buildExamUrl(
      formData.chapters,
      formData.duration,
      formData.level,
      formData.k
    );

    console.log('📡 Exam - URL construite:', url);

    streamMutation.mutate({
      url,
      onToken: (token) => {
        setResponse((prev) => prev + token);
      },
      onError: (err) => {
        setError(err);
      }
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <Card variant="gradient">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="📋 Chapitres (séparés par des virgules)"
            placeholder="Ex: Chapitre 1, Chapitre 2, Chapitre 3"
            value={formData.chapters}
            onChange={(e) => setFormData({ ...formData, chapters: e.target.value })}
            icon="📚"
          />

          <div className="grid grid-cols-3 gap-4">
            <Input
              label="⏱️ Durée"
              placeholder="Ex: 2h"
              value={formData.duration}
              onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
            />

            <Select
              label="🎯 Niveau"
              value={formData.level}
              onChange={(e) => setFormData({ ...formData, level: e.target.value })}
              options={LEVEL_OPTIONS}
            />

            <Input
              type="number"
              label="📊 Nombre de docs (k)"
              value={formData.k}
              onChange={(e) => setFormData({ ...formData, k: parseInt(e.target.value) || 10 })}
              min={1}
              max={20}
            />
          </div>

          <Button
            type="submit"
            isLoading={streamMutation.isPending}
            icon="🚀"
            className="w-full"
          >
            Générer l'examen
          </Button>
        </form>
      </Card>

      {(response || error || streamMutation.isPending) && (
        <Card title="📋 Sujet d'examen">
          <OutputBox isLoading={streamMutation.isPending} error={error}>
            {response && <MarkdownMath content={response} autoScroll />}
          </OutputBox>
        </Card>
      )}
    </motion.div>
  );
}
