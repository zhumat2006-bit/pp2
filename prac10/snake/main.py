import pygame
import random
import sys

pygame.init()

CELL  = 20          # размер одной клетки
COLS  = 30          # количество колонок
ROWS  = 25          # количество строк
WIDTH  = COLS * CELL
HEIGHT = ROWS * CELL + 50  # +50 для панели счёта

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# ЦВЕТ
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
GREEN      = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED        = (220, 0, 0)
YELLOW     = (255, 215, 0)
BLUE       = (50, 50, 200)

font = pygame.font.SysFont("Arial", 22, bold=True)

# УРОВНИ
# food_to_next — сколько еды нужно для следующего уровня
LEVELS = [
    {"speed": 6,  "food_to_next": 3},
    {"speed": 9,  "food_to_next": 3},
    {"speed": 12, "food_to_next": 4},
    {"speed": 16, "food_to_next": 4},
    {"speed": 20, "food_to_next": 999},  # последний уровень
]

def random_food(snake):
    """Генерирует еду случайно, не на змейке и не на стене"""
    while True:
        x = random.randint(1, COLS - 2)  # отступ от стен
        y = random.randint(1, ROWS - 2)
        pos = (x, y)
        if pos not in snake:
            return pos

def draw_grid(screen):
    """Рисует сетку"""
    for x in range(0, COLS * CELL, CELL):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, ROWS * CELL))
    for y in range(0, ROWS * CELL, CELL):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (COLS * CELL, y))

def draw_walls(screen):
    """Рисует стены по краям"""
    wall_color = (100, 70, 40)
    pygame.draw.rect(screen, wall_color, (0, 0, WIDTH, CELL))               # верх
    pygame.draw.rect(screen, wall_color, (0, (ROWS-1)*CELL, WIDTH, CELL))   # низ
    pygame.draw.rect(screen, wall_color, (0, 0, CELL, ROWS*CELL))           # лево
    pygame.draw.rect(screen, wall_color, ((COLS-1)*CELL, 0, CELL, ROWS*CELL)) # право

def main():
    # Начальное состояние змейки
    snake = [(COLS//2, ROWS//2), (COLS//2 - 1, ROWS//2), (COLS//2 - 2, ROWS//2)]
    direction = (1, 0)   # движение вправо
    next_dir  = (1, 0)

    food = random_food(snake)

    score       = 0
    level_idx   = 0       # текущий уровень (индекс в LEVELS)
    food_eaten  = 0       # еда на текущем уровне

    running = True
    while running:
        clock.tick(LEVELS[level_idx]["speed"])

        # === СОБЫТИЯ ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP    and direction != (0, 1):
                    next_dir = (0, -1)
                elif event.key == pygame.K_DOWN  and direction != (0, -1):
                    next_dir = (0, 1)
                elif event.key == pygame.K_LEFT  and direction != (1, 0):
                    next_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_dir = (1, 0)

        direction = next_dir

        # === ДВИЖЕНИЕ ===
        head_x = snake[0][0] + direction[0]
        head_y = snake[0][1] + direction[1]
        new_head = (head_x, head_y)

        # === ПРОВЕРКА СТОЛКНОВЕНИЙ ===
        # Со стеной (граница)
        if head_x <= 0 or head_x >= COLS-1 or head_y <= 0 or head_y >= ROWS-1:
            game_over(screen, score, level_idx + 1)
            return

        # С собой
        if new_head in snake:
            game_over(screen, score, level_idx + 1)
            return

        snake.insert(0, new_head)

        # === ЕДА ===
        if new_head == food:
            score      += 10
            food_eaten += 1
            food = random_food(snake)  # новая еда

            # Проверка перехода на следующий уровень
            if food_eaten >= LEVELS[level_idx]["food_to_next"]:
                if level_idx < len(LEVELS) - 1:
                    level_idx  += 1
                    food_eaten  = 0
                    show_level_up(screen, level_idx + 1)
        else:
            snake.pop()  # убираем хвост если еда не съедена

        # === ОТРИСОВКА ===
        screen.fill((20, 20, 20))
        draw_grid(screen)
        draw_walls(screen)

        # Змейка
        for i, (sx, sy) in enumerate(snake):
            color = GREEN if i > 0 else DARK_GREEN  # голова темнее
            pygame.draw.rect(screen, color,
                             (sx * CELL + 1, sy * CELL + 1, CELL - 2, CELL - 2))

        # Еда
        fx, fy = food
        pygame.draw.circle(screen, RED,
                           (fx * CELL + CELL//2, fy * CELL + CELL//2), CELL//2 - 2)

        # === ПАНЕЛЬ СЧЁТА ===
        panel_y = ROWS * CELL
        pygame.draw.rect(screen, (30, 30, 30), (0, panel_y, WIDTH, 50))

        score_text = font.render(f"Счёт: {score}", True, WHITE)
        level_text = font.render(f"Уровень: {level_idx + 1}", True, YELLOW)
        food_text  = font.render(f"Еда: {food_eaten}/{LEVELS[level_idx]['food_to_next']}", True, GREEN)

        screen.blit(score_text, (10, panel_y + 12))
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, panel_y + 12))
        screen.blit(food_text,  (WIDTH - food_text.get_width() - 10, panel_y + 12))

        pygame.display.flip()

def show_level_up(screen, level):
    """Показывает сообщение о новом уровне"""
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    text = font_big.render(f"Уровень {level}!", True, YELLOW)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 30))
    pygame.display.flip()
    pygame.time.wait(1200)

def game_over(screen, score, level):
    """Экран конца игры"""
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    screen.fill(BLACK)
    go   = font_big.render("GAME OVER", True, RED)
    info = font.render(f"Счёт: {score}  |  Уровень: {level}", True, WHITE)
    screen.blit(go,   (WIDTH//2 - go.get_width()//2,   HEIGHT//2 - 60))
    screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 10))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

main()