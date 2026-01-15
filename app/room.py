# python
import pyray
import random
from typing import Dict, Tuple, Optional, Set
from app import assets

Tile = Tuple[int, int]

class Room:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # maps tile -> state string, e.g. "cracked", "floor_flower_1", ...
        self._tile_states: Dict[Tile, str] = {}
        self._floors_initialized = False
        self.busy = 0

    def __repr__(self):
        return f"Room(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    def center(self) -> Tile:
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        return (cx, cy)

    def wall_tiles(self, exclude_tiles: Optional[Set[Tile]] = None) -> Set[Tile]:
        tiles = set()
        x0, y0, w, h = self.x, self.y, self.width, self.height
        for x in range(x0, x0 + w):
            tiles.add((x, y0))
            tiles.add((x, y0 + h - 1))
        for y in range(y0, y0 + h):
            tiles.add((x0, y))
            tiles.add((x0 + w - 1, y))

        # Remove tiles that collide with corridor tiles
        if exclude_tiles:
            tiles -= exclude_tiles

        return tiles

    def background_tiles(self) -> Set[Tile]:
        tiles = set()
        x0, y0, w, h = self.x, self.y, self.width, self.height
        for x in range(x0 + 1, x0 + w - 1):
            for y in range(y0 + 1, y0 + h - 1):
                tiles.add((x, y))
        return tiles

    def collision_rects(self, tile_size: int, corridor_tiles: Optional[Set[Tile]] = None):
        """Returns collision rectangles for wall tiles as (x, y, width, height) tuples."""
        wall_tiles = self.wall_tiles(exclude_tiles=corridor_tiles)
        rects = []
        for tx, ty in wall_tiles:
            # Convert each wall tile to a rectangle (pixel coordinates)
            rx = tx * tile_size
            ry = ty * tile_size
            rects.append((rx, ry, tile_size, tile_size))
        return rects

    def one_collision_rect(self, tile_size: int, corridor_tiles: Optional[Set[Tile]] = None):
        """Returns one big collision rectangle for the whole room (excluding corridors)."""
        wall_tiles = self.wall_tiles(exclude_tiles=corridor_tiles)
        if not wall_tiles:
            return None
        x_coords = [tx for tx, ty in wall_tiles]
        y_coords = [ty for tx, ty in wall_tiles]
        min_x = min(x_coords) * tile_size
        max_x = (max(x_coords) + 1) * tile_size
        min_y = min(y_coords) * tile_size
        max_y = (max(y_coords) + 1) * tile_size
        return (min_x, min_y, max_x - min_x, max_y - min_y)

    def randomize_floors(
        self,
        cracked_chance: float = 0.02,
        flower1_chance: float = 0.005,
        flower2_chance: float = 0.005,
        flower3_chance: float = 0.005,
        seed: Optional[int] = None,
    ) -> None:
        """
        Simple floor decoration assignment. For each background tile we roll once
        and pick at most one decoration (flowers or cracked). If no decoration
        is chosen the tile is left as the normal floor.
        """
        rng = random.Random(seed)
        self._tile_states.clear()

        # Precompute cumulative thresholds
        t1 = flower1_chance
        t2 = t1 + flower2_chance
        t3 = t2 + flower3_chance
        t4 = t3 + cracked_chance

        for tile in self.background_tiles():
            r = rng.random()
            if r < t1:
                self._tile_states[tile] = "floor_flower_1"
            elif r < t2:
                self._tile_states[tile] = "floor_flower_2"
            elif r < t3:
                self._tile_states[tile] = "floor_flower_3"
            elif r < t4:
                self._tile_states[tile] = "cracked"
            # else: leave as normal floor (no entry in _tile_states)

        self._floors_initialized = True

    def set_tile_state(self, tile: Tile, state: Optional[str]) -> None:
        """Set tile state (use None to clear). Valid states: 'cracked', 'floor_flower_1/2/3'."""
        if state is None:
            self._tile_states.pop(tile, None)
        else:
            self._tile_states[tile] = state

    def set_cracked(self, tile: Tile, cracked: bool = True) -> None:
        """Mark a tile cracked or not."""
        if cracked:
            self._tile_states[tile] = "cracked"
        else:
            self._tile_states.pop(tile, None)

    def get_tile_state(self, tile: Tile) -> Optional[str]:
        return self._tile_states.get(tile)

    def is_cracked(self, tile: Tile) -> bool:
        return self._tile_states.get(tile) == "cracked"

    def draw(self, tile_size: int = 16, color: pyray.Color = pyray.RED, corridor_tiles: Optional[Set[Tile]] = None):
        if not self._floors_initialized:
            seed = (self.x * 73856093) ^ (self.y * 19349663) ^ (self.width * 83492791)
            self.randomize_floors(seed=seed)

        px = self.x * tile_size
        py = self.y * tile_size
        pw = self.width * tile_size
        ph = self.height * tile_size

        floor_tex = assets.images.get("Floor_Default")
        cracked_tex = assets.images.get("Floor_Cracked")
        flower1_tex = assets.images.get("Floor_flower_1")
        flower2_tex = assets.images.get("Floor_flower_2")
        flower3_tex = assets.images.get("Floor_flower_3")

        for tx, ty in self.background_tiles():
            dest_x = tx * tile_size
            dest_y = ty * tile_size
            state = self.get_tile_state((tx, ty))
            if state == "cracked" and cracked_tex:
                pyray.draw_texture_ex(cracked_tex, (dest_x, dest_y), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif state == "floor_flower_1" and flower1_tex:
                pyray.draw_texture_ex(flower1_tex, (dest_x, dest_y), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif state == "floor_flower_2" and flower2_tex:
                pyray.draw_texture_ex(flower2_tex, (dest_x, dest_y), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif state == "floor_flower_3" and flower3_tex:
                pyray.draw_texture_ex(flower3_tex, (dest_x, dest_y), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif floor_tex:
                pyray.draw_texture_ex(floor_tex, (dest_x, dest_y), 0, 1 / 4 / tile_size, pyray.WHITE)
            else:
                pyray.draw_rectangle(dest_x, dest_y, tile_size, tile_size, pyray.DARKGRAY)

        wall_h_tex = assets.images.get("Wall_horizontal")
        wall_v_tex = assets.images.get("Wall_vertical")
        wall_corner_tex = assets.images.get("Wall_corner")

        x0, y0, w, h = self.x, self.y, self.width, self.height
        corners = [
            (x0, y0),
            (x0 + w - 1, y0),
            (x0, y0 + h - 1),
            (x0 + w - 1, y0 + h - 1),
        ]

        all_wall_tiles = self.wall_tiles()  # without exclusions
        visible_wall_tiles = self.wall_tiles(exclude_tiles=corridor_tiles)

        for wx, wy in visible_wall_tiles:
            dest_x = wx * tile_size
            dest_y = wy * tile_size

            if (wx, wy) == corners[0]:
                pyray.draw_texture_ex(wall_corner_tex, (dest_x + tile_size/3, dest_y + tile_size/3+2/3), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif (wx, wy) == corners[1]:
                pyray.draw_texture_ex(wall_corner_tex, (dest_x - tile_size/3, dest_y + tile_size/3+2/3), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif (wx, wy) == corners[2]:
                pyray.draw_texture_ex(wall_corner_tex, (dest_x + tile_size/3, dest_y - tile_size/3), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif (wx, wy) == corners[3]:
                pyray.draw_texture_ex(wall_corner_tex, (dest_x - tile_size/3, dest_y - tile_size/3), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif wy == y0:
                pyray.draw_texture_ex(wall_h_tex, (dest_x, dest_y + tile_size/3), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif wy == y0 + h - 1:
                pyray.draw_texture_ex(wall_h_tex, (dest_x, dest_y - tile_size/3), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif wx == x0:
                pyray.draw_texture_ex(wall_v_tex, (dest_x + tile_size/3, dest_y), 0, 1 / 4 / tile_size, pyray.WHITE)
            elif wx == x0 + w - 1:
                pyray.draw_texture_ex(wall_v_tex, (dest_x - tile_size/3, dest_y), 0, 1 / 4 / tile_size, pyray.WHITE)

