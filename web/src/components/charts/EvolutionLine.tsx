import ReactECharts from "echarts-for-react";
import { fmt1 } from "@/lib/maturity";

export interface EvoPoint {
  label: string;
  score: number | null;
}

/** Overall maturity (0–5) across assessment cycles. */
export function EvolutionLine({ points }: { points: EvoPoint[] }) {
  const option = {
    grid: { left: 30, right: 20, top: 14, bottom: 24 },
    tooltip: {
      trigger: "axis",
      formatter: (p: any) => `${p[0].axisValue}<br/><b>${fmt1(p[0].data)}</b> / 5`,
    },
    xAxis: {
      type: "category",
      data: points.map((p) => p.label),
      axisLabel: { color: "#64748b", fontSize: 11 },
      axisLine: { lineStyle: { color: "#e5e7eb" } },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 5,
      interval: 1,
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "#eef2f7" } },
    },
    series: [
      {
        type: "line",
        smooth: true,
        symbolSize: 7,
        data: points.map((p) => p.score),
        lineStyle: { color: "#2563eb", width: 2.5 },
        itemStyle: { color: "#2563eb" },
        areaStyle: { color: "rgba(37,99,235,.08)" },
        label: { show: true, formatter: (p: any) => fmt1(p.data), color: "#2563eb", fontSize: 11, position: "top" },
      },
    ],
  };
  return <ReactECharts option={option} opts={{ renderer: "svg" }} style={{ height: 210 }} notMerge />;
}
