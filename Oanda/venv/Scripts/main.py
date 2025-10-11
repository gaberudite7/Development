from api.oanda_api import OandaApi
from infrastructure.instrument_collection import instrumentCollection


if __name__ == "__main__":
    api = OandaApi()

    #data = api.get_account_instruments()
    #[print(x['name']) for x in data]

    # data = api.get_account_summary()
    # print(data)

    instrumentCollection.CreateFile(api.get_account_instruments(), r"C:\Development\Oanda\Data")

    instrumentCollection.LoadInstruments(r"C:\Development\Oanda\Data")
    instrumentCollection.PrintInstruments()