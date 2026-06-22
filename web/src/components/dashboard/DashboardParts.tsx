import { Link } from "react-router-dom";
import { CircleDashed } from "lucide-react";
import { band, bandSoft, bandText, fmt1, levelName } from "@/lib/maturity";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export interface DomainView {
  key: string;
  full: string;
  score: number | null;
  cap: number | null;
  answered: number;
  total: number;
  assessed: boolean;
  hasCapability?: boolean;
}

export function Kpi({ label, value, sub, color }: { label: string; value: string; sub?: string; color?: string }) {
  return (
    <div className="rounded-lg border bg-muted/40 p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-0.5 text-xl font-semibold" style={color ? { color, fontSize: 15 } : undefined}>
        {value}
      </div>
      {sub && <div className="text-xs text-muted-foreground">{sub}</div>}
    </div>
  );
}

/** Per-domain score card with a 0–5 segmented level bar; explicit "não avaliado" state. */
export function DomainScoreCard({ d, withCapability }: { d: DomainView; withCapability?: boolean }) {
  if (!d.assessed) {
    return (
      <div className="rounded-lg border border-dashed p-3 opacity-85" title={d.full}>
        <div className="truncate text-xs font-semibold text-slate-700">{d.key}</div>
        <div className="mt-2 text-sm text-muted-foreground">— não avaliado</div>
        <div className="mt-4 text-xs text-muted-foreground">0/{d.total} itens</div>
      </div>
    );
  }
  return (
    <div className="rounded-lg border p-3" title={d.full}>
      <div className="truncate text-xs font-semibold text-slate-700">{d.key}</div>
      <div className="text-2xl font-semibold" style={{ color: bandText(d.score) }}>
        {fmt1(d.score)} <span className="text-xs text-muted-foreground">/5</span>
      </div>
      <span
        className="inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold"
        style={{ background: bandSoft(d.score), color: bandText(d.score) }}
      >
        {levelName(d.score)}
      </span>
      <div className="mt-2 flex gap-[3px]">
        {[0, 1, 2, 3, 4].map((k) => (
          <span
            key={k}
            className="h-1.5 flex-1 rounded-sm"
            style={{ background: k < Math.round(d.score ?? 0) ? band(d.score) : "#e2e8f0" }}
          />
        ))}
      </div>
      <div className="mt-1.5 text-xs text-muted-foreground">
        cobertura {d.answered}/{d.total}
        {withCapability && d.hasCapability ? ` · cap ${d.cap == null ? "—" : fmt1(d.cap) + "/3"}` : ""}
      </div>
    </div>
  );
}

export function EmptyDashboard({ runHref }: { runHref: string }) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center py-12 text-center">
        <CircleDashed className="h-10 w-10 text-slate-300" />
        <h3 className="mt-2 font-semibold">Nenhum item avaliado ainda</h3>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          Comece a preencher as respostas para ver o score consolidado, o ranking de domínios e os gráficos.
        </p>
        <Button asChild className="mt-4">
          <Link to={runHref}>Começar a preencher</Link>
        </Button>
      </CardContent>
    </Card>
  );
}

function SkelBox({ h }: { h: number }) {
  return <div className="animate-pulse rounded-lg bg-muted" style={{ height: h }} />;
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <div className="grid gap-4" style={{ gridTemplateColumns: "300px 1fr" }}>
        <SkelBox h={240} />
        <SkelBox h={240} />
      </div>
      <div className="grid gap-4" style={{ gridTemplateColumns: "1.25fr 1fr" }}>
        <SkelBox h={320} />
        <SkelBox h={320} />
      </div>
      <SkelBox h={160} />
    </div>
  );
}

export function ChartCard({ title, extra, children }: { title: string; extra?: React.ReactNode; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="flex-row items-center gap-2 space-y-0 pb-2">
        <CardTitle className="text-sm">{title}</CardTitle>
        {extra}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
