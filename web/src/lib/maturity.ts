// Maturity scale (0–5) helpers — accessible red→amber→green bands, shared by all charts.

export const LEVEL_NAMES = [
  "Inexistente",
  "Inicial",
  "Limitado",
  "Definido",
  "Gerenciado",
  "Otimizado",
];

/** Convert a normalized percentage (0–100) to the 0–5 maturity scale. */
export function pctToScore(pct: number | null | undefined): number | null {
  return pct == null ? null : (pct / 100) * 5;
}

export function band(s: number | null): string {
  if (s == null) return "#cbd5e1";
  if (s < 1) return "#dc2626";
  if (s < 2) return "#ea580c";
  if (s < 3) return "#d97706";
  if (s < 4) return "#65a30d";
  return "#16a34a";
}
export function bandSoft(s: number | null): string {
  if (s == null) return "#f1f5f9";
  if (s < 1) return "#fee2e2";
  if (s < 2) return "#ffedd5";
  if (s < 3) return "#fef3c7";
  if (s < 4) return "#ecfccb";
  return "#dcfce7";
}
export function bandText(s: number | null): string {
  if (s == null) return "#64748b";
  if (s < 1) return "#991b1b";
  if (s < 2) return "#9a3412";
  if (s < 3) return "#854d0e";
  if (s < 4) return "#3f6212";
  return "#166534";
}
export function levelName(s: number | null): string {
  return s == null ? "não avaliado" : LEVEL_NAMES[Math.max(0, Math.min(5, Math.round(s)))];
}
export function fmt1(s: number | null): string {
  return s == null ? "—" : ((Math.round(s * 10) / 10).toFixed(1));
}

/** Split a long label into ≤3 lines without cutting words (for radar axis names). */
export function wrapLabel(s: string, width = 13): string {
  const words = String(s).split(" ");
  let lines: string[] = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > width) {
      if (cur) lines.push(cur);
      cur = w;
    } else cur = (cur ? cur + " " : "") + w;
  }
  if (cur) lines.push(cur);
  if (lines.length > 3) {
    lines = lines.slice(0, 3);
    lines[2] += "…";
  }
  return lines.join("\n");
}
