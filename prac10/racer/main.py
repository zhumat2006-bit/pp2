import pygame
import random
import sys

pygame.init()

# === НАСТРОЙКИ ===
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Game")
clock = pygame.time.Clock()
FPS = 60

# === ЦВЕТА ===
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
YELLOW = (255, 215, 0)
RED    = (255, 0, 0)
GRAY   = (50, 50, 50)

# === ДОРОГА ===
road_x = 80        # левая граница дороги
road_w = 240       # ширина дороги

# === РАЗМЕТКА ДОРОГИ ===
class RoadMark:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width  = 10
        self.height = 50
        self.speed  = 5

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = -self.height

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

# === МАШИНА ИГРОКА ===
class PlayerCar:
    def __init__(self):
        self.width  = 50
        self.height = 80
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 120
        self.speed = 5
        self.color = (0, 100, 255)  # синяя

    def move(self, keys):
        # Двигаемся влево/вправо, не выходим за дорогу
        if keys[pygame.K_LEFT] and self.x > road_x:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.width < road_x + road_w:
            self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Окна машины
        pygame.draw.rect(screen, (200, 230, 255), (self.x+8, self.y+10, 34, 20))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# === МАШИНА ВРАГА ===
class EnemyCar:
    def __init__(self, speed):
        self.width  = 50
        self.height = 80
        self.x = random.randint(road_x, road_x + road_w - self.width)
        self.y = -self.height
        self.speed = speed
        self.color = (255, 50, 50)  # красная

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (255, 200, 200), (self.x+8, self.y+10, 34, 20))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_off_screen(self):
        return self.y > HEIGHT

# === МОНЕТА ===
class Coin:
    def __init__(self, speed):
        self.radius = 12
        self.x = random.randint(road_x + self.radius, road_x + road_w - self.radius)
        self.y = random.randint(-400, -50)  # появляется случайно сверху
        self.speed = speed
        self.color = YELLOW

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Буква $ на монете
        font = pygame.font.SysFont("Arial", 14, bold=True)
        text = font.render("$", True, BLACK)
        screen.blit(text, (self.x - 5, self.y - 8))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def is_off_screen(self):
        return self.y > HEIGHT

# === ИГРА ===
def main():
    player = PlayerCar()
    enemies = []
    coins   = []
    marks   = [RoadMark(WIDTH//2 - 5, i * 120) for i in range(6)]

    score      = 0   # очки за проехавших врагов
    coin_count = 0   # собранные монеты
    speed      = 4   # скорость врагов
    enemy_timer = 0
    coin_timer  = 0

    font      = pygame.font.SysFont("Arial", 24, bold=True)
    font_big  = pygame.font.SysFont("Arial", 48, bold=True)

    running = True
    while running:
        clock.tick(FPS)

        # === СОБЫТИЯ ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.move(keys)

        # === СПАВН ВРАГОВ каждые 90 кадров ===
        enemy_timer += 1
        if enemy_timer >= 90:
            enemies.append(EnemyCar(speed))
            enemy_timer = 0

        # === СПАВН МОНЕТ каждые 120 кадров ===
        coin_timer += 1
        if coin_timer >= 120:
            coins.append(Coin(speed))
            coin_timer = 0

        # === ОБНОВЛЕНИЕ ===
        for mark in marks:
            mark.update()

        for enemy in enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                enemies.remove(enemy)
                score += 1  # +1 очко за пропущенного врага

        for coin in coins[:]:
            coin.update()
            if coin.is_off_screen():
                coins.remove(coin)

        # === КОЛЛИЗИЯ: игрок + монета ===
        for coin in coins[:]:
            if player.get_rect().colliderect(coin.get_rect()):
                coins.remove(coin)
                coin_count += 1  # собрали монету!

        # === КОЛЛИЗИЯ: игрок + враг → GAME OVER ===
        for enemy in enemies:
            if player.get_rect().colliderect(enemy.get_rect()):
                # Экран Game Over
                screen.fill(BLACK)
                go_text  = font_big.render("GAME OVER", True, RED)
                sc_text  = font.render(f"Очки: {score}  Монеты: {coin_count}", True, WHITE)
                screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, 220))
                screen.blit(sc_text, (WIDTH//2 - sc_text.get_width()//2, 300))
                pygame.display.flip()
                pygame.time.wait(3000)
                pygame.quit()
                sys.exit()

        # === УВЕЛИЧЕНИЕ СКОРОСТИ каждые 5 очков ===
        if score > 0 and score % 5 == 0:
            speed = 4 + score // 5

        # === ОТРИСОВКА ===
        screen.fill(GRAY)  # фон

        # Дорога
        pygame.draw.rect(screen, (80, 80, 80), (road_x, 0, road_w, HEIGHT))

        # Обочины
        pygame.draw.rect(screen, (34, 139, 34), (0, 0, road_x, HEIGHT))
        pygame.draw.rect(screen, (34, 139, 34), (road_x + road_w, 0, WIDTH - road_x - road_w, HEIGHT))

        for mark in marks:
            mark.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        for coin in coins:
            coin.draw(screen)

        player.draw(screen)

        # === UI: очки и монеты ===
        score_text = font.render(f"Очки: {score}", True, WHITE)
        coin_text  = font.render(f"🪙 {coin_count}", True, YELLOW)

        screen.blit(score_text, (10, 10))
        screen.blit(coin_text, (WIDTH - coin_text.get_width() - 10, 10))  # правый верхний угол

        pygame.display.flip()

main()