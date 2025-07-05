import requests
from bs4 import BeautifulSoup
import re

class BookScraper:
    BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

    def __init__(self):
        self.books = []

    def extract_rating(self, star_class):
        star_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        for star_name, value in star_map.items():
            if star_name in star_class:
                return value
        return 0

    def scrape_books(self, pages=50):
        for page in range(1, pages + 1):
            url = self.BASE_URL.format(page)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article", class_="product_pod")

            for article in articles:
                title = article.h3.a["title"]
                price = re.sub(r"[^\d.]", "", article.find("p", class_="price_color").text)
                rating = self.extract_rating(" ".join(article.p["class"]))
                availability = article.find("p", class_="instock availability").text.strip()

                self.books.append({
                    "Titre": title,
                    "Prix (£)": float(price),
                    "Disponibilité": availability,
                    "Note (étoiles)": rating
                })

        return self.books
