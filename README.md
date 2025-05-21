# Mean Reversion Trading Strategies on Nifty 50

This project implements and compares two rule-based trading strategies on the Nifty 50 index using historical data (2020–2023). Both strategies aim to capture mean-reverting behavior using technical indicators like Bollinger Bands and Simple Moving Averages (SMAs).

---

## Strategies Implemented

### 1. Bollinger Band Reversion
- Buy when the price drops below the lower Bollinger Band (10-day window).
- Sell when the price crosses above the upper Bollinger Band.
- Only one position at a time (long-only strategy).

### 2. SMA Crossover + Bollinger Band Exit
- Entry: Buy when 5-day SMA crosses above 20-day SMA.
- Exit: Sell when price hits the upper Bollinger Band (7-day window).
- This combines momentum entry with volatility-based profit-taking.

---




