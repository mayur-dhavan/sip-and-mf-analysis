interface MetricCardProps {
  title: string;
  value: string | number;
  variant?: 'default' | 'success' | 'danger' | 'warning' | 'info';
  icon?: React.ReactNode;
  subtitle?: string;
}

export function MetricCard({ title, value, variant = 'default', icon, subtitle }: MetricCardProps) {
  const styles: Record<string, { card: string; text: string; icon: string }> = {
    default: {
      card: 'bg-[var(--card-background)] border-[var(--card-border)]',
      text: 'text-[var(--foreground)]',
      icon: 'text-[var(--accent)] bg-[var(--accent-light)]',
    },
    success: {
      card: 'bg-[var(--success-light)] border-[var(--success)]',
      text: 'text-[var(--success)]',
      icon: 'text-[var(--success)] bg-[var(--success-light)]',
    },
    danger: {
      card: 'bg-[var(--danger-light)] border-[var(--danger)]',
      text: 'text-[var(--danger)]',
      icon: 'text-[var(--danger)] bg-[var(--danger-light)]',
    },
    warning: {
      card: 'bg-[var(--warning-light)] border-[var(--warning)]',
      text: 'text-[var(--warning)]',
      icon: 'text-[var(--warning)] bg-[var(--warning-light)]',
    },
    info: {
      card: 'bg-[var(--accent-light)] border-[var(--accent)]',
      text: 'text-[var(--accent)]',
      icon: 'text-[var(--accent)] bg-[var(--accent-light)]',
    },
  };

  const s = styles[variant] || styles.default;

  return (
    <div className={`rounded-xl border p-5 ${s.card} hover:shadow-md transition-shadow duration-200`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium uppercase tracking-wider text-[var(--muted)] mb-1">{title}</p>
          <p className={`text-2xl font-bold ${s.text} truncate`}>{value}</p>
          {subtitle && (
            <p className="text-xs text-[var(--muted)] mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`flex-shrink-0 ml-3 w-10 h-10 rounded-lg flex items-center justify-center ${s.icon}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
