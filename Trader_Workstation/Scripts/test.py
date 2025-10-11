from ib_async import *

ib = IB()
# Make sure to specify host and port if different from defaults
ib.connect(host='127.0.0.1', port=7497, clientId=1)

print(ib.positions())

if ib.isConnected():
    print("Successfully connected to IB!")
else:
    print("Connection failed.")
