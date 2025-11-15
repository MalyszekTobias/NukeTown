import pyray as rl
from typing import Tuple, Optional
from app import assets

Tile = Tuple[int, int]

class Gate:
    def __init__(self, game_map, tile: Tile, room_ref=None, is_open: bool = False, interaction_radius: float = 24.0, required_atom: Optional[str] = None):
        self.map = game_map
        self.tile = tile
        self.tile_size = getattr(game_map, 'tile_size', 16)
        self.x = tile[0] * self.tile_size
        self.y = tile[1] * self.tile_size
        self.room = room_ref
        self.is_open = is_open
        self.interaction_radius = interaction_radius
        self.required_atom = required_atom  # e.g., "hydrogen", "helium", "oxygen", etc.
        self.orientation = 'horizontal0'
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

    def __str__(self):
        return f"Gate(tile={self.tile}, is_open={self.is_open}, orientation={self.orientation}, required_atom={self.required_atom})"

    def draw(self, tile_size: Optional[int] = None):
        tile_size = tile_size or self.tile_size
        tex = assets.images.get('GateOpen' if self.is_open else 'GateClosed')
        if not tex:
            return
        dest_x = self.x
        dest_y = self.y
        rotation = 0
        if self.orientation == 'vertical0':
            rotation = 270
            dest_y += tile_size
        elif self.orientation == 'vertical1':
            rotation = 90
            dest_x += tile_size
        elif self.orientation == 'horizontal1':
            rotation = 180
            dest_x += tile_size
            dest_y += tile_size
        elif self.orientation == 'horizontal0':
            rotation = 0

        # Draw the gate
        measured_text = rl.measure_text(self.required_atom or "", tile_size)
        if self.required_atom:
            rl.draw_texture_ex(tex, (dest_x, dest_y), rotation, 1 / 4 / tile_size, rl.RED)
            rl.draw_text(self.required_atom, dest_x, dest_y, 10, rl.WHITE)
        else:
            rl.draw_texture_ex(tex, (dest_x, dest_y), rotation, 1 / 4 / tile_size, rl.WHITE)
        if self.required_atom and not self.is_open:
            atom_asset_name = self.required_atom.capitalize() + "_Standby"
            atom_tex = assets.images.get(atom_asset_name)
            if atom_tex:
                atom_scale = 0.01
                rl.draw_texture_ex(atom_tex, (dest_x-(measured_text*0.3), dest_y), 0, atom_scale, rl.WHITE)

    def collision_rect(self):
        gate_thickness = 4  # pixels

        if self.orientation == 'vertical1':
            # Vertical gate: thin width, full height
            return (self.x, self.y, gate_thickness, self.tile_size)
        elif self.orientation == 'vertical0':
            return (self.x + self.tile_size - gate_thickness, self.y, gate_thickness, self.tile_size)
        elif self.orientation == 'horizontal0':
            # Horizontal gate: full width, thin height
            return (self.x, self.y + self.tile_size - gate_thickness, self.tile_size, gate_thickness)
        else:  # 'horizontal0'
            return (self.x, self.y, self.tile_size, gate_thickness)
    def can_interact(self, player) -> bool:
        # AABB collision: expand gate rect by interaction_radius
        gate_rect_expanded = (
            self.x - self.interaction_radius,
            self.y - self.interaction_radius,
            self.tile_size + 2 * self.interaction_radius,
            self.tile_size + 2 * self.interaction_radius
        )
        if hasattr(player, 'rect'):
            px, py, pw, ph = player.rect.x, player.rect.y, player.rect.width, player.rect.height
        else:
            radius = getattr(player, 'radius', 10)
            px = player.x - radius / 2
            py = player.y - radius / 2
            pw = radius
            ph = radius

        gx, gy, gw, gh = gate_rect_expanded
        return px < gx + gw and px + pw > gx and py < gy + gh and py + ph > gy

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
        if self.required_atom and not self.is_open:
            try:
                inventory = self.map.game.crafting_display.inventory.inv
                # Check if player has the required atom
                if self.required_atom in inventory and inventory[self.required_atom] > 0:
                    self.open()
                else:
                    return
            except Exception as e:
                print(f"Could not access inventory: {e}")
                return
        else:
            self.toggle()
