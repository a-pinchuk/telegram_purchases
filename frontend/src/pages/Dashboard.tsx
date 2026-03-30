import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import type { Summary, CategoryTotal, Expense, ExpenseListResponse } from "../types";
import PeriodSelector from "../components/PeriodSelector";
import SummaryCard from "../components/SummaryCard";
import CategoryDonut from "../components/CategoryDonut";
import TransactionList from "../components/TransactionList";

export default function Dashboard() {
  const [period, setPeriod] = useState("month");
  const [currency, setCurrency] = useState("EUR");
  const [currencies, setCurrencies] = useState<string[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [categories, setCategories] = useState<CategoryTotal[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      try {
        const curs = await apiFetch<string[]>("/analytics/currencies", { period });
        if (cancelled) return;
        setCurrencies(curs);
        const cur = curs.includes(currency) ? currency : curs[0] || "EUR";
        setCurrency(cur);

        const [sum, cats, exps] = await Promise.all([
          apiFetch<Summary>("/analytics/summary", { period, currency: cur }),
          apiFetch<CategoryTotal[]>("/analytics/categories", { period, currency: cur }),
          apiFetch<ExpenseListResponse>("/expenses/", { period, currency: cur, limit: "5" }),
        ]);
        if (cancelled) return;
        setSummary(sum);
        setCategories(cats);
        setExpenses(exps.items);
      } catch (err) {
        console.error("Failed to load dashboard", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [period]);

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="px-4 pt-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold">{summary?.period_label || "..."}</h1>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      {currencies.length > 1 && (
        <div className="flex gap-1.5">
          {currencies.map((c) => (
            <button
              key={c}
              onClick={() => setCurrency(c)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                c === currency
                  ? "bg-accent-primary/20 text-accent-secondary"
                  : "text-text-muted"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      )}

      {summary && (
        <div className="grid grid-cols-2 gap-3">
          <SummaryCard
            title="Всего"
            value={summary.total}
            currency={summary.currency}
            delta={summary.delta_pct}
            subtitle="vs прошл."
            icon="\ud83d\udcb0"
          />
          <SummaryCard
            title="Средний чек"
            value={summary.average}
            currency={summary.currency}
            icon="\ud83d\udcdd"
          />
          <SummaryCard
            title="Операций"
            value={summary.count}
            currency=""
            icon="\ud83e\uddfe"
          />
          <SummaryCard
            title="Прошлый период"
            value={summary.prev_total}
            currency={summary.currency}
            icon="\ud83d\udcc5"
          />
        </div>
      )}

      <CategoryDonut data={categories} currency={currency} />
      <TransactionList expenses={expenses} />
    </div>
  );
}
