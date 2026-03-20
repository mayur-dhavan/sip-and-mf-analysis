export function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-16 animate-fade-in-up">
      <div className="relative w-16 h-16 mb-6">
        <div className="absolute inset-0 rounded-full border-4 border-[var(--card-border)]" />
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-[var(--accent)] animate-spin" />
        <div className="absolute inset-2 rounded-full border-4 border-transparent border-b-[var(--accent)] animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }} />
      </div>
      <p className="text-sm font-medium text-[var(--foreground)]">Analyzing fund data</p>
      <p className="text-xs text-[var(--muted)] mt-1">Fetching NAV data & running ML model...</p>
    </div>
  );
}
