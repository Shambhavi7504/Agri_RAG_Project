# modules/dynamic_scraper.py
import requests
from bs4 import BeautifulSoup

def get_latest_wheat_price():
    url = "https://agmarknet.gov.in/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Dummy logic – replace with actual table scraping
    return "Latest wheat price: ₹2,150/quintal in Delhi Mandi."

def handle_dynamic_query(query: str):
    if "price" in query.lower():
        return get_latest_wheat_price()
    return "Sorry, I can't fetch that dynamic info yet."
