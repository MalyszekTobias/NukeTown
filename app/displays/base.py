import pyray as rl
class BaseDisplay:
    def __init__(self, game):
        self.game = game

    def __str__(self):
        return self.__class__.__name__

    def render(self):
        rl.clear_background(rl.BLACK)

    def update(self):
        pass
