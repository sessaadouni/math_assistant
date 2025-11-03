/**
 * ReviewPanel component - Review and correct exercise sheet
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button, TextArea, Card, MarkdownMath, OutputBox } from '@/components/ui';
import { useStream } from '@/hooks';
import { MathRagAPI } from '@/lib/api';

const api = new MathRagAPI('http://localhost:8000');

export default function ReviewPanel() {
  const [sheetContent, setSheetContent] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState<string | null>(null);

  const streamMutation = useStream();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 Review - handleSubmit called');

    if (!sheetContent.trim()) {
      setError('Veuillez coller le contenu de votre fiche');
      return;
    }

    setResponse('');
    setError(null);

    const url = api.getReviewUrl();
    console.log('📡 Review - URL:', url);

    streamMutation.mutate({
      url,
      method: 'POST',
      body: JSON.stringify({ sheet_content: sheetContent }),
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
          <TextArea
            label="✅ Collez votre fiche complétée"
            placeholder="Collez ici le contenu de votre fiche d'exercices avec vos réponses..."
            value={sheetContent}
            onChange={(e) => setSheetContent(e.target.value)}
            rows={12}
          />

          <Button
            type="submit"
            isLoading={streamMutation.isPending}
            icon="🔍"
            className="w-full"
          >
            Corriger la fiche
          </Button>
        </form>
      </Card>

      {(response || error || streamMutation.isPending) && (
        <Card title="✅ Correction détaillée">
          <OutputBox isLoading={streamMutation.isPending} error={error}>
            {response && <MarkdownMath content={response} autoScroll />}
          </OutputBox>
        </Card>
      )}
    </motion.div>
  );
}
