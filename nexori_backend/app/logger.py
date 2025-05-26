# app/logger.py
import logging

logger = logging.getLogger("nexori")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Если требуется, можно добавить обработчик для записи в файл:
# file_handler = logging.FileHandler("nexori.log")
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
