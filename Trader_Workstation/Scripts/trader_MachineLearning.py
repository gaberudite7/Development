
# Please run the following code only with your Paper Trading Account!!!
# Check the Regular Trading Hours!!!

from ib_async import * 
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime, timezone # new
from IPython.display import display, clear_output
import os # new
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
import pickle
#util.startLoop()

ib = IB()
ib.connect()

# strategy parameters
freq = "5 mins"
lm = pickle.load(open("logreg.pkl", "rb"))
lags = 2
params = pickle.load(open("params.pkl", "rb"))
means = params["mu"]
stand_devs = params["std"]
units = 1000
end_time = dt.time(21, 59, 0) # stop condition
contract = Forex('EURUSD') 
ib.qualifyContracts(contract)
cfd = CFD("EUR", currency = "USD")
ib.qualifyContracts(cfd)
conID = cfd.conId

def onBarUpdate(bars, hasNewBar):  
    global df, last_bar
    
    if bars[-1].date > last_bar: 
        last_bar = bars[-1].date
    
        # Data Processing
        df = pd.DataFrame(bars)[["date", "open", "high", "low", "close"]]#.iloc[:-1] keep latest incomplete bar
        df.set_index("date", inplace = True)
        
        ####################### Trading Strategy ###########################
        df = df[["close"]].copy()
        df["returns"] = np.log(df["close"] / df["close"].shift())

        cols = []
        for lag in range(1, lags + 1):
            col = "lag{}".format(lag)
            df[col] = df.returns.shift(lag)
            cols.append(col)
        df.dropna(inplace = True)
        df[cols] = (df[cols] - means) / stand_devs
        
        df["position"] = lm.predict(df[cols])
        ####################################################################
        
        # Trading
        target = df["position"][-1] * units
        execute_trade(target = target)
        
        # Display
        clear_output(wait=True)
        display(df)
    else:
        try:
            trade_reporting()
        except:
            pass

def execute_trade(target):
    global current_pos
    
    # 1. get current Position
    try:
        current_pos = [pos.position for pos in ib.positions() if pos.contract.conId == conID][0]
    except:
        current_pos = 0
         
    # 2. identify required trades
    trades = target - current_pos
        
    # 3. trade execution
    if trades > 0:
        side = "BUY"
        order = MarketOrder(side, abs(trades))
        trade = ib.placeOrder(cfd, order)  
    elif trades < 0:
        side = "SELL"
        order = MarketOrder(side, abs(trades))
        trade = ib.placeOrder(cfd, order)
    else:
        pass

def trade_reporting():
    global report
    
    fill_df = util.df([fs.execution for fs in ib.fills()])[["execId", "time", "side", "cumQty", "avgPrice"]].set_index("execId")
    profit_df = util.df([fs.commissionReport for fs in ib.fills()])[["execId", "realizedPNL"]].set_index("execId")
    report = pd.concat([fill_df, profit_df], axis = 1).set_index("time").loc[session_start:]
    report = report.groupby("time").agg({"side":"first", "cumQty":"max", "avgPrice":"mean", "realizedPNL":"sum"})
    report["cumPNL"] = report.realizedPNL.cumsum()
        
    clear_output(wait=True)
    display(df, report)
  
    
if __name__ == "__main__": # if you run trader.py as python script

    # start trading session
    session_start = pd.to_datetime(datetime.now(timezone.utc))# new
    bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting=freq,
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=2,
            keepUpToDate=True)
    last_bar = bars[-1].date
    bars.updateEvent += onBarUpdate
    ib.sleep(30) # new - to be added (optional)

    # stop trading session
    while True:
        ib.sleep(5) # check every 5 seconds
        if datetime.now(timezone.utc).time() >= end_time: # if stop conditions has been met
            execute_trade(target = 0) # close open position 
            ib.cancelHistoricalData(bars) # stop stream
            ib.sleep(10)
            try:
                trade_reporting() # final reporting
            except:
                pass
            print("Session Stopped.")
            ib.disconnect()
            break
        else:
            pass