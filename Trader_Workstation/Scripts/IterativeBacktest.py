from IterativeBase import *

class IterativeBacktest(IterativeBase):
    ''' Class for iterative (event-driven) backtesting of trading strategies. '''

    def go_long(self, bar, units=None, amount=None):
        if self.position == -1:
            self.buy_instrument(bar, units=-self.units)  # neutralize short
        if units:
            self.buy_instrument(bar, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.buy_instrument(bar, amount=amount)
        self.position = 1

    def go_short(self, bar, units=None, amount=None):
        if self.position == 1:
            self.sell_instrument(bar, units=self.units)  # neutralize long
        if units:
            self.sell_instrument(bar, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.sell_instrument(bar, amount=amount)
        self.position = -1

    def test_sma_strategy(self, SMA_S, SMA_L):
        print("-" * 75)
        print(f"Testing SMA strategy | {self.symbol} | SMA_S = {SMA_S} & SMA_L = {SMA_L}")
        print("-" * 75)

        self.position = 0
        self.trades = 0
        self.current_balance = self.initial_balance
        self.get_data()

        # ✅ Reset performance tracking
        self.nav = []
        self.bh = []

        self.data["SMA_S"] = self.data["price"].rolling(SMA_S).mean()
        self.data["SMA_L"] = self.data["price"].rolling(SMA_L).mean()
        self.data.dropna(inplace=True)

        for bar in range(len(self.data) - 1):
            if self.data["SMA_S"].iloc[bar] > self.data["SMA_L"].iloc[bar]:
                if self.position in [0, -1]:
                    self.go_long(bar, amount="all")
            elif self.data["SMA_S"].iloc[bar] < self.data["SMA_L"].iloc[bar]:
                if self.position in [0, 1]:
                    self.go_short(bar, amount="all")
            self.update_performance_tracking(bar)

        self.close_pos(bar + 1)

    def test_con_strategy(self, window=1):
        print("-" * 75)
        print(f"Testing Contrarian strategy | {self.symbol} | Window = {window}")
        print("-" * 75)

        self.position = 0
        self.trades = 0
        self.current_balance = self.initial_balance
        self.get_data()

        # ✅ Reset performance tracking
        self.nav = []
        self.bh = []

        self.data["rolling_returns"] = self.data["returns"].rolling(window).mean()
        self.data.dropna(inplace=True)

        for bar in range(len(self.data) - 1):
            if self.data["rolling_returns"].iloc[bar] <= 0:
                if self.position in [0, -1]:
                    self.go_long(bar, amount="all")
            elif self.data["rolling_returns"].iloc[bar] > 0:
                if self.position in [0, 1]:
                    self.go_short(bar, amount="all")
            self.update_performance_tracking(bar)

        self.close_pos(bar + 1)

    def test_boll_strategy(self, SMA, dev):
        print("-" * 75)
        print(f"Testing Bollinger Bands Strategy | {self.symbol} | SMA = {SMA} & dev = {dev}")
        print("-" * 75)

        self.position = 0
        self.trades = 0
        self.current_balance = self.initial_balance
        self.get_data()

        # ✅ Reset performance tracking
        self.nav = []
        self.bh = []

        self.data["SMA"] = self.data["price"].rolling(SMA).mean()
        self.data["Lower"] = self.data["SMA"] - self.data["price"].rolling(SMA).std() * dev
        self.data["Upper"] = self.data["SMA"] + self.data["price"].rolling(SMA).std() * dev
        self.data.dropna(inplace=True)

        for bar in range(len(self.data) - 1):
            price = self.data["price"].iloc[bar]
            upper = self.data["Upper"].iloc[bar]
            lower = self.data["Lower"].iloc[bar]
            sma = self.data["SMA"].iloc[bar]

            if self.position == 0:
                if price < lower:
                    self.go_long(bar, amount="all")
                elif price > upper:
                    self.go_short(bar, amount="all")
            elif self.position == 1:
                if price > sma:
                    if price > upper:
                        self.go_short(bar, amount="all")
                    else:
                        self.sell_instrument(bar, units=self.units)
                        self.position = 0
            elif self.position == -1:
                if price < sma:
                    if price < lower:
                        self.go_long(bar, amount="all")
                    else:
                        self.buy_instrument(bar, units=-self.units)
                        self.position = 0

            self.update_performance_tracking(bar)

        self.close_pos(bar + 1)

if __name__ == "__main__":
    
    bt = IterativeBacktest("CMCSA", "2024-01-16", "2025-09-13", 100000, use_spread=False)

    # Drawdown measures how far a strategy’s portfolio value falls from its previous peak. It helps answer:
    # “How bad did it get before it got better?”
    #     💡 Interpretation:
    # A drawdown of -0.10 (or -10%) means your portfolio has fallen 10% from its recent high.
    # The maximum drawdown is the largest drop you’ve experienced over the backtest.
    # 📈 Use:
    # Helps assess risk and recovery time
    # A system with great returns but big drawdowns might be too risky    
    #bc.plot_drawdowns()

    # Rolling Sharpe gives you a time-varying measure of risk-adjusted return.
    # 📌 What It Shows:
    # “How attractive were the returns over time, adjusted for volatility?”
    # 💡 Interpretation:
    # A Sharpe > 1.0 = strong risk-adjusted return
    # A negative Sharpe = losing money or too volatile
    # Rolling Sharpe lets you see when the strategy was performing well (or not)
    #bc.get_rolling_sharpe(window=30)


    bt.test_sma_strategy(50, 200)
    bt.plot_performance()
    bt.plot_drawdowns()
    bt.get_rolling_sharpe(window=30)
    bt.export_performance("con_strategy.csv")

    bt.test_con_strategy(window=3)
    bt.plot_performance()
    bt.plot_drawdowns()
    bt.get_rolling_sharpe(window=30)
    bt.export_performance("con_strategy.csv")

    bt.test_boll_strategy(SMA=50, dev=2)
    bt.plot_performance()
    bt.plot_drawdowns()
    bt.get_rolling_sharpe(window=30)
    bt.export_performance("boll_strategy.csv")