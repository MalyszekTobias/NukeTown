from app.displays.base import BaseDisplay
from app.ui import text
import pyray as rl
import time
from app import sprite, assets





class GameOver(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        self.drawn = False


    def render(self):
        super().render()

        if self.drawn:
            time.sleep(3)
            quit()


        text.draw_text('GAME OVER!', self.game.width / 2 - rl.measure_text('GAME OVER!', 120) / 2,
                       self.game.height / 2 - 60, 120, rl.RED)
        self.drawn = True


