import pandas as pd

def BollingerBands(df: pd.DataFrame, n=20, s=2):
    typical_p = (df.mid_c + df.mid_h + df.mid_l) / 3
    stddev = typical_p.rolling(window=n).std()
    df['BB_MA'] = typical_p.rolling(window=n).mean()
    df['BB_UPPER'] = df['BB_MA'] + stddev*s
    df['BB_LOWER'] = df['BB_MA'] - stddev*s
    return df


# Keltner Channel Middle line = EMA
# Keltntner Channel Upper Band = EMA +2*ATR
# Keltntner Channel Lower Band = EMA -2*ATR
# mean reversion type of stuff.

# Exponential Moving average (typically over 20 periods)
# Average True Range (typically over 14 periods) shows the volatility of the range
# True Range is: Max of (High - Low), Abs(High - Previous Close), Abs(Low - Previous Close)
# Average True Range is the moving average of the True Range over the specified number of periods (1/n* the sum of the true range number of periods)

def ATR(df: pd.DataFrame, n=14):
    prev_c = df.mid_c.shift(1)
    tr1 = df.mid_h - df.mid_l
    tr2 = (df.mid_h - prev_c).abs()
    tr3 = (df.mid_l - prev_c).abs()

    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    df[f'ATR_{n}'] = tr.rolling(window=n).mean()
    return df

def KeltnerChannels(df: pd.DataFrame, n_ema= 20, n_atr=10):
    df['EMA'] = df.mid_c.ewm(span=n_ema, min_periods=n_ema).mean() #exponential weight
    df = ATR(df, n= n_atr)
    c_atr = f"ATR_{n_atr}"
    df['KeUp'] = df[c_atr] * 2 + df.EMA
    df['KeLo'] = df.EMA - df[c_atr] * 2
    df.drop(c_atr, axis=1, inplace=True)
    return df

# RSI: whether asset is overbought or oversold
# or if crosses over center reverse current asset

def RSI(df: pd.DataFrame, n=14):
    alpha = 1.0 / n
    gains = df.mid_c.diff() #absolute difference

    wins = pd.Series([x if x >=0 else 0.0 for x in gains], name = 'wins')
    losses = pd.Series([x * -1 if x <0 else 0.0 for x in gains], name = 'losses')

    wins_rma = wins.ewm(min_periods=n, alpha=alpha).mean()
    losses_rma = losses.ewm(min_periods=n, alpha=alpha).mean()    

    rs = wins_rma / losses_rma

    df[f"RSI_{n}"] = 100.0 - (100.0 / (1.0 + rs))
    return df

# Moving average convergence/divergence (MACD)
# Orange is signal line, blue is MACD line...histogram is difference
# difference btetween 26 and 12 exponential movign average
# below 0 if 12 below 26
# downward cross is sell upward cross is buy

def MACD(df: pd.DataFrame, n_slow=26, n_fast=12, n_signal=9):

    ema_long = df.mid_c.ewm(min_periods=n_slow, span=n_slow).mean()
    ema_short = df.mid_c.ewm(min_periods=n_fast, span=n_fast).mean()
    
    df['MACD'] = ema_short - ema_long
    df['SIGNAL'] = df.MACD.ewm(min_periods=n_signal, span=n_signal).mean()
    df['HIST'] = df.MACD - df.SIGNAL

    return df