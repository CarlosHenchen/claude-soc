import ReactECharts from "echarts-for-react";
import { band, fmt1, levelName } from "@/lib/maturity";

export interface RankItem {
  name: string; // short label (axis)
  full: string; // full name (tooltip)
  score: number | null;
  target: number | null;
  assessed: boolean;
}

/**
 * Horizontal bar ranking sorted by maturity (best on top). Long names wrap (no
 * truncation), unassessed domains are explicitly shown as "não avaliado",
 * target shown as a marker. Primary comparison view.
 */
export function DomainRanking({ items, avg }: { items: RankItem[]; avg?: number | null }) {
  const cats = items.map((x) => x.name);
  const option = {
    grid: { left: 8, right: 48, top: 6, bottom: 22, containLabel: true },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (p: any) => {
        const it = items[p[0].dataIndex];
        return it.assessed
          ? `${it.full}<br/><b>${fmt1(it.score)}</b> / 5 · ${levelName(it.score)}${
              it.target != null ? ` · meta ${fmt1(it.target)}` : ""
            }`
          : `${it.full}<br/>não avaliado`;
      },
    },
    xAxis: {
      type: "value",
      min: 0,
      max: 5,
      interval: 1,
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "#eef2f7" } },
    },
    yAxis: {
      type: "category",
      data: cats,
      inverse: true,
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: { width: 150, overflow: "break", color: "#334155", fontSize: 11, lineHeight: 13 },
    },
    series: [
      {
        type: "bar",
        barWidth: 13,
        z: 2,
        data: items.map((it) => ({
          value: it.assessed ? it.score : 0,
          itemStyle: { color: it.assessed ? band(it.score) : "#e2e8f0", borderRadius: [0, 4, 4, 0] },
        })),
        label: {
          show: true,
          position: "right",
          distance: 6,
          fontSize: 11,
          color: "#94a3b8",
          formatter: (p: any) => {
            const it = items[p.dataIndex];
            return it.assessed ? fmt1(it.score) : "não avaliado";
          },
        },
        markLine:
          avg == null
            ? undefined
            : {
                silent: true,
                symbol: "none",
                lineStyle: { color: "#0f172a", type: "dashed", width: 1 },
                data: [{ xAxis: avg }],
                label: { formatter: `média ${fmt1(avg)}`, position: "insideEndTop", fontSize: 10, color: "#475569" },
              },
      },
      {
        type: "scatter",
        symbol: "rect",
        symbolSize: [3, 15],
        z: 3,
        silent: true,
        itemStyle: { color: "#0f172a" },
        data: items.map((it, i) => (it.target != null ? [it.target, i] : null)),
      },
    ],
  };
  const height = Math.max(170, items.length * 30 + 30);
  return <ReactECharts option={option} opts={{ renderer: "svg" }} style={{ height }} notMerge />;
}
