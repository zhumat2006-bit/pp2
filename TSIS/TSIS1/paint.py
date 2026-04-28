import pygame as p
import math
import os
from datetime import datetime

p.init()

# экран и иконки
try:
    icon = p.image.load("images/icon_paint.png")
    p.display.set_icon(icon)
except:
    print("Icon not found, using default.")

WIDTH, HEIGHT = 1000, 850
p.display.set_caption("Paint")
screen = p.display.set_mode((WIDTH, HEIGHT))
clock = p.time.Clock()
font = p.font.SysFont("Arial", 12, bold=True)
large_font = p.font.SysFont("Arial", 18, bold=True)

# холст
canvas_offset = (100, 150)
canvas = p.Surface((800, 600))
canvas.fill((255, 255, 255))

# переменные 
color = (0, 0, 0)
brush_size = 3
tool = "draw"
drawing = False
start_pos = None 
text_input = ""
text_pos = None
last_draw_pos = None

btns = {
    # цвета
    "black":   {"rect": p.Rect(10, 10, 40, 40), "color": (0,0,0)},
    "red":     {"rect": p.Rect(60, 10, 40, 40), "color": (255,0,0)},
    "green":   {"rect": p.Rect(110, 10, 40, 40), "color": (0,255,0)},
    "blue":    {"rect": p.Rect(160, 10, 40, 40), "color": (0,0,255)},
    "purple":  {"rect": p.Rect(210, 10, 40, 40), "color": (128,0,128)},
    "orange":  {"rect": p.Rect(260, 10, 40, 40), "color": (255,165,0)},
    "cyan":    {"rect": p.Rect(310, 10, 40, 40), "color": (0,255,255)},
    "eraser":  {"rect": p.Rect(370, 10, 60, 40), "color": (255,255,255), "label": "eraser"},
    
    # фигуры и инструменты
    "draw":    {"rect": p.Rect(10, 60, 70, 40), "label": "pencil"},
    "line":    {"rect": p.Rect(90, 60, 70, 40), "label": "line"},
    "square":  {"rect": p.Rect(170, 60, 70, 40), "label": "rectangle"},
    "circle":  {"rect": p.Rect(250, 60, 70, 40), "label": "circle"},
    "rect_tri": {"rect": p.Rect(330, 60, 70, 40), "label": "r-tri"},
    "eq_tri":  {"rect": p.Rect(410, 60, 70, 40), "label": "e-tri"},
    "rhombus": {"rect": p.Rect(490, 60, 70, 40), "label": "rhombus"},
    "fill":    {"rect": p.Rect(570, 60, 70, 40), "label": "fill"},
    "text":    {"rect": p.Rect(650, 60, 70, 40), "label": "text"},
    
    # управ кисточкой
    "minus":   {"rect": p.Rect(740, 60, 40, 40), "label": "-"},
    "plus":    {"rect": p.Rect(790, 60, 40, 40), "label": "+"},
    "clear":   {"rect": p.Rect(910, 10, 70, 40), "label": "clear"}
}

def flood_fill(surf, x, y, new_col):
    """Efficient stack-based flood fill."""
    target_col = surf.get_at((x, y))
    if target_col == new_col: return
    stack = [(x, y)]
    while stack:
        cur_x, cur_y = stack.pop()
        if 0 <= cur_x < 800 and 0 <= cur_y < 600:
            if surf.get_at((cur_x, cur_y)) == target_col:
                surf.set_at((cur_x, cur_y), new_col)
                stack.append((cur_x + 1, cur_y))
                stack.append((cur_x - 1, cur_y))
                stack.append((cur_x, cur_y + 1))
                stack.append((cur_x, cur_y - 1))

def get_shape_points(shape_type, start, end):
    x1, y1 = start
    x2, y2 = end
    w, h = x2 - x1, y2 - y1
    if shape_type == "rect_tri": return [(x1, y1), (x1, y2), (x2, y2)]
    elif shape_type == "eq_tri":
        side = x2 - x1
        h_tri = (math.sqrt(3) / 2) * side
        return [(x1 + side/2, y1), (x1, y1 + h_tri), (x1 + side, y1 + h_tri)]
    elif shape_type == "rhombus": 
        return [(x1 + w/2, y1), (x2, y1 + h/2), (x1 + w/2, y2), (x1, y1 + h/2)]
    return []

