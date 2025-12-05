import pandas as pd
from exploration.plotting import CandlePlot
pd.set_option('display.max_columns', None)

df_ma_res = pd.read_pickle(r"C:\Development\Oanda\Data\ma_res.pkl")
df_ma_trades = pd.read_pickle(r"C:\Development\Oanda\Data\ma_trades.pkl")

# print(df_ma_res.granularity.unique())

df_ma_res_h1 = df_ma_res[df_ma_res.granularity == "H1"].copy()
df_ma_trades_h1 = df_ma_trades[df_ma_trades.granularity == "H1"].copy()

df_cross_summary = df_ma_res_h1[['pair', 'num_trades', 'total_gain', 'cross']].copy()
df_cross_grouped = df_cross_summary.groupby(by='cross', as_index = False).sum()
df_cross_grouped.sort_values(by='total_gain', ascending=False, inplace=True)

total_pairs = len(df_ma_res_h1.pair.unique())
#print(total_pairs)

temp = df_ma_res_h1[df_ma_res_h1.cross == "MA_10_MA_40"].copy()
#print(temp[temp.total_gain > 0].shape[0])

for c in df_ma_res_h1.cross.unique():
    temp = df_ma_res_h1[df_ma_res_h1.cross == c].copy()
    pg = temp[temp.total_gain > 0].shape[0]
    print(f"{c}: pg:{pg} perc gain:{(pg/total_pairs)*100:.0f}%")