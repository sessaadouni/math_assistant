/**
 * CoursePanel component - Generate course summary
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button, Input, Select, Card, MarkdownMath, OutputBox } from '@/components/ui';
import { useStream, useLocalStorage } from '@/hooks';
import { MathRagAPI } from '@/lib/api';
import type { CourseFormData } from '@/types';

const api = new MathRagAPI('http://localhost:8000');

const LEVEL_OPTIONS = [
  { value: 'simple', label: '😊 Simple' },
  { value: 'detaille', label: '📚 Détaillé' },
  { value: 'expert', label: '🎓 Expert' }
];

export default function CoursePanel() {
  const [formData, setFormData] = useLocalStorage<CourseFormData>('course_form', {
    notion: '',
    level: 'detaille',
    k: 7,
    chapter: ''
  });
  const [response, setResponse] = useState('');
  const [error, setError] = useState<string | null>(null);

  const streamMutation = useStream();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 Course - handleSubmit called', formData);

    if (!formData.notion.trim()) {
      setError('Veuillez saisir une notion');
      return;
    }

    setResponse('');
    setError(null);

    const url = api.buildCourseUrl(
      formData.notion,
      formData.level,
      formData.k,
      formData.chapter || undefined
    );

    console.log('📡 Course - URL construite:', url);

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
            label="📖 Notion à résumer"
            placeholder="Ex: Les limites de fonctions"
            value={formData.notion}
            onChange={(e) => setFormData({ ...formData, notion: e.target.value })}
            icon="💡"
          />

          <div className="grid grid-cols-3 gap-4">
            <Select
              label="🎯 Niveau de détail"
              value={formData.level}
              onChange={(e) => setFormData({ ...formData, level: e.target.value })}
              options={LEVEL_OPTIONS}
            />

            <Input
              type="number"
              label="📊 Nombre de docs (k)"
              value={formData.k}
              onChange={(e) => setFormData({ ...formData, k: parseInt(e.target.value) || 7 })}
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
            Générer le résumé
          </Button>
        </form>
      </Card>

      {(response || error || streamMutation.isPending) && (
        <Card title="📖 Résumé de cours">
          <OutputBox isLoading={streamMutation.isPending} error={error}>
            {response && <MarkdownMath content={response} autoScroll />}
          </OutputBox>
        </Card>
      )}
    </motion.div>
  );
}
