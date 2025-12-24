from bs4 import BeautifulSoup
import cloudscraper

def get_soup_from_file(fn):
    
    file_path = fr"C:\Development\Oanda\venv\Scripts\Web_Scraping\Files\{fn}.html"
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()
    return BeautifulSoup(data, "html.parser")

def get_soup_from_url(url, verb="get", data=None, extra_headers=None):
    
    scraper = cloudscraper.create_scraper()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }

    if extra_headers:
        headers.update(extra_headers)

    if verb == 'get':
        response = scraper.get(url, data= data, headers=headers)

    elif verb == 'post':
        response = scraper.get(url, data= data, headers=headers)

    return BeautifulSoup(response.content, "html.parser")