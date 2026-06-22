import ReactECharts from "echarts-for-react";
import { band, fmt1 } from "@/lib/maturity";

/** Hero gauge on the 0–5 maturity scale, colored by score band. SVG renderer → vector for PDF. */
export function MaturityGauge({ score }: { score: number | null }) {
  const option = {
    series: [
      {
        type: "gauge",
        min: 0,
        max: 5,
        splitNumber: 5,
        radius: "94%",
        center: ["50%", "60%"],
        progress: { show: true, width: 13, roundCap: true, itemStyle: { color: band(score) } },
        axisLine: { lineStyle: { width: 13, color: [[1, "#e5e7eb"]] } },
        axisTick: { show: false },
        splitLine: { length: 7, lineStyle: { color: "#cbd5e1", width: 1 } },
        axisLabel: { fontSize: 9, color: "#94a3b8", distance: 11 },
        pointer: { show: false },
        anchor: { show: false },
        detail: {
          valueAnimation: false,
          offsetCenter: [0, "-6%"],
          fontSize: 30,
          fontWeight: "bolder",
          color: band(score),
          formatter: () => (score == null ? "—" : fmt1(score)),
        },
        data: [{ value: score == null ? 0 : score }],
        title: { show: false },
      },
    ],
  };
  return <ReactECharts option={option} opts={{ renderer: "svg" }} style={{ height: 180 }} notMerge />;
}
