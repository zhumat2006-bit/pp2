from db import Database
from game import SnakeGame


if __name__ == "__main__":
    # Создаем базу и запускаем игру
    db = Database()
    game = SnakeGame(db)
    game.run()