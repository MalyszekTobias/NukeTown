import random
import pyray as rl

from app import assets
from app.sprite import Sprite


class RussianWalker(Sprite):
    """
    Simple NPC that walks randomly and switches texture based on facing direction.
    Collides with walls and respects corridor tiles similarly to Atom.
    """

    def __init__(self, display, x, y, scaleXframewidth=10):
        # Start facing down by default
        self.img = assets.images["RusDown"]
        super().__init__(display, scaleXframewidth)
        self.x = float(x)
        self.y = float(y)

        self.speed = 0.8
        self.radius = 13
        self.rect = rl.Rectangle(self.x - self.radius / 2, self.y - self.radius / 2, self.radius, self.radius)

        self.dir = rl.Vector2(0.0, 1.0)
        self._choose_new_dir_time = 0.0
        self._min_dir_time = 0.6
        self._max_dir_time = 2.0
        self._touch_cooldown = 0.0

        self._refresh_frame_metrics()

    def _refresh_frame_metrics(self):
        self.num_of_frames = max(1, int(self.img.height / max(1, self.img.width)))
        self.frame_width = int(self.img.width)
        self.frame_height = int(self.img.height / self.num_of_frames)
        self.current_frame = min(getattr(self, "current_frame", 0), self.num_of_frames - 1)
        self.frame_timer = 0.0
        self.frame_duration = 0.12

    def _set_orientation_texture(self, vx: float, vy: float):
        # Determine primary axis
        if abs(vx) >= abs(vy):
            new_img = assets.images["RusRight"] if vx > 0 else assets.images["RusLeft"]
        else:
            new_img = assets.images["RusDown"] if vy > 0 else assets.images["RusUp"]
        if new_img is not self.img:
            self.img = new_img
            self._refresh_frame_metrics()

    def _pick_random_direction(self):
        choices = [
            rl.Vector2(1, 0), rl.Vector2(-1, 0), rl.Vector2(0, 1), rl.Vector2(0, -1),
            rl.Vector2(1, 1), rl.Vector2(-1, 1), rl.Vector2(1, -1), rl.Vector2(-1, -1)
        ]
        d = random.choice(choices)
        # normalize diagonals
        length = max(1.0, (d.x * d.x + d.y * d.y) ** 0.5)
        self.dir = rl.Vector2(d.x / length, d.y / length)
        self._choose_new_dir_time = random.uniform(self._min_dir_time, self._max_dir_time)
        self._set_orientation_texture(self.dir.x, self.dir.y)

    def _resolve_wall_collisions(self, rooms, tile_size, corridor_tiles=None):
        if not rooms:
            return
        ax, ay, aw, ah = self.rect.x, self.rect.y, self.rect.width, self.rect.height

        for room in rooms:
            for (wx, wy, ww, wh) in room.collision_rects(tile_size, corridor_tiles):
                if ax < wx + ww and ax + aw > wx and ay < wy + wh and ay + ah > wy:
                    pen_left = (ax + aw) - wx
                    pen_right = (wx + ww) - ax
                    pen_top = (ay + ah) - wy
                    pen_bottom = (wy + wh) - ay
                    min_pen = min(pen_left, pen_right, pen_top, pen_bottom)
                    if min_pen == pen_left:
                        ax -= pen_left
                    elif min_pen == pen_right:
                        ax += pen_right
                    elif min_pen == pen_top:
                        ay -= pen_top
                    else:
                        ay += pen_bottom
                    self.x = ax + aw / 2
                    self.y = ay + ah / 2
                    return

        try:
            mp = getattr(self.display, 'map', None)
            if mp and getattr(mp, 'gates', None):
                for gate in mp.gates.values():
                    if not gate.is_open:
                        wx, wy, ww, wh = gate.collision_rect()
                        if ax < wx + ww and ax + aw > wx and ay < wy + wh and ay + ah > wy:
                            pen_left = (ax + aw) - wx
                            pen_right = (wx + ww) - ax
                            pen_top = (ay + ah) - wy
                            pen_bottom = (wy + wh) - ay
                            min_pen = min(pen_left, pen_right, pen_top, pen_bottom)
                            if min_pen == pen_left:
                                ax -= pen_left
                            elif min_pen == pen_right:
                                ax += pen_right
                            elif min_pen == pen_top:
                                ay -= pen_top
                            else:
                                ay += pen_bottom
                            self.x = ax + aw / 2
                            self.y = ay + ah / 2
                            return
        except Exception:
            pass

    def update(self):
        dt = rl.get_frame_time()
        self._touch_cooldown = max(0.0, self._touch_cooldown - dt)
        self.frame_timer += dt
        while self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_of_frames
            if self.current_frame == 0:
                self.frame_timer = 0.0
                break

        self._choose_new_dir_time -= dt
        if self._choose_new_dir_time <= 0:
            self._pick_random_direction()

        step_x = self.dir.x * self.speed
        step_y = self.dir.y * self.speed
        old_x, old_y = self.x, self.y

        self.x += step_x
        self.y += step_y

        self.rect = rl.Rectangle(self.x - self.radius / 2, self.y - self.radius / 2, self.radius, self.radius)

        mp = getattr(self.display, 'map', None)
        if mp is not None:
            tile_size = getattr(mp, 'tile_size', 16)
            rooms = getattr(mp, 'rooms', None)
            corridor_tiles = getattr(mp, 'corridor_tiles', None)

            if corridor_tiles is not None:
                old_tile = (int(old_x) // tile_size, int(old_y) // tile_size)
                new_tile = (int(self.x) // tile_size, int(self.y) // tile_size)

                was_in_corridor = old_tile in corridor_tiles if old_tile is not None else False
                now_in_corridor = new_tile in corridor_tiles if new_tile is not None else False

                entering_room = False
                if rooms and new_tile is not None:
                    for rm in rooms:
                        if new_tile in rm.background_tiles():
                            entering_room = True
                            break

                if was_in_corridor and (not now_in_corridor) and (not entering_room):
                    self.x, self.y = old_x, old_y
                    self._choose_new_dir_time = 0

            self.rect = rl.Rectangle(self.x - self.radius / 2, self.y - self.radius / 2, self.radius, self.radius)
            self._resolve_wall_collisions(rooms, getattr(mp, 'tile_size', 16), getattr(mp, 'corridor_tiles', None))

        if abs(step_x) > 1e-4 or abs(step_y) > 1e-4:
            self._set_orientation_texture(step_x, step_y)

        self.rect = rl.Rectangle(self.x - self.radius / 2, self.y - self.radius / 2, self.radius, self.radius)

        try:
            pl = self.display.player
            if hasattr(pl, 'spawn_point') and self._touch_cooldown <= 0.0:
                if rl.check_collision_circles(rl.Vector2(self.x, self.y), self.radius / 2,
                                              rl.Vector2(pl.x, pl.y), getattr(pl, 'radius', 10) / 2):
                    sx, sy = pl.spawn_point
                    pl.x, pl.y = sx, sy
                    if hasattr(pl, 'velUp'):
                        pl.velUp = 0
                    if hasattr(pl, 'velRight'):
                        pl.velRight = 0
                    self._touch_cooldown = 0.6
        except Exception:
            pass
