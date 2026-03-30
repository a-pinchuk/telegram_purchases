const periods = [
  { value: "week", label: "Неделя" },
  { value: "month", label: "Месяц" },
  { value: "year", label: "Год" },
];

interface Props {
  value: string;
  onChange: (period: string) => void;
}

export default function PeriodSelector({ value, onChange }: Props) {
  return (
    <div className="flex gap-1.5 bg-bg-secondary rounded-xl p-1">
      {periods.map((p) => (
        <button
          key={p.value}
          onClick={() => onChange(p.value)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            value === p.value
              ? "bg-accent-primary text-white shadow-md"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}
