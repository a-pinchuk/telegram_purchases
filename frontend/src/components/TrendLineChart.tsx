import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from "recharts";
import { MonthlyTotal, CURRENCY_SYMBOLS } from "../types";

const MONTHS_RU: Record<string, string> = {
  "01": "Янв", "02": "Фев", "03": "Мар", "04": "Апр",
  "05": "Май", "06": "Июн", "07": "Июл", "08": "Авг",
  "09": "Сен", "10": "Окт", "11": "Ноя", "12": "Дек",
};

interface Props {
  data: MonthlyTotal[];
  currency: string;
}

export default function TrendLineChart({ data, currency }: Props) {
  const sym = CURRENCY_SYMBOLS[currency] || currency;

  const formatted = data.map((d) => {
    const [, m] = d.month.split("-");
    return { ...d, label: MONTHS_RU[m] || m };
  });

  return (
    <div className="bg-bg-card rounded-2xl p-4 border border-white/5">
      <h3 className="text-sm font-semibold text-text-primary mb-3">Тренд расходов</h3>
      {!data.length ? (
        <div className="text-text-muted text-sm py-8 text-center">Нет данных</div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={formatted} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fill: "#64748b", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
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
              formatter={(value: number) => [`${value.toLocaleString("ru-RU")} ${sym}`, "Итого"]}
            />
            <Area
              type="monotone"
              dataKey="total"
              stroke="#6366f1"
              strokeWidth={2.5}
              fill="url(#areaGrad)"
              dot={{ fill: "#6366f1", r: 4, strokeWidth: 2, stroke: "#0f0f0f" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
