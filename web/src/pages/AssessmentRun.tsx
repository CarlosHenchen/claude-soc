import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, BarChart3, Save } from "lucide-react";
import { api } from "@/lib/api";
import type { Assessment, Domain, FrameworkDetail, ResponseItem } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface Draft {
  current_value: number | null;
  target_value: number | null;
  evidence: string | null;
}

const NONE = "__none__";

export function AssessmentRun() {
  const { id } = useParams();
  const aid = Number(id);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [framework, setFramework] = useState<FrameworkDetail | null>(null);
  const [drafts, setDrafts] = useState<Record<number, Draft>>({});
  const [activeDomain, setActiveDomain] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const a = await api.get<Assessment>(`/assessments/${aid}`);
      setAssessment(a);
      const fw = await api.get<FrameworkDetail>(`/frameworks/${a.framework_id}`);
      setFramework(fw);
      setActiveDomain(fw.domains[0]?.id ?? null);
      const resp = await api.get<ResponseItem[]>(`/assessments/${aid}/responses`);
      const map: Record<number, Draft> = {};
      for (const r of resp)
        map[r.question_id] = {
          current_value: r.current_value,
          target_value: r.target_value,
          evidence: r.evidence,
        };
      setDrafts(map);
    })();
  }, [aid]);

  function setDraft(qid: number, patch: Partial<Draft>) {
    setDrafts((d) => ({
      ...d,
      [qid]: { current_value: null, target_value: null, evidence: null, ...d[qid], ...patch },
    }));
  }

  async function save() {
    setSaving(true);
    try {
      const payload = Object.entries(drafts)
        .filter(([, d]) => d.current_value != null || d.target_value != null || d.evidence)
        .map(([qid, d]) => ({
          question_id: Number(qid),
          current_value: d.current_value,
          target_value: d.target_value,
          evidence: d.evidence,
        }));
      await api.put(`/assessments/${aid}/responses`, payload);
      setSavedAt(new Date().toLocaleTimeString());
    } finally {
      setSaving(false);
    }
  }

  const domainProgress = useMemo(() => {
    const prog: Record<number, { answered: number; total: number }> = {};
    framework?.domains.forEach((d) => {
      let answered = 0;
      let total = 0;
      d.controls.forEach((c) =>
        c.questions.forEach((q) => {
          total++;
          if (drafts[q.id]?.current_value != null) answered++;
        })
      );
      prog[d.id] = { answered, total };
    });
    return prog;
  }, [framework, drafts]);

  if (!framework || !assessment) return <p className="text-muted-foreground">Carregando…</p>;

  const domain = framework.domains.find((d) => d.id === activeDomain) ?? framework.domains[0];

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="icon">
          <Link to="/assessments">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-xl font-bold">{assessment.name}</h1>
          <p className="text-sm text-muted-foreground">
            {assessment.client ?? "—"} · {framework.name}
          </p>
        </div>
        {savedAt && <span className="text-xs text-muted-foreground">Salvo às {savedAt}</span>}
        <Button onClick={save} disabled={saving}>
          <Save className="h-4 w-4" /> {saving ? "Salvando…" : "Salvar"}
        </Button>
        <Button asChild variant="outline">
          <Link to={`/assessments/${aid}/dashboard`}>
            <BarChart3 className="h-4 w-4" /> Dashboard
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-[220px_1fr] gap-5">
        {/* Domain navigation */}
        <div className="space-y-1">
          {framework.domains.map((d) => {
            const p = domainProgress[d.id];
            const done = p && p.answered === p.total && p.total > 0;
            return (
              <button
                key={d.id}
                onClick={() => setActiveDomain(d.id)}
                className={cn(
                  "flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm",
                  d.id === domain.id ? "bg-primary/10 text-primary" : "hover:bg-accent"
                )}
              >
                <span className="font-medium">{d.key}</span>
                <span className={cn("text-xs", done ? "text-emerald-600" : "text-muted-foreground")}>
                  {p?.answered}/{p?.total}
                </span>
              </button>
            );
          })}
        </div>

        {/* Questions for the selected domain */}
        <div className="space-y-4">
          <DomainHeader domain={domain} />
          {domain.controls.map((c) => (
            <Card key={c.id}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">
                  <Badge variant="secondary" className="mr-2">
                    {c.code}
                  </Badge>
                  {c.name}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {c.questions.map((q) => {
                  const d = drafts[q.id];
                  return (
                    <div key={q.id} className="border-t pt-3 first:border-t-0 first:pt-0">
                      <div className="mb-2">
                        <span className="text-xs font-semibold text-primary">{q.code}</span>
                        <p className="text-sm">{q.text}</p>
                        {q.guidance && (
                          <p className="mt-0.5 text-xs text-muted-foreground">{q.guidance}</p>
                        )}
                      </div>
                      <div className="grid gap-3 md:grid-cols-2">
                        <LevelSelect
                          label="Avaliação atual"
                          domain={domain}
                          value={d?.current_value ?? null}
                          onChange={(v) => setDraft(q.id, { current_value: v })}
                        />
                        <LevelSelect
                          label="Meta (nível desejado)"
                          domain={domain}
                          value={d?.target_value ?? null}
                          onChange={(v) => setDraft(q.id, { target_value: v })}
                        />
                      </div>
                      <Textarea
                        className="mt-2"
                        placeholder="Evidências / observações"
                        value={d?.evidence ?? ""}
                        onChange={(e) => setDraft(q.id, { evidence: e.target.value })}
                      />
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

function DomainHeader({ domain }: { domain: Domain }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <h2 className="font-semibold">{domain.name}</h2>
      <p className="text-xs text-muted-foreground">
        {domain.reference_model} · escala {domain.scale.min_value}–{domain.scale.max_value}
      </p>
    </div>
  );
}

function LevelSelect({
  label,
  domain,
  value,
  onChange,
}: {
  label: string;
  domain: Domain;
  value: number | null;
  onChange: (v: number | null) => void;
}) {
  return (
    <div className="space-y-1">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <Select
        value={value == null ? NONE : String(value)}
        onValueChange={(v) => onChange(v === NONE ? null : Number(v))}
      >
        <SelectTrigger>
          <SelectValue placeholder="Selecione…" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={NONE}>— não avaliado —</SelectItem>
          {domain.scale.options.map((o) => (
            <SelectItem key={o.value} value={String(o.value)}>
              {o.value} · {o.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
