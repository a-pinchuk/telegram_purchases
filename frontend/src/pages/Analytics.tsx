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
      <div className="flex items-center justify-center h-screen">
        <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="px-4 pt-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold">Аналитика</h1>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      <DailyBarChart data={daily} currency={currency} />
      <TrendLineChart data={monthly} currency={currency} />
      <WeekdayHeatmap data={weekday} currency={currency} />
      <CategoryDonut data={categories} currency={currency} />
    </div>
  );
}
