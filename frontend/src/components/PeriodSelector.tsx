const periods = [
  { value: "week", label: "7D" },
  { value: "month", label: "1M" },
  { value: "year", label: "1Y" },
];

interface Props {
  value: string;
  onChange: (period: string) => void;
}

export default function PeriodSelector({ value, onChange }: Props) {
  return (
    <div className="flex gap-0.5 bg-bg-secondary rounded-xl p-0.5 border border-border">
      {periods.map((p) => (
        <button
          key={p.value}
          onClick={() => onChange(p.value)}
          className={`px-3.5 py-1.5 rounded-[10px] text-xs font-semibold transition-all duration-200 ${
            value === p.value
              ? "bg-accent-primary text-white shadow-glow"
              : "text-text-muted hover:text-text-secondary"
          }`}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}
