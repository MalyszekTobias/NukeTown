from app import sprite, assets

class Reactor(sprite.Sprite):
    def __init__(self, game):
        self.img = assets.images["Elektrownia"]
        super().__init__(game)

