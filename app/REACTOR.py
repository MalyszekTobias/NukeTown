from app import sprite, assets

class Reactor(sprite.Sprite):
    def __init__(self, display, scaleXframewidth=60):
        self.img = assets.images["Elektrownia"]
        super().__init__(display, scaleXframewidth=scaleXframewidth)
        self.x = 200
        self.y = 189

