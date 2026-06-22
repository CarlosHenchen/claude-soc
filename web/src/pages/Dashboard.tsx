import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Download, Pencil } from "lucide-react";
import { api, getToken } from "@/lib/api";
import type { Assessment, Dashboard as DashboardData, FrameworkDetail } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { bandSoft, bandText, fmt1, levelName, pctToScore } from "@/lib/maturity";
import { MaturityGauge } from "@/components/charts/MaturityGauge";
import { DomainRanking, type RankItem } from "@/components/charts/DomainRanking";
import { MaturityRadar } from "@/components/charts/MaturityRadar";
import { EvolutionLine, type EvoPoint } from "@/components/charts/EvolutionLine";
import {
  ChartCard,
  DashboardSkeleton,
  DomainScoreCard,
  EmptyDashboard,
  Kpi,
  type DomainView,
} from "@/components/dashboard/DashboardParts";
import { DomainDetailCard } from "@/components/dashboard/DomainDetailCard";
import type { SubView } from "@/components/charts/SubdomainCharts";

export function Dashboard() {
  const { id } = useParams();
  const aid = Number(id);
  const [data, setData] = useState<DashboardData | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [controlNames, setControlNames] = useState<Record<number, string>>({});
  const [domainNames, setDomainNames] = useState<Record<number, string>>({});
  const [evo, setEvo] = useState<EvoPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get<Assessment>(`/assessments/${aid}`),
      api.get<DashboardData>(`/assessments/${aid}/dashboard`),
    ])
      .then(async ([a, d]) => {
        setAssessment(a);
        setData(d);
        // Map control id -> full name for the per-domain detail (the dashboard
        // payload only carries the short code).
        try {
          const fw = await api.get<FrameworkDetail>(`/frameworks/${a.framework_id}`);
          const names: Record<number, string> = {};
          const doms: Record<number, string> = {};
          fw.domains.forEach((dom) => {
            doms[dom.id] = dom.name;
            dom.controls.forEach((c) => (names[c.id] = c.name));
          });
          setControlNames(names);
          setDomainNames(doms);
        } catch {
          /* full names are optional; fall back to codes */
        }
      })
      .finally(() => setLoading(false));
  }, [aid]);

  // Evolution: other assessments of the same framework + client, ordered by date.
  useEffect(() => {
    if (!assessment) return;
    api.get<Assessment[]>("/assessments").then(async (all) => {
      const siblings = all
        .filter((x) => x.framework_id === assessment.framework_id && x.client === assessment.client)
        .sort((x, y) => x.created_at.localeCompare(y.created_at));
      if (siblings.length < 2) return;
      const pts = await Promise.all(
        siblings.map(async (s) => {
          const d = await api.get<DashboardData>(`/assessments/${s.id}/dashboard`);
          return {
            label: s.name.slice(0, 14),
            score: pctToScore(d.overall.normalized_pct),
          } as EvoPoint;
        })
      );
      setEvo(pts);
    });
  }, [assessment]);

  const model = useMemo(() => {
    if (!data) return null;
    const D: DomainView[] = data.domains.map((d) => ({
      key: d.label ?? "",
      full: domainNames[d.scope_id ?? -1] ?? d.label ?? "",
      score: pctToScore(d.normalized_pct),
      cap: null,
      target: pctToScore(d.target_pct),
      answered: d.answered,
      total: d.total,
      assessed: d.answered > 0,
    })) as any;
    const overall = pctToScore(data.overall.normalized_pct);
    const overallTgt = pctToScore(data.overall.target_pct);
    const assessed = D.filter((d) => d.assessed);
    const best = [...assessed].sort((a, b) => (b.score ?? 0) - (a.score ?? 0))[0];
    const worst = [...assessed].sort((a, b) => (a.score ?? 0) - (b.score ?? 0))[0];
    return { D, overall, overallTgt, assessed, best, worst };
  }, [data, domainNames]);

  async function downloadPdf() {
    setDownloading(true);
    try {
      const res = await fetch(`/api/assessments/${aid}/report.pdf`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (!res.ok) throw new Error("Falha ao gerar PDF");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `relatorio-${aid}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloading(false);
    }
  }

  if (loading) return <DashboardSkeleton />;
  if (!data || !assessment || !model) return <p className="text-muted-foreground">Não foi possível carregar.</p>;

  const header = (
    <div className="flex items-center gap-3">
      <Button asChild variant="ghost" size="icon">
        <Link to="/assessments">
          <ArrowLeft className="h-4 w-4" />
        </Link>
      </Button>
      <div className="flex-1">
        <h1 className="text-xl font-bold">{assessment.name} · Dashboard</h1>
        <p className="text-sm text-muted-foreground">{assessment.client ?? "—"}</p>
      </div>
      <Button asChild variant="outline">
        <Link to={`/assessments/${aid}/run`}>
          <Pencil className="h-4 w-4" /> Avaliar
        </Link>
      </Button>
      <Button onClick={downloadPdf} disabled={downloading}>
        <Download className="h-4 w-4" /> {downloading ? "Gerando…" : "Exportar PDF"}
      </Button>
    </div>
  );

  if (data.overall.answered === 0) {
    return (
      <div className="space-y-4">
        {header}
        <EmptyDashboard runHref={`/assessments/${aid}/run`} />
      </div>
    );
  }

  const { D, overall, overallTgt, assessed, best, worst } = model;
  const ranked = [...D].sort((a, b) => (b.assessed ? 1 : 0) - (a.assessed ? 1 : 0) || (b.score ?? 0) - (a.score ?? 0));
  const rankItems: RankItem[] = ranked.map((d) => ({
    name: d.key,
    full: d.full,
    score: d.score,
    target: d.target,
    assessed: d.assessed,
  }));
  const radarItems = assessed.map((d) => ({ name: d.key, full: d.full, score: d.score, cap: d.cap }));
  const naCount = D.length - assessed.length;

  return (
    <div className="space-y-4">
      {header}

      <div className="grid gap-4" style={{ gridTemplateColumns: "300px 1fr" }}>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm">Maturidade geral</CardTitle>
          </CardHeader>
          <CardContent>
            <MaturityGauge score={overall} />
            <div className="-mt-2 text-center">
              <span
                className="inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold"
                style={{ background: bandSoft(overall), color: bandText(overall) }}
              >
                {levelName(overall)}
              </span>
              <div className="mt-1.5 text-xs text-muted-foreground">
                {data.overall.answered}/{data.overall.total} itens
                {overallTgt != null ? ` · meta ${fmt1(overallTgt)}` : ""}
              </div>
            </div>
          </CardContent>
        </Card>
        <ChartCard title="Resumo">
          <div className="grid grid-cols-2 gap-3">
            <Kpi label="domínios avaliados" value={`${assessed.length} / ${D.length}`} />
            <Kpi
              label="cobertura de itens"
              value={`${Math.round((data.overall.answered / data.overall.total) * 100)}%`}
              sub={`${data.overall.answered}/${data.overall.total}`}
            />
            <Kpi
              label="maior maturidade"
              value={best ? `${best.key} · ${fmt1(best.score)}` : "—"}
              color={best ? bandText(best.score) : undefined}
            />
            <Kpi
              label="menor maturidade"
              value={worst ? `${worst.key} · ${fmt1(worst.score)}` : "—"}
              color={worst ? bandText(worst.score) : undefined}
            />
          </div>
        </ChartCard>
      </div>

      <div className="grid gap-4" style={{ gridTemplateColumns: "1.25fr 1fr" }}>
        <ChartCard title="Ranking de domínios · 0–5, ordenado">
          <DomainRanking items={rankItems} avg={overall} />
        </ChartCard>
        <ChartCard title="Radar — shape">
          {radarItems.length >= 3 ? (
            <MaturityRadar items={radarItems} />
          ) : (
            <p className="py-10 text-center text-sm text-muted-foreground">
              Radar disponível a partir de 3 domínios avaliados.
            </p>
          )}
          {naCount > 0 && (
            <p className="mt-1 text-center text-xs text-muted-foreground">
              {naCount} domínio(s) não avaliado(s) fora do radar
            </p>
          )}
        </ChartCard>
      </div>

      <ChartCard title="Score por domínio · nível 0–5">
        <div className="grid gap-3" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))" }}>
          {D.map((d) => (
            <DomainScoreCard key={d.key} d={d} />
          ))}
        </div>
      </ChartCard>

      {evo.length >= 2 && (
        <ChartCard title="Evolução · maturidade geral (0–5)">
          <EvolutionLine points={evo} />
        </ChartCard>
      )}

      <div className="space-y-3">
        <h2 className="text-lg font-semibold">
          Detalhe por domínio{" "}
          <span className="text-sm font-normal text-muted-foreground">(clique para abrir · alterne Radar/Barras)</span>
        </h2>
        {data.domains
          .filter((dom) => dom.answered > 0)
          .map((dom) => {
            const views: SubView[] = (dom.controls ?? []).map((c) => ({
              code: c.label ?? "",
              full: controlNames[c.scope_id ?? -1] ?? c.label ?? "",
              score: pctToScore(c.normalized_pct),
              assessed: c.answered > 0,
            }));
            return (
              <DomainDetailCard
                key={dom.scope_id ?? dom.label}
                d={{
                  key: dom.label ?? "",
                  full: domainNames[dom.scope_id ?? -1] ?? dom.label ?? "",
                  score: pctToScore(dom.normalized_pct),
                  views,
                }}
              />
            );
          })}
      </div>
    </div>
  );
}
