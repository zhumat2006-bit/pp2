import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
PANEL_H = 60  
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

COLORS = [
    (0,0,0), (255,255,255), (255,0,0), (0,200,0),
    (0,0,255), (255,165,0), (255,255,0), (128,0,128),
    (0,255,255), (255,20,147), (139,69,19), (128,128,128)
]

TOOLS = ["pencil", "rect", "circle", "eraser"]

def draw_panel(screen, current_color, current_tool, brush_size):
    """Рисует панель инструментов"""
    pygame.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, PANEL_H))
    pygame.draw.line(screen, (150,150,150), (0, PANEL_H), (WIDTH, PANEL_H), 2)

    for i, color in enumerate(COLORS):
        rect = pygame.Rect(10 + i * 38, 10, 32, 32)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0,0,0), rect, 2)
        if color == current_color:
            pygame.draw.rect(screen, (255,255,0), rect, 3)  # выбранный цвет

    tool_labels = {"pencil": "✏ Карандаш", "rect": "⬜ Прямоугольник",
                   "circle": "⭕ Круг",    "eraser": "🧹 Ластик"}
    font = pygame.font.SysFont("Arial", 14)
    for i, tool in enumerate(TOOLS):
        x = 480 + i * 90
        color = (100, 200, 100) if tool == current_tool else (180, 180, 180)
        pygame.draw.rect(screen, color, (x, 8, 85, 35), border_radius=5)
        pygame.draw.rect(screen, (0,0,0), (x, 8, 85, 35), 1, border_radius=5)
        label = tool_labels[tool]
        text = font.render(label, True, (0,0,0))
        screen.blit(text, (x + 5, 18))

    font2 = pygame.font.SysFont("Arial", 13)
    size_text = font2.render(f"Размер: {brush_size}", True, (0,0,0))
    screen.blit(size_text, (10, 44))

def main():
    canvas = pygame.Surface((WIDTH, HEIGHT - PANEL_H))
    canvas.fill((255, 255, 255))  

    current_color = (0, 0, 0)    
    current_tool  = "pencil"
    brush_size    = 5
    drawing       = False
    start_pos     = None          

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            
            if event.type == pygame.MOUSEWHEEL:
                brush_size = max(1, min(50, brush_size + event.y))

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if my < PANEL_H:
                    for i, color in enumerate(COLORS):
                        rect = pygame.Rect(10 + i * 38, 10, 32, 32)
                        if rect.collidepoint(mx, my):
                            current_color = color

                    
                    for i, tool in enumerate(TOOLS):
                        x = 480 + i * 90
                        if pygame.Rect(x, 8, 85, 35).collidepoint(mx, my):
                            current_tool = tool
                else:
                    
                    drawing   = True
                    start_pos = (mx, my - PANEL_H)

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing and start_pos:
                    mx, my = event.pos
                    end_pos = (mx, my - PANEL_H)

                    if current_tool == "rect":
                        x = min(start_pos[0], end_pos[0])
                        y = min(start_pos[1], end_pos[1])
                        w = abs(end_pos[0] - start_pos[0])
                        h = abs(end_pos[1] - start_pos[1])
                        pygame.draw.rect(canvas, current_color, (x, y, w, h), brush_size)

                    elif current_tool == "circle":
                        cx = (start_pos[0] + end_pos[0]) // 2
                        cy = (start_pos[1] + end_pos[1]) // 2
                        r  = int(((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)**0.5 // 2)
                        pygame.draw.circle(canvas, current_color, (cx, cy), max(1, r), brush_size)

                drawing   = False
                start_pos = None

            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                if my > PANEL_H: 
                    pos = (mx, my - PANEL_H)

                    if current_tool == "pencil":
                        pygame.draw.circle(canvas, current_color, pos, brush_size)

                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, (255,255,255), pos, brush_size * 3)

        screen.fill((255, 255, 255))
        screen.blit(canvas, (0, PANEL_H))

        if drawing and start_pos and current_tool in ("rect", "circle"):
            mx, my = pygame.mouse.get_pos()
            preview = canvas.copy()
            end_pos = (mx, my - PANEL_H)

            if current_tool == "rect":
                x = min(start_pos[0], end_pos[0])
                y = min(start_pos[1], end_pos[1])
                w = abs(end_pos[0] - start_pos[0])
                h = abs(end_pos[1] - start_pos[1])
                pygame.draw.rect(preview, current_color, (x, y, w, h), brush_size)

            elif current_tool == "circle":
                cx = (start_pos[0] + end_pos[0]) // 2
                cy = (start_pos[1] + end_pos[1]) // 2
                r  = int(((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)**0.5 // 2)
                pygame.draw.circle(preview, current_color, (cx, cy), max(1, r), brush_size)

            screen.blit(preview, (0, PANEL_H))

        draw_panel(screen, current_color, current_tool, brush_size)
        pygame.display.flip()
        clock.tick(60)

main()