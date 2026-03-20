/**
 * Type definitions for Mutual Fund Volatility Analyzer
 */

/**
 * Represents a single historical NAV data point
 */
export interface HistoricalNavPoint {
  date: string;  // ISO date format (YYYY-MM-DD)
  nav: number;   // Net Asset Value
}

/**
 * Prediction response data from the backend API
 */
export interface PredictionData {
  prediction: 'Stable' | 'High_Risk';
  historicalNav: HistoricalNavPoint[];
  currentRsi: number;
  currentVolatility: number;
  currentNav: number;
  currentMacd?: number;
  currentMacdSignal?: number;
  bbWidth?: number;
  dailyReturn?: number;
  sma20?: number;
  sma50?: number;
}

/**
 * API error response structure
 */
export interface ApiError {
  message: string;
  code: string;
}
