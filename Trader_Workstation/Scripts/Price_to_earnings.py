from ib_async import *
import pandas as pd
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import yfinance as yf

'''=================================================='''
'''Load SP500 tickers'''
'''=================================================='''

# Load local HTML file
with open(r'C:\Development\Trader_Workstation\Scripts\SP500.html', 'r', encoding='utf-8') as f:
    html = f.read()
# Parse HTML using BeautifulSoup
soup = BeautifulSoup(html, 'lxml')

# Find the table (Wikipedia uses class "wikitable sortable")
table = soup.find('table', {'class': 'wikitable'})

# Parse table rows
rows = table.find_all('tr')

# Extract headers
headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]

# Extract data
data = []
for row in rows[1:]:
    cols = [td.get_text(strip=True) for td in row.find_all('td')]
    if cols:
        data.append(cols)

# Create DataFrame
df = pd.DataFrame(data, columns=headers)

tickers = df['Symbol'].to_list()
print(tickers)

'''=================================================='''
'''Filter lowest P/E Ratios based on SP500 tickers'''
'''=================================================='''

results = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        pe = stock.info.get("trailingPE", None)
        
        if pe is not None:
            print(f"{ticker}: P/E = {pe}")
            if pe < 10:
                results.append((ticker, pe))
        else:
            print(f"{ticker}: No P/E data available.")
        
        time.sleep(0.5)  # Be nice to Yahoo's servers

    except Exception as e:
        print(f"⚠️ Error with {ticker}: {e}")

# Save filtered stocks with P/E < 15
pe_df = pd.DataFrame(results, columns=["Symbol", "PE_Ratio"])
pe_df.to_csv(r"C:\Development\Trader_Workstation\Files\low_pe_sp500.csv", index=False)

print("\n✅ Saved results to low_pe_sp500.csv")