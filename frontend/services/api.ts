/**
 * API Service Module
 * Handles communication with the backend API
 */

import { PredictionData, ApiError, FundSearchResult } from '../types';

interface BackendHistoricalPoint {
  date: string;
  nav: number;
}

interface BackendPredictionResponse {
  prediction: 'Stable' | 'High_Risk';
  ticker: string;
  fund_name: string;
  historical_nav: BackendHistoricalPoint[];
  current_rsi: number;
  current_volatility: number;
  current_nav: number;
  risk_probability?: number;
  model_confidence?: number;
  analysis_summary?: string;
  current_macd?: number;
  current_macd_signal?: number;
  bb_width?: number;
  daily_return?: number;
  sma_20?: number;
  sma_50?: number;
}

/**
 * Base URL for the backend API
 * Defaults to localhost:8000 if not set in environment
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Custom error class for API-related errors
 */
export class ApiServiceError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'ApiServiceError';
  }
}

/**
 * Predict volatility for a given mutual fund ticker
 * 
 * @param ticker - Mutual fund ticker symbol (e.g., "NIPPONINDIA.NS")
 * @returns Promise resolving to prediction data
 * @throws ApiServiceError for network or HTTP errors
 * 
 * Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
 */
export async function predictVolatility(ticker: string): Promise<PredictionData> {
  try {
    // Configure POST request
    const response = await fetch(`${API_BASE_URL}/api/predict-volatility/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ticker }),
    });

    // Handle HTTP errors
    if (!response.ok) {
      // Try to parse error response
      let errorData: ApiError | null = null;
      try {
        const errorJson = await response.json();
        errorData = errorJson.error || errorJson;
      } catch {
        // If JSON parsing fails, use status text
      }

      const errorMessage = errorData?.message || response.statusText || 'Request failed';
      const errorCode = errorData?.code || 'HTTP_ERROR';

      throw new ApiServiceError(errorMessage, errorCode, response.status);
    }

    // Parse JSON response
    const data: BackendPredictionResponse = await response.json();

    // Transform backend response to frontend format
    // Backend uses snake_case, frontend uses camelCase
    const predictionData: PredictionData = {
      prediction: data.prediction,
      ticker: data.ticker,
      fundName: data.fund_name,
      historicalNav: data.historical_nav.map((point) => ({
        date: point.date,
        nav: point.nav,
      })),
      currentRsi: data.current_rsi,
      currentVolatility: data.current_volatility,
      currentNav: data.current_nav,
      riskProbability: data.risk_probability,
      modelConfidence: data.model_confidence,
      analysisSummary: data.analysis_summary,
      currentMacd: data.current_macd,
      currentMacdSignal: data.current_macd_signal,
      bbWidth: data.bb_width,
      dailyReturn: data.daily_return,
      sma20: data.sma_20,
      sma50: data.sma_50,
    };

    return predictionData;
  } catch (error) {
    // Handle network errors
    if (error instanceof ApiServiceError) {
      throw error;
    }

    // Network or other errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiServiceError(
        'Unable to connect to the server. Please check your network connection.',
        'NETWORK_ERROR'
      );
    }

    // Unknown errors
    throw new ApiServiceError(
      error instanceof Error ? error.message : 'An unexpected error occurred',
      'UNKNOWN_ERROR'
    );
  }
}

/**
 * Search mutual fund tickers by query text.
 */
export async function searchFunds(query: string): Promise<FundSearchResult[]> {
  const normalized = query.trim();
  if (normalized.length < 2) {
    return [];
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/search-funds/?query=${encodeURIComponent(normalized)}&limit=8`
    );

    if (!response.ok) {
      throw new ApiServiceError('Failed to search mutual funds.', 'HTTP_ERROR', response.status);
    }

    const data = await response.json();
    return Array.isArray(data.results) ? data.results : [];
  } catch (error) {
    if (error instanceof ApiServiceError) {
      throw error;
    }

    throw new ApiServiceError(
      'Unable to search mutual funds right now. Please enter ticker directly.',
      'NETWORK_ERROR'
    );
  }
}
