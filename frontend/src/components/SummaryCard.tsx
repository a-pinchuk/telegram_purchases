import { CURRENCY_SYMBOLS } from "../types";

interface Props {
  title: string;
  value: number;
  currency: string;
  subtitle?: string;
  delta?: number;
}

export default function SummaryCard({ title, value, currency, subtitle, delta }: Props) {
  const sym = CURRENCY_SYMBOLS[currency] || currency;
  const formatted = value.toLocaleString("ru-RU", { minimumFractionDigits: 0, maximumFractionDigits: 0 });

  return (
    <div className="bg-bg-card rounded-2xl p-3.5 border border-border hover:border-border-hover transition-colors">
      <span className="text-text-muted text-[11px] font-medium uppercase tracking-wider">{title}</span>
      <div className="text-lg font-bold text-text-primary mt-1">
        {formatted}{currency ? <span className="text-text-secondary text-sm font-medium ml-1">{sym}</span> : ""}
      </div>
      {(delta !== undefined || subtitle) && (
        <div className="flex items-center gap-1.5 mt-1">
          {delta !== undefined && delta !== 0 && (
            <span className={`text-[11px] font-semibold px-1.5 py-0.5 rounded-md ${
              delta > 0 ? "text-danger bg-danger-muted" : "text-success bg-success-muted"
            }`}>
              {delta > 0 ? "+" : ""}{delta.toFixed(1)}%
            </span>
          )}
          {subtitle && <span className="text-[11px] text-text-muted">{subtitle}</span>}
        </div>
      )}
    </div>
  );
}
