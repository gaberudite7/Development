from my_fx_book import run_sentiment_scrape
from bloomberg_com import run_bloomberg_com

#run_sentiment_scrape()

data = run_bloomberg_com()

[print(x) for x in data]