# глав цикл
running = True
while running:
    mx, my = p.mouse.get_pos()
    cx, cy = mx - canvas_offset[0], my - canvas_offset[1]
    
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False

        if event.type == p.KEYDOWN:
            # 3.2 размеры кисточки
            if event.key == p.K_1: brush_size = 2
            if event.key == p.K_2: brush_size = 5
            if event.key == p.K_3: brush_size = 10
            
            # 3.4 сохранить холст(Ctrl+S)
            if event.key == p.K_s and (p.key.get_mods() & p.KMOD_CTRL):
                fname = f"paint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                p.image.save(canvas, fname)
                print(f"Canvas saved as {fname}")

            # 3.5 текстовой инструмент
            if tool == "text" and text_pos:
                if event.key == p.K_RETURN:
                    txt_surf = large_font.render(text_input, True, color)
                    canvas.blit(txt_surf, text_pos)
                    text_input, text_pos = "", None
                elif event.key == p.K_ESCAPE:
                    text_input, text_pos = "", None
                elif event.key == p.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode

        if event.type == p.MOUSEBUTTONDOWN:
            clicked_ui = False
            for name, info in btns.items():
                if info["rect"].collidepoint(mx, my):
                    clicked_ui = True
                    if "color" in info:
                        color = info["color"]
                        if name == "eraser": tool = "draw"
                    elif name == "plus": brush_size = min(50, brush_size + 1)
                    elif name == "minus": brush_size = max(1, brush_size - 1)
                    elif name == "clear": canvas.fill((255, 255, 255))
                    else: tool = name
            
            if not clicked_ui and 0 <= cx < 800 and 0 <= cy < 600:
                if tool == "fill":
                    flood_fill(canvas, cx, cy, color)
                elif tool == "text":
                    text_pos = (cx, cy)
                    text_input = ""
                else:
                    drawing = True
                    start_pos = (cx, cy)
                    last_draw_pos = (cx, cy)

        if event.type == p.MOUSEBUTTONUP:
            if drawing:
                # фигуры на холст
                if tool == "line":
                    p.draw.line(canvas, color, start_pos, (cx, cy), brush_size)
                elif tool == "circle":
                    rad = int(math.hypot(cx - start_pos[0], cy - start_pos[1]))
                    p.draw.circle(canvas, color, start_pos, rad, brush_size)
                elif tool == "square":
                    side = max(abs(cx - start_pos[0]), abs(cy - start_pos[1]))
                    rect = p.Rect(start_pos[0], start_pos[1], side, side)
                    p.draw.rect(canvas, color, rect, brush_size)
                elif tool != "draw":
                    pts = get_shape_points(tool, start_pos, (cx, cy))
                    if len(pts) > 2: p.draw.polygon(canvas, color, pts, brush_size)
                
                drawing = False
                start_pos = None

    # 3.1 ручка
    if drawing and tool == "draw":
        if 0 <= cx < 800 and 0 <= cy < 600:
            p.draw.line(canvas, color, last_draw_pos, (cx, cy), brush_size)
            # Circle interpolation for smooth lines
            p.draw.circle(canvas, color, (cx, cy), brush_size // 2)
            last_draw_pos = (cx, cy)

    # фил
    screen.fill((230, 230, 230))
    
    # кнопки
    for name, info in btns.items():
        bg = info.get("color", (255, 255, 255))
        if tool == name: bg = (255, 255, 0) 
        
        p.draw.rect(screen, bg, info["rect"])
        p.draw.rect(screen, (0, 0, 0), info["rect"], 2)
        
        if "label" in info:
            txt = font.render(info["label"], True, (0,0,0))
            screen.blit(txt, (info["rect"].centerx - txt.get_width()//2, 
                             info["rect"].centery - txt.get_height()//2))

    # инфо статус
    screen.blit(large_font.render(f"Width: {brush_size}", True, (0,0,0)), (840, 65))
    p.draw.rect(screen, color, (940, 60, 40, 40))
    p.draw.rect(screen, (0,0,0), (940, 60, 40, 40), 2)

    # рендер холста
    screen.blit(canvas, canvas_offset)
    p.draw.rect(screen, (0,0,0), (canvas_offset[0], canvas_offset[1], 800, 600), 2)

    # предварительные показы
    if drawing and start_pos and tool != "draw":
        ps = (start_pos[0] + canvas_offset[0], start_pos[1] + canvas_offset[1])
        if tool == "line":
            p.draw.line(screen, color, ps, (mx, my), brush_size)
        elif tool == "circle":
            rad = int(math.hypot(mx - ps[0], my - ps[1]))
            p.draw.circle(screen, color, ps, rad, 1)
        elif tool == "square":
            side = max(abs(mx - ps[0]), abs(my - ps[1]))
            p.draw.rect(screen, color, (ps[0], ps[1], side, side), 1)
        else:
            pts = get_shape_points(tool, ps, (mx, my))
            if len(pts) > 2: p.draw.polygon(screen, color, pts, 1)

    # писать
    if tool == "text" and text_pos:
        cursor_txt = text_input + "|"
        txt_prev = large_font.render(cursor_txt, True, color)
        screen.blit(txt_prev, (text_pos[0] + canvas_offset[0], text_pos[1] + canvas_offset[1]))

    p.display.flip()
    clock.tick(120)

p.quit()