import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { CategoryTotal, CURRENCY_SYMBOLS } from "../types";

const COLORS = ["#8b5cf6", "#f59e0b", "#ef4444", "#22c55e", "#3b82f6", "#ec4899", "#a78bfa", "#14b8a6", "#f97316", "#52525b"];

interface Props {
  data: CategoryTotal[];
  currency: string;
}

export default function CategoryDonut({ data, currency }: Props) {
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  const total = data.reduce((s, c) => s + c.total, 0);

  if (!data.length) {
    return (
      <div className="bg-bg-card rounded-2xl p-5 border border-border flex flex-col items-center justify-center h-48 gap-2">
        <div className="w-10 h-10 rounded-full bg-bg-elevated flex items-center justify-center">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#52525b" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/></svg>
        </div>
        <span className="text-text-muted text-sm">Нет данных за период</span>
      </div>
    );
  }

  return (
    <div className="bg-bg-card rounded-2xl p-5 border border-border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-text-primary">Категории</h3>
        <span className="text-[11px] text-text-muted">{data.length} категорий</span>
      </div>
      <div className="flex items-center gap-5">
        <div className="w-32 h-32 relative flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={38}
                outerRadius={60}
                dataKey="total"
                stroke="#09090b"
                strokeWidth={2}
              >
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-base font-bold text-text-primary">
              {total >= 1000
                ? `${(total / 1000).toFixed(1)}k`
                : total.toLocaleString("ru-RU", { maximumFractionDigits: 0 })
              }
            </span>
            <span className="text-[10px] text-text-muted">{sym}</span>
          </div>
        </div>
        <div className="flex flex-col gap-2.5 flex-1 min-w-0">
          {data.slice(0, 5).map((cat, i) => (
            <div key={cat.name} className="flex items-center gap-2.5">
              <div
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: COLORS[i % COLORS.length] }}
              />
              <span className="text-[12px] text-text-secondary truncate flex-1">
                {cat.icon} {cat.name}
              </span>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className="text-[12px] font-medium text-text-primary">
                  {cat.total.toLocaleString("ru-RU", { maximumFractionDigits: 0 })}
                </span>
                <span className="text-[10px] text-text-muted w-8 text-right">
                  {cat.percentage.toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
      {/* Category progress bars */}
      <div className="mt-4 space-y-2">
        {data.slice(0, 4).map((cat, i) => (
          <div key={cat.name} className="flex items-center gap-3">
            <span className="text-[11px] text-text-muted w-20 truncate">{cat.name}</span>
            <div className="flex-1 h-1.5 bg-bg-elevated rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${cat.percentage}%`,
                  backgroundColor: COLORS[i % COLORS.length],
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
