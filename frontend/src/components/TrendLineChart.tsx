import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
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

  // Calculate trend
  let trendText = "";
  if (data.length >= 2) {
    const first = data[0].total;
    const last = data[data.length - 1].total;
    if (first > 0) {
      const pct = ((last - first) / first * 100).toFixed(0);
      trendText = Number(pct) > 0 ? `+${pct}%` : `${pct}%`;
    }
  }

  return (
    <div className="bg-bg-card rounded-2xl p-5 border border-border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-text-primary">Тренд</h3>
        {trendText && (
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-md ${
            trendText.startsWith("+") ? "text-danger bg-danger-muted" : "text-success bg-success-muted"
          }`}>
            {trendText}
          </span>
        )}
      </div>
      {!data.length ? (
        <div className="flex items-center justify-center py-12">
          <span className="text-text-muted text-sm">Нет данных</span>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={formatted} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="label"
              tick={{ fill: "#52525b", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#52525b", fontSize: 9 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "#18181b",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 12,
                fontSize: 12,
                color: "#fafafa",
                boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
              }}
              labelStyle={{ color: "#a1a1aa" }}
              formatter={(value: number) => [`${value.toLocaleString("ru-RU")} ${sym}`, "Итого"]}
            />
            <Area
              type="monotone"
              dataKey="total"
              stroke="#8b5cf6"
              strokeWidth={2.5}
              fill="url(#trendGrad)"
              dot={{ fill: "#8b5cf6", r: 3, strokeWidth: 2, stroke: "#09090b" }}
              activeDot={{ r: 5, fill: "#a78bfa", stroke: "#09090b", strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
