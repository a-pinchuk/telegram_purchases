import { Expense, CURRENCY_SYMBOLS } from "../types";

interface Props {
  expenses: Expense[];
  title?: string;
  showAll?: boolean;
}

export default function TransactionList({ expenses, title = "Последние расходы", showAll }: Props) {
  const items = showAll ? expenses : expenses.slice(0, 5);

  return (
    <div className="bg-bg-card rounded-2xl border border-white/5">
      {title && (
        <div className="px-4 pt-4 pb-2">
          <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
        </div>
      )}
      {!items.length ? (
        <div className="px-4 pb-4 pt-2 text-text-muted text-sm">Нет расходов</div>
      ) : (
        <div className="divide-y divide-white/5">
          {items.map((exp) => {
            const sym = CURRENCY_SYMBOLS[exp.currency] || exp.currency;
            const date = new Date(exp.created_at);
            const dateStr = date.toLocaleDateString("ru-RU", { day: "numeric", month: "short" });
            const timeStr = date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });

            return (
              <div key={exp.id} className="flex items-center gap-3 px-4 py-3">
                <div className="w-9 h-9 rounded-full bg-accent-glow flex items-center justify-center text-base flex-shrink-0">
                  {exp.category_icon || "\ud83d\udce6"}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-text-primary truncate">
                    {exp.description || "Без описания"}
                  </div>
                  <div className="text-[11px] text-text-muted">
                    {exp.category_name || "Без категории"} &middot; {dateStr} {timeStr}
                  </div>
                </div>
                <div className="text-sm font-semibold text-text-primary flex-shrink-0">
                  -{exp.amount.toLocaleString("ru-RU", { maximumFractionDigits: 2 })} {sym}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
