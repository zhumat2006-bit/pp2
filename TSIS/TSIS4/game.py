# game.py — основная логика Snake Game
import json
import os
import random
import pygame

from config import (
    WIDTH, HEIGHT, CELL_SIZE, FPS, TOP_PANEL, COLS, ROWS,
    BASE_SPEED, LEVEL_UP_EVERY, OBSTACLES_PER_LEVEL,
    IMAGE_DIR, SETTINGS_FILE, IMAGE_FILES
)


class Button:
    # Класс кнопки для меню
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, screen, font):
        # Цвет меняется при наведении мышки
        mouse = pygame.mouse.get_pos()
        color = (80, 120, 170) if self.rect.collidepoint(mouse) else (55, 85, 125)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (220, 230, 240), self.rect, 2, border_radius=10)
        label = font.render(self.text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        # Проверяем клик по кнопке
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class SnakeGame:
    # Основной класс игры
    def __init__(self, db):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TSIS4 Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 44, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.db = db
        self.images = self.load_images()
        self.settings = self.load_settings()
        self.username = ""
        self.state = "menu"
        self.last_saved = False
        self.running = True
        self.reset_game()

    def load_images(self):
        # Загружаем PNG, если они есть в папке images
        images = {}
        for key, filename in IMAGE_FILES.items():
            path = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    images[key] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
                except Exception:
                    images[key] = None
            else:
                images[key] = None
        return images

    def load_settings(self):
        # Читаем настройки из JSON
        default = {"snake_color": [0, 200, 90], "grid": True, "sound": True}
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                default.update(data)
        except Exception:
            pass
        return default

    def save_settings(self):
        # Сохраняем настройки в JSON
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, indent=2)

    def grid_to_pixel(self, pos):
        # Перевод клетки поля в пиксели
        x, y = pos
        return x * CELL_SIZE, TOP_PANEL + y * CELL_SIZE

    def random_empty_cell(self):
        # Ищем свободную клетку, чтобы еда не появилась в змее или стене
        blocked = set(self.snake) | set(self.obstacles)
        if self.food:
            blocked.add(self.food["pos"])
        if self.poison:
            blocked.add(self.poison)
        if self.powerup:
            blocked.add(self.powerup["pos"])
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in blocked]
        return random.choice(free) if free else (1, 1)

    def reset_game(self):
        # Начальное состояние игры
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.speed = BASE_SPEED
        self.move_timer = 0
        self.food = None
        self.poison = None
        self.powerup = None
        self.active_power = None
        self.active_until = 0
        self.shield = False
        self.obstacles = []
        self.personal_best = 0
        self.last_saved = False
        self.spawn_food()

    def start_playing(self):
        # Начинаем новую игру
        self.reset_game()
        name = self.username.strip() or "Player"
        self.username = name
        self.personal_best = self.db.get_personal_best(name)
        self.state = "play"

    def spawn_food(self):
        # Еда имеет разные очки и исчезает по таймеру
        weights = [1, 2, 3]
        self.food = {
            "pos": self.random_empty_cell(),
            "points": random.choice(weights),
            "created": pygame.time.get_ticks(),
            "life": random.randint(5000, 9000),
        }

    def spawn_poison(self):
        # Иногда создаем ядовитую еду
        if self.poison is None and random.random() < 0.01:
            self.poison = self.random_empty_cell()

    def spawn_powerup(self):
        # На поле может быть только один power-up
        if self.powerup is None and random.random() < 0.008:
            self.powerup = {
                "pos": self.random_empty_cell(),
                "type": random.choice(["speed", "slow", "shield"]),
                "created": pygame.time.get_ticks(),
            }

    def create_obstacles(self):
        # Препятствия появляются с 3 уровня и не ставятся возле головы змеи
        if self.level < 3:
            self.obstacles = []
            return
        head = self.snake[0]
        safe_zone = {
            (head[0] + dx, head[1] + dy)
            for dx in range(-2, 3)
            for dy in range(-2, 3)
        }
        count = (self.level - 2) * OBSTACLES_PER_LEVEL
        self.obstacles = []
        tries = 0
        while len(self.obstacles) < count and tries < 500:
            tries += 1
            cell = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
            if cell not in self.snake and cell not in safe_zone and cell not in self.obstacles:
                self.obstacles.append(cell)

    def apply_powerup(self, power_type):
        # Включаем эффект power-up
        now = pygame.time.get_ticks()
        if power_type == "speed":
            self.active_power = "speed"
            self.active_until = now + 5000
        elif power_type == "slow":
            self.active_power = "slow"
            self.active_until = now + 5000
        elif power_type == "shield":
            self.shield = True

    def current_speed(self):
        # Временные эффекты меняют скорость на 5 секунд
        now = pygame.time.get_ticks()
        if self.active_power and now > self.active_until:
            self.active_power = None
        speed = self.speed
        if self.active_power == "speed":
            speed += 5
        elif self.active_power == "slow":
            speed = max(3, speed - 4)
        return speed

    def handle_collision(self, new_head):
        # Проверяем столкновения
        x, y = new_head
        hit_wall = x < 0 or x >= COLS or y < 0 or y >= ROWS
        hit_self = new_head in self.snake
        hit_obstacle = new_head in self.obstacles
        if hit_wall or hit_self or hit_obstacle:
            if self.shield and not hit_obstacle:
                # Shield спасает один раз от стены или тела
                self.shield = False
                if hit_wall:
                    new_head = (x % COLS, y % ROWS)
                return False, new_head
            return True, new_head
        return False, new_head

    def move_snake(self):
        # Двигаем змейку на одну клетку
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        game_over, new_head = self.handle_collision(new_head)
        if game_over:
            self.state = "game_over"
            return

        self.snake.insert(0, new_head)
        ate_food = self.food and new_head == self.food["pos"]
        ate_poison = self.poison and new_head == self.poison
        ate_power = self.powerup and new_head == self.powerup["pos"]

        if ate_food:
            # Еда дает очки и может повысить уровень
            self.score += self.food["points"] * 10
            self.food_eaten += 1
            if self.food_eaten % LEVEL_UP_EVERY == 0:
                self.level += 1
                self.speed += 1
                self.create_obstacles()
            self.spawn_food()
        else:
            self.snake.pop()

        if ate_poison:
            # Poison укорачивает змейку на 2 сегмента
            self.poison = None
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            if len(self.snake) <= 1:
                self.state = "game_over"

        if ate_power:
            self.apply_powerup(self.powerup["type"])
            self.powerup = None

    def update_game(self):
        # Обновляем таймеры и движение
        now = pygame.time.get_ticks()
        if self.food and now - self.food["created"] > self.food["life"]:
            self.spawn_food()
        if self.powerup and now - self.powerup["created"] > 8000:
            self.powerup = None

        self.spawn_poison()
        self.spawn_powerup()

        delay = 1000 // self.current_speed()
        if now - self.move_timer > delay:
            self.move_timer = now
            self.move_snake()

    def draw_cell(self, pos, color, image_key=None):
        # Рисуем PNG или обычный квадрат
        px, py = self.grid_to_pixel(pos)
        rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
        img = self.images.get(image_key) if image_key else None
        if img:
            self.screen.blit(img, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=5)

    def draw_grid(self):
        # Рисуем сетку, если она включена
        if not self.settings.get("grid", True):
            return
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (35, 40, 45), (x, TOP_PANEL), (x, HEIGHT))
        for y in range(TOP_PANEL, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (35, 40, 45), (0, y), (WIDTH, y))

    def draw_play(self):
        # Рисуем игровой экран
        self.screen.fill((18, 22, 28))
        bg = self.images.get("background")
        if bg:
            self.screen.blit(pygame.transform.scale(bg, (WIDTH, HEIGHT - TOP_PANEL)), (0, TOP_PANEL))
        pygame.draw.rect(self.screen, (28, 35, 45), (0, 0, WIDTH, TOP_PANEL))
        info = f"User: {self.username}   Score: {self.score}   Level: {self.level}   Best: {self.personal_best}"
        self.screen.blit(self.font.render(info, True, (240, 240, 240)), (20, 18))
        if self.shield:
            self.screen.blit(self.font.render("Shield ON", True, (120, 200, 255)), (650, 18))

        self.draw_grid()
        for obstacle in self.obstacles:
            self.draw_cell(obstacle, (90, 90, 90), "obstacle")
        if self.food:
            self.draw_cell(self.food["pos"], (230, 70, 70), "food")
        if self.poison:
            self.draw_cell(self.poison, (100, 0, 0), "poison")
        if self.powerup:
            colors = {"speed": (255, 200, 60), "slow": (80, 180, 255), "shield": (150, 100, 255)}
            self.draw_cell(self.powerup["pos"], colors[self.powerup["type"]], self.powerup["type"])

        snake_color = tuple(self.settings.get("snake_color", [0, 200, 90]))
        for i, segment in enumerate(self.snake):
            key = "snake_head" if i == 0 else "snake_body"
            color = (40, 255, 120) if i == 0 else snake_color
            self.draw_cell(segment, color, key)

    def draw_menu(self):
        # Рисуем главное меню
        self.screen.fill((18, 22, 28))
        title = self.big_font.render("TSIS4 Snake Game", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))
        label = self.font.render("Enter username:", True, (230, 230, 230))
        self.screen.blit(label, (270, 140))
        input_rect = pygame.Rect(250, 175, 300, 45)
        pygame.draw.rect(self.screen, (35, 45, 60), input_rect, border_radius=8)
        pygame.draw.rect(self.screen, (220, 230, 240), input_rect, 2, border_radius=8)
        username_text = self.font.render(self.username or "Player", True, (255, 255, 255))
        self.screen.blit(username_text, (input_rect.x + 12, input_rect.y + 10))

        self.menu_buttons = [
            Button((300, 250, 200, 45), "Play"),
            Button((300, 310, 200, 45), "Leaderboard"),
            Button((300, 370, 200, 45), "Settings"),
            Button((300, 430, 200, 45), "Quit"),
        ]
        for button in self.menu_buttons:
            button.draw(self.screen, self.font)

    def draw_leaderboard(self):
        # Рисуем таблицу лидеров
        self.screen.fill((18, 22, 28))
        title = self.big_font.render("Leaderboard", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))
        rows = self.db.get_leaderboard()
        headers = ["#", "Username", "Score", "Level", "Date"]
        xs = [80, 140, 360, 470, 570]
        for x, h in zip(xs, headers):
            self.screen.blit(self.font.render(h, True, (200, 220, 255)), (x, 120))
        if not rows:
            text = "No database data. Check PostgreSQL connection."
            self.screen.blit(self.font.render(text, True, (255, 180, 180)), (180, 220))
        for i, row in enumerate(rows, start=1):
            username, score, level, played_at = row
            date_text = played_at.strftime("%Y-%m-%d") if hasattr(played_at, "strftime") else str(played_at)
            values = [str(i), username, str(score), str(level), date_text]
            for x, value in zip(xs, values):
                self.screen.blit(self.small_font.render(value, True, (240, 240, 240)), (x, 155 + i * 32))
        self.back_button = Button((300, 520, 200, 45), "Back")
        self.back_button.draw(self.screen, self.font)

    def draw_settings(self):
        # Рисуем экран настроек
        self.screen.fill((18, 22, 28))
        title = self.big_font.render("Settings", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))
        grid_text = f"Grid: {'ON' if self.settings['grid'] else 'OFF'}"
        sound_text = f"Sound: {'ON' if self.settings['sound'] else 'OFF'}"
        color_text = f"Snake color: {self.settings['snake_color']}"
        self.settings_buttons = [
            Button((260, 160, 280, 45), grid_text),
            Button((260, 225, 280, 45), sound_text),
            Button((260, 290, 280, 45), color_text),
            Button((260, 390, 280, 45), "Save & Back"),
        ]
        hint = self.small_font.render("Color button switches between green, blue, yellow, pink", True, (200, 200, 200))
        self.screen.blit(hint, (220, 350))
        for button in self.settings_buttons:
            button.draw(self.screen, self.font)

    def draw_game_over(self):
        # Сохраняем результат после проигрыша
        if not self.last_saved:
            self.db.save_result(self.username, self.score, self.level)
            self.personal_best = max(self.personal_best, self.score)
            self.last_saved = True
        self.screen.fill((18, 22, 28))
        title = self.big_font.render("Game Over", True, (255, 100, 100))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 110)))
        lines = [
            f"Final score: {self.score}",
            f"Level reached: {self.level}",
            f"Personal best: {self.personal_best}",
        ]
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (240, 240, 240))
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, 190 + i * 45)))
        self.over_buttons = [
            Button((300, 360, 200, 45), "Retry"),
            Button((300, 425, 200, 45), "Main Menu"),
        ]
        for button in self.over_buttons:
            button.draw(self.screen, self.font)

    def handle_menu_event(self, event):
        # Обрабатываем имя и кнопки меню
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN:
                self.start_playing()
            elif len(self.username) < 20 and event.unicode.isprintable():
                self.username += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in getattr(self, "menu_buttons", []):
                if button.clicked(event):
                    if button.text == "Play":
                        self.start_playing()
                    elif button.text == "Leaderboard":
                        self.state = "leaderboard"
                    elif button.text == "Settings":
                        self.state = "settings"
                    elif button.text == "Quit":
                        self.running = False

    def handle_play_event(self, event):
        # Управление змейкой
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
                self.next_direction = (0, -1)
            elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
                self.next_direction = (0, 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
                self.next_direction = (-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
                self.next_direction = (1, 0)
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"

    def handle_settings_event(self, event):
        # Обрабатываем кнопки настроек
        if event.type == pygame.MOUSEBUTTONDOWN:
            buttons = getattr(self, "settings_buttons", [])
            if len(buttons) < 4:
                return
            if buttons[0].clicked(event):
                self.settings["grid"] = not self.settings["grid"]
            elif buttons[1].clicked(event):
                self.settings["sound"] = not self.settings["sound"]
            elif buttons[2].clicked(event):
                colors = [[0, 200, 90], [70, 160, 255], [240, 220, 60], [240, 90, 170]]
                current = self.settings["snake_color"]
                index = (colors.index(current) + 1) % len(colors) if current in colors else 0
                self.settings["snake_color"] = colors[index]
            elif buttons[3].clicked(event):
                self.save_settings()
                self.state = "menu"

    def handle_game_over_event(self, event):
        # Кнопки Retry и Main Menu
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in getattr(self, "over_buttons", []):
                if button.clicked(event):
                    if button.text == "Retry":
                        self.start_playing()
                    elif button.text == "Main Menu":
                        self.state = "menu"

    def run(self):
        # Главный цикл игры
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.state == "menu":
                    self.handle_menu_event(event)
                elif self.state == "play":
                    self.handle_play_event(event)
                elif self.state == "settings":
                    self.handle_settings_event(event)
                elif self.state == "leaderboard":
                    if event.type == pygame.MOUSEBUTTONDOWN and hasattr(self, "back_button") and self.back_button.clicked(event):
                        self.state = "menu"
                elif self.state == "game_over":
                    self.handle_game_over_event(event)

            if self.state == "play":
                self.update_game()
                self.draw_play()
            elif self.state == "menu":
                self.draw_menu()
            elif self.state == "leaderboard":
                self.draw_leaderboard()
            elif self.state == "settings":
                self.draw_settings()
            elif self.state == "game_over":
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()