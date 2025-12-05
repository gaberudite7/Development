from bot.bot import Bot
from infrastructure.instrument_collection import instrumentCollection

if __name__ == "__main__":
    
    instrumentCollection.LoadInstruments(r"C:\Development\Oanda\Data")    
    b = Bot()
    b.run()