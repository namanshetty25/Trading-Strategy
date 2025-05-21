import yfinance as yf
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import matplotlib.pyplot as plt

# Fetch Nifty 50 data from 2020 to 2023
data = yf.download("^NSEI", start="2020-01-01", end="2023-12-31", auto_adjust=True)

# Flatten multi-index columns if present
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

# Keep relevant columns and clean data
data = data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
data.index = pd.to_datetime(data.index)

# Set business day frequency and fill gaps
data = data.asfreq('B').interpolate(method='linear').dropna()

# Bollinger Band strategy
class BollingerStrategy(Strategy):
    def init(self):
        close = self.data.df['Close']
        self.ma = self.I(lambda: close.rolling(10).mean())
        self.std = self.I(lambda: close.rolling(10).std())
        self.upper = self.I(lambda: self.ma + 2 * self.std)
        self.lower = self.I(lambda: self.ma - 2 * self.std)

    def next(self):
        price = self.data.Close[-1]
        if price < self.lower[-1] and not self.position:
            print(f"BUY at {price:.2f} on {self.data.index[-1].date()}")
            self.buy(size=1.0)
        elif price > self.upper[-1] and self.position:
            print(f"SELL at {price:.2f} on {self.data.index[-1].date()}")
            self.position.close()

    def stop(self):
        if self.position:
            self.position.close()

# SMA + Bollinger Band strategy
class WorkingMeanReversion(Strategy):
    def init(self):
        close = self.data.df['Close']
        self.ma_short = self.I(lambda: close.rolling(5).mean())
        self.ma_long = self.I(lambda: close.rolling(20).mean())
        std = close.rolling(7).std()
        ma = close.rolling(7).mean()
        self.upper = self.I(lambda: ma + 2 * std)
        self.lower = self.I(lambda: ma - 2 * std)

    def next(self):
        price = self.data.Close[-1]
        if self.ma_short[-2] < self.ma_long[-2] and self.ma_short[-1] > self.ma_long[-1] and not self.position:
            print(f"BUY at {price:.2f} on {self.data.index[-1].date()}")
            self.buy(size=1.0)
        elif price > self.upper[-1] and self.position:
            print(f"SELL at {price:.2f} on {self.data.index[-1].date()}")
            self.position.close()

    def stop(self):
        if self.position:
            self.position.close()

# Print performance metrics
def print_metrics(name, stats, data):
    print(f"\n--- {name} Strategy Metrics ---")
    metrics = ['Return [%]', 'Sharpe Ratio', 'Sortino Ratio', 'Max. Drawdown [%]', 'Win Rate [%]', 'Profit Factor']
    for metric in metrics:
        print(f"{metric}: {stats.get(metric, 'N/A'):.2f}")
    days = (data.index[-1] - data.index[0]).days
    cumulative_return = stats['Return [%]'] / 100
    annualized = ((1 + cumulative_return) ** (252 / days) - 1) * 100
    print(f"Annualized Return [%]: {annualized:.2f}")
    trades = stats['_trades']
    print(f"\nTotal Trades: {trades.shape[0]}")
    if not trades.empty:
        trades['PnL'] = trades['ExitPrice'] - trades['EntryPrice']
        print(f"Average Profit: ₹{trades[trades['PnL'] > 0]['PnL'].mean():.2f}")
        print(f"Average Loss: ₹{trades[trades['PnL'] < 0]['PnL'].mean():.2f}")
        print(f"Max Profit: ₹{trades['PnL'].max():.2f}")
        print(f"Max Loss: ₹{trades['PnL'].min():.2f}")

# Run Bollinger Band strategy
bt1 = Backtest(data, BollingerStrategy, cash=100000, commission=0.001)
stats1 = bt1.run()
bt1.plot()
print_metrics("Bollinger Band", stats1, data)

# Run SMA + BB strategy
bt2 = Backtest(data, WorkingMeanReversion, cash=100000, commission=0.001)
stats2 = bt2.run()
bt2.plot()
print_metrics("SMA + BB", stats2, data)

# Plot drawdown for SMA + BB
stats2['_equity_curve']['Drawdown'] = (
    stats2['_equity_curve']['Equity'].cummax() - stats2['_equity_curve']['Equity']
)
plt.figure(figsize=(10, 4))
stats2['_equity_curve']['Drawdown'].plot(color='red')
plt.title('Drawdown Curve (SMA + BB Strategy)')
plt.ylabel('Drawdown in ₹')
plt.grid(True)
plt.tight_layout()
plt.show()

# Compare equity curves
plt.figure(figsize=(10, 4))
(100000 * data['Close'] / data['Close'].iloc[0]).plot(label="Buy & Hold (Nifty)")
stats2['_equity_curve']['Equity'].plot(label="SMA + BB Strategy")
plt.legend()
plt.title("Equity Curve Comparison: Strategy vs Nifty Buy & Hold")
plt.ylabel("Portfolio Value in ₹")
plt.grid(True)
plt.tight_layout()
plt.show()

# Export trade history
stats1['_trades'].to_csv("bb_trades.csv")
stats2['_trades'].to_csv("sma_bb_trades.csv")
