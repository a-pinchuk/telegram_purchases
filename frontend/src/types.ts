export interface Summary {
  period_label: string;
  total: number;
  count: number;
  average: number;
  prev_total: number;
  delta_pct: number;
  currency: string;
}

export interface CategoryTotal {
  name: string;
  icon: string;
  total: number;
  count: number;
  percentage: number;
}

export interface DailyTotal {
  date: string;
  total: number;
}

export interface MonthlyTotal {
  month: string;
  total: number;
}

export interface WeekdayTotal {
  day: string;
  day_index: number;
  total: number;
  count: number;
}

export interface Expense {
  id: number;
  amount: number;
  currency: string;
  description: string;
  category_name: string | null;
  category_icon: string;
  store: string | null;
  created_at: string;
}

export interface ExpenseListResponse {
  items: Expense[];
  total_count: number;
  period_label: string;
}

export interface Category {
  id: number;
  name: string;
  icon: string;
}

export const CURRENCY_SYMBOLS: Record<string, string> = {
  EUR: "\u20ac",
  RUB: "\u20bd",
  PLN: "z\u0142",
  USD: "$",
  GBP: "\u00a3",
  CZK: "K\u010d",
};
