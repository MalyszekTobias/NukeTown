from app.displays.base import BaseDisplay
from app.ui import text
import pyray as rl
import time

class Chapter2(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.opacity = 255
        self.speed = 6.25
        self.opacity_speed = 25
        self.move = True
        self.text_y = self.game.height / 2 - 60

        self.drawn = False

        self.xleft = -328
        self.xright = 1946

    def render(self):
        super().render()

        if self.move:
            self.xleft += self.speed
            self.xright -= self.speed

            text.draw_text('Chap', self.xleft, self.text_y , 120, rl.ORANGE)
            text.draw_text('ter 1', self.xright, self.text_y, 120, rl.BLUE)

            if self.xleft == 672 or self.xright == 946:
                self.move = False
        elif not self.move and self.drawn:
            time.sleep(2)
            self.game.change_display(self.game.display2)

        else:
            text.draw_text('Chap', self.xleft, self.text_y, 120, rl.GREEN)
            text.draw_text('ter 2', self.xright, self.text_y, 120, rl.GREEN)
            self.drawn = True


        # rl.draw_rectangle(0, 0, self.game.width, self.game.height, (0, 0, 0, self.opacity_speed))



