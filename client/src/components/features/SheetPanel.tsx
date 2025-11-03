/**
 * SheetPanel component - Generate exercise sheets
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button, Input, Select, Card, MarkdownMath, OutputBox } from '@/components/ui';
import { useStream, useLocalStorage } from '@/hooks';
import { MathRagAPI } from '@/lib/api';
import type { SheetFormData } from '@/types';

const api = new MathRagAPI('http://localhost:8000');

const LEVEL_OPTIONS = [
  { value: 'facile', label: '😊 Facile' },
  { value: 'moyen', label: '🤔 Moyen' },
  { value: 'difficile', label: '😰 Difficile' }
];

export default function SheetPanel() {
  const [formData, setFormData] = useLocalStorage<SheetFormData>('sheet_form', {
    topic: '',
    level: 'moyen',
    k: 5,
    chapter: ''
  });
  const [response, setResponse] = useState('');
  const [error, setError] = useState<string | null>(null);

  const streamMutation = useStream();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 Sheet - handleSubmit called', formData);

    if (!formData.topic.trim()) {
      setError('Veuillez saisir un thème');
      return;
    }

    setResponse('');
    setError(null);

    const url = api.buildSheetUrl(
      formData.topic,
      formData.level,
      formData.k,
      formData.chapter || undefined
    );

    console.log('📡 Sheet - URL construite:', url);

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
            label="📝 Thème de la fiche"
            placeholder="Ex: Suites numériques"
            value={formData.topic}
            onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
            icon="📚"
          />

          <div className="grid grid-cols-3 gap-4">
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
              onChange={(e) => setFormData({ ...formData, k: parseInt(e.target.value) || 5 })}
              min={1}
              max={20}
            />

            <Input
              label="📖 Chapitre (optionnel)"
              placeholder="Ex: Chapitre 1"
              value={formData.chapter}
              onChange={(e) => setFormData({ ...formData, chapter: e.target.value })}
            />
          </div>

          <Button
            type="submit"
            isLoading={streamMutation.isPending}
            icon="🚀"
            className="w-full"
          >
            Générer la fiche
          </Button>
        </form>
      </Card>

      {(response || error || streamMutation.isPending) && (
        <Card title="📝 Fiche d'exercices">
          <OutputBox isLoading={streamMutation.isPending} error={error}>
            {response && <MarkdownMath content={response} autoScroll />}
          </OutputBox>
        </Card>
      )}
    </motion.div>
  );
}
