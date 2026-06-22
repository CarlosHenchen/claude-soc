import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import type { Framework, FrameworkDetail } from "@/lib/types";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Frameworks() {
  const { user } = useAuth();
  const [detail, setDetail] = useState<FrameworkDetail | null>(null);
  const [reseeding, setReseeding] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function load() {
    const list = await api.get<Framework[]>("/frameworks");
    if (list[0]) setDetail(await api.get<FrameworkDetail>(`/frameworks/${list[0].id}`));
  }
  useEffect(() => {
    load();
  }, []);

  async function reseed() {
    setReseeding(true);
    setMsg(null);
    try {
      const r = await api.post<Record<string, unknown>>("/admin/reseed");
      setMsg(`Re-seed concluído: ${r.domains} domínios, ${r.controls} controles, ${r.questions} perguntas.`);
      await load();
    } catch (e) {
      setMsg((e as Error).message);
    } finally {
      setReseeding(false);
    }
  }

  if (!detail) return <p className="text-muted-foreground">Carregando…</p>;

  const totalQ = detail.domains.reduce(
    (s, d) => s + d.controls.reduce((a, c) => a + c.questions.length, 0),
    0
  );

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{detail.name}</h1>
          <p className="text-sm text-muted-foreground">
            {detail.domains.length} domínios · {totalQ} perguntas · fonte: {detail.source_file}
          </p>
        </div>
        {user?.is_admin && (
          <Button onClick={reseed} disabled={reseeding} variant="outline">
            <RefreshCw className={reseeding ? "h-4 w-4 animate-spin" : "h-4 w-4"} /> Re-seed da planilha
          </Button>
        )}
      </div>
      {msg && <p className="text-sm text-primary">{msg}</p>}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {detail.domains.map((d) => (
          <Card key={d.id}>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-sm">
                <span>{d.key}</span>
                <Badge variant="muted">
                  escala {d.scale.min_value}–{d.scale.max_value}
                </Badge>
              </CardTitle>
              <p className="text-xs text-muted-foreground">{d.reference_model}</p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1 text-sm">
                {d.controls.map((c) => (
                  <li key={c.id} className="flex items-center justify-between">
                    <span className="truncate text-muted-foreground">{c.code}</span>
                    <span className="text-xs">{c.questions.length} itens</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
