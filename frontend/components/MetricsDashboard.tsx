import { MetricCard } from './MetricCard';
import { PredictionData } from '@/types';

interface MetricsDashboardProps {
  data: PredictionData;
}

function NavIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function RsiIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  );
}

function VolatilityIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );
}

function MacdIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
    </svg>
  );
}

function ReturnIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
    </svg>
  );
}

function TrendIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" />
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth={2} fill="none" />
    </svg>
  );
}

function getRsiVariant(rsi: number): 'success' | 'danger' | 'warning' | 'default' {
  if (rsi > 70) return 'danger';
  if (rsi < 30) return 'success';
  if (rsi > 60 || rsi < 40) return 'warning';
  return 'default';
}

function getRsiLabel(rsi: number): string {
  if (rsi > 70) return 'Overbought';
  if (rsi < 30) return 'Oversold';
  return 'Neutral zone';
}

function RiskBar({ probability }: { probability: number }) {
  const pct = Math.round(probability * 100);
  const barColor = pct > 65 ? 'var(--danger)' : pct > 35 ? 'var(--warning)' : 'var(--success)';
  return (
    <div className="mt-3">
      <div className="flex justify-between text-xs mb-1">
        <span className="text-[var(--muted)]">Risk Level</span>
        <span className="font-semibold" style={{ color: barColor }}>{pct}%</span>
      </div>
      <div className="w-full h-2 rounded-full bg-[var(--surface)]">
        <div className="h-2 rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: barColor }} />
      </div>
    </div>
  );
}

export function MetricsDashboard({ data }: MetricsDashboardProps) {
  const predictionVariant = data.prediction === 'Stable' ? 'success' : 'danger';
  const predictionDisplay = data.prediction === 'High_Risk' ? 'High Risk' : 'Stable';
  const rsiVariant = getRsiVariant(data.currentRsi);
  const dailyReturnVariant = (data.dailyReturn ?? 0) >= 0 ? 'success' : 'danger';

  return (
    <div className="space-y-4">
      {/* Risk Overview Banner */}
      <div className={`rounded-xl border p-5 flex flex-col sm:flex-row sm:items-center gap-4 animate-fade-in-up ${
        data.prediction === 'Stable'
          ? 'bg-[var(--success-light)] border-[var(--success)]'
          : 'bg-[var(--danger-light)] border-[var(--danger)]'
      }`}>
        <div className="flex items-center gap-3 flex-1">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
            data.prediction === 'Stable' ? 'bg-[var(--success)] bg-opacity-20' : 'bg-[var(--danger)] bg-opacity-20'
          }`}>
            <ShieldIcon />
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-[var(--muted)]">AI Risk Prediction — Next 15 Days</p>
            <p className={`text-2xl font-bold ${data.prediction === 'Stable' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
              {predictionDisplay}
            </p>
          </div>
        </div>
        <div className="flex gap-6 sm:gap-8">
          <div className="text-center">
            <p className="text-xs text-[var(--muted)]">Confidence</p>
            <p className="text-lg font-bold text-[var(--foreground)]">
              {data.modelConfidence !== undefined ? `${(data.modelConfidence * 100).toFixed(0)}%` : 'N/A'}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-[var(--muted)]">Risk Prob.</p>
            <p className="text-lg font-bold text-[var(--foreground)]">
              {data.riskProbability !== undefined ? `${(data.riskProbability * 100).toFixed(0)}%` : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Primary metrics row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="animate-fade-in-up stagger-1">
          <MetricCard
            title="Current NAV"
            value={`₹${data.currentNav.toFixed(2)}`}
            icon={<NavIcon />}
            subtitle={data.sma50 ? `SMA₅₀: ₹${data.sma50.toFixed(2)}` : undefined}
          />
        </div>
        <div className="animate-fade-in-up stagger-2">
          <MetricCard
            title="RSI (14-day)"
            value={data.currentRsi.toFixed(1)}
            variant={rsiVariant}
            icon={<RsiIcon />}
            subtitle={getRsiLabel(data.currentRsi)}
          />
        </div>
        <div className="animate-fade-in-up stagger-3">
          <MetricCard
            title="30-Day Volatility"
            value={data.currentVolatility.toFixed(4)}
            variant="default"
            icon={<VolatilityIcon />}
            subtitle={data.volatilityRatio !== undefined ? `Vol Ratio: ${data.volatilityRatio.toFixed(2)}` : 'Rolling std deviation'}
          />
        </div>
        <div className="animate-fade-in-up stagger-4">
          <MetricCard
            title="Daily Return"
            value={data.dailyReturn !== undefined ? `${(data.dailyReturn * 100).toFixed(2)}%` : 'N/A'}
            variant={dailyReturnVariant}
            icon={<ReturnIcon />}
            subtitle={data.bbWidth ? `BB Width: ${data.bbWidth.toFixed(4)}` : undefined}
          />
        </div>
      </div>

      {/* Secondary metrics row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {data.currentMacd !== undefined && data.currentMacd !== null && (
          <div className="animate-fade-in-up stagger-5">
            <MetricCard
              title="MACD"
              value={data.currentMacd.toFixed(3)}
              variant={data.currentMacd > (data.currentMacdSignal ?? 0) ? 'success' : 'danger'}
              icon={<MacdIcon />}
              subtitle={data.currentMacdSignal !== undefined ? `Signal: ${data.currentMacdSignal.toFixed(3)}` : undefined}
            />
          </div>
        )}
        {data.return20 !== undefined && data.return20 !== null && (
          <div className="animate-fade-in-up stagger-5">
            <MetricCard
              title="20-Day Return"
              value={`${(data.return20 * 100).toFixed(2)}%`}
              variant={data.return20 >= 0 ? 'success' : 'danger'}
              icon={<TrendIcon />}
              subtitle={data.return5 !== undefined ? `5-Day: ${(data.return5 * 100).toFixed(2)}%` : undefined}
            />
          </div>
        )}
        {data.sharpe30 !== undefined && data.sharpe30 !== null && (
          <div className="animate-fade-in-up stagger-6">
            <MetricCard
              title="Sharpe Ratio (30D)"
              value={data.sharpe30.toFixed(2)}
              variant={data.sharpe30 > 1 ? 'success' : data.sharpe30 < 0 ? 'danger' : 'warning'}
              icon={<RsiIcon />}
              subtitle={data.sharpe30 > 1 ? 'Good risk-adjusted return' : data.sharpe30 < 0 ? 'Negative risk-adjusted return' : 'Moderate'}
            />
          </div>
        )}
        {data.drawdown60 !== undefined && data.drawdown60 !== null && (
          <div className="animate-fade-in-up stagger-6">
            <MetricCard
              title="Max Drawdown (60D)"
              value={`${(data.drawdown60 * 100).toFixed(2)}%`}
              variant={data.drawdown60 < -0.10 ? 'danger' : data.drawdown60 < -0.05 ? 'warning' : 'success'}
              icon={<VolatilityIcon />}
              subtitle="From 60-day rolling peak"
            />
          </div>
        )}
      </div>

      {/* Risk probability bar */}
      {data.riskProbability !== undefined && (
        <div className="bg-[var(--card-background)] rounded-xl border border-[var(--card-border)] p-5 animate-fade-in-up">
          <RiskBar probability={data.riskProbability} />
        </div>
      )}
    </div>
  );
}
