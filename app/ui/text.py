import pyray
from app import assets



def draw_text(text, x, y, size, color):
    global_font = assets.font
    pyray.draw_text_ex(global_font, text, (x, y), size, 2, color)

def draw_text_with_border(text, x, y, size, color, border_color=pyray.BLACK, border_width=2):
    global_font = assets.font
    for dx in [-border_width, 0, border_width]:
        for dy in [-border_width, 0, border_width]:
            if dx != 0 or dy != 0:
                pyray.draw_text_ex(global_font, text, (x + dx, y + dy), size, 2, border_color)
    pyray.draw_text_ex(global_font, text, (x, y), size, 2, color)
