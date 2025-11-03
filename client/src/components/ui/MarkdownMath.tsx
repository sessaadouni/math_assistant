/**
 * MarkdownMath component - Renders markdown with KaTeX math support and auto-scroll
 */

'use client';

import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { enhanceMathMarkdown } from '@/lib/markdown';

interface MarkdownMathProps {
  content: string;
  autoScroll?: boolean;
}

export default function MarkdownMath({ content, autoScroll = false }: MarkdownMathProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [content, autoScroll]);

  const enhancedContent = enhanceMathMarkdown(content);

  return (
    <div
      ref={containerRef}
      className="markdown-body p-6 overflow-y-auto max-h-[600px] bg-white/5 rounded-lg border border-white/10"
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
      >
        {enhancedContent}
      </ReactMarkdown>
    </div>
  );
}
