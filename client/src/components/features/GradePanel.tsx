/**
 * GradePanel component - Grade student work
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button, TextArea, Card, MarkdownMath, OutputBox } from '@/components/ui';
import { useStream } from '@/hooks';
import { MathRagAPI } from '@/lib/api';

const api = new MathRagAPI('http://localhost:8000');

export default function GradePanel() {
  const [studentWork, setStudentWork] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState<string | null>(null);

  const streamMutation = useStream();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 Grade - handleSubmit called');

    if (!studentWork.trim()) {
      setError('Veuillez coller le travail à évaluer');
      return;
    }

    setResponse('');
    setError(null);

    const url = api.getGradeUrl();
    console.log('📡 Grade - URL:', url);

    streamMutation.mutate({
      url,
      method: 'POST',
      body: JSON.stringify({ student_work: studentWork }),
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
            label="🎯 Collez le travail de l'élève"
            placeholder="Collez ici le travail à évaluer (exercice, devoir, exam...)..."
            value={studentWork}
            onChange={(e) => setStudentWork(e.target.value)}
            rows={12}
          />

          <Button
            type="submit"
            isLoading={streamMutation.isPending}
            icon="📊"
            className="w-full"
          >
            Évaluer le travail
          </Button>
        </form>
      </Card>

      {(response || error || streamMutation.isPending) && (
        <Card title="🎯 Évaluation détaillée">
          <OutputBox isLoading={streamMutation.isPending} error={error}>
            {response && <MarkdownMath content={response} autoScroll />}
          </OutputBox>
        </Card>
      )}
    </motion.div>
  );
}
