import { WeekdayTotal } from "../types";

interface Props {
  data: WeekdayTotal[];
  currency: string;
}

export default function WeekdayHeatmap({ data, currency }: Props) {
  const maxTotal = Math.max(...data.map((d) => d.total), 1);

  return (
    <div className="bg-bg-card rounded-2xl p-4 border border-white/5">
      <h3 className="text-sm font-semibold text-text-primary mb-3">По дням недели</h3>
      <div className="grid grid-cols-7 gap-1.5">
        {data.map((d) => {
          const intensity = d.total / maxTotal;
          const bg = `rgba(99, 102, 241, ${Math.max(intensity * 0.8, 0.05)})`;
          return (
            <div key={d.day_index} className="flex flex-col items-center gap-1">
              <span className="text-[10px] text-text-muted">{d.day}</span>
              <div
                className="w-full aspect-square rounded-lg flex items-center justify-center"
                style={{ backgroundColor: bg }}
              >
                <span className="text-[10px] font-medium text-text-primary">
                  {d.total > 0 ? d.total.toLocaleString("ru-RU", { maximumFractionDigits: 0 }) : ""}
                </span>
              </div>
              <span className="text-[9px] text-text-muted">{d.count} шт</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
