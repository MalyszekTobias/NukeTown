import pyray
from app import assets



def draw_text(text, x, y, size, color):
    global_font = assets.font
    pyray.draw_text_ex(global_font, text, (x, y), size, 2, color)