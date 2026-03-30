import { WeekdayTotal, CURRENCY_SYMBOLS } from "../types";

interface Props {
  data: WeekdayTotal[];
  currency: string;
}

export default function WeekdayHeatmap({ data, currency }: Props) {
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  const maxTotal = Math.max(...data.map((d) => d.total), 1);
  const totalAll = data.reduce((s, d) => s + d.total, 0);
  const maxDay = data.reduce((a, b) => (b.total > a.total ? b : a), data[0]);

  return (
    <div className="bg-bg-card rounded-2xl p-5 border border-border">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-sm font-semibold text-text-primary">Дни недели</h3>
        {maxDay && maxDay.total > 0 && (
          <span className="text-[11px] text-text-muted">
            Макс: {maxDay.day}
          </span>
        )}
      </div>
      <p className="text-[11px] text-text-muted mb-4">
        Всего: {totalAll.toLocaleString("ru-RU", {maximumFractionDigits: 0})} {sym}
      </p>
      <div className="grid grid-cols-7 gap-2">
        {data.map((d) => {
          const intensity = d.total / maxTotal;
          const isMax = d === maxDay && d.total > 0;
          return (
            <div key={d.day_index} className="flex flex-col items-center gap-1.5">
              <span className={`text-[10px] font-medium ${isMax ? "text-accent-primary" : "text-text-muted"}`}>
                {d.day}
              </span>
              <div
                className={`w-full aspect-square rounded-xl flex items-center justify-center transition-all ${
                  isMax ? "ring-1 ring-accent-primary/30" : ""
                }`}
                style={{
                  backgroundColor: d.total > 0
                    ? `rgba(139, 92, 246, ${Math.max(intensity * 0.5, 0.08)})`
                    : "rgba(39, 39, 42, 0.5)",
                }}
              >
                <span className={`text-[10px] font-semibold ${
                  d.total > 0 ? "text-text-primary" : "text-text-muted"
                }`}>
                  {d.total > 0 ? d.total.toLocaleString("ru-RU", { maximumFractionDigits: 0 }) : "-"}
                </span>
              </div>
              <span className="text-[9px] text-text-muted">
                {d.count > 0 ? `${d.count}x` : ""}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
