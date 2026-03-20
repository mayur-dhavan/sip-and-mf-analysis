'use client';

import { useState } from 'react';
import { SearchComponent } from '@/components/SearchComponent';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ErrorMessage } from '@/components/ErrorMessage';
import { MetricsDashboard } from '@/components/MetricsDashboard';
import { ChartComponent } from '@/components/ChartComponent';
import { predictVolatility, ApiServiceError } from '@/services/api';
import { PredictionData } from '@/types';

export default function Home() {
  const [data, setData] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSearchedTicker, setLastSearchedTicker] = useState<string>('');
  const [lastSearchedFundName, setLastSearchedFundName] = useState<string>('');

  const handleSearch = async (ticker: string, selectedFundName?: string) => {
    setError(null);
    setData(null);
    setLastSearchedTicker(ticker);
    setLastSearchedFundName(selectedFundName || '');
    setLoading(true);
    
    const startTime = Date.now();
    
    try {
      const result = await predictVolatility(ticker);
      setLastSearchedFundName(result.fundName || selectedFundName || '');
      
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, 500 - elapsedTime);
      if (remainingTime > 0) {
        await new Promise(resolve => setTimeout(resolve, remainingTime));
      }
      
      setData(result);
    } catch (err) {
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, 500 - elapsedTime);
      if (remainingTime > 0) {
        await new Promise(resolve => setTimeout(resolve, remainingTime));
      }
      
      if (err instanceof ApiServiceError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    if (lastSearchedTicker) {
      handleSearch(lastSearchedTicker);
    }
  };

  // Calculate 50-day SMA from NAV data
  const calculateSMA = (navData: Array<{ date: string; nav: number }>, period: number = 50) => {
    return navData.map((point, index) => {
      if (index < period - 1) {
        return { ...point, sma: undefined };
      }
      const slice = navData.slice(index - period + 1, index + 1);
      const sum = slice.reduce((acc, p) => acc + p.nav, 0);
      const sma = sum / period;
      return { ...point, sma };
    });
  };

  const chartData = data ? calculateSMA(data.historicalNav) : [];

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Top bar */}
      <nav className="sticky top-0 z-10 bg-[var(--card-background)] border-b border-[var(--card-border)] backdrop-blur-sm bg-opacity-80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[var(--accent)] flex items-center justify-center">
            <svg className="w-4.5 h-4.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <span className="font-semibold text-sm text-[var(--foreground)]">MF Volatility Analyzer</span>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {/* Hero / Header */}
        <header className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-[var(--foreground)] mb-3 tracking-tight">
            Mutual Fund Volatility Analyzer
          </h1>
          <p className="text-[var(--muted)] max-w-xl mx-auto text-sm sm:text-base">
            AI-powered risk analysis for Indian Mutual Funds using machine learning
            with 19 technical indicators and a stacked ensemble model.
          </p>
        </header>

        {/* Search */}
        <div className="mb-10">
          <SearchComponent onSearch={handleSearch} isLoading={loading} />
        </div>

        {/* Loading State */}
        {loading && <LoadingSpinner />}

        {/* Error State */}
        {!loading && error && (
          <ErrorMessage message={error} onRetry={handleRetry} />
        )}

        {/* Results */}
        {!loading && !error && data && (
          <div className="space-y-6">
            {/* Ticker header */}
            <div className="flex items-center gap-2 animate-fade-in-up">
              <span className="text-xs font-medium uppercase tracking-wider text-[var(--muted)]">Results for</span>
              <span className="text-sm font-semibold text-[var(--foreground)] bg-[var(--surface)] px-3 py-1 rounded-lg">
                {data.fundName || lastSearchedFundName || 'Mutual Fund'}
              </span>
              <span className="text-sm font-bold text-[var(--foreground)] bg-[var(--surface)] px-3 py-1 rounded-lg font-mono">
                {data.ticker || lastSearchedTicker}
              </span>
            </div>

            {/* Metrics Dashboard */}
            <MetricsDashboard data={data} />

            {/* Chart */}
            <ChartComponent data={chartData} />

            {/* Analysis Summary Card */}
            <div className="bg-[var(--card-background)] rounded-xl border border-[var(--card-border)] p-6 animate-fade-in-up">
              <h3 className="text-sm font-semibold text-[var(--foreground)] mb-4">Analysis Summary</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-xs text-[var(--muted)] mb-0.5">Data Points</p>
                  <p className="font-semibold text-[var(--foreground)]">{data.historicalNav.length} days</p>
                </div>
                <div>
                  <p className="text-xs text-[var(--muted)] mb-0.5">Model</p>
                  <p className="font-semibold text-[var(--foreground)]">XGBoost + RF Ensemble</p>
                </div>
                <div>
                  <p className="text-xs text-[var(--muted)] mb-0.5">Features Used</p>
                  <p className="font-semibold text-[var(--foreground)]">19 indicators</p>
                </div>
                <div>
                  <p className="text-xs text-[var(--muted)] mb-0.5">Prediction Window</p>
                  <p className="font-semibold text-[var(--foreground)]">15 days</p>
                </div>
              </div>
              <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-[var(--surface)] rounded-lg p-3">
                  <p className="text-xs text-[var(--muted)] mb-1">High Risk Probability</p>
                  <p className="text-base font-semibold text-[var(--foreground)]">
                    {data.riskProbability !== undefined ? `${(data.riskProbability * 100).toFixed(1)}%` : 'N/A'}
                  </p>
                </div>
                <div className="bg-[var(--surface)] rounded-lg p-3">
                  <p className="text-xs text-[var(--muted)] mb-1">Model Confidence</p>
                  <p className="text-base font-semibold text-[var(--foreground)]">
                    {data.modelConfidence !== undefined ? `${(data.modelConfidence * 100).toFixed(1)}%` : 'N/A'}
                  </p>
                </div>
              </div>
              {data.analysisSummary && (
                <p className="mt-4 text-sm text-[var(--foreground)] leading-relaxed">
                  {data.analysisSummary}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && !data && (
          <div className="text-center py-20 animate-fade-in-up">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-[var(--surface)] flex items-center justify-center">
              <svg className="w-8 h-8 text-[var(--muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-[var(--foreground)]">No analysis yet</h3>
            <p className="mt-1 text-sm text-[var(--muted)] max-w-sm mx-auto">
              Enter a mutual fund ticker symbol above to analyze its volatility and risk prediction.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-[var(--card-border)] py-6">
        <p className="text-center text-xs text-[var(--muted)]">
          Powered by ML Ensemble (XGBoost + Random Forest) &middot; 92% accuracy &middot; Not financial advice
        </p>
      </footer>
    </div>
  );
}
