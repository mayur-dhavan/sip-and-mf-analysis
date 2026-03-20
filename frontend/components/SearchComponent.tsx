'use client';

import { useState, FormEvent } from 'react';

interface SearchComponentProps {
  onSearch: (ticker: string) => void;
  isLoading: boolean;
}

export function SearchComponent({ onSearch, isLoading }: SearchComponentProps) {
  const [ticker, setTicker] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    const trimmedTicker = ticker.trim();
    
    if (!trimmedTicker) {
      setError('Please enter a ticker symbol');
      return;
    }
    
    setError('');
    onSearch(trimmedTicker);
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
                setTicker(e.target.value);
                if (error) setError('');
              }}
              placeholder="Enter ticker symbol (e.g., NIPPONINDIA.NS)"
              className="w-full pl-12 pr-4 py-3.5 bg-[var(--card-background)] border border-[var(--card-border)] rounded-xl text-[var(--foreground)] placeholder-[var(--muted)] focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent outline-none transition-all duration-200"
              disabled={isLoading}
            />
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
        <span className="text-xs text-[var(--muted)]">Try:</span>
        {['0P0000XVKR.BO', '0P0000XVL1.BO', '0P0000XVKY.BO', '^NSEI'].map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => { setTicker(t); setError(''); }}
            className="text-xs px-2.5 py-1 rounded-lg bg-[var(--surface)] text-[var(--muted)] hover:text-[var(--accent)] hover:bg-[var(--accent-light)] transition-colors duration-150"
            disabled={isLoading}
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}
