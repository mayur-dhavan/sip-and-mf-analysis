'use client';

import { useEffect, useState, FormEvent } from 'react';
import { searchFunds } from '@/services/api';
import { FundSearchResult } from '@/types';

interface SearchComponentProps {
  onSearch: (ticker: string, fundName?: string) => void;
  isLoading: boolean;
}

export function SearchComponent({ onSearch, isLoading }: SearchComponentProps) {
  const [ticker, setTicker] = useState('');
  const [error, setError] = useState('');
  const [suggestions, setSuggestions] = useState<FundSearchResult[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    if (ticker.trim().length < 2 || isLoading) {
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const results = await searchFunds(ticker);
        setSuggestions(results);
        setShowSuggestions(true);
      } catch {
        setSuggestions([]);
        setShowSuggestions(true);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [ticker, isLoading]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    const trimmedTicker = ticker.trim();
    
    if (!trimmedTicker) {
      setError('Please enter a ticker symbol');
      return;
    }
    
    setError('');
    onSearch(trimmedTicker);
    setShowSuggestions(false);
  };

  const handleSuggestionClick = (item: FundSearchResult) => {
    const executableTicker = item.yahoo_ticker || item.ticker;
    setTicker(executableTicker);
    setError('');
    setShowSuggestions(false);

    if (item.is_supported) {
      onSearch(executableTicker, item.name);
      return;
    }

    setError('AMFI entry found, but Yahoo ticker mapping is not available yet for direct analysis.');
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit}>
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-[var(--muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              id="ticker"
              type="text"
              value={ticker}
              onChange={(e) => {
                const next = e.target.value;
                setTicker(next);
                if (next.trim().length < 2) {
                  setSuggestions([]);
                  setShowSuggestions(false);
                }
                if (error) setError('');
              }}
              placeholder="Search mutual fund name or ticker (e.g., Axis Small Cap / 0P0000XVKR.BO)"
              className="w-full pl-12 pr-4 py-3.5 bg-[var(--card-background)] border border-[var(--card-border)] rounded-xl text-[var(--foreground)] placeholder-[var(--muted)] focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent outline-none transition-all duration-200"
              disabled={isLoading}
              onFocus={() => setShowSuggestions(suggestions.length > 0)}
            />
            {showSuggestions && ticker.trim().length >= 2 && (
              <div className="absolute z-20 mt-2 w-full bg-[var(--card-background)] border border-[var(--card-border)] rounded-xl shadow-lg max-h-64 overflow-auto">
                {suggestions.length > 0 ? (
                  suggestions.map((item) => (
                    <button
                      key={item.ticker}
                      type="button"
                      onClick={() => handleSuggestionClick(item)}
                      className="w-full text-left px-4 py-3 hover:bg-[var(--surface)] transition-colors"
                      disabled={isLoading}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="text-sm font-medium text-[var(--foreground)]">{item.name}</div>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${item.is_supported ? 'bg-[var(--success-light)] text-[var(--success)]' : 'bg-[var(--warning-light)] text-[var(--warning)]'}`}>
                          {item.is_supported ? 'Analyzable' : 'Lookup only'}
                        </span>
                      </div>
                      <div className="text-xs text-[var(--muted)] font-mono mt-0.5">{item.yahoo_ticker || item.ticker}</div>
                      <div className="text-[11px] text-[var(--muted)] mt-0.5">
                        {[item.fund_house, item.category, item.amfi_code ? `AMFI ${item.amfi_code}` : null].filter(Boolean).join(' | ')}
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="px-4 py-3 text-sm text-[var(--muted)]">
                    No funds matched this query. Press Analyze to try direct ticker/scheme code lookup.
                  </div>
                )}
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="px-8 py-3.5 bg-[var(--accent)] text-white font-semibold rounded-xl hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 whitespace-nowrap flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Analyzing...
              </>
            ) : (
              'Analyze'
            )}
          </button>
        </div>
        {error && (
          <p className="mt-2 text-sm text-[var(--danger)] pl-4">{error}</p>
        )}
      </form>

      {/* Quick ticker suggestions */}
      <div className="mt-3 flex items-center gap-2 flex-wrap pl-1">
        <span className="text-xs text-[var(--muted)]">Popular:</span>
        {[
          { ticker: '0P0000XVKR.BO', label: 'Axis Small Cap' },
          { ticker: '0P0000XVL1.BO', label: 'SBI Small Cap' },
          { ticker: '0P0001K4CC.BO', label: 'PPFAS Flexi Cap' },
          { ticker: '0P0001BAP8.BO', label: 'Quant Small Cap' },
          { ticker: '^NSEI', label: 'NIFTY 50' },
          { ticker: '0P00013CZ6.BO', label: 'HDFC Small Cap' },
        ].map((item) => (
          <button
            key={item.ticker}
            type="button"
            onClick={() => { setTicker(item.ticker); setError(''); onSearch(item.ticker, item.label); }}
            className="text-xs px-2.5 py-1 rounded-lg bg-[var(--surface)] text-[var(--muted)] hover:text-[var(--accent)] hover:bg-[var(--accent-light)] transition-colors duration-150"
            disabled={isLoading}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
