'use client';

import React, { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import 'katex/dist/katex.min.css';

/**
 * Math RAG Teacher — Front-end v2 (Amélioré)
 * Dark UI • TailwindCSS • Framer Motion • Markdown + KaTeX
 * 
 * Améliorations:
 * - Gestion d'erreurs robuste avec retry
 * - Loading states et indicateurs de progression
 * - Auto-scroll pendant le streaming
 * - Meilleure UX avec animations fluides
 * - Responsive design optimisé
 * - CSS custom pour un meilleur rendu mathématique
 */

// -----------------------------
// Utilities
// -----------------------------
function classNames(...xs: (string | false | null | undefined)[]) {
  return xs.filter(Boolean).join(' ');
}

function saveLocal<T>(key: string, val: T) {
  try { localStorage.setItem(key, JSON.stringify(val)); } catch {}
}
function loadLocal<T>(key: string, fallback: T): T {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) as T : fallback; } catch { return fallback; }
}

// Improved SSE parser with better error handling and timeout
async function streamSSE(
  url: string,
  opts: { 
    method?: 'GET'|'POST', 
    body?: any, 
    headers?: Record<string,string>, 
    signal?: AbortSignal,
    onToken: (t: string) => void,
    onError?: (e: Error) => void,
    timeout?: number
  }
) {
  const timeoutMs = opts.timeout ?? 60000; // 60s par défaut
  const timeoutId = setTimeout(() => {
    opts.signal?.dispatchEvent(new Event('abort'));
    opts.onError?.(new Error('Timeout - La requête a pris trop de temps'));
  }, timeoutMs);

  try {
    const res = await fetch(url, {
      method: opts.method ?? 'GET',
      headers: { 
        'Accept': 'text/event-stream', 
        ...(opts.headers||{}), 
        ...(opts.body ? {'Content-Type':'application/json'} : {}) 
      },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      signal: opts.signal,
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    if (!res.body) {
      throw new Error('ReadableStream non supporté par le navigateur');
    }
    
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buf += decoder.decode(value, { stream: true });
      
      // Split on double-newline (end of event)
      let idx;
      while ((idx = buf.indexOf('\n\n')) !== -1) {
        const chunk = buf.slice(0, idx);
        buf = buf.slice(idx + 2);
        const lines = chunk.split(/\n/);
        for (const line of lines) {
          const m = /^data:\s?(.*)$/.exec(line);
          if (m && m[1]) opts.onToken(m[1]);
        }
      }
    }
    
    // Flush trailing data
    if (buf.trim()) {
      const lines = buf.split(/\n/);
      for (const line of lines) {
        const m = /^data:\s?(.*)$/.exec(line);
        if (m && m[1]) opts.onToken(m[1]);
      }
    }
  } catch (e: any) {
    if (e?.name !== 'AbortError') {
      opts.onError?.(e);
    }
    throw e;
  } finally {
    clearTimeout(timeoutId);
  }
}

// Add fancy wrappers for math-y callouts inside Markdown source
function enhanceMathMarkdown(src: string): string {
  const labels = ['Théorème','Définition','Lemme','Proposition','Corollaire','Preuve'];
  const lines = src.split('\n');
  const out: string[] = [];
  let i = 0;

  while (i < lines.length) {
    const raw = lines[i];
    const trimmedStart = raw.replace(/^\s+/, '');
    const L = labels.find(lbl =>
      trimmedStart.startsWith(`**${lbl}**`) || trimmedStart.startsWith(`**${lbl}**:`)
    );

    if (L) {
      let rest = trimmedStart.replace(`**${L}**`, '').trimStart();
      if (rest.startsWith(':')) rest = rest.slice(1).trimStart();

      const body: string[] = [];
      if (rest) body.push(rest);
      i++;

      // Accumule jusqu'à une ligne vide (paragraphe) ou EOF
      while (i < lines.length && lines[i].trim() !== '') {
        body.push(lines[i]);
        i++;
      }

      out.push('');
      out.push(
        `<div class="callout ${L.toLowerCase()}"><div class="callout-title">${L}</div><div class="callout-body">${body.join('\n')}</div></div>`
      );

      if (i < lines.length && lines[i].trim() === '') { out.push(''); i++; }
      continue;
    }

    out.push(raw);
    i++;
  }

  return out.join('\n');
}


const SectionTitle: React.FC<{icon?: React.ReactNode, title: string, subtitle?: string}> = ({icon, title, subtitle}) => (
  <div className="flex items-end justify-between gap-6">
    <div>
      <h2 className="text-xl md:text-2xl font-semibold tracking-tight text-white flex items-center gap-3">
        {icon}{title}
      </h2>
      {subtitle && <p className="text-sm text-zinc-400 mt-1">{subtitle}</p>}
    </div>
  </div>
);

const Card: React.FC<{children: React.ReactNode, className?: string}> = ({children, className}) => (
  <motion.div
    initial={{ opacity: 0, y: 8 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.25 }}
    className={classNames(
      "rounded-2xl bg-zinc-900/60 ring-1 ring-white/10 shadow-lg shadow-black/30 backdrop-blur-xl",
      "p-4 md:p-6",
      className
    )}
  >
    {children}
  </motion.div>
);

const TextInput: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = (props) => (
  <input {...props} className={classNames("w-full rounded-xl bg-zinc-800/70 ring-1 ring-white/10 px-3 py-2 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500", props.className)} />
);
const NumberInput: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = (props) => (
  <input type="number" {...props} className={classNames("w-full rounded-xl bg-zinc-800/70 ring-1 ring-white/10 px-3 py-2 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500", props.className)} />
);
const Select: React.FC<React.SelectHTMLAttributes<HTMLSelectElement>> = (props) => (
  <select {...props} className={classNames("w-full rounded-xl bg-zinc-800/70 ring-1 ring-white/10 px-3 py-2 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-indigo-500", props.className)} />
);
const TextArea: React.FC<React.TextareaHTMLAttributes<HTMLTextAreaElement>> = (props) => (
  <textarea {...props} className={classNames("w-full min-h-[120px] rounded-xl bg-zinc-800/70 ring-1 ring-white/10 px-3 py-2 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500", props.className)} />
);

const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement> & {variant?: 'primary'|'ghost'|'danger'|'outline', loading?: boolean}> = ({children, variant='primary', loading, className, disabled, ...rest}) => {
  const base = "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition active:scale-[.99] disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-indigo-600/90 hover:bg-indigo-500 text-white ring-1 ring-white/10",
    ghost:   "bg-transparent hover:bg-white/5 text-zinc-200 ring-1 ring-white/10",
    danger:  "bg-rose-600/90 hover:bg-rose-600 text-white ring-1 ring-white/10",
    outline: "bg-transparent border border-zinc-700 hover:border-zinc-500 text-zinc-200"
  } as const;
  
  return (
    <button {...rest} disabled={disabled || loading} className={classNames(base, variants[variant], className)}>
      {loading && (
        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {children}
    </button>
  );
};

const CopyBtn: React.FC<{text: string}> = ({text}) => {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <Button variant="ghost" onClick={handleCopy} className="gap-1.5">
      {copied ? (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Copié !
        </>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          Copier
        </>
      )}
    </Button>
  );
};

// Output Box Component
const OutputBox: React.FC<{content: string, isStreaming?: boolean, height?: string}> = ({content, isStreaming, height = '360px'}) => {
  return (
    <div className={`relative overflow-auto rounded-xl border ${isStreaming ? 'border-indigo-500/50 ring-2 ring-indigo-500/20' : 'border-white/10'} p-4 bg-zinc-900/50 transition-all`} style={{height}}>
      {isStreaming && (
        <div className="absolute top-2 right-2 flex items-center gap-2 px-2 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 text-xs font-medium">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
          </span>
          Génération en cours...
        </div>
      )}
      {content ? (
        <MarkdownMath source={content} autoScroll={isStreaming} />
      ) : (
        <div className="text-zinc-500 text-sm italic flex items-center justify-center h-full">
          {isStreaming ? 'En attente de réponse...' : 'Aucune sortie pour le moment'}
        </div>
      )}
    </div>
  );
};

// -----------------------------
// Markdown+Math Viewer with Auto-scroll
// -----------------------------
const MarkdownMath: React.FC<{source: string, autoScroll?: boolean}> = ({ source, autoScroll = false }) => {
  const enhanced = useMemo(() => enhanceMathMarkdown(source), [source]);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll pendant le streaming
  useEffect(() => {
    if (autoScroll && containerRef.current) {
      const container = containerRef.current;
      const parent = container.parentElement;
      if (parent) {
        parent.scrollTop = parent.scrollHeight;
      }
    }
  }, [source, autoScroll]);
  
  return (
    <div ref={containerRef} className="markdown-body">
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeRaw]}
      >
        {enhanced}
      </ReactMarkdown>
    </div>
  );
};

