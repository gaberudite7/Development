import threading
from queue import Queue
import datetime as dt
import time
from models.trade_settings import TradeSettings
from infrastructure.log_wrapper import LogWrapper
from api.oanda_api import OandaApi
import pandas as pd
from bot.technicals_manager import process_candles
from constants import defs
from models.trade_decision import TradeDecision




class CandleWorker(threading.Thread):

    def __init__(self, trade_settings: TradeSettings, 
                 candle_work: Queue,
                 trade_work_queue: Queue,
                 granularity: str):
        super().__init__()
        self.trade_settings = trade_settings
        self.candle_work = candle_work
        self.trade_work_queue = trade_work_queue
        self.granularity = granularity

        self.log = LogWrapper(f"CandleWorker_{trade_settings.pair}")
        self.api = OandaApi()
        self.log_message(f"Created CandleWorker for {trade_settings.pair} {trade_settings}")

    def log_message(self, msg, error=False):
        if error:
            self.log.logger.error(msg)
        else:
            self.log.logger.error(msg)
    

    def place_trade_work(self, df: pd.DataFrame):
        try:
            last_row = process_candles(
                df, 
                self.trade_settings.pair,
                self.trade_settings,
                self.log_message
            )
            if last_row is None:
                self.log_message("process_candles within candle_worker.py failed", error=True)
                return
            
            print(f"CandleWorker script {self.trade_settings.pair} SIGNAL", last_row.SIGNAL)

            if last_row.SIGNAL != defs.NONE:
                td: TradeDecision = TradeDecision(last_row)
                print(f"CandleWorker {self.trade_settings.pair} TradeDecision", td)
                self.trade_work_queue.put(td)
        except Exception as error:
            self.log_message(f"Exception: {error}", error=True)


    def run_analysis(self, expected_time: dt.datetime):
        # Multiple attempts needed sometimes due to API issues/ candle not completed
        attempts = 0
        tries = 5

        try: 
            while attempts < tries:
                candles = self.api.get_candles_df(self.trade_settings.pair,
                                                  granularity = self.granularity,
                                                  count = 50)
                
                if candles.shape[0] == 0:
                    self.log_message(f"No candles returned for {self.trade_settings.pair} at {expected_time}", error=True)
                    # print("NO CANDLES")
                elif candles.iloc[-1].time != expected_time: 
                    # print("NO NEW CANDLE")
                    time.sleep(0.5)
                else:
                    self.place_trade_work(candles)
                    break
                attempts += 1                
        except Exception as error:
            self.log_message(f"Exception: {error}", error=True)

    def run(self):
        while True:
            candle_time: dt.datetime = self.candle_work.get()
            print(f"CandleWorker new candle: {candle_time} {self.trade_settings.pair}")
            self.run_analysis(candle_time)