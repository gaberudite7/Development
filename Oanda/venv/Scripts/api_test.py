from api.oanda_api import OandaApi
from infrastructure.instrument_collection import instrumentCollection
from models.candle_timing import CandleTiming
from bot.trade_risk_calculator import get_trade_units
import constants.defs as defs
import time


def lm(msg, pair):
    #print(msg, pair)
    pass

if __name__ == "__main__":
    #instrumentCollection = InstrumentCollection()
    instrumentCollection.LoadInstruments(r"C:\Development\Oanda\Data")
    api = OandaApi() 
    # instrumentCollection.PrintInstruments()
    
    #api = OandaApi(instrumentCollection)
    
    #Place trade
    #api.place_trade("EUR_USD", 100, 1, take_profit=1.10200, stop_loss=1.09200)
    
    # Open and close trade
    #trade_id = api.place_trade("EUR_USD", 100, 1)
    #print("opened:", trade_id)
    #time.sleep(10)
    #print(f"Closing {trade_id}", api.close_trade(trade_id))

    # get trades with required id
    #print(api.get_open_trade(23))

    # get all trades without required id
    #print(api.get_open_trades())

    # formatted get all trades with no id
    #[print(x) for x in api.get_open_trades()]

    # close all trades
    #[api.close_trade(x.id) for x in api.get_open_trades]

    #dd = api.last_complete_candle("EUR_USD", granularity="M5")
    #print(CandleTiming(dd))

    #print(api.get_prices(["GBP_JPY", "AUD_NZD"]))
    #print(get_trade_units(api, "AUD_NZD", defs.BUY, .0055, 30, lm))
    print("USD_CAD", get_trade_units(api, "USD_CAD", defs.BUY, 0.004, 20, lm))