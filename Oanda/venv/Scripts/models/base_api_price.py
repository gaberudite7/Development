class BaseApiPrice:

    def __init__(self, api_ob, homeConversions):
        
        # test for homeconversions
        if homeConversions is None:
            raise ValueError("BaseAPiPrice requires homeConversions")
        
        self.instrument = api_ob['instrument']
        self.ask = float(api_ob['asks'][0]['price'])
        self.bids = float(api_ob['bids'][0]['price'])
        self.home_Conversions = homeConversions