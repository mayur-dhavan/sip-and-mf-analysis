'use client';

import { useState } from 'react';

interface SipCalculatorProps {
  currentNav?: number;
  fundName?: string;
}

export function SipCalculator({ currentNav, fundName }: SipCalculatorProps) {
  const [monthlyAmount, setMonthlyAmount] = useState<string>('5000');
  const [years, setYears] = useState<string>('10');
  const [expectedReturn, setExpectedReturn] = useState<string>('12');

  const monthly = parseFloat(monthlyAmount) || 0;
  const period = parseFloat(years) || 0;
  const rate = parseFloat(expectedReturn) || 0;

  const monthlyRate = rate / 12 / 100;
  const totalMonths = period * 12;
  const totalInvested = monthly * totalMonths;

  // SIP Future Value: P × [(1+r)^n - 1] / r × (1+r)
  const futureValue = monthlyRate > 0
    ? monthly * ((Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate) * (1 + monthlyRate)
    : totalInvested;

  const estimatedReturns = futureValue - totalInvested;

  const formatCurrency = (value: number): string => {
    if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)} Cr`;
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)} L`;
    return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  };

  const returnPct = totalInvested > 0 ? ((futureValue - totalInvested) / totalInvested * 100) : 0;

  return (
    <div className="bg-[var(--card-background)] rounded-xl border border-[var(--card-border)] p-6 animate-fade-in-up">
      <div className="flex items-center gap-2 mb-5">
        <div className="w-8 h-8 rounded-lg bg-[var(--accent-light)] flex items-center justify-center">
          <svg className="w-4 h-4 text-[var(--accent)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-[var(--foreground)]">SIP Calculator</h3>
          {fundName && <p className="text-xs text-[var(--muted)]">{fundName}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-xs font-medium text-[var(--muted)] mb-1.5">Monthly SIP (₹)</label>
          <input
            type="number"
            value={monthlyAmount}
            onChange={(e) => setMonthlyAmount(e.target.value)}
            min="500"
            step="500"
            className="w-full px-3 py-2.5 bg-[var(--surface)] border border-[var(--card-border)] rounded-lg text-sm text-[var(--foreground)] focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-[var(--muted)] mb-1.5">Investment Period (Years)</label>
          <input
            type="number"
            value={years}
            onChange={(e) => setYears(e.target.value)}
            min="1"
            max="40"
            className="w-full px-3 py-2.5 bg-[var(--surface)] border border-[var(--card-border)] rounded-lg text-sm text-[var(--foreground)] focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-[var(--muted)] mb-1.5">Expected Return (% p.a.)</label>
          <input
            type="number"
            value={expectedReturn}
            onChange={(e) => setExpectedReturn(e.target.value)}
            min="1"
            max="30"
            step="0.5"
            className="w-full px-3 py-2.5 bg-[var(--surface)] border border-[var(--card-border)] rounded-lg text-sm text-[var(--foreground)] focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent outline-none"
          />
        </div>
      </div>

      {/* Preset buttons */}
      <div className="flex gap-2 mb-5 flex-wrap">
        <span className="text-xs text-[var(--muted)] self-center">Quick:</span>
        {[
          { amount: '1000', label: '₹1K' },
          { amount: '5000', label: '₹5K' },
          { amount: '10000', label: '₹10K' },
          { amount: '25000', label: '₹25K' },
        ].map((preset) => (
          <button
            key={preset.amount}
            type="button"
            onClick={() => setMonthlyAmount(preset.amount)}
            className={`text-xs px-2.5 py-1 rounded-lg transition-colors duration-150 ${
              monthlyAmount === preset.amount
                ? 'bg-[var(--accent)] text-white'
                : 'bg-[var(--surface)] text-[var(--muted)] hover:text-[var(--accent)]'
            }`}
          >
            {preset.label}
          </button>
        ))}
      </div>

      {/* Results */}
      <div className="grid grid-cols-3 gap-4 p-4 bg-[var(--surface)] rounded-lg">
        <div className="text-center">
          <p className="text-xs text-[var(--muted)] mb-1">Invested</p>
          <p className="text-base font-bold text-[var(--foreground)]">{formatCurrency(totalInvested)}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-[var(--muted)] mb-1">Est. Returns</p>
          <p className="text-base font-bold text-[var(--success)]">{formatCurrency(estimatedReturns)}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-[var(--muted)] mb-1">Total Value</p>
          <p className="text-base font-bold text-[var(--accent)]">{formatCurrency(futureValue)}</p>
        </div>
      </div>

      {/* Invested vs Returns visual bar */}
      <div className="mt-4">
        <div className="flex h-3 rounded-full overflow-hidden bg-[var(--surface)]">
          <div
            className="bg-[var(--accent)] transition-all duration-500"
            style={{ width: futureValue > 0 ? `${(totalInvested / futureValue) * 100}%` : '100%' }}
          />
          <div
            className="bg-[var(--success)] transition-all duration-500"
            style={{ width: futureValue > 0 ? `${(estimatedReturns / futureValue) * 100}%` : '0%' }}
          />
        </div>
        <div className="flex justify-between mt-1.5 text-[10px] text-[var(--muted)]">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[var(--accent)]" />
            Invested ({futureValue > 0 ? `${((totalInvested / futureValue) * 100).toFixed(0)}%` : '—'})
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[var(--success)]" />
            Returns ({returnPct.toFixed(0)}% gain)
          </span>
        </div>
      </div>

      {currentNav && (
        <p className="mt-3 text-[11px] text-[var(--muted)] text-center">
          At current NAV ₹{currentNav.toFixed(2)}, your monthly SIP would buy ~{(monthly / currentNav).toFixed(2)} units/month
        </p>
      )}
    </div>
  );
}
