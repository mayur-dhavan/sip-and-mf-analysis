'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface ChartDataPoint {
  date: string;
  nav: number;
  sma?: number;
}

interface ChartComponentProps {
  data: ChartDataPoint[];
}

interface TooltipPayloadItem {
  color?: string;
  name?: string;
  value?: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[var(--card-background)] border border-[var(--card-border)] rounded-xl shadow-xl p-4">
        <p className="text-xs font-medium text-[var(--muted)] mb-2">
          {new Date(label).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          })}
        </p>
        {payload.map((entry, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-[var(--muted)]">{entry.name}:</span>
            <span className="font-semibold text-[var(--foreground)]">
              ₹{entry.value?.toFixed(2)}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export function ChartComponent({ data }: ChartComponentProps) {
  const formatXAxis = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="w-full bg-[var(--card-background)] rounded-xl border border-[var(--card-border)] p-6 animate-fade-in-up">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-[var(--foreground)]">
            NAV Price History
          </h3>
          <p className="text-xs text-[var(--muted)] mt-0.5">
            Last 6 months with 50-day Simple Moving Average
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs text-[var(--muted)]">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-0.5 rounded-full bg-[#3b82f6]" />
            NAV
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-0.5 rounded-full bg-[#f59e0b]" style={{ opacity: 0.8 }} />
            SMA 50
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--card-border)" opacity={0.5} />
          <XAxis
            dataKey="date"
            tickFormatter={formatXAxis}
            stroke="var(--muted)"
            style={{ fontSize: '11px' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="var(--muted)"
            style={{ fontSize: '11px' }}
            domain={['auto', 'auto']}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v: number) => `₹${v.toFixed(0)}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="nav"
            stroke="#3b82f6"
            strokeWidth={2}
            name="NAV"
            dot={false}
            activeDot={{ r: 5, strokeWidth: 2, fill: '#3b82f6' }}
          />
          <Line
            type="monotone"
            dataKey="sma"
            stroke="#f59e0b"
            strokeWidth={1.5}
            name="50-Day SMA"
            dot={false}
            activeDot={{ r: 4, strokeWidth: 2, fill: '#f59e0b' }}
            connectNulls={true}
            strokeDasharray="6 3"
            opacity={0.8}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
