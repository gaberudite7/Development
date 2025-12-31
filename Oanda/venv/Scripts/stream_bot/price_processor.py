import copy
import threading
from queue import Queue
import datetime as dt

import pytz
from stream_example.stream_base import StreamBase
from stream_example.stream_worker import WorkProcessor
from models.live_api_price import LiveApiPrice

GRANULARITIES = {
    "M1": 1, 
    "M5": 5, 
    "M15": 15,
    "M30": 30, 
    "H1": 60
}

class PriceProcessor(StreamBase):

    def __init__(self, shared_prices, price_lock:threading.Lock, price_events, 
                 candle_queue: Queue,
                 logname, pair, granularity):
        super().__init__(shared_prices, price_lock, price_events, logname)
        self.pair = pair
        self.candle_queue = candle_queue
        self.granularity = GRANULARITIES[granularity]

        now = dt.datetime.now(pytz.timezone("UTC"))
        self.set_last_candle(now)
        #print(f" PriceProcessor: {self.set_last_complete_candle_time} {now}")

    def set_last_candle(self, price_time: dt.datetime):
        self.set_last_complete_candle_time = self.round_time_down(price_time - dt.timedelta(minutes=self.granularity)) # will need to correct if using seconds/hours


    # subtract current time from remainder to get expected actual approximate candle time
    # If current time is 10:21:15 subtract 1 minute (for M1 candles) to go to 10:20:15 then round down to 10:20:00
    def round_time_down(self, round_me: dt.datetime) -> dt.datetime:
        remainder = round_me.minute % self.granularity
        candle_time = dt.datetime(round_me.year, 
                                  round_me.month, 
                                  round_me.day,
                                  round_me.hour,
                                  round_me.minute - remainder,
                                  tzinfo=pytz.timezone("UTC"))
        return candle_time


    def detect_new_candle(self, price: LiveApiPrice):
        old = self.set_last_complete_candle_time
        self.set_last_candle(price.time)

        if old < self.set_last_complete_candle_time:
            msg = f"----->>>{self.pair} New Candle : {self.set_last_complete_candle_time} {price.time}" 
            print(msg)
            self.candle_queue.put(self.set_last_complete_candle_time)

    def process_price(self):

        try:
            self.price_lock.acquire()
            price = copy.deepcopy(self.shared_prices[self.pair])
            # print("PriceProcessor:", price)
            if price is not None:
                self.detect_new_candle(price)
        except Exception as error:
            self.log_message(F"CRASH: {error}", error=True)
        finally:
            self.price_lock.release()

    def run(self):
        while True:
            self.price_events[self.pair].wait()
            self.process_price()
            self.price_events[self.pair].clear()