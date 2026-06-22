import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, Pencil, Plus, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import type { Assessment, Framework } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const statusLabel: Record<string, { label: string; variant: "muted" | "warning" | "success" }> = {
  draft: { label: "Rascunho", variant: "muted" },
  in_progress: { label: "Em andamento", variant: "warning" },
  completed: { label: "Concluída", variant: "success" },
};

export function Assessments() {
  const [items, setItems] = useState<Assessment[]>([]);
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [form, setForm] = useState({ name: "", client: "", assessor: "" });
  const [creating, setCreating] = useState(false);

  async function load() {
    setItems(await api.get<Assessment[]>("/assessments"));
  }
  useEffect(() => {
    load();
    api.get<Framework[]>("/frameworks").then(setFrameworks);
  }, []);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    if (!frameworks.length || !form.name) return;
    setCreating(true);
    try {
      await api.post<Assessment>("/assessments", {
        framework_id: frameworks[0].id,
        name: form.name,
        client: form.client || null,
        assessor: form.assessor || null,
      });
      setForm({ name: "", client: "", assessor: "" });
      await load();
    } finally {
      setCreating(false);
    }
  }

  async function remove(id: number) {
    if (!confirm("Excluir esta avaliação?")) return;
    await api.del(`/assessments/${id}`);
    await load();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Avaliações</h1>
        <p className="text-sm text-muted-foreground">
          Execuções do Health Check de maturidade de SOC.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Nova avaliação</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={create} className="flex flex-wrap items-end gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="n">Nome *</Label>
              <Input
                id="n"
                className="w-56"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Ex.: Health Check 2026 - ACME"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="c">Cliente</Label>
              <Input
                id="c"
                className="w-44"
                value={form.client}
                onChange={(e) => setForm({ ...form, client: e.target.value })}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="a">Responsável</Label>
              <Input
                id="a"
                className="w-44"
                value={form.assessor}
                onChange={(e) => setForm({ ...form, assessor: e.target.value })}
              />
            </div>
            <Button type="submit" disabled={creating || !form.name}>
              <Plus className="h-4 w-4" /> Criar
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-5">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Responsável</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((a) => {
                const s = statusLabel[a.status];
                return (
                  <TableRow key={a.id}>
                    <TableCell className="font-medium">{a.name}</TableCell>
                    <TableCell>{a.client ?? "—"}</TableCell>
                    <TableCell>{a.assessor ?? "—"}</TableCell>
                    <TableCell>
                      <Badge variant={s.variant}>{s.label}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex justify-end gap-1">
                        <Button asChild variant="outline" size="sm">
                          <Link to={`/assessments/${a.id}/run`}>
                            <Pencil className="h-3.5 w-3.5" /> Avaliar
                          </Link>
                        </Button>
                        <Button asChild variant="outline" size="sm">
                          <Link to={`/assessments/${a.id}/dashboard`}>
                            <BarChart3 className="h-3.5 w-3.5" /> Dashboard
                          </Link>
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => remove(a.id)}>
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
              {items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                    Nenhuma avaliação ainda. Crie a primeira acima.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
