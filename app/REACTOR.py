from app import sprite, assets

class Reactor(sprite.Sprite):
    def __init__(self, display, scaleXframewidth=60):
        self.img = assets.images["Elektrownia"]
        super().__init__(display, scaleXframewidth=scaleXframewidth)
        self.x = 200
        self.y = 189
        # Precompute display size for interaction/collision
        self.visible_width = float(self.scaleXframewidth)
        self.visible_height = (self.frame_height / float(self.frame_width)) * self.visible_width if self.frame_width else self.visible_width

    def _reactor_rect(self):
        """Return the on-screen axis-aligned rect of the reactor as (x,y,w,h)."""
        rx = float(self.x) - self.visible_width / 1.5
        ry = float(self.y) - self.visible_height / 1.5
        return rx, ry, self.visible_width, self.visible_height

    def can_interact(self, player):
        """Return True if the player's rect overlaps the reactor's on-screen rect (collision)."""
        try:
            # Player rect (already maintained by Atom.update)
            pr = getattr(player, 'rect', None)
            if pr is None:
                return False
            px, py, pw, ph = float(pr.x), float(pr.y), float(pr.width), float(pr.height)
            rx, ry, rw, rh = self._reactor_rect()
            return (px < rx + rw and px + pw > rx and py < ry + rh and py + ph > ry)
        except Exception:
            return False
