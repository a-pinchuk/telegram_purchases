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
    <div className="px-4 pt-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold">История</h1>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      <input
        type="text"
        placeholder="Поиск по описанию..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full bg-bg-card border border-white/5 rounded-xl px-3 py-2.5 text-sm text-text-primary placeholder:text-text-muted outline-none focus:border-accent-primary/50 transition-colors"
      />

      <div className="flex gap-1.5 overflow-x-auto pb-1 -mx-4 px-4 no-scrollbar">
        <button
          onClick={() => setSelectedCategory("")}
          className={`px-2.5 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition-all flex-shrink-0 ${
            !selectedCategory
              ? "bg-accent-primary/20 text-accent-secondary"
              : "text-text-muted"
          }`}
        >
          Все
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.name)}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition-all flex-shrink-0 ${
              selectedCategory === cat.name
                ? "bg-accent-primary/20 text-accent-secondary"
                : "text-text-muted"
            }`}
          >
            {cat.icon} {cat.name}
          </button>
        ))}
      </div>

      <div className="text-xs text-text-muted">
        {periodLabel} &middot; {totalCount} записей
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="w-6 h-6 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <TransactionList expenses={expenses} showAll title="" />
      )}
    </div>
  );
}
