import pyray

from typing import Set, Tuple
from app import assets

Tile = Tuple[int, int]

class Room:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self) -> Tile:
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        return (cx, cy)

    def wall_tiles(self) -> Set[Tile]:
        tiles = set()
        x0, y0, w, h = self.x, self.y, self.width, self.height
        for x in range(x0, x0 + w):
            tiles.add((x, y0))
            tiles.add((x, y0 + h - 1))
        for y in range(y0, y0 + h):
            tiles.add((x0, y))
            tiles.add((x0 + w - 1, y))
        return tiles

    def background_tiles(self) -> Set[Tile]:
        tiles = set()
        x0, y0, w, h = self.x, self.y, self.width, self.height
        for x in range(x0 + 1, x0 + w - 1):
            for y in range(y0 + 1, y0 + h - 1):
                tiles.add((x, y))
        return tiles

    def draw(self, tile_size: int = 16, color: pyray.Color = pyray.RED):
        px = self.x * tile_size
        py = self.y * tile_size
        pw = self.width * tile_size
        ph = self.height * tile_size
        pyray.draw_rectangle_lines(px, py, pw, ph, color)

        floor_tex = assets.images["Floor_Default"]
        if floor_tex:
            for tx, ty in self.background_tiles():
                pyray.draw_texture_ex(floor_tex, (tx * tile_size, ty * tile_size),0, 1/4/tile_size, pyray.WHITE)

