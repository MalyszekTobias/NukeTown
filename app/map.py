# python
# File: app/map.py
import pyray
from typing import List, Set, Tuple
from app.room import Room

Tile = Tuple[int, int]

class Map:
    def __init__(self):
        self.rooms: List[Room] = []
        self.corridor_tiles: Set[Tile] = set()

    def add_room(self, room: Room):
        self.rooms.append(room)

    def _create_corridor_between(self, a: Tile, b: Tile):
        # L-shaped: horizontal from a.x to b.x at a.y, then vertical to b.y
        ax, ay = a
        bx, by = b
        tiles = set()
        # horizontal
        x_start, x_end = sorted((ax, bx))
        for x in range(x_start, x_end + 1):
            tiles.add((x, ay))
        # vertical
        y_start, y_end = sorted((ay, by))
        for y in range(y_start, y_end + 1):
            tiles.add((bx, y))
        return tiles

    def connect_rooms(self):
        self.corridor_tiles.clear()
        if len(self.rooms) < 2:
            return
        # sort by center x to create a simple chain
        rooms_sorted = sorted(self.rooms, key=lambda r: r.center()[0])
        for i in range(len(rooms_sorted) - 1):
            a = rooms_sorted[i].center()
            b = rooms_sorted[i + 1].center()
            self.corridor_tiles.update(self._create_corridor_between(a, b))

    def draw(self, tile_size: int = 16):
        # draw rooms (walls) and corridors
        # corridors first (different color)
        for (x, y) in self.corridor_tiles:
            pyray.draw_rectangle(x * tile_size, y * tile_size, tile_size, tile_size, pyray.DARKGRAY)
        for room in self.rooms:
            room.draw(tile_size=tile_size, color=pyray.RED)
