# python
import pyray
import random
import json
import os
from typing import Dict, Tuple, Optional, Any, Set
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

    def randomize_floors(
        self,
        cracked_chance: float = 0.02,
        flower1_chance: float = 0.005,
        flower2_chance: float = 0.005,
        flower3_chance: float = 0.005,
        normal_floor_chance: float = 1 - 0.02 - 0.01 - 0.01 - 0.01,
        seed: Optional[int] = None,
    ) -> None:
        """
        Populate `_tile_states` using exclusive probabilities. The chances are
        treated cumulatively and at most one state is assigned per tile.
        Order of evaluation: floor_flower_1 -> floor_flower_2 -> floor_flower_3 -> cracked.
        """
        rng = random.Random(seed)
        self._tile_states.clear()

        probs = [
            ("floor_flower_1", float(flower1_chance)),
            ("floor_flower_2", float(flower2_chance)),
            ("floor_flower_3", float(flower3_chance)),
            ("cracked", float(cracked_chance)),
            {None, float(normal_floor_chance)},
        ]
        total = sum(p for _, p in probs)
        for tile in self.background_tiles():
            if total <= 0.0:
                continue
            r = rng.random() * total
            acc = 0.0
            for state, p in probs:
                acc += p
                if r < acc:
                    self._tile_states[tile] = state
                    break

        self._floors_initialized = True

    def set_tile_state(self, tile: Tile, state: Optional[str]) -> None:
        """Set tile state (use None to clear). Valid states: 'cracked', 'floor_flower_1/2/3'."""
        if state is None:
            self._tile_states.pop(tile, None)
        else:
            self._tile_states[tile] = state

    def set_cracked(self, tile: Tile, cracked: bool = True) -> None:
        """Compatibility helper to mark a tile cracked or not."""
        if cracked:
            self._tile_states[tile] = "cracked"
        else:
            self._tile_states.pop(tile, None)

    def get_tile_state(self, tile: Tile) -> Optional[str]:
        return self._tile_states.get(tile)

    def is_cracked(self, tile: Tile) -> bool:
        return self._tile_states.get(tile) == "cracked"

    def draw(self, tile_size: int = 16, color: pyray.Color = pyray.RED):
        if not self._floors_initialized:
            seed = (self.x * 73856093) ^ (self.y * 19349663) ^ (self.width * 83492791)
            self.randomize_floors(seed=seed)

        px = self.x * tile_size
        py = self.y * tile_size
        pw = self.width * tile_size
        ph = self.height * tile_size
        pyray.draw_rectangle_lines(px, py, pw, ph, color)

        floor_tex = assets.images.get("Floor_Default")
        cracked_tex = assets.images["Floor_Cracked"]
        flower1_tex = assets.images["Floor_flower_1"]
        flower2_tex = assets.images["Floor_flower_2"]
        flower3_tex = assets.images["Floor_flower_3"]

        if floor_tex:
            for tx, ty in self.background_tiles():
                dest_x = tx * tile_size
                dest_y = ty * tile_size
                state = self.get_tile_state((tx, ty))
                if state == "cracked" and cracked_tex:
                    pyray.draw_texture_ex(cracked_tex, (dest_x, dest_y), 0, 1/4/tile_size, pyray.WHITE)
                elif state == "floor_flower_1" and flower1_tex:
                    pyray.draw_texture_ex(flower1_tex, (dest_x, dest_y), 0, 1/4/tile_size, pyray.WHITE)
                elif state == "floor_flower_2" and flower2_tex:
                    pyray.draw_texture_ex(flower2_tex, (dest_x, dest_y), 0, 1/4/tile_size, pyray.WHITE)
                elif state == "floor_flower_3" and flower3_tex:
                    pyray.draw_texture_ex(flower3_tex, (dest_x, dest_y), 0, 1/4/tile_size, pyray.WHITE)
                else:
                    pyray.draw_texture_ex(floor_tex, (dest_x, dest_y), 0, 1/4/tile_size, pyray.WHITE)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize room with tile states. Uses 'decorations' as list of [x,y,state].
        For backward compatibility, previously used 'cracked' list is not emitted.
        """
        decorations = [[tx, ty, state] for (tx, ty), state in sorted(self._tile_states.items())]
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "decorations": decorations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Room":
        r = cls(int(data["x"]), int(data["y"]), int(data["width"]), int(data["height"]))
        r._tile_states = {}
        # support new 'decorations' format
        for item in data.get("decorations", []):
            if len(item) >= 3:
                a, b, state = item[0], item[1], item[2]
                r._tile_states[(int(a), int(b))] = str(state)
        # backward compatibility: accept old 'cracked' list
        for item in data.get("cracked", []):
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                r._tile_states[(int(item[0]), int(item[1]))] = "cracked"
        r._floors_initialized = True
        return r

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "Room":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
