import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import type { DailyTotal, MonthlyTotal, WeekdayTotal, CategoryTotal } from "../types";
import PeriodSelector from "../components/PeriodSelector";
import DailyBarChart from "../components/DailyBarChart";
import TrendLineChart from "../components/TrendLineChart";
import WeekdayHeatmap from "../components/WeekdayHeatmap";
import CategoryDonut from "../components/CategoryDonut";

export default function Analytics() {
  const [period, setPeriod] = useState("month");
  const [currency, setCurrency] = useState("EUR");
  const [daily, setDaily] = useState<DailyTotal[]>([]);
  const [monthly, setMonthly] = useState<MonthlyTotal[]>([]);
  const [weekday, setWeekday] = useState<WeekdayTotal[]>([]);
  const [categories, setCategories] = useState<CategoryTotal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const curs = await apiFetch<string[]>("/analytics/currencies", { period });
        if (cancelled) return;
        const cur = curs.includes(currency) ? currency : curs[0] || "EUR";
        setCurrency(cur);

        const [d, m, w, c] = await Promise.all([
          apiFetch<DailyTotal[]>("/analytics/daily", { period, currency: cur }),
          apiFetch<MonthlyTotal[]>("/analytics/monthly", { months: "6", currency: cur }),
          apiFetch<WeekdayTotal[]>("/analytics/weekday", { period, currency: cur }),
          apiFetch<CategoryTotal[]>("/analytics/categories", { period, currency: cur }),
        ]);
        if (cancelled) return;
        setDaily(d);
        setMonthly(m);
        setWeekday(w);
        setCategories(c);
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [period]);

  if (loading && !daily.length) {
    return (
      <div className="px-4 pt-6 space-y-4">
        <div className="skeleton h-8 w-36" />
        <div className="skeleton h-52 w-full rounded-2xl" />
        <div className="skeleton h-52 w-full rounded-2xl" />
        <div className="skeleton h-36 w-full rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="px-4 pt-5 pb-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Аналитика</h1>
          <p className="text-[12px] text-text-muted mt-0.5">Детальная статистика</p>
        </div>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      <div className="animate-fade-up">
        <DailyBarChart data={daily} currency={currency} />
      </div>
      <div className="animate-fade-up" style={{ animationDelay: "0.1s" }}>
        <TrendLineChart data={monthly} currency={currency} />
      </div>
      <div className="animate-fade-up" style={{ animationDelay: "0.15s" }}>
        <WeekdayHeatmap data={weekday} currency={currency} />
      </div>
      <div className="animate-fade-up" style={{ animationDelay: "0.2s" }}>
        <CategoryDonut data={categories} currency={currency} />
      </div>
    </div>
  );
}
