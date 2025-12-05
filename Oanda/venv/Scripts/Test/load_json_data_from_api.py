import requests
import pandas as pd
import json

API_KEY = "7f091d472fff565970e1a3608cb77fc4-afefbf8c0474bc102685de26ce6ec6d1"
ACCOUNT_ID = "101-001-37195846-001"
OANDA_URL = "https://api-fxpractice.oanda.com/v3"

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {API_KEY}",
     "Content-Type": "application/json"    
})

params = dict(
    count = 4000, 
    granularity = "H1", 
    price = "MBA"
)

# url = f"{OANDA_URL}/instruments/EUR_USD/candles"
url = f"{OANDA_URL}/accounts/{ACCOUNT_ID}/instruments"

# response = session.get(url, params=params, data = None, headers =None)

response = session.get(url, params=params, data = None, headers =None)

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

print(instruments_dict)

with open(r"C:\Development\Oanda\Data\instruments.json", "w") as f:
    f.write(json.dumps(instruments_dict, indent =2))