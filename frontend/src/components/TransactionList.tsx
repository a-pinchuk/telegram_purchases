import { Expense, CURRENCY_SYMBOLS } from "../types";

const CATEGORY_COLORS: Record<string, string> = {
  "\u041f\u0440\u043e\u0434\u0443\u043a\u0442\u044b": "#22c55e",
  "\u0420\u0435\u0441\u0442\u043e\u0440\u0430\u043d\u044b \u0438 \u043a\u0430\u0444\u0435": "#f59e0b",
  "\u0422\u0440\u0430\u043d\u0441\u043f\u043e\u0440\u0442": "#3b82f6",
  "\u041e\u0434\u0435\u0436\u0434\u0430": "#ec4899",
  "\u0420\u0430\u0437\u0432\u043b\u0435\u0447\u0435\u043d\u0438\u044f": "#a78bfa",
  "\u0417\u0434\u043e\u0440\u043e\u0432\u044c\u0435": "#ef4444",
  "\u041a\u043e\u043c\u043c\u0443\u043d\u0430\u043b\u044c\u043d\u044b\u0435": "#14b8a6",
  "\u0411\u044b\u0442\u043e\u0432\u044b\u0435 \u0442\u043e\u0432\u0430\u0440\u044b": "#f97316",
  "\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0438": "#8b5cf6",
};

interface Props {
  expenses: Expense[];
  title?: string;
  showAll?: boolean;
}

export default function TransactionList({ expenses, title, showAll }: Props) {
  const items = showAll ? expenses : expenses.slice(0, 5);

  if (!items.length) {
    return (
      <div className="bg-bg-card rounded-2xl border border-border p-5 flex flex-col items-center justify-center gap-2 py-8">
        <div className="w-10 h-10 rounded-full bg-bg-elevated flex items-center justify-center">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#52525b" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/></svg>
        </div>
        <span className="text-text-muted text-sm">Нет расходов</span>
      </div>
    );
  }

  // Group by date
  const grouped = new Map<string, Expense[]>();
  for (const exp of items) {
    const dateKey = new Date(exp.created_at).toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
    if (!grouped.has(dateKey)) grouped.set(dateKey, []);
    grouped.get(dateKey)!.push(exp);
  }

  return (
    <div className="bg-bg-card rounded-2xl border border-border overflow-hidden">
      {title && (
        <div className="px-5 pt-4 pb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
          <span className="text-[11px] text-text-muted">{expenses.length} записей</span>
        </div>
      )}
      <div>
        {Array.from(grouped.entries()).map(([dateLabel, group]) => (
          <div key={dateLabel}>
            {showAll && (
              <div className="px-5 py-2 bg-bg-secondary/50">
                <span className="text-[11px] font-medium text-text-muted uppercase tracking-wider">{dateLabel}</span>
              </div>
            )}
            {group.map((exp) => {
              const sym = CURRENCY_SYMBOLS[exp.currency] || exp.currency;
              const color = CATEGORY_COLORS[exp.category_name || ""] || "#52525b";
              const time = new Date(exp.created_at).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });

              return (
                <div key={exp.id} className="flex items-center gap-3 px-5 py-3 hover:bg-bg-hover/50 transition-colors">
                  <div
                    className="w-9 h-9 rounded-xl flex items-center justify-center text-base flex-shrink-0"
                    style={{ backgroundColor: `${color}15` }}
                  >
                    {exp.category_icon || "\u{1f4e6}"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[13px] font-medium text-text-primary truncate capitalize">
                      {exp.description || "Без описания"}
                    </div>
                    <div className="text-[11px] text-text-muted mt-0.5">
                      {exp.category_name || "Без категории"} &middot; {time}
                    </div>
                  </div>
                  <div className="text-[13px] font-semibold text-text-primary flex-shrink-0 tabular-nums">
                    -{exp.amount.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    <span className="text-text-muted text-[11px] ml-0.5">{sym}</span>
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
