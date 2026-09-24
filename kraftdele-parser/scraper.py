import requests
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(level=logging.INFO)

SITEMAP_URL = "https://kraftdele.info/1_pl_0_sitemap.xml"
PRODUCT_URL_PATTERN = re.compile(r'/[a-z0-9-]+/\d+-[a-z0-9-]+\.html$')


class KraftDeleScraper:
    def __init__(self):
        self.base_url = "https://kraftdele.info"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def get_product_links_from_sitemap(self, max_items: int = 10) -> list:
        """
        Отримує посилання на товари з Sitemap XML.
        Це найнадійніший метод - не залежить від JS-рендерингу.
        """
        links = []
        try:
            logging.info(f"Завантаження Sitemap: {SITEMAP_URL}")
            response = requests.get(SITEMAP_URL, headers=self.headers, timeout=30)
            response.raise_for_status()

            # Парсимо XML за допомогою lxml
            soup = BeautifulSoup(response.content, "xml")

            for url_tag in soup.find_all("url"):
                loc = url_tag.find("loc")
                if not loc:
                    continue
                href = loc.get_text(strip=True)

                # Беремо тільки URL товарів (формат: /category/123-name.html)
                if PRODUCT_URL_PATTERN.search(href):
                    links.append(href)
                    if len(links) >= max_items:
                        break

            logging.info(f"Знайдено {len(links)} товарів у Sitemap")
        except Exception as e:
            logging.error(f"Помилка читання Sitemap: {e}")
        return links

    def get_product_data_from_sitemap(self, max_items: int = 10) -> list:
        """
        Отримує ПОВНІ дані товарів прямо із Sitemap (URL + зображення + назва).
        Не потрібно завантажувати окремо кожну сторінку.
        """
        products = []
        try:
            logging.info(f"Завантаження Sitemap: {SITEMAP_URL}")
            response = requests.get(SITEMAP_URL, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "xml")

            for url_tag in soup.find_all("url"):
                loc = url_tag.find("loc")
                if not loc:
                    continue
                href = loc.get_text(strip=True)

                if not PRODUCT_URL_PATTERN.search(href):
                    continue

                # Витягуємо SKU з URL (числовий ID)
                url_match = re.search(r'/(\d+)-', href.split("/")[-1])
                sku = url_match.group(1) if url_match else href.split("/")[-1]

                # Зображення з Sitemap image:loc
                images = []
                for img_loc in url_tag.find_all("image:loc"):
                    images.append(img_loc.get_text(strip=True))

                # Назва з image:title
                title_tag = url_tag.find("image:title")
                title = title_tag.get_text(strip=True) if title_tag else f"Kraft&Dele {sku}"

                # Додатковий опис/характеристики з image:caption
                caption_tag = url_tag.find("image:caption")
                caption = caption_tag.get_text(strip=True) if caption_tag else ""

                products.append({
                    "sku": sku,
                    "title_pl": title,
                    "description_html_pl": f"<p>{caption}</p>" if caption else "",
                    "images": images,
                    "params_pl": {},
                    "url": href
                })

                if len(products) >= max_items:
                    break

            logging.info(f"Отримано {len(products)} товарів з Sitemap")
        except Exception as e:
            logging.error(f"Помилка парсингу Sitemap: {e}")
        return products

    def parse_product(self, url: str) -> dict:
        """Парсить дані з окремої сторінки товару (запасний метод)"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            url_match = re.search(r'/(\d+)-', url.split("/")[-1])
            sku = url_match.group(1) if url_match else url.split("/")[-1]

            title_elem = soup.select_one("h1[itemprop='name'], h1.product-title, h1")
            title = title_elem.get_text(strip=True) if title_elem else "Kraft&Dele Product"

            images = []
            for img in soup.select(".product-images img, .product-cover img, #bigpic"):
                src = img.get("src") or img.get("data-image")
                if src and src not in images:
                    images.append(src if src.startswith("http") else f"{self.base_url}{src}")

            desc_elem = soup.select_one("#description, .product-description, #tab-description")
            description_html = str(desc_elem) if desc_elem else ""

            params = {}
            for row in soup.select(".data-sheet tr, .table-data-sheet tr"):
                cols = row.select("td, th")
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    if key and value:
                        params[key] = value

            return {
                "sku": sku,
                "title_pl": title,
                "description_html_pl": description_html,
                "images": images,
                "params_pl": params,
                "url": url
            }

        except Exception as e:
            logging.error(f"Помилка парсингу {url}: {e}")
            return None
