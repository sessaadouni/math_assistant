/**
 * ChatPanel component - Q&A interface with course content
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button, Input, Select, Card, MarkdownMath, OutputBox } from '@/components/ui';
import { useStream, useLocalStorage } from '@/hooks';
import { MathRagAPI } from '@/lib/api';
import type { ChatFormData } from '@/types';

const api = new MathRagAPI('http://localhost:8000');

const DOC_TYPE_OPTIONS = [
  { value: 'all', label: 'Tous' },
  { value: 'cours', label: 'Cours' },
  { value: 'exercice', label: 'Exercice' },
  { value: 'methode', label: 'Méthode' }
];

export default function ChatPanel() {
  const [formData, setFormData] = useLocalStorage<ChatFormData>('chat_form', {
    question: '',
    k: 5,
    docType: 'all',
    chapter: ''
  });
  const [response, setResponse] = useState('');
  const [error, setError] = useState<string | null>(null);

  const streamMutation = useStream();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 Chat - handleSubmit called', formData);

    if (!formData.question.trim()) {
      setError('Veuillez saisir une question');
      return;
    }

    setResponse('');
    setError(null);

    const url = api.buildChatUrl(
      formData.question,
      formData.k,
      formData.docType === 'all' ? undefined : formData.docType,
      formData.chapter || undefined
    );

    console.log('📡 Chat - URL construite:', url);

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
            label="💬 Votre question"
            placeholder="Ex: Comment démontrer la convergence d'une suite?"
            value={formData.question}
            onChange={(e) => setFormData({ ...formData, question: e.target.value })}
            icon="❓"
          />

          <div className="grid grid-cols-3 gap-4">
            <Input
              type="number"
              label="📊 Nombre de docs (k)"
              value={formData.k}
              onChange={(e) => setFormData({ ...formData, k: parseInt(e.target.value) || 5 })}
              min={1}
              max={20}
            />

            <Select
              label="📚 Type de doc"
              value={formData.docType}
              onChange={(e) => setFormData({ ...formData, docType: e.target.value })}
              options={DOC_TYPE_OPTIONS}
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
            Poser la question
          </Button>
        </form>
      </Card>

      {(response || error || streamMutation.isPending) && (
        <Card title="💡 Réponse">
          <OutputBox isLoading={streamMutation.isPending} error={error}>
            {response && <MarkdownMath content={response} autoScroll />}
          </OutputBox>
        </Card>
      )}
    </motion.div>
  );
}
