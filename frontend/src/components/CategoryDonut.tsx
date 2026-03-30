import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { CategoryTotal, CURRENCY_SYMBOLS } from "../types";

const COLORS = ["#6366f1", "#f59e0b", "#ef4444", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6", "#14b8a6", "#f97316", "#6b7280"];

interface Props {
  data: CategoryTotal[];
  currency: string;
}

export default function CategoryDonut({ data, currency }: Props) {
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  const total = data.reduce((s, c) => s + c.total, 0);

  if (!data.length) {
    return (
      <div className="bg-bg-card rounded-2xl p-4 border border-white/5 flex items-center justify-center h-64">
        <span className="text-text-muted text-sm">Нет данных</span>
      </div>
    );
  }

  return (
    <div className="bg-bg-card rounded-2xl p-4 border border-white/5">
      <h3 className="text-sm font-semibold text-text-primary mb-3">По категориям</h3>
      <div className="flex items-center gap-4">
        <div className="w-36 h-36 relative flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={65}
                dataKey="total"
                stroke="none"
              >
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-lg font-bold text-text-primary">
              {total.toLocaleString("ru-RU", { maximumFractionDigits: 0 })}
            </span>
            <span className="text-[10px] text-text-muted">{sym}</span>
          </div>
        </div>
        <div className="flex flex-col gap-1.5 flex-1 min-w-0">
          {data.slice(0, 5).map((cat, i) => (
            <div key={cat.name} className="flex items-center gap-2">
              <div
                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: COLORS[i % COLORS.length] }}
              />
              <span className="text-xs text-text-secondary truncate flex-1">
                {cat.icon} {cat.name}
              </span>
              <span className="text-xs font-medium text-text-primary">
                {cat.percentage.toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
