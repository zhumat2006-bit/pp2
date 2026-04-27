# config.py — основные настройки игры
import os

# Размер окна и одной клетки поля
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
FPS = 60

# Поле начинается ниже панели со счетом
TOP_PANEL = 60
COLS = WIDTH // CELL_SIZE
ROWS = (HEIGHT - TOP_PANEL) // CELL_SIZE

# Скорость, уровни и количество препятствий
BASE_SPEED = 8
LEVEL_UP_EVERY = 5
OBSTACLES_PER_LEVEL = 4

# Пути к папке картинок и файлу настроек
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# Названия PNG, которые можно положить в папку images
IMAGE_FILES = {
    "food": "food.png",
    "poison": "poison.png",
    "speed": "speed.png",
    "slow": "slow.png",
    "shield": "shield.png",
    "snake_head": "snake_head.png",
    "snake_body": "snake_body.png",
    "obstacle": "obstacle.png",
    "background": "background.png"
}

# Данные PostgreSQL. Измени под свой компьютер.
DB_CONFIG = {
    "host": "localhost",
    "database": "snake_db",
    "user": "zhumat",
    "password": "",
    "port": 5432,
}