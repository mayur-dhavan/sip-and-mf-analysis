'use client';

import { useState } from 'react';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ErrorMessage } from '@/components/ErrorMessage';

export default function ComponentDemo() {
  const [showLoading, setShowLoading] = useState(false);
  const [showError, setShowError] = useState(false);

  const handleRetry = () => {
    console.log('Retry clicked');
    setShowError(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Component Demo</h1>
        
        <div className="space-y-8">
          <section className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">LoadingSpinner Component</h2>
            <button
              onClick={() => setShowLoading(!showLoading)}
              className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {showLoading ? 'Hide' : 'Show'} Loading Spinner
            </button>
            {showLoading && <LoadingSpinner />}
          </section>

          <section className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">ErrorMessage Component</h2>
            <button
              onClick={() => setShowError(!showError)}
              className="mb-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              {showError ? 'Hide' : 'Show'} Error Message
            </button>
            {showError && (
              <ErrorMessage
                message="Unable to fetch mutual fund data. Please check the ticker symbol and try again."
                onRetry={handleRetry}
              />
            )}
          </section>

          <section className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">ErrorMessage without Retry</h2>
            <ErrorMessage message="This is an error message without a retry button." />
          </section>
        </div>
      </div>
    </div>
  );
}
