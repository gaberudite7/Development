import sys
import plotly.graph_objects as go


sys.path.append("..")
from exploration.plotting import CandlePlot
import pandas as pd
from technicals.indicators import BollingerBands
from technicals.indicators import ATR, KeltnerChannels, RSI, MACD

df = pd.read_pickle(r"C:\Development\Oanda\Data\AUD_CAD_H1.pkl")
df_an = df.copy()
#df_an = BollingerBands(df_an, n=40, s=3)
#df_an = KeltnerChannels(df_an)
# df_an = ATR(df_an, n=14)
#df_an = RSI(df_an)
df_an = MACD(df_an)
#print(df_an.tail())

df_plot = df_an.iloc[-300:]

cp = CandlePlot(df_plot, candles=False)
cp.fig.add_trace(go.Bar(
    x=cp.df_plot.sTime, 
    y= cp.df_plot.HIST,
    name="HIST"
))
cp.show_plot(line_traces=['SIGNAL', 'MACD'])
print("done")