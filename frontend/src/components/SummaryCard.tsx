import { CURRENCY_SYMBOLS } from "../types";

interface Props {
  title: string;
  value: number;
  currency: string;
  subtitle?: string;
  delta?: number;
  icon: string;
}

export default function SummaryCard({ title, value, currency, subtitle, delta, icon }: Props) {
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  const formatted = value.toLocaleString("ru-RU", { minimumFractionDigits: 0, maximumFractionDigits: 0 });

  return (
    <div className="bg-bg-card rounded-2xl p-4 border border-white/5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-text-secondary text-xs font-medium">{title}</span>
        <span className="text-lg">{icon}</span>
      </div>
      <div className="text-xl font-bold text-text-primary">
        {formatted}{currency ? ` ${sym}` : ""}
      </div>
      <div className="flex items-center gap-2 mt-1">
        {delta !== undefined && (
          <span
            className={`text-xs font-semibold ${
              delta > 0 ? "text-danger" : delta < 0 ? "text-success" : "text-text-muted"
            }`}
          >
            {delta > 0 ? "+" : ""}
            {delta.toFixed(1)}%
          </span>
        )}
        {subtitle && <span className="text-xs text-text-muted">{subtitle}</span>}
      </div>
    </div>
  );
}
