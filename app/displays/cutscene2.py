from stringprep import c6_set

from app.displays.base import BaseDisplay
from app.ui import text
import pyray as rl
import time
from app import sprite, assets


class scene(sprite.Sprite):
    def __init__(self, game, scaleXframewidth=1920):
        self.img = assets.images['Cutscene2']
        super().__init__(game, scaleXframewidth)
        self.x = 960
        self.y = 540
        self.frame_duration = 0.2




    def render(self):
        super().render()
        if self.current_frame == self.num_of_frames-1:
            self.display.finish = True
            self.display.game_objects.remove(self)






class Cutscene(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        scene(self)
        self.finish = False
        self.drawn= False

    def render(self):
        super().render()
        if self.drawn:
            time.sleep(10)
            quit()
        if self.finish:
            text.draw_text('VICTORY!', self.game.width/2 - rl.measure_text('VICTORY!', 120)/2, self.game.height/2 - 60, 120, rl.WHITE)
            self.drawn = True
