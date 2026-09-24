import xml.etree.ElementTree as ET
from xml.dom import minidom

class YmlGenerator:
    def __init__(self, shop_name="Kraft&Dele Store"):
        self.root = ET.Element("yml_catalog", date="2026-03-30 12:00")
        self.shop = ET.SubElement(self.root, "shop")
        ET.SubElement(self.shop, "name").text = shop_name
        
        # Додаємо категорії (за замовчуванням)
        categories = ET.SubElement(self.shop, "categories")
        cat = ET.SubElement(categories, "category", id="1")
        cat.text = "Інструменти Kraft&Dele"
        
        self.offers = ET.SubElement(self.shop, "offers")

    def add_product(self, product_data: dict):
        """Формує оффер у форматі YML Prom.ua"""
        offer = ET.SubElement(self.offers, "offer", id=product_data["sku"], available="true")
        
        # Основні поля
        ET.SubElement(offer, "name").text = f"{product_data['title_uk']} (Kraft&Dele)"
        ET.SubElement(offer, "vendor").text = "Kraft&Dele"
        ET.SubElement(offer, "vendorCode").text = product_data["sku"]
        ET.SubElement(offer, "categoryId").text = "1"
        
        # Ціна і валюта (заглушка або нуль для контент-файлу)
        ET.SubElement(offer, "price").text = "0"
        ET.SubElement(offer, "currencyId").text = "UAH"
        
        # Фотографії
        for img_url in product_data.get("images", []):
            ET.SubElement(offer, "picture").text = img_url
            
        # Опис HTML
        ET.SubElement(offer, "description").text = f"<![CDATA[{product_data.get('description_uk', '')}]]>"
        
        # Характеристики Prom.ua <param name="...">
        for param_name, param_value in product_data.get("params_uk", {}).items():
            param_elem = ET.SubElement(offer, "param", name=param_name)
            param_elem.text = param_value

    def save_to_file(self, filename="prom_feed.xml"):
        """Зберігає красивий XML-файл з форматуванням"""
        xml_str = ET.tostring(self.root, encoding="utf-8")
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="  ", encoding="utf-8")
        
        with open(filename, "wb") as f:
            f.write(pretty_xml)
