import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8")


class IterativeBase():
    ''' Base class for iterative (event-driven) backtesting of trading strategies. '''

    def __init__(self, symbol, start, end, amount, use_spread=True):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.initial_balance = amount
        self.current_balance = amount
        self.units = 0
        self.trades = 0
        self.position = 0
        self.use_spread = use_spread
        self.get_data()
        self.results = None
        self.nav = []
        self.bh = []

    def get_data(self):
        raw = pd.read_csv(
            r"C:\Development\Trader_Workstation\yahoo_finance_data\CMCSA.csv",
            parse_dates=["Date"],
            index_col="Date", 
            encoding='latin1'
        ).dropna()
        raw = raw.loc[self.start:self.end].copy()
        raw["returns"] = np.log(raw.price / raw.price.shift(1))
        self.full_data = raw.copy()
        self.data = raw.copy()

    def plot_data(self, cols=None):
        if cols is None:
            cols = "price"
        self.data[cols].plot(figsize=(12, 8), title=self.symbol)

    def get_values(self, bar):
        date = str(self.data.index[bar].date())
        price = round(self.data.price.iloc[bar], 5)
        spread = round(self.data.spread.iloc[bar], 5)
        return date, price, spread

    def print_current_balance(self, bar):
        date, price, spread = self.get_values(bar)
        print(f"{date} | Current Balance: {round(self.current_balance, 2)}")

    def buy_instrument(self, bar, units=None, amount=None):
        date, price, spread = self.get_values(bar)
        if self.use_spread:
            price += spread / 2
        if amount is not None:
            units = int(amount / price)
        self.current_balance -= units * price
        self.units += units
        self.trades += 1
        print(f"{date} | Buying {units} for {round(price, 5)}")

    def sell_instrument(self, bar, units=None, amount=None):
        date, price, spread = self.get_values(bar)
        if self.use_spread:
            price -= spread / 2
        if amount is not None:
            units = int(amount / price)
        self.current_balance += units * price
        self.units -= units
        self.trades += 1
        print(f"{date} | Selling {units} for {round(price, 5)}")

    def print_current_position_value(self, bar):
        date, price, spread = self.get_values(bar)
        cpv = self.units * price
        print(f"{date} | Current Position Value = {round(cpv, 2)}")

    def print_current_nav(self, bar):
        date, price, spread = self.get_values(bar)
        nav = self.current_balance + self.units * price
        print(f"{date} | Net Asset Value = {round(nav, 2)}")

    def close_pos(self, bar):
        date, price, spread = self.get_values(bar)
        print(75 * "-")
        print(f"{date} | +++ CLOSING FINAL POSITION +++")
        self.current_balance += self.units * price
        self.current_balance -= (abs(self.units) * spread / 2 * self.use_spread)
        print(f"{date} | closing position of {self.units} for {price}")
        self.units = 0
        self.trades += 1
        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        start_price = self.full_data["price"].iloc[0]
        end_price = self.full_data["price"].iloc[-1]
        bh_perf = (end_price / start_price - 1) * 100
        self.print_current_balance(bar)
        print(f"{date} | net performance (%) = {round(perf, 2)}")
        print(f"{date} | buy and hold performance (%) = {round(bh_perf, 2)}")
        print(f"{date} | number of trades executed = {self.trades}")
        print(75 * "-")

    def update_performance_tracking(self, bar):
        price = self.data["price"].iloc[bar]
        full_start_price = self.full_data["price"].iloc[0]
        nav = self.current_balance + self.units * price
        self.nav.append(nav)
        bh_value = self.initial_balance * (price / full_start_price)
        self.bh.append(bh_value)

    def plot_performance(self):
        if not self.nav or not self.bh:
            print("No performance data to plot. Run a strategy first.")
            return
        df = pd.DataFrame({
            "Strategy": self.nav,
            "Buy & Hold": self.bh
        }, index=self.data.index[:len(self.nav)])
        df.plot(figsize=(12, 8), title=f"{self.symbol} | Strategy vs Buy & Hold", lw=2)
        plt.ylabel("Portfolio Value")
        plt.show()

    def plot_drawdowns(self):
        '''Plots drawdowns from the NAV time series.'''
        if not self.nav:
            print("No NAV data. Run a strategy first.")
            return
        df = pd.DataFrame(self.nav, index=self.data.index[:len(self.nav)], columns=["NAV"])
        df["Cumulative Max"] = df["NAV"].cummax()
        df["Drawdown"] = df["NAV"] / df["Cumulative Max"] - 1
        df["Drawdown"].plot(figsize=(12, 6), title=f"{self.symbol} | Strategy Drawdowns", color="red")
        plt.ylabel("Drawdown")
        plt.show()

    def get_rolling_sharpe(self, window=30):
        '''Calculates and plots the rolling Sharpe ratio.'''
        if not self.nav:
            print("No NAV data. Run a strategy first.")
            return
        df = pd.DataFrame(self.nav, index=self.data.index[:len(self.nav)], columns=["NAV"])
        df["returns"] = df["NAV"].pct_change()
        df["rolling_mean"] = df["returns"].rolling(window).mean()
        df["rolling_std"] = df["returns"].rolling(window).std()
        df["rolling_sharpe"] = df["rolling_mean"] / df["rolling_std"] * np.sqrt(252)  # annualized
        df["rolling_sharpe"].plot(figsize=(12, 6), title=f"{self.symbol} | Rolling Sharpe Ratio ({window}-bar window)")
        plt.ylabel("Sharpe Ratio")
        plt.axhline(0, color='black', linestyle='--', lw=1)
        plt.show()

    def export_performance(self, filename="performance_export.csv"):
        '''Exports performance data (NAV, B&H, Drawdown, Sharpe) to CSV.'''
        df = pd.DataFrame(index=self.data.index[:len(self.nav)])
        df["NAV"] = self.nav
        df["Buy & Hold"] = self.bh
        df["returns"] = df["NAV"].pct_change()
        df["drawdown"] = df["NAV"] / df["NAV"].cummax() - 1
        df["sharpe"] = df["returns"].rolling(30).mean() / df["returns"].rolling(30).std() * np.sqrt(252)
        df.to_csv(filename)
        print(f"Exported performance data to {filename}")
