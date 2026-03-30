import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import type { Summary, CategoryTotal, Expense, ExpenseListResponse } from "../types";
import { CURRENCY_SYMBOLS } from "../types";
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
      <div className="px-4 pt-6 space-y-4">
        <div className="skeleton h-8 w-48" />
        <div className="skeleton h-40 w-full rounded-3xl" />
        <div className="grid grid-cols-2 gap-3">
          <div className="skeleton h-20 rounded-2xl" />
          <div className="skeleton h-20 rounded-2xl" />
        </div>
        <div className="skeleton h-56 w-full rounded-2xl" />
      </div>
    );
  }

  const sym = summary ? (CURRENCY_SYMBOLS[summary.currency] || summary.currency) : "";

  return (
    <div className="px-4 pt-5 pb-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary">{summary?.period_label || "..."}</h1>
          <p className="text-[12px] text-text-muted mt-0.5">Обзор расходов</p>
        </div>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      {/* Currency selector */}
      {currencies.length > 1 && (
        <div className="flex gap-1">
          {currencies.map((c) => (
            <button
              key={c}
              onClick={() => setCurrency(c)}
              className={`px-3 py-1.5 rounded-xl text-[11px] font-semibold transition-all border ${
                c === currency
                  ? "bg-accent-primary/15 text-accent-secondary border-accent-primary/30"
                  : "text-text-muted border-border hover:border-border-hover"
              }`}
            >
              {CURRENCY_SYMBOLS[c] || c} {c}
            </button>
          ))}
        </div>
      )}

      {/* Hero card — Total spending */}
      {summary && (
        <div className="relative overflow-hidden bg-gradient-to-br from-accent-primary/20 via-bg-card to-bg-card rounded-3xl p-5 border border-accent-primary/20 animate-fade-up">
          {/* Decorative glow */}
          <div className="absolute -top-10 -right-10 w-32 h-32 bg-accent-primary/10 rounded-full blur-3xl" />
          <div className="relative">
            <div className="flex items-center justify-between mb-1">
              <span className="text-text-secondary text-[12px] font-medium">Потрачено</span>
              {summary.delta_pct !== 0 && (
                <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-lg ${
                  summary.delta_pct > 0 ? "text-danger bg-danger-muted" : "text-success bg-success-muted"
                }`}>
                  {summary.delta_pct > 0 ? "+" : ""}{summary.delta_pct.toFixed(1)}% vs прошл.
                </span>
              )}
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-4xl font-extrabold text-text-primary tracking-tight">
                {summary.total.toLocaleString("ru-RU", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
              </span>
              <span className="text-lg text-text-secondary font-medium">{sym}</span>
            </div>
            <div className="flex items-center gap-4 mt-3">
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-accent-secondary" />
                <span className="text-[11px] text-text-muted">{summary.count} операций</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-warning" />
                <span className="text-[11px] text-text-muted">
                  Ср. чек {summary.average.toLocaleString("ru-RU", {maximumFractionDigits: 0})} {sym}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick stats */}
      {summary && (
        <div className="grid grid-cols-2 gap-3 animate-fade-up" style={{ animationDelay: "0.1s" }}>
          <SummaryCard
            title="Средний чек"
            value={summary.average}
            currency={summary.currency}
          />
          <SummaryCard
            title="Прошлый период"
            value={summary.prev_total}
            currency={summary.currency}
          />
        </div>
      )}

      {/* Category donut */}
      <div className="animate-fade-up" style={{ animationDelay: "0.15s" }}>
        <CategoryDonut data={categories} currency={currency} />
      </div>

      {/* Recent transactions */}
      <div className="animate-fade-up" style={{ animationDelay: "0.2s" }}>
        <TransactionList expenses={expenses} title="Последние расходы" />
      </div>
    </div>
  );
}
