# db.py — работа с PostgreSQL через psycopg2
from datetime import datetime
import psycopg2
from psycopg2 import sql
from config import DB_CONFIG


class Database:
    # Класс отвечает за базу данных
    def __init__(self):
        self.conn = None
        self.available = False
        self.connect()

    def connect(self):
        # Подключаемся к PostgreSQL
        # Если база не включена, игра всё равно запустится без сохранения
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.conn.autocommit = True
            self.available = True
            self.create_tables()
        except Exception as error:
            print("Database is not available:", error)
            self.available = False

    def create_tables(self):
        # Создаем таблицы, если их еще нет
        query = """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query)

    def get_or_create_player(self, username):
        # Ищем игрока или создаем нового
        if not self.available:
            return None
        username = username.strip() or "Player"
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute("INSERT INTO players(username) VALUES(%s) RETURNING id", (username,))
            return cur.fetchone()[0]

    def save_result(self, username, score, level):
        # Сохраняем результат после Game Over
        if not self.available:
            return
        player_id = self.get_or_create_player(username)
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO game_sessions(player_id, score, level_reached) VALUES(%s, %s, %s)",
                (player_id, score, level),
            )

    def get_personal_best(self, username):
        # Берем лучший результат игрока
        if not self.available:
            return 0
        player_id = self.get_or_create_player(username)
        with self.conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s", (player_id,))
            return cur.fetchone()[0]

    def get_leaderboard(self):
        # Получаем топ-10 результатов
        if not self.available:
            return []
        query = """
        SELECT p.username, g.score, g.level_reached, g.played_at
        FROM game_sessions g
        JOIN players p ON p.id = g.player_id
        ORDER BY g.score DESC, g.level_reached DESC, g.played_at ASC
        LIMIT 10;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()