import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from "recharts";
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

  return (
    <div className="bg-bg-card rounded-2xl p-4 border border-white/5">
      <h3 className="text-sm font-semibold text-text-primary mb-3">Расходы по дням</h3>
      {!data.length ? (
        <div className="text-text-muted text-sm py-8 text-center">Нет данных</div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={formatted} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fill: "#64748b", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: "#64748b", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "#1a1a2e",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 12,
                fontSize: 12,
              }}
              labelStyle={{ color: "#94a3b8" }}
              formatter={(value: number) => [`${value.toLocaleString("ru-RU")} ${sym}`, "Сумма"]}
            />
            <Bar dataKey="total" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={24} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
