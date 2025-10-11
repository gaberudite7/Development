import requests
import pandas as pd
import json
from dateutil import parser

API_KEY = "7f091d472fff565970e1a3608cb77fc4-afefbf8c0474bc102685de26ce6ec6d1"
ACCOUNT_ID = "101-001-37195846-001"
OANDA_URL = "https://api-fxpractice.oanda.com/v3"

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {API_KEY}",
     "Content-Type": "application/json"    
})

def fetch_instruments(url):
    response = session.get(url, params=None, data = None, headers =None)

    data = response.json()
    #print(data)

    # List of instruments
    instruments_list = data['instruments']
    #print(instruments_list[0].keys())

    key_i = ['name', 'type', 'displayName', 'pipLocation', 'displayPrecision', 'tradeUnitsPrecision', 'minimumTradeSize', 'maximumTrailingStopDistance', 'minimumTrailingStopDistance', 'maximumPositionSize', 'maximumOrderUnits', 'marginRate', 'guaranteedStopLossOrderMode', 'tags', 'financing']

    instruments_dict = {}

    for i in instruments_list:
        key = i['name']
        instruments_dict[key] = {k: i[k] for k in key_i}

    return instruments_dict


def fetch_candles(pair_name, count=10, granularity="H1"): # pair EURUSD, count number of candles, granularity is hours 1
    url = f"{OANDA_URL}/instruments/{pair_name}/candles"
    params = dict(
        count = 10, 
        granularity = "H1", 
        price = "MBA"
        )

    response = session.get(url, params=params, data = None, headers =None)
    data = response.json()

    if response.status_code == 200:
        if 'candles' not in data:
            data = []
        else:
            data = data['candles']
    return response.status_code, data

def get_candles_df(data):
    if len(data) == 0:
        return pd.DataFrame()

    # loop through prices and make a key
    prices = ['mid', 'bid', 'ask']
    ohlc = ['o', 'h', 'l', 'c']

    final_data = []
    for candle in data:
        new_dict = {}
        new_dict['time'] = parser.parse(candle['time'])
        new_dict['volume'] = candle['volume']
        for p in prices:
            for o in ohlc:
                new_dict[f"{p}_{o}"] = float(candle[p][o])
        final_data.append(new_dict)

    df = pd.DataFrame.from_dict(final_data)
    return df

def create_data_file(pair_name, count=10, granularity="H1"):
    code, data = fetch_candles(pair_name, count, granularity)
    if code != 200:
        print("Failed", pair_name, data)
        return
    if len(data) == 0:
        print("No candles", pair_name)
    candles_df = get_candles_df(data)
    candles_df.to_pickle(fr"C:\Development\Oanda\Data\{pair_name}_{granularity}.pkl")
    print(f"{pair_name} {granularity} {candles_df.shape[0]} candles, {candles_df.time.min()} {candles_df.time.max()}")

# code, data = fetch_candles("EUR_USD", count = 10, granularity="H4")
# candles_df = get_candles_df(data)
create_data_file("EUR_USD", count = 10, granularity="H4")

our_curr = ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'NZD', 'CAD', 'AUD']

instruments_dict = fetch_instruments(url=f"{OANDA_URL}/accounts/{ACCOUNT_ID}/instruments")

for p1 in our_curr:
    for p2 in our_curr:
        pr = f"{p1}_{p2}"
        if pr in instruments_dict:
            for g in ["H1", "H4"]:
                create_data_file(pr, count = 4001, granularity="H4")