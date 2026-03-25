"""
Mutual Fund Volatility Predictor - Hugging Face Space
Gradio app that serves ML model predictions for mutual fund volatility.
"""

import gradio as gr
import joblib
import numpy as np
import pandas as pd
import yfinance as yf
from huggingface_hub import hf_hub_download
from pathlib import Path

# ── Feature configuration ──────────────────────────────────────────────────────

FEATURE_COLS = [
    "RSI", "SMA_50", "SMA_20", "EMA_20", "Rolling_Volatility_30",
    "Rolling_Volatility_10", "Daily_Return", "ROC_10", "MACD",
    "MACD_Signal", "MACD_Hist", "BB_Width", "NAV_to_SMA50_Ratio",
    "Volatility_Ratio", "Return_5", "Return_20", "Sharpe_30",
    "ZScore_20", "Drawdown_60",
]

# ── Feature calculation helpers ────────────────────────────────────────────────

def calculate_rsi(nav: pd.Series, period=14):
    delta = nav.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).fillna(100)

def calculate_features(nav_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all 19 technical features from a Close-price DataFrame."""
    df = nav_df.copy()
    nav = df["Close"]
    df["RSI"] = calculate_rsi(nav)
    df["SMA_50"] = nav.rolling(50).mean()
    df["SMA_20"] = nav.rolling(20).mean()
    df["EMA_20"] = nav.ewm(span=20, min_periods=20, adjust=False).mean()
    df["Rolling_Volatility_30"] = nav.rolling(30).std()
    df["Rolling_Volatility_10"] = nav.rolling(10).std()
    df["Daily_Return"] = nav.pct_change(fill_method=None)
    df["ROC_10"] = (nav - nav.shift(10)) / nav.shift(10) * 100

    ema12 = nav.ewm(span=12, min_periods=12, adjust=False).mean()
    ema26 = nav.ewm(span=26, min_periods=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, min_periods=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    mid = nav.rolling(20).mean()
    std = nav.rolling(20).std()
    df["BB_Width"] = ((mid + 2 * std) - (mid - 2 * std)) / mid

    df["NAV_to_SMA50_Ratio"] = nav / df["SMA_50"]
    df["Volatility_Ratio"] = df["Rolling_Volatility_10"] / df["Rolling_Volatility_30"]
    df["Return_5"] = nav.pct_change(periods=5, fill_method=None)
    df["Return_20"] = nav.pct_change(periods=20, fill_method=None)

    daily_ret = nav.pct_change(fill_method=None)
    rm = daily_ret.rolling(30).mean()
    rs = daily_ret.rolling(30).std()
    df["Sharpe_30"] = ((rm / rs) * np.sqrt(252)).replace([np.inf, -np.inf], np.nan)

    rmean = nav.rolling(20).mean()
    rstd = nav.rolling(20).std()
    df["ZScore_20"] = ((nav - rmean) / rstd).replace([np.inf, -np.inf], np.nan)

    rolling_max = nav.rolling(60).max()
    df["Drawdown_60"] = (nav / rolling_max) - 1.0

    return df

# ── Model loading ──────────────────────────────────────────────────────────────

MODEL_CACHE = {}

def load_model():
    if "model" in MODEL_CACHE:
        return MODEL_CACHE["model"], MODEL_CACHE["threshold"]
    
    model_path = Path("volatility_model.pkl")
    if not model_path.exists():
        model_path = Path(hf_hub_download(
            repo_id="mayur6901/sip-mf-volatility-predictor",
            filename="volatility_model.pkl",
            repo_type="space",
        ))
    
    artifact = joblib.load(model_path)
    if isinstance(artifact, dict) and "model" in artifact:
        model = artifact["model"]
        threshold = float(np.clip(artifact.get("decision_threshold", 0.5), 0.15, 0.85))
    else:
        model = artifact
        threshold = 0.5
    
    MODEL_CACHE["model"] = model
    MODEL_CACHE["threshold"] = threshold
    return model, threshold

# ── Prediction logic ───────────────────────────────────────────────────────────

def predict(ticker: str):
    """Run volatility prediction for a ticker symbol."""
    if not ticker or not ticker.strip():
        return "Please enter a ticker symbol", "", ""
    
    ticker = ticker.strip()
    
    try:
        # Fetch data
        data = yf.download(ticker, period="1y", progress=False)
        if data is None or data.empty or len(data) < 60:
            return f"Insufficient data for '{ticker}'. Need at least 60 trading days.", "", ""
        
        # Flatten multi-level columns if present
        if hasattr(data.columns, 'levels') and len(data.columns.levels) > 1:
            data.columns = data.columns.get_level_values(0)
        
        if "Close" not in data.columns:
            return f"No 'Close' price data found for '{ticker}'.", "", ""
        
        # Calculate features
        features_df = calculate_features(data)
        available = [c for c in FEATURE_COLS if c in features_df.columns]
        complete = features_df.dropna(subset=available)
        
        if complete.empty:
            row = features_df.iloc[-1]
        else:
            row = complete.iloc[-1]
        
        # Build feature vector
        feature_values = []
        for col in FEATURE_COLS:
            val = row.get(col, 0.0)
            if pd.isna(val) or np.isinf(val):
                val = 0.0
            feature_values.append(float(val))
        
        feature_array = pd.DataFrame([feature_values], columns=FEATURE_COLS)
        
        # Predict
        model, threshold = load_model()
        
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(feature_array)[0]
            prob = float(probs[1]) if len(probs) >= 2 else float(probs[0])
        elif hasattr(model, "decision_function"):
            score = float(model.decision_function(feature_array)[0])
            prob = float(1.0 / (1.0 + np.exp(-score)))
        else:
            prob = float(model.predict(feature_array)[0])
        
        prob = float(np.clip(prob, 0.0, 1.0))
        prediction = "High_Risk" if prob >= threshold else "Stable"
        confidence = max(prob, 1.0 - prob)
        
        # Format results
        status = f"## {'🔴 High Risk' if prediction == 'High_Risk' else '🟢 Stable'}"
        
        details = f"""**Ticker:** {ticker}
**Prediction:** {prediction}
**Risk Probability:** {prob:.1%}
**Confidence:** {confidence:.1%}
**Decision Threshold:** {threshold:.2f}"""
        
        indicators = f"""| Indicator | Value |
|-----------|-------|
| RSI | {row.get('RSI', 'N/A'):.2f} |
| SMA 50 | {row.get('SMA_50', 'N/A'):.2f} |
| Rolling Volatility 30d | {row.get('Rolling_Volatility_30', 'N/A'):.4f} |
| MACD | {row.get('MACD', 'N/A'):.4f} |
| Bollinger Band Width | {row.get('BB_Width', 'N/A'):.4f} |
| Sharpe Ratio 30d | {row.get('Sharpe_30', 'N/A'):.2f} |
| Z-Score 20d | {row.get('ZScore_20', 'N/A'):.2f} |
| Drawdown 60d | {row.get('Drawdown_60', 'N/A'):.4f} |"""
        
        return status, details, indicators
        
    except Exception as e:
        return f"Error: {str(e)}", "", ""

# ── Gradio UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="MF Volatility Predictor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""# 📊 Mutual Fund Volatility Predictor
    
Predict whether a mutual fund or stock is at **High Risk** of volatility or **Stable**.
Enter a Yahoo Finance ticker symbol (e.g., `INFY.NS`, `^NSEBANK`, `AAPL`).
""")
    
    with gr.Row():
        ticker_input = gr.Textbox(
            label="Ticker Symbol",
            placeholder="e.g., INFY.NS, ^NSEBANK, AAPL",
            scale=3,
        )
        predict_btn = gr.Button("Predict", variant="primary", scale=1)
    
    status_output = gr.Markdown(label="Status")
    
    with gr.Row():
        details_output = gr.Markdown(label="Prediction Details")
        indicators_output = gr.Markdown(label="Technical Indicators")
    
    predict_btn.click(
        fn=predict,
        inputs=[ticker_input],
        outputs=[status_output, details_output, indicators_output],
    )
    
    gr.Examples(
        examples=["INFY.NS", "^NSEBANK", "^NSMIDCP", "AAPL", "RELIANCE.NS"],
        inputs=ticker_input,
    )

demo.launch()
