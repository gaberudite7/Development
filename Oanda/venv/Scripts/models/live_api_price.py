from dateutil import parser
from models.base_api_price import BaseApiPrice


class LiveApiPrice(BaseApiPrice):
    
    def __init__(self, api_ob, homeConversions):
        super().__init__(api_ob, homeConversions)
        self.time = parser.parse(api_ob['time'])
    
    def __repr__(self):
        return f"LiveApiPrice() {self.instrument}, {self.ask}, {self.bids} {self.time}"
    
    def get_dict(self):
        return dict(instrument=self.instrument, 
                    ask=self.ask, 
                    bid=self.bids, 
                    time=self.time
        )