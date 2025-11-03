/**
 * API client for the Math RAG backend
 */

import type { HealthResponse } from '@/types';

export class MathRagAPI {
  constructor(private baseUrl: string) {}

  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }

  async ragCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/rag_check`);
    return response.json();
  }

  buildChatUrl(question: string, k: number, docType?: string, chapter?: string): string {
    const params = new URLSearchParams({ question, k: String(k) });
    if (docType) params.set('doc_type', docType);
    if (chapter) params.set('chapter', chapter);
    return `${this.baseUrl}/chat?${params.toString()}`;
  }

  buildSheetUrl(topic: string, level: string, k: number, chapter?: string): string {
    const params = new URLSearchParams({ topic, level, k: String(k) });
    if (chapter) params.set('chapter', chapter);
    return `${this.baseUrl}/sheet?${params.toString()}`;
  }

  buildFormulaUrl(query: string, k: number): string {
    const params = new URLSearchParams({ query, k: String(k) });
    return `${this.baseUrl}/formula?${params.toString()}`;
  }

  buildExamUrl(chapters: string, duration: string, level: string, k: number): string {
    const params = new URLSearchParams({ chapters, duration, level, k: String(k) });
    return `${this.baseUrl}/exam?${params.toString()}`;
  }

  buildCourseUrl(notion: string, level: string, k: number, chapter?: string): string {
    const params = new URLSearchParams({ notion, level, k: String(k) });
    if (chapter) params.set('chapter', chapter);
    return `${this.baseUrl}/course?${params.toString()}`;
  }

  getReviewUrl(): string {
    return `${this.baseUrl}/sheet_review`;
  }

  getGradeUrl(): string {
    return `${this.baseUrl}/grade`;
  }
}
