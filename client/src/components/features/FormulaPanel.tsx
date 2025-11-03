/**
 * FormulaPanel component - Search for mathematical formulas
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button, Input, Card, MarkdownMath, OutputBox } from '@/components/ui';
import { useStream, useLocalStorage } from '@/hooks';
import { MathRagAPI } from '@/lib/api';
import type { FormulaFormData } from '@/types';

const api = new MathRagAPI('http://localhost:8000');

export default function FormulaPanel() {
  const [formData, setFormData] = useLocalStorage<FormulaFormData>('formula_form', {
    query: '',
    k: 3
  });
  const [response, setResponse] = useState('');
  const [error, setError] = useState<string | null>(null);

  const streamMutation = useStream();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 Formula - handleSubmit called', formData);

    if (!formData.query.trim()) {
      setError('Veuillez décrire la formule recherchée');
      return;
    }

    setResponse('');
    setError(null);

    const url = api.buildFormulaUrl(formData.query, formData.k);
    console.log('📡 Formula - URL construite:', url);

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
            label="🧮 Description de la formule"
            placeholder="Ex: formule de la dérivée d'un produit"
            value={formData.query}
            onChange={(e) => setFormData({ ...formData, query: e.target.value })}
            icon="🔍"
          />

          <Input
            type="number"
            label="📊 Nombre de résultats (k)"
            value={formData.k}
            onChange={(e) => setFormData({ ...formData, k: parseInt(e.target.value) || 3 })}
            min={1}
            max={10}
          />

          <Button
            type="submit"
            isLoading={streamMutation.isPending}
            icon="🚀"
            className="w-full"
          >
            Rechercher la formule
          </Button>
        </form>
      </Card>

      {(response || error || streamMutation.isPending) && (
        <Card title="🧮 Formules trouvées">
          <OutputBox isLoading={streamMutation.isPending} error={error}>
            {response && <MarkdownMath content={response} autoScroll />}
          </OutputBox>
        </Card>
      )}
    </motion.div>
  );
}
