/**
 * Markdown enhancement for mathematical callouts
 */

const MATH_LABELS = [
  'Théorème',
  'Définition',
  'Lemme',
  'Proposition',
  'Corollaire',
  'Preuve',
  'Démonstration'
] as const;

export function enhanceMathMarkdown(source: string): string {
  const lines = source.split('\n');
  const output: string[] = [];
  let i = 0;

  while (i < lines.length) {
    const raw = lines[i];
    const trimmed = raw.replace(/^\s+/, '');
    
    const label = MATH_LABELS.find(
      lbl => trimmed.startsWith(`**${lbl}**`) || trimmed.startsWith(`**${lbl}**:`)
    );

    if (label) {
      let rest = trimmed.replace(`**${label}**`, '').trimStart();
      if (rest.startsWith(':')) rest = rest.slice(1).trimStart();

      const body: string[] = [];
      if (rest) body.push(rest);
      i++;

      // Accumulate until empty line or EOF
      while (i < lines.length && lines[i].trim() !== '') {
        body.push(lines[i]);
        i++;
      }

      output.push('');
      output.push(
        `<div class="callout ${label.toLowerCase()}">` +
        `<div class="callout-title">${label}</div>` +
        `<div class="callout-body">${body.join('\n')}</div>` +
        `</div>`
      );

      if (i < lines.length && lines[i].trim() === '') {
        output.push('');
        i++;
      }
      continue;
    }

    output.push(raw);
    i++;
  }

  return output.join('\n');
}
