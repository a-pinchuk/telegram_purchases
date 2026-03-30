import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import type { Expense, ExpenseListResponse, Category } from "../types";
import PeriodSelector from "../components/PeriodSelector";
import TransactionList from "../components/TransactionList";

export default function History() {
  const [period, setPeriod] = useState("month");
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [periodLabel, setPeriodLabel] = useState("");
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Category[]>("/categories/").then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const params: Record<string, string> = { period, limit: "100" };
        if (selectedCategory) params.category = selectedCategory;
        if (search) params.search = search;

        const res = await apiFetch<ExpenseListResponse>("/expenses/", params);
        if (cancelled) return;
        setExpenses(res.items);
        setTotalCount(res.total_count);
        setPeriodLabel(res.period_label);
      } catch (err) {
        console.error("Failed to load expenses", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [period, selectedCategory, search]);

  return (
    <div className="px-4 pt-5 pb-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary">История</h1>
          <p className="text-[12px] text-text-muted mt-0.5">
            {periodLabel} &middot; {totalCount} записей
          </p>
        </div>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      {/* Search */}
      <div className="relative">
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
        </svg>
        <input
          type="text"
          placeholder="Поиск..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-bg-card border border-border rounded-xl pl-9 pr-3 py-2.5 text-sm text-text-primary placeholder:text-text-muted outline-none focus:border-accent-primary/40 focus:ring-1 focus:ring-accent-primary/20 transition-all"
        />
      </div>

      {/* Category chips */}
      <div className="flex gap-1.5 overflow-x-auto pb-1 -mx-4 px-4 no-scrollbar">
        <button
          onClick={() => setSelectedCategory("")}
          className={`px-3 py-1.5 rounded-xl text-[11px] font-semibold whitespace-nowrap transition-all flex-shrink-0 border ${
            !selectedCategory
              ? "bg-accent-primary/15 text-accent-secondary border-accent-primary/30"
              : "text-text-muted border-border hover:border-border-hover"
          }`}
        >
          Все
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.name === selectedCategory ? "" : cat.name)}
            className={`px-3 py-1.5 rounded-xl text-[11px] font-semibold whitespace-nowrap transition-all flex-shrink-0 border ${
              selectedCategory === cat.name
                ? "bg-accent-primary/15 text-accent-secondary border-accent-primary/30"
                : "text-text-muted border-border hover:border-border-hover"
            }`}
          >
            {cat.icon} {cat.name}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-16 rounded-2xl" />
          ))}
        </div>
      ) : (
        <TransactionList expenses={expenses} showAll />
      )}
    </div>
  );
}
