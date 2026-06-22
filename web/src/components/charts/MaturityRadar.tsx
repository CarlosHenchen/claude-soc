import ReactECharts from "echarts-for-react";
import { fmt1, levelName, wrapLabel } from "@/lib/maturity";

export interface RadarItem {
  name: string;
  full?: string; // full domain name for the tooltip
  score: number | null;
  cap?: number | null; // 0–3, optional (SOC-CMM capability)
}

/**
 * Domain "shape" radar on the 0–5 scale. Only assessed domains are passed in
 * (so the polygon never looks broken). Long axis names wrap without cutting words.
 */
export function MaturityRadar({ items, withCapability }: { items: RadarItem[]; withCapability?: boolean }) {
  const indicator = items.map((x) => ({ name: x.name, max: 5 }));
  const data: any[] = [
    {
      value: items.map((x) => x.score),
      name: "Maturidade",
      areaStyle: { color: "rgba(37,99,235,.15)" },
      lineStyle: { color: "#2563eb", width: 2 },
      itemStyle: { color: "#2563eb" },
    },
  ];
  if (withCapability) {
    data.push({
      value: items.map((x) => (x.cap == null ? null : (x.cap / 3) * 5)),
      name: "Capability",
      areaStyle: { color: "rgba(124,58,237,.08)" },
      lineStyle: { color: "#7c3aed", width: 1.5, type: "dashed" },
      itemStyle: { color: "#7c3aed" },
    });
  }
  const option = {
    tooltip: {
      trigger: "item",
      confine: true,
      formatter: () =>
        items
          .map(
            (x) =>
              `<div style="display:flex;justify-content:space-between;gap:14px"><span>${
                x.full ?? x.name
              }</span><b>${x.score == null ? "—" : `${fmt1(x.score)} · ${levelName(x.score)}`}</b></div>`
          )
          .join(""),
    },
    legend: { bottom: 0, itemWidth: 14, textStyle: { fontSize: 11, color: "#475569" } },
    radar: {
      indicator,
      radius: "66%",
      center: ["50%", "48%"],
      splitNumber: 5,
      axisName: { color: "#475569", fontSize: 10, formatter: (v: string) => wrapLabel(v, 13) },
      splitLine: { lineStyle: { color: "#e5e7eb" } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: "#e5e7eb" } },
    },
    series: [{ type: "radar", symbolSize: 3, data }],
  };
  return <ReactECharts option={option} opts={{ renderer: "svg" }} style={{ height: 360 }} notMerge />;
}
