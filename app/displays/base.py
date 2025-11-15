import pyray as rl
class BaseDisplay:
    def __init__(self, game):
        self.game = game
        self.game_objects = []

    def __str__(self):
        return self.__class__.__name__

    def render(self):
        rl.clear_background(rl.BLACK)

        for object in self.game_objects:
            object.render()

    def update(self):
        for object in self.game_objects:
            object.update()
