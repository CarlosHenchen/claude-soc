import { useState } from "react";
import { ChevronRight } from "lucide-react";
import { band, bandSoft, bandText, fmt1, levelName } from "@/lib/maturity";
import { Card } from "@/components/ui/card";
import { SubBars, SubRadar, type SubView } from "@/components/charts/SubdomainCharts";

export interface DomainDetailData {
  key: string;
  full: string;
  score: number | null;
  views: SubView[];
}

/**
 * Collapsible per-domain card with a Radar | Barras toggle. Both views read the
 * same `views` array and the same `band()` color scale — no duplicated logic.
 */
export function DomainDetailCard({ d, defaultOpen = false }: { d: DomainDetailData; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  const [mode, setMode] = useState<"radar" | "bars">("radar");
  const nAssessed = d.views.filter((v) => v.assessed).length;
  const useRadar = mode === "radar" && nAssessed >= 3;

  return (
    <Card>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2 px-4 py-3 text-left hover:bg-muted/40"
      >
        <ChevronRight className={`h-4 w-4 text-muted-foreground transition-transform ${open ? "rotate-90" : ""}`} />
        <b className="text-sm">{d.key}</b>
        <span className="truncate text-xs text-muted-foreground">
          {d.full} · {d.views.length} subdomínios
        </span>
        <span
          className="ml-auto shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
          style={{ background: bandSoft(d.score), color: bandText(d.score) }}
        >
          {fmt1(d.score)} · {levelName(d.score)}
        </span>
      </button>
      {open && (
        <div className="px-4 pb-4">
          <div className="mb-2 inline-flex overflow-hidden rounded-md border">
            {(["radar", "bars"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-3 py-1 text-xs font-semibold ${
                  mode === m ? "bg-primary text-primary-foreground" : "bg-card text-muted-foreground"
                }`}
              >
                {m === "radar" ? "Radar" : "Barras"}
              </button>
            ))}
          </div>
          {mode === "radar" && nAssessed < 3 && (
            <p className="mb-1 text-xs text-muted-foreground">
              Radar requer ≥3 subdomínios avaliados — mostrando barras.
            </p>
          )}
          {useRadar ? (
            <SubRadar views={d.views} accent={band(d.score)} />
          ) : (
            <SubBars views={d.views} domAvg={d.score} />
          )}
        </div>
      )}
    </Card>
  );
}
