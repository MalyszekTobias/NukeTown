import pyray



def draw_text(text, x, y, size, color):
    global_font = pyray.load_font('app/assets/Fonts/Chernobyl.otf')
    pyray.draw_text_ex(global_font, text, pyray.Vector2(x, y), size, 2, color)