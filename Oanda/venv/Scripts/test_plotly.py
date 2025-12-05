import pandas as pd
import plotly.graph_objects as go
import datetime as dt
from exploration.plotting import CandlePlot
from infrastructure.instrument_collection import instrumentCollection as ic

# In case we need to import other folders
# import sys
# sys.path.append(r"C:\Development\Oanda\venv\Scripts")

pair = "EUR_USD"
granularity = "H4"
df = pd.read_pickle(fr"C:\Development\Oanda\Data\{pair}_{granularity}.pkl")

# Moving Averages...loop or set
MA_LIST = [10, 20, 50, 100, 200]
MA_S = "MA_10"
MA_L = "MA_20"
BUY = 1
SELL = -1
NONE = 0


df_ma = df[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c']].copy()

#df_ma['MA_10'] = df_ma['mid_c'].rolling(window=10).mean()

# Create moving averages
for ma in MA_LIST:
    df_ma[f"MA_{ma}"] = df_ma['mid_c'].rolling(window=ma).mean()



# Drop rows with NaN values (can't get average until days add up)
df_ma.dropna(inplace=True)
df_ma.reset_index(drop=True, inplace=True)

df_an = df_ma[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c', MA_S, MA_L]].copy()

# df_an processing
# Calculate delta between MAs (if positive then buy if negative then sell)
df_an['DELTA'] = df_an.MA_10 - df_an.MA_20
df_an['DELTA_PREV'] = df_an.DELTA.shift(1)


def is_trade(row):
    # Above the line
    if row.DELTA > 0 and row.DELTA_PREV <= 0:
        return BUY
    # Below the line
    elif row.DELTA < 0 and row.DELTA_PREV >= 0:
        return SELL
    else:
        return NONE

df_an['TRADE'] = df_an.apply(is_trade, axis=1)
df_trades = df_an[df_an.TRADE != 0].copy()

print(df_trades.shape)
print(df_trades)
df_plot = df_ma.iloc[:100]

cp = CandlePlot(df_plot)

traces = [ f"MA_{ma}" for ma in MA_LIST ]

#cp.show_plot(line_traces=traces)

ic.LoadInstruments(fr"C:\Development\Oanda\Data")
ic.instruments_dict[pair]
ins_data = ic.instruments_dict[pair]
df_trades.head()
df_trades['DIFF'] = df_trades.mid_c.diff().shift(-1)
df_trades.fillna(0, inplace=True)
df_trades['GAIN'] = df_trades['DIFF'] / ins_data.pipLocation
df_trades['GAIN'] = df_trades['DIFF'] * df_trades['TRADE']
print(df_trades.GAIN.sum())
df_trades['GAIN_CUM'] = df_trades.GAIN.cumsum()
cp = CandlePlot(df_trades, candles=False)
cp.show_plot(line_traces=['GAIN_CUM'])