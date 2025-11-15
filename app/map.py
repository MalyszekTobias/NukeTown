# python
# File: app/map.py
import pyray
from typing import List, Set, Tuple, Dict, Any
from app.room import Room

Tile = Tuple[int, int]
Light = Dict[str, Any]


class Map:
    def __init__(self, game):
        self.game = game
        self.rooms: List[Room] = []
        self.corridor_tiles: Set[Tile] = set()
        self.tile_size: int = 16
        # gates keyed by tile coordinate -> Gate instance
        self.gates = {}
        self.lights: List[Light] = []

    def add_light(self, x: float, y: float, radius: float, color: pyray.Color):
        self.lights.append({'pos': pyray.Vector2(x, y), 'radius': radius, 'color': color})

    def add_room(self, room: Room):
        self.rooms.append(room)
        return room

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
    def connect_two_rooms(self,room1,room2):
        # self.corridor_tiles.clear()
        if len(self.rooms) < 2:
            return
        # sort by center x to create a simple chain
        rooms_sorted = [room1,room2]
        for i in range(len(rooms_sorted) - 1):
            a = rooms_sorted[i].center()
            b = rooms_sorted[i + 1].center()
            self.corridor_tiles.update(self._create_corridor_between(a, b))
        # After corridor generation, populate gates for removed wall tiles
        try:
            from app.gate import Gate
        except Exception:
            Gate = None
        if Gate:
            # create gates for wall tiles that were removed by corridors
            for room in self.rooms:
                all_walls = room.wall_tiles()
                visible_walls = room.wall_tiles(exclude_tiles=self.corridor_tiles)
                removed = all_walls - visible_walls
                for tile in removed:
                    if tile not in self.gates:
                        self.gates[tile] = Gate(self, tile, room_ref=room, is_open=False)
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
        # After corridor generation, populate gates for removed wall tiles
        try:
            from app.gate import Gate
        except Exception:
            Gate = None
        if Gate:
            # create gates for wall tiles that were removed by corridors
            for room in self.rooms:
                all_walls = room.wall_tiles()
                visible_walls = room.wall_tiles(exclude_tiles=self.corridor_tiles)
                removed = all_walls - visible_walls
                for tile in removed:
                    if tile not in self.gates:
                        self.gates[tile] = Gate(self, tile, room_ref=room, is_open=False)

    def check_collision_point(self, x: float, y: float) -> bool:
        """Check if a point collides with walls or closed gates. Returns True if collision detected."""
        for room in self.rooms:
            for (wx, wy, ww, wh) in room.collision_rects(self.tile_size, self.corridor_tiles):
                if wx <= x <= wx + ww and wy <= y <= wy + wh:
                    return True

        for gate in self.gates.values():
            if not gate.is_open:
                gx, gy, gw, gh = gate.collision_rect()
                if gx <= x <= gx + gw and gy <= y <= gy + gh:
                    return True

        return False

    def draw(self):
        tile_size = self.tile_size
        # draw rooms (walls) and corridors
        # corridors first (different color)
        for (x, y) in self.corridor_tiles:
            pyray.draw_rectangle(x * tile_size, y * tile_size, tile_size, tile_size, pyray.DARKGRAY)
        for room in self.rooms:
            room.draw(tile_size=tile_size, color=pyray.RED, corridor_tiles=self.corridor_tiles)
        # draw gates on top of rooms/corridors
        for g in list(self.gates.values()):
            try:
                g.draw(tile_size)
            except Exception:
                pass
