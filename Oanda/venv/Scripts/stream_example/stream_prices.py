import json
import requests
import threading
import pandas as pd
import time
from timeit import default_timer as timer
from models.live_api_price import LiveApiPrice
from infrastructure.log_wrapper import LogWrapper
from stream_example.stream_base import StreamBase
import constants.defs as defs

STREAM_URL = "https://stream-fxpractice.oanda.com/v3/"

class PriceStreamer(StreamBase):

    LOG_FREQ = 20

    def __init__(self, shared_prices, price_lock: threading.Lock, price_events):
        super().__init__(shared_prices, price_lock, price_events, logname="PriceStreamer")
        self.pairs_list = shared_prices.keys()
        print(self.pairs_list)
    
    def fire_new_price_event(self, instrument):
        if self.price_events[instrument].is_set() == False:
            self.price_events[instrument].set()

    def update_live_price(self, live_price: LiveApiPrice):
        try: 
            self.price_lock.acquire()
            self.shared_prices[live_price.instrument] = live_price
            self.fire_new_price_event(live_price.instrument)
        except Exception as error:
            self.log_message(f"Exception, {error}", error=True)
        finally:
            self.price_lock.release()
    
    def log_data(self):
        self.log_message("")
        self.log_message(f"\n{pd.DataFrame.from_dict([v.get_dict() for _, v in self.shared_prices.items()])}")

    def run(self):

        start = timer() - PriceStreamer.LOG_FREQ + 10

        params = dict(instruments=",".join(self.pairs_list))
        url = f"{STREAM_URL}/accounts/{defs.ACCOUNT_ID}/pricing/stream"
        try:
            with requests.get(url, params=params, headers=defs.SECURE_HEADER, stream=True, timeout=60) as resp:
                for raw_line in resp.iter_lines():

                    if not raw_line:
                        continue  # skip empty lines

                    try:
                        line = raw_line.decode("utf-8")
                        decoded = json.loads(line)
                    except Exception as e:
                        print("Streaming parse error:", raw_line, e)
                        continue

                    if decoded.get("type") == "HEARTBEAT":
                        # print("♥ heartbeat")
                        continue

                    if decoded.get("type") == "PRICE":
                        home_conversions = decoded.get("homeConversions", {})
                        price = LiveApiPrice(decoded, home_conversions).get_dict()
                        self.update_live_price(LiveApiPrice(decoded, home_conversions))
                        # logs based on log_frequency
                        if timer() - start > PriceStreamer.LOG_FREQ:                        
                            print(price)
                            self.log_data()
                            start = timer()
        # Connection closed by server or network issue, attempt to reconnect
        except requests.exceptions.ChunkedEncodingError as e:
            self.log_message(f"ChunkedEncodingError: {e}, reconnecting in 5 seconds...", error=True)
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            self.log_message(f"RequestException: {e}, reconnecting in 10 seconds...", error=True)
            time.sleep(10)
        except Exception as e:
            self.log_message(f"Unexpected error: {e}, reconnecting in 10 seconds...", error=True)
            time.sleep(10)