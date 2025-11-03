export type PanelType = 'chat' | 'sheet' | 'review' | 'formula' | 'exam' | 'course' | 'grade';

export interface HealthResponse {
  ok: boolean;
  model: string;
  error?: string;
}

export interface StreamOptions {
  method?: 'GET' | 'POST';
  body?: string;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  onToken: (token: string) => void;
  onError?: (error: string) => void;
  timeout?: number;
}

export interface ChatFormData {
  question: string;
  k: number;
  docType: string;
  chapter: string;
}

export interface SheetFormData {
  topic: string;
  level: string;
  k: number;
  chapter: string;
}

export interface FormulaFormData {
  query: string;
  k: number;
}

export interface ExamFormData {
  chapters: string;
  duration: string;
  level: string;
  k: number;
}

export interface CourseFormData {
  notion: string;
  level: string;
  k: number;
  chapter: string;
}

export interface GradeFormData {
  statement: string;
  studentAnswer: string;
}
