from stringprep import c6_set

from app.displays.base import BaseDisplay
from app.ui import text
import pyray as rl
import time
from app import sprite, assets


class scene(sprite.Sprite):
    def __init__(self, game, scaleXframewidth=1920):
        self.img = assets.images['Cutscene1']
        super().__init__(game, scaleXframewidth)
        self.x = 960
        self.y = 540



    def render(self):
        super().render()
        if self.current_frame == self.num_of_frames-1:
            self.display.game.change_display(self.display.game.crafting_display)





class Cutscene(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        scene(self)

    def render(self):
        super().render()
