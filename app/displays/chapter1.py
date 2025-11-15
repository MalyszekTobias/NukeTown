from app.displays.base import BaseDisplay
from app.ui import text
import pyray as rl
import time

class Chapter1(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.opacity = 255
        self.speed = 25
        self.opacity_speed = 25
        self.text_y = self.game.height / 2 - 60



    def render(self):
        super().render()
        self.opacity -= self.opacity_speed
        if self.opacity < 0:
            time.sleep(2)
            self.opacity_speed = 0
            self.opacity = 0

        text.draw_text('Chap', self.game.width / 2 - rl.measure_text('Chap', 120), self.text_y , 120, rl.WHITE)
        text.draw_text('ter 1', self.game.width / 2 - 14,
                       self.game.height - self.text_y - 120, 120, rl.WHITE)
        rl.draw_rectangle(0, 0, self.game.width, self.game.height, (0, 0, 0, self.opacity_speed))

        if self.opacity <=0:
            self.text_y -= self.speed

        if self.text_y <= -150:
            self.game.change_display(self.game.twodgame)

