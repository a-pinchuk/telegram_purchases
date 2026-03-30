import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import { DailyTotal, CURRENCY_SYMBOLS } from "../types";

interface Props {
  data: DailyTotal[];
  currency: string;
}

export default function DailyBarChart({ data, currency }: Props) {
  const sym = CURRENCY_SYMBOLS[currency] || currency;

  const formatted = data.map((d) => ({
    ...d,
    label: new Date(d.date).toLocaleDateString("ru-RU", { day: "numeric", month: "short" }),
  }));

  const maxVal = Math.max(...data.map(d => d.total), 0);
  const avgVal = data.length ? data.reduce((s, d) => s + d.total, 0) / data.length : 0;

  return (
    <div className="bg-bg-card rounded-2xl p-5 border border-border">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-sm font-semibold text-text-primary">По дням</h3>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-accent-primary" />
            <span className="text-[10px] text-text-muted">Расход</span>
          </div>
        </div>
      </div>
      <div className="flex items-baseline gap-2 mb-4">
        <span className="text-[11px] text-text-muted">
          Макс: {maxVal.toLocaleString("ru-RU", {maximumFractionDigits: 0})} {sym}
        </span>
        <span className="text-[11px] text-text-muted">
          &middot; Сред: {avgVal.toLocaleString("ru-RU", {maximumFractionDigits: 0})} {sym}
        </span>
      </div>
      {!data.length ? (
        <div className="flex items-center justify-center py-12">
          <span className="text-text-muted text-sm">Нет данных</span>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={formatted} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <XAxis
              dataKey="label"
              tick={{ fill: "#52525b", fontSize: 9 }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: "#52525b", fontSize: 9 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: "rgba(139, 92, 246, 0.06)" }}
              contentStyle={{
                background: "#18181b",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 12,
                fontSize: 12,
                color: "#fafafa",
                boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
              }}
              labelStyle={{ color: "#a1a1aa", marginBottom: 4 }}
              formatter={(value: number) => [`${value.toLocaleString("ru-RU")} ${sym}`, "Сумма"]}
            />
            <Bar
              dataKey="total"
              fill="url(#barGradient)"
              radius={[6, 6, 0, 0]}
              maxBarSize={20}
            />
            <defs>
              <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8b5cf6" />
                <stop offset="100%" stopColor="#6d28d9" stopOpacity={0.6} />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
