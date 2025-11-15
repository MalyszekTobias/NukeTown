import pyray
from app.ui import text

class Button:
    def __init__(self, game, x, y, width, height, text, text_size, text_color, button_color, hover_color, click_color):
        self.rect = pyray.Rectangle(x, y, width, height)
        self.text = text
        self.text_size = text_size
        self.text_color = text_color
        self.button_color = button_color
        self.hover_color = hover_color
        self.click_color = click_color
        self.is_hovered = False
        self.is_clicked = False
        self.is_focused = False
        self.game = game

    def update(self, focused = False):
        self.is_focused = focused
        mouse_point = pyray.get_mouse_position()
        mouse_hover = pyray.check_collision_point_rec(mouse_point, self.rect)
        self.is_hovered = mouse_hover or self.is_focused

        mouse_click = self.is_hovered and pyray.is_mouse_button_pressed(pyray.MouseButton.MOUSE_BUTTON_LEFT)
        gp_click = self.is_focused and pyray.is_gamepad_button_pressed(self.game.gamepad_id, pyray.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_DOWN)

        self.is_clicked = mouse_click or gp_click

    def draw(self):
        # if self.is_clicked:
        #     color = self.click_color
        #
        # else:
        #     color = self.button_color

        color = self.button_color

        if self.is_hovered:
            text_color = self.hover_color
        else:
            text_color = self.text_color

        pyray.draw_rectangle_rec(self.rect, color)
        text_width = pyray.measure_text(self.text, self.text_size)
        text_x = (self.rect.x + self.rect.width//2) - text_width//2 + 10
        text_y = (self.rect.y + self.rect.height//2) - self.text_size//2 + 5
        text.draw_text(self.text, int(text_x), int(text_y), self.text_size, text_color)


    def move_out(self, speed):
        self.rect.x -= speed