import ReactECharts from "echarts-for-react";
import { band, fmt1, levelName, wrapLabel } from "@/lib/maturity";

export interface SubView {
  code: string; // short code (axis)
  full: string; // full name (tooltip / bar label)
  score: number | null; // 0–5
  assessed: boolean;
}

function shortOrFull(name: string): string {
  const i = name.indexOf("·");
  return i > 0 ? name.slice(0, i).trim() : name;
}

/** Per-domain subdomain radar — short code on axis, full name + value + level in tooltip. */
export function SubRadar({ views, accent }: { views: SubView[]; accent: string }) {
  const a = views.filter((v) => v.assessed);
  const option = {
    tooltip: {
      trigger: "item",
      confine: true,
      formatter: () =>
        a
          .map(
            (v) =>
              `<div style="display:flex;justify-content:space-between;gap:16px"><span>${v.full}</span><b>${fmt1(
                v.score
              )} · ${levelName(v.score)}</b></div>`
          )
          .join(""),
    },
    radar: {
      indicator: a.map((v) => ({ name: shortOrFull(v.full), max: 5 })),
      radius: "60%",
      center: ["50%", "52%"],
      splitNumber: 5,
      axisName: { color: "#475569", fontSize: 10, formatter: (v: string) => wrapLabel(v, 12) },
      splitLine: { lineStyle: { color: "#e5e7eb" } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: "#e5e7eb" } },
    },
    series: [
      {
        type: "radar",
        symbolSize: 3,
        data: [
          {
            value: a.map((v) => v.score),
            name: "Maturidade",
            areaStyle: { color: accent, opacity: 0.12 },
            lineStyle: { color: accent, width: 2 },
            itemStyle: { color: accent },
          },
        ],
      },
    ],
  };
  return <ReactECharts option={option} opts={{ renderer: "svg" }} style={{ height: 320 }} notMerge />;
}

/** Per-domain subdomain bars — full names (wrap), sorted, value, domain-average reference line. */
export function SubBars({ views, domAvg }: { views: SubView[]; domAvg: number | null }) {
  const s = [...views].sort(
    (x, y) => (y.assessed ? 1 : 0) - (x.assessed ? 1 : 0) || (y.score ?? 0) - (x.score ?? 0)
  );
  const option = {
    grid: { left: 8, right: 54, top: 8, bottom: 24, containLabel: true },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      confine: true,
      formatter: (p: any) => {
        const v = s[p[0].dataIndex];
        return v.assessed
          ? `${v.full}<br/><b>${fmt1(v.score)}</b> / 5 · ${levelName(v.score)}`
          : `${v.full}<br/>não avaliado`;
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
      inverse: true,
      data: s.map((v) => v.full),
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: { width: 160, overflow: "break", color: "#334155", fontSize: 11, lineHeight: 13 },
    },
    series: [
      {
        type: "bar",
        barWidth: 12,
        data: s.map((v) => ({
          value: v.assessed ? v.score : 0,
          itemStyle: { color: v.assessed ? band(v.score) : "#e2e8f0", borderRadius: [0, 4, 4, 0] },
        })),
        label: {
          show: true,
          position: "right",
          distance: 6,
          fontSize: 11,
          color: "#94a3b8",
          formatter: (p: any) => {
            const v = s[p.dataIndex];
            return v.assessed ? fmt1(v.score) : "não avaliado";
          },
        },
        markLine:
          domAvg == null
            ? undefined
            : {
                silent: true,
                symbol: "none",
                lineStyle: { color: "#0f172a", type: "dashed", width: 1 },
                data: [{ xAxis: domAvg }],
                label: { formatter: `média ${fmt1(domAvg)}`, position: "insideEndTop", fontSize: 10, color: "#475569" },
              },
      },
    ],
  };
  const height = Math.max(150, s.length * 26 + 34);
  return <ReactECharts option={option} opts={{ renderer: "svg" }} style={{ height }} notMerge />;
}
