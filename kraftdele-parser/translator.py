from deep_translator import MyMemoryTranslator
import time
import re
import logging

logger = logging.getLogger(__name__)

# Словник корекції польських термінів -> українські
TERM_DICTIONARY = {
    "agregat": "генератор",
    "sprężarka": "компресор",
    "spawarka": "зварювальний апарат",
    "klucz udarowy": "ударний гайковерт",
    "podnośnik": "домкрат",
    "kompresor": "компресор",
    "wiertarka": "дриль",
    "szlifierka": "шліфувальна машина",
    "wyrzynarka": "лобзик",
    "zgrzewarka": "зварювальний апарат",
    "nagrzewnica": "теплогенератор",
    "kosiarki": "газонокосарка",
    "myjka": "мийка",
}

# Рекламні слова для видалення з назви
STOP_WORDS = ["HIT", "PROMO", "TANI", "WYPRZEDAŻ", "OKAZJA"]

# Затримка між запитами (секунди) - щоб не перевищити ліміт Google
TRANSLATE_DELAY = 0.5


class ContentTranslator:
    def __init__(self):
        self.translator = MyMemoryTranslator(source='pl-PL', target='uk-UA')

    def clean_title(self, text: str) -> str:
        """Очищує назву від рекламних слів"""
        for word in STOP_WORDS:
            text = re.sub(rf'\b{word}\b', '', text, flags=re.IGNORECASE)
        return text.strip()

    def apply_dictionary(self, text: str) -> str:
        """Замінює польські терміни на Ukrainian перед відправкою в перекладач"""
        cleaned = self.clean_title(text)
        for pl_term, uk_term in TERM_DICTIONARY.items():
            cleaned = re.sub(rf'\b{pl_term}\b', uk_term, cleaned, flags=re.IGNORECASE)
        return cleaned

    def translate_text(self, text: str) -> str:
        """Перекладає один текст з повторними спробами при помилці"""
        if not text or not text.strip():
            return ""

        preprocessed = self.apply_dictionary(text)

        for attempt in range(3):
            try:
                time.sleep(TRANSLATE_DELAY)
                result = self.translator.translate(preprocessed)
                return result if result else preprocessed
            except Exception as e:
                logger.warning(f"Спроба {attempt + 1}/3 невдала: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s

        logger.error(f"Не вдалося перекласти текст: {preprocessed[:50]}...")
        return preprocessed  # Повертаємо оригінал якщо переклад не вдався

    def translate_params(self, params_pl: dict) -> dict:
        """Пакетний переклад технічних характеристик"""
        if not params_pl:
            return {}

        translated_params = {}
        for key, value in params_pl.items():
            uk_key = self.translate_text(key)
            uk_val = self.translate_text(value)
            translated_params[uk_key] = uk_val
        return translated_params
