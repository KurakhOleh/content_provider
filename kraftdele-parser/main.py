import logging
from scraper import run_scraper
from translator import run_translator
from yml_generator import generate_yml

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Початок роботи парсера...")
    
    # 1. Збір даних
    data = run_scraper()
    
    # 2. Переклад та заміна
    translated_data = run_translator(data)
    
    # 3. Генерація YML/XML
    generate_yml(translated_data)
    
    logger.info("Роботу завершено успішно.")

if __name__ == "__main__":
    main()