// -----------------------------
// Main Component
// -----------------------------
export default function App() {
  const [baseUrl, setBaseUrl] = useState(() => loadLocal('mathrag.baseUrl', 'http://localhost:8000'));
  const [health, setHealth] = useState<any>(null);
  const [ragCheck, setRagCheck] = useState<string>('');

  const [active, setActive] = useState<'chat'|'sheet'|'review'|'formula'|'exam'|'course'|'grade'>('chat');

  // Shared streaming state per panel
  const [out, setOut] = useState<Record<string,string>>({});
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => { saveLocal('mathrag.baseUrl', baseUrl); }, [baseUrl]);

  // Fetch health on mount
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${baseUrl}/health`);
        const j = await r.json();
        setHealth(j);
      } catch (e) {
        setHealth({ ok: false, error: String(e) });
      }
    })();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runStream = async (key: string, url: string, opts: { method?: 'GET'|'POST', body?: any } = {}) => {
    console.log('🚀 Starting stream:', { key, url, opts }); // Debug
    
    try {
      abortRef.current?.abort();
      const ac = new AbortController();
      abortRef.current = ac;
      setBusyKey(key);
      setOut(prev => ({ ...prev, [key]: '' }));
      
      console.log('📡 Fetching:', url); // Debug
      
      await streamSSE(url, { 
        method: opts.method, 
        body: opts.body, 
        signal: ac.signal,
        onToken: (t: string) => {
          console.log('📥 Token received:', t.substring(0, 50)); // Debug
          setOut(prev => ({ ...prev, [key]: (prev[key] ?? '') + t }));
        },
        onError: (e: Error) => {
          console.error('❌ SSE Error:', e); // Debug
          setOut(prev => ({ ...prev, [key]: (prev[key] ?? '') + `\n\n❌ **Erreur**: ${e.message}` }));
        },
        timeout: 120000 // 2 minutes
      });
      
      console.log('✅ Stream completed for:', key); // Debug
    } catch (e:any) {
      console.error('❌ Stream error:', e); // Debug
      if (e?.name === 'AbortError') return; // stopped by user
      setOut(prev => ({ ...prev, [key]: (prev[key] ?? '') + `\n\n❌ **Erreur**: ${e.message || String(e)}` }));
    } finally {
      setBusyKey(null);
    }
  };

  const stop = () => { abortRef.current?.abort(); setBusyKey(null); };

  // -----------------------------
  // Forms state
  // -----------------------------
  const [chatQ, setChatQ] = useState('Explique-moi la méthode de Cauchy-Schwarz et un exemple.');
  const [chatK, setChatK] = useState(6);
  const [chatType, setChatType] = useState<string>('');
  const [chatChapter, setChatChapter] = useState<string>('');

  const [sheetTopic, setSheetTopic] = useState('Équations différentielles linéaires');
  const [sheetLevel, setSheetLevel] = useState('Prépa');
  const [sheetK, setSheetK] = useState(8);
  const [sheetChapter, setSheetChapter] = useState('');

  const [reviewText, setReviewText] = useState('**Théorème**: Soit un espace vectoriel euclidien (E, ⟨·,·⟩). Pour tout x,y ∈ E, on a |⟨x,y⟩| ≤ ∥x∥∥y∥.');

  const [formulaQuery, setFormulaQuery] = useState('Formule de Taylor-Young à l’ordre 2');
  const [formulaK, setFormulaK] = useState(6);

  const [examChapters, setExamChapters] = useState('Complexes, EDL, Coniques');
  const [examDuration, setExamDuration] = useState('3h');
  const [examLevel, setExamLevel] = useState('Prépa');
  const [examK, setExamK] = useState(10);

  const [courseNotion, setCourseNotion] = useState('Série de Fourier');
  const [courseLevel, setCourseLevel] = useState('Prépa');
  const [courseK, setCourseK] = useState(10);
  const [courseChapter, setCourseChapter] = useState('');

  const [gradeStatement, setGradeStatement] = useState('Montrer que la série ∑_{n≥1} 1/n^2 converge et trouver sa somme.');
  const [gradeAnswer, setGradeAnswer] = useState("On utilise le développement de Fourier de x^2 sur [−π,π]…");

  // -----------------------------
  // Panels
  // -----------------------------
  const panels: { key: typeof active; title: string }[] = [
    { key: 'chat', title: 'Chat (Prof)' },
    { key: 'sheet', title: 'Fiche cours' },
    { key: 'review', title: 'Relecture fiche' },
    { key: 'formula', title: 'Formulaire/Recherche formule' },
    { key: 'exam', title: 'Générateur d’examen' },
    { key: 'course', title: 'Construire un cours' },
    { key: 'grade', title: 'Correcteur (évaluation)' },
  ];

  // -----------------------------
  // Render
  // -----------------------------
  return (
    <div className="min-h-screen bg-[radial-gradient(1200px_600px_at_20%_-10%,rgba(99,102,241,0.25),transparent),radial-gradient(1000px_600px_at_100%_10%,rgba(56,189,248,0.15),transparent)] bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur-lg supports-[backdrop-filter]:bg-zinc-950/80 border-b border-white/10 shadow-lg shadow-black/10">
        <div className="max-w-7xl mx-auto px-4 md:px-6 py-4">
          <div className="flex flex-col md:flex-row md:items-center gap-4">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <motion.div 
                className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-cyan-400 grid place-items-center font-bold text-white shadow-lg"
                whileHover={{ scale: 1.05, rotate: 5 }}
                transition={{ type: "spring", stiffness: 400 }}
              >
                𝛑
              </motion.div>
              <div>
                <div className="text-lg md:text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                  Math RAG Teacher
                </div>
                <div className="text-[11px] text-zinc-400 flex items-center gap-2">
                  <span className="flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    {health?.ok ? 'Online' : 'Offline'}
                  </span>
                  <span>•</span>
                  <span>Markdown + KaTeX</span>
                </div>
              </div>
            </div>
            
            {/* Controls */}
            <div className="flex-1 flex flex-wrap items-center gap-2 md:justify-end">
              <TextInput 
                value={baseUrl} 
                onChange={(e)=>setBaseUrl(e.target.value)} 
                placeholder="http://localhost:8000" 
                className="w-full md:w-[220px] text-sm" 
              />
              <Button 
                variant="outline" 
                className="text-xs"
                onClick={async ()=>{ 
                  try{ 
                    const r=await fetch(`${baseUrl}/health`); 
                    const j=await r.json(); 
                    setHealth(j);
                  }catch(e){
                    setHealth({ok:false,error:String(e)})
                  }
                }}
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Health
              </Button>
              <Button 
                variant="outline"
                className="text-xs"
                onClick={async ()=>{ 
                  try{ 
                    const r=await fetch(`${baseUrl}/rag_check`); 
                    const j= await r.json(); 
                    setRagCheck(JSON.stringify(j,null,2)); 
                  }catch(e){ 
                    setRagCheck(String(e)); 
                  } 
                }}
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                RAG Check
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 md:px-6 py-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Panels */}
        <div className="lg:col-span-8 space-y-6">
          <Card>
            <div className="flex flex-wrap gap-2">
              {panels.map(p => (
                <Button key={p.key} variant={active===p.key? 'primary':'ghost'} onClick={()=>setActive(p.key)}>
                  {p.title}
                </Button>
              ))}
            </div>
          </Card>

          {active==='chat' && (
            <Card>
              <SectionTitle 
                icon={<span className="text-2xl">💬</span>}
                title="Chat (Prof)" 
                subtitle="Pose une question, choisis la granularité de récupération et le type de document." 
              />
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-zinc-300 mb-1.5">Question</label>
                    <TextArea 
                      value={chatQ} 
                      onChange={e=>setChatQ(e.target.value)} 
                      placeholder="Explique-moi..." 
                      rows={3}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-zinc-300 mb-1.5">Nombre de docs (k)</label>
                      <NumberInput value={chatK} onChange={e=>setChatK(parseInt(e.target.value||'6'))} min={1} max={20} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-zinc-300 mb-1.5">Type de doc</label>
                      <Select value={chatType} onChange={e=>setChatType(e.target.value)}>
                        <option value="">Tous</option>
                        <option value="théorie">Théorie</option>
                        <option value="exercice">Exercice</option>
                        <option value="méthode">Méthode</option>
                        <option value="exemple">Exemple</option>
                      </Select>
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-zinc-300 mb-1.5">Chapitre (optionnel)</label>
                      <TextInput value={chatChapter} onChange={e=>setChatChapter(e.target.value)} placeholder="ex: 1, 5, 7" />
                    </div>
                  </div>
                  <div className="flex gap-2 pt-2">
                    <Button 
                      loading={busyKey==='chat'}
                      disabled={!chatQ.trim()}
                      onClick={()=>{
                        console.log('🔵 Chat button clicked!', { chatQ, chatK, chatType, chatChapter }); // Debug
                        const params = new URLSearchParams({ question: chatQ, k: String(chatK) });
                        if (chatType) params.set('doc_type', chatType);
                        if (chatChapter) params.set('chapter', chatChapter);
                        const url = `${baseUrl}/chat?${params.toString()}`;
                        console.log('🔗 URL:', url); // Debug
                        runStream('chat', url);
                      }}
                    >
                      {busyKey==='chat' ? 'Génération...' : 'Lancer'}
                    </Button>
                    {busyKey==='chat' && <Button variant="danger" onClick={stop}>Arrêter</Button>}
                    {out.chat && <CopyBtn text={out.chat} />}
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Réponse (Markdown + KaTeX)</label>
                  <OutputBox content={out.chat ?? ''} isStreaming={busyKey==='chat'} />
                </div>
              </div>
            </Card>
          )}

          {active==='sheet' && (
            <Card>
              <SectionTitle title="Fiche cours" subtitle="Génère une fiche thématique avec contexte RAG." />
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="space-y-3">
                  <TextInput value={sheetTopic} onChange={e=>setSheetTopic(e.target.value)} placeholder="Sujet (ex: EDL, suites, probas)" />
                  <div className="grid grid-cols-2 gap-3">
                    <Select value={sheetLevel} onChange={e=>setSheetLevel(e.target.value)}>
                      <option>Prépa</option>
                      <option>Licence</option>
                      <option>Classes prépas</option>
                      <option>Lycée</option>
                    </Select>
                    <NumberInput value={sheetK} onChange={e=>setSheetK(parseInt(e.target.value||'0'))} min={1} max={20} />
                    <TextInput value={sheetChapter} onChange={e=>setSheetChapter(e.target.value)} placeholder="chapter (optionnel)" className="col-span-2" />
                  </div>
                  <div className="flex gap-3">
                    <Button disabled={busyKey==='sheet'} onClick={()=>{
                      const params = new URLSearchParams({ topic: sheetTopic, level: sheetLevel, k: String(sheetK) });
                      if (sheetChapter) params.set('chapter', sheetChapter);
                      runStream('sheet', `${baseUrl}/sheet?${params.toString()}`);
                    }}>Lancer</Button>
                    <Button variant="danger" onClick={stop}>Stop</Button>
                    <CopyBtn text={out.sheet ?? ''} />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="text-sm text-zinc-400">Sortie</div>
                  <div className="h-[360px] overflow-auto rounded-xl border border-white/10 p-4 bg-zinc-900/50">
                    <MarkdownMath source={out.sheet ?? ''} />
                  </div>
                </div>
              </div>
            </Card>
          )}

          {active==='review' && (
            <Card>
              <SectionTitle title="Relecture de fiche" subtitle="Envoie une fiche pour retour/annotations." />
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="space-y-3">
                  <TextArea value={reviewText} onChange={e=>setReviewText(e.target.value)} placeholder="Colle ici le contenu de la fiche…" />
                  <div className="flex gap-3">
                    <Button disabled={busyKey==='review'} onClick={()=>{
                      runStream('review', `${baseUrl}/sheet_review`, { method: 'POST', body: { sheet_text: reviewText } });
                    }}>Lancer</Button>
                    <Button variant="danger" onClick={stop}>Stop</Button>
                    <CopyBtn text={out.review ?? ''} />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="text-sm text-zinc-400">Sortie</div>
                  <div className="h-[360px] overflow-auto rounded-xl border border-white/10 p-4 bg-zinc-900/50">
                    <MarkdownMath source={out.review ?? ''} />
                  </div>
                </div>
              </div>
            </Card>
          )}

          {active==='formula' && (
            <Card>
              <SectionTitle title="Recherche de formule" subtitle="Cherche d’abord dans le formulaire, fallback général sinon." />
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="space-y-3">
                  <TextInput value={formulaQuery} onChange={e=>setFormulaQuery(e.target.value)} placeholder="Ex: Inégalité de Jensen" />
                  <div className="grid grid-cols-2 gap-3">
                    <NumberInput value={formulaK} onChange={e=>setFormulaK(parseInt(e.target.value||'0'))} min={1} max={20} />
                  </div>
                  <div className="flex gap-3">
                    <Button disabled={busyKey==='formula'} onClick={()=>{
                      const params = new URLSearchParams({ query: formulaQuery, k: String(formulaK) });
                      runStream('formula', `${baseUrl}/formula?${params.toString()}`);
                    }}>Lancer</Button>
                    <Button variant="danger" onClick={stop}>Stop</Button>
                    <CopyBtn text={out.formula ?? ''} />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="text-sm text-zinc-400">Sortie</div>
                  <div className="h-[360px] overflow-auto rounded-xl border border-white/10 p-4 bg-zinc-900/50">
                    <MarkdownMath source={out.formula ?? ''} />
                  </div>
                </div>
              </div>
            </Card>
          )}

          {active==='exam' && (
            <Card>
              <SectionTitle title="Générateur d’examen" subtitle="Liste de chapitres CSV, durée, niveau, k." />
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="space-y-3">
                  <TextInput value={examChapters} onChange={e=>setExamChapters(e.target.value)} placeholder="ex: 1,5,7 ou Complexes, EDL" />
                  <div className="grid grid-cols-2 gap-3">
                    <TextInput value={examDuration} onChange={e=>setExamDuration(e.target.value)} placeholder="3h" />
                    <Select value={examLevel} onChange={e=>setExamLevel(e.target.value)}>
                      <option>Prépa</option>
                      <option>Licence</option>
                      <option>Terminale</option>
                    </Select>
                    <NumberInput value={examK} onChange={e=>setExamK(parseInt(e.target.value||'0'))} min={3} max={30} className="col-span-2" />
                  </div>
                  <div className="flex gap-3">
                    <Button disabled={busyKey==='exam'} onClick={()=>{
                      const params = new URLSearchParams({ chapters: examChapters, duration: examDuration, level: examLevel, k: String(examK) });
                      runStream('exam', `${baseUrl}/exam?${params.toString()}`);
                    }}>Lancer</Button>
                    <Button variant="danger" onClick={stop}>Stop</Button>
                    <CopyBtn text={out.exam ?? ''} />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="text-sm text-zinc-400">Sujet généré</div>
                  <div className="h-[360px] overflow-auto rounded-xl border border-white/10 p-4 bg-zinc-900/50">
                    <MarkdownMath source={out.exam ?? ''} />
                  </div>
                </div>
              </div>
            </Card>
          )}

          {active==='course' && (
            <Card>
              <SectionTitle title="Construire un cours" subtitle="À partir d’une notion + niveau (option: chapter, k)." />
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="space-y-3">
                  <TextInput value={courseNotion} onChange={e=>setCourseNotion(e.target.value)} placeholder="Notion (ex: Série de Fourier)" />
                  <div className="grid grid-cols-2 gap-3">
                    <Select value={courseLevel} onChange={e=>setCourseLevel(e.target.value)}>
                      <option>Prépa</option>
                      <option>Licence</option>
                      <option>Terminale</option>
                    </Select>
                    <NumberInput value={courseK} onChange={e=>setCourseK(parseInt(e.target.value||'0'))} min={1} max={20} />
                    <TextInput value={courseChapter} onChange={e=>setCourseChapter(e.target.value)} placeholder="chapter (optionnel)" className="col-span-2" />
                  </div>
                  <div className="flex gap-3">
                    <Button disabled={busyKey==='course'} onClick={()=>{
                      const params = new URLSearchParams({ notion: courseNotion, level: courseLevel, k: String(courseK) });
                      if (courseChapter) params.set('chapter', courseChapter);
                      runStream('course', `${baseUrl}/course?${params.toString()}`);
                    }}>Lancer</Button>
                    <Button variant="danger" onClick={stop}>Stop</Button>
                    <CopyBtn text={out.course ?? ''} />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="text-sm text-zinc-400">Cours généré</div>
                  <div className="h-[360px] overflow-auto rounded-xl border border-white/10 p-4 bg-zinc-900/50">
                    <MarkdownMath source={out.course ?? ''} />
                  </div>
                </div>
              </div>
            </Card>
          )}

          {active==='grade' && (
            <Card>
              <SectionTitle title="Correcteur" subtitle="Envoie un énoncé + copie de l’étudiant." />
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="space-y-3">
                  <TextArea value={gradeStatement} onChange={e=>setGradeStatement(e.target.value)} placeholder="Énoncé…" />
                  <TextArea value={gradeAnswer} onChange={e=>setGradeAnswer(e.target.value)} placeholder="Réponse de l’étudiant…" />
                  <div className="flex gap-3">
                    <Button disabled={busyKey==='grade'} onClick={()=>{
                      runStream('grade', `${baseUrl}/grade`, { method: 'POST', body: { statement: gradeStatement, student_answer: gradeAnswer } });
                    }}>Lancer</Button>
                    <Button variant="danger" onClick={stop}>Stop</Button>
                    <CopyBtn text={out.grade ?? ''} />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="text-sm text-zinc-400">Évaluation</div>
                  <div className="h-[360px] overflow-auto rounded-xl border border-white/10 p-4 bg-zinc-900/50">
                    <MarkdownMath source={out.grade ?? ''} />
                  </div>
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Right: Status, Health, RAG */}
        <div className="lg:col-span-4 space-y-6">
          <Card>
            <SectionTitle title="État du modèle" subtitle="/health" />
            <div className="mt-3 text-sm">
              {health ? (
                <pre className="whitespace-pre-wrap break-words text-zinc-300">{JSON.stringify(health, null, 2)}</pre>
              ) : (
                <div className="text-zinc-400">—</div>
              )}
            </div>
          </Card>

          <Card>
            <SectionTitle title="RAG self-check" subtitle="/rag_check" />
            <div className="mt-3 text-sm">
              {ragCheck ? (
                <pre className="whitespace-pre-wrap break-words text-zinc-300">{ragCheck}</pre>
              ) : (
                <div className="text-zinc-400">Clique sur “RAG check” en haut pour actualiser.</div>
              )}
            </div>
          </Card>

          <Card>
            <SectionTitle title="Astuces" subtitle="Rendu des démonstrations et formules" />
            <ul className="list-disc pl-5 space-y-2 text-sm text-zinc-300">
              <li>Le rendu math utilise <span className="font-semibold">KaTeX</span>. Tu peux écrire du LaTeX inline <code>$(a+b)^2$</code> ou en bloc <code>$$\\int f$$</code>.</li>
              <li>Les blocs commençant par <span className="italic">**Théorème**</span>, <span className="italic">**Définition**</span>, etc. sont encadrés automatiquement.</li>
              <li>Le bouton <span className="font-semibold">Stop</span> coupe le flux SSE côté client.</li>
            </ul>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-6 text-center text-xs text-zinc-500">
        <div className="max-w-7xl mx-auto px-4 md:px-6 flex items-center justify-between">
          <div>Conçu pour ton serveur FastAPI • Thème 100% sombre</div>
          <div className="flex items-center gap-2">
            <span className="text-zinc-600">|</span>
            <span>{new Date().getFullYear()}</span>
            <span className="text-zinc-600">|</span>
            <a href="https://github.com" className="hover:text-zinc-300 transition">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
