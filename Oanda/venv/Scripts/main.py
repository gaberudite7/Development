# ...existing code...
import sys;
import os

# Ensure project root (two levels up from venv\Scripts) is on sys.path so
# imports like `api.oanda_api` and `infrastructure.*` resolve when running
# this script from the venv\Scripts folder.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from api.oanda_api import OandaApi
from infrastructure.instrument_collection import instrumentCollection
from simulation.ma_cross import run_ma_sim
from dateutil import parser
from infrastructure.collect_data import run_collection
from api.stream_prices import stream_prices


if __name__ == "__main__":
    api = OandaApi()
    # instrumentCollection = InstrumentCollection()
    instrumentCollection.LoadInstruments(r"C:\Development\Oanda\Data")
    # run_collection(instrumentCollection, api)
    #run_ma_sim()
    stream_prices(['GBP_JPY', 'AUD_NZD'])