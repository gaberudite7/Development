import threading
from queue import Queue
from infrastructure.log_wrapper import LogWrapper
from models.trade_decision import TradeDecision
from bot.trade_manager import place_trade
from api.oanda_api import OandaApi

class TradeWorker(threading.Thread):

    def __init__(self, trade_work_queue: Queue, trade_risk: float):
        super().__init__()
        self.trade_work_queue = trade_work_queue
        self.trade_risk = trade_risk
        self.api = OandaApi()
        self.log = LogWrapper("TradeWorker")
    
    def log_message(self, msg, error=False):
        if error:
            self.log.logger.error(msg)
        else:
            self.log.logger.info(msg)
    
    def do_work(self, work: TradeDecision):
        try:
            place_trade(
                work, 
                self.api, 
                self.log_message, 
                self.log_message, 
                self.trade_risk
            )
        except Exception as error:
            self.log_message(f"Exception in do_work: {error}", error=True)

    def run(self):
        while True:
            work: TradeDecision = self.trade_work_queue.get()
            self.log_message(f"Received trade work: {work}")
            print("TradeWorker.py received trade work:", work)
            self.do_work(work)