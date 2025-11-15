# app/gate.py
import pyray as rl
from typing import Tuple, Optional
from app import assets

Tile = Tuple[int, int]

class Gate:
    def __init__(self, game_map, tile: Tile, room_ref=None, is_open: bool = False, interaction_radius: float = 24.0):
        self.map = game_map
        self.tile = tile
        self.tile_size = getattr(game_map, 'tile_size', 16)
        self.x = tile[0] * self.tile_size
        self.y = tile[1] * self.tile_size
        self.room = room_ref
        self.is_open = is_open
        self.interaction_radius = interaction_radius
        # Determine orientation based on room if available
        self.orientation = 'horizontal'
        if room_ref is not None:
            x0, y0, w, h = room_ref.x, room_ref.y, room_ref.width, room_ref.height
            tx, ty = tile
            if tx == x0:
                self.orientation = 'vertical0'
            elif tx == x0 + w - 1:
                self.orientation = 'vertical1'
            elif ty == y0:
                self.orientation = 'horizontal0'
            elif ty == y0 + h - 1:
                self.orientation = 'horizontal1'

    def draw(self, tile_size: Optional[int] = None):
        tile_size = tile_size or self.tile_size
        tex = assets.images.get('GateOpen' if self.is_open else 'GateClosed')
        if not tex:
            return
        dest_x = self.x
        dest_y = self.y
        # rotation: 0 for horizontal, 90 for vertical
        if self.orientation == 'vertical0':
            rotation = 270
            dest_y += tile_size  # Slight offsets to better align with room walls (copied style from room.draw)
        elif self.orientation == 'vertical1':
            rotation = 90
            dest_x += tile_size  # Slight offsets to better align with room walls (copied style from room.draw)
        elif self.orientation == 'horizontal1':
            rotation = 180
            dest_x += tile_size  # Slight offsets to better align with room walls (copied
            dest_y += tile_size
        elif self.orientation == 'horizontal0':
            rotation = 0
        # Slight offsets to better align with room walls (copied style from room.draw)

        rl.draw_texture_ex(tex, (dest_x, dest_y), rotation, 1 / 4 / tile_size, rl.WHITE)

    def collision_rect(self):
        """Returns a rectangle (x,y,w,h) in world pixels representing the blocking area when closed."""
        return (self.x, self.y, self.tile_size, self.tile_size)

    def can_interact(self, player) -> bool:
        # interaction center is gate center
        gx = self.x + self.tile_size / 2
        gy = self.y + self.tile_size / 2
        dx = player.x - gx
        dy = player.y - gy
        return (dx * dx + dy * dy) <= (self.interaction_radius * self.interaction_radius)

    def open(self):
        if not self.is_open:
            self.is_open = True
            try:
                self.map.game.music_manager.play_sound(assets.sounds.get('shot'))
            except Exception:
                pass

    def close(self):
        if self.is_open:
            self.is_open = False

    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()

    def interact(self, player):
        # default interaction: toggle open/closed
        self.toggle()

