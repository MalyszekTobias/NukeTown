import math
import pyray as rl

import app.atom
from app import assets
from app import bullet, sprite


class EnemyBlob(sprite.Sprite):
    def __init__(self, display, x, y, health, weight, scaleXframe=10, room=None):

        self.weight = weight
        self.health = health

        self.scaleXframe = scaleXframe
        self.img = self.get_sprite()
        self.room = room
        # print(self.img.width, self.img.height)
        # print(self.img)
        super().__init__(display, self.scaleXframe)
        self.x, self.y = x, y
        self.speed = 0.55
        self.detection_radius = 100
        self.shootin = False

        self.shooting_range = 26


        self.cooldown_timer = 0

        # collision/radius used by atom; add here so enemy blobs also collide with walls/gates
        self.radius = 10
        self.rect = rl.Rectangle(0, 0, self.radius, self.radius)


    def get_sprite(self):
        if self.weight in [0, 92]:
            return assets.images["movingblob"]
        elif self.weight == 1:
            return assets.images["Hydrogen"]
        elif self.weight == 2:
            return assets.images["Helium"]
        elif self.weight == 8:
            return assets.images["Oxygen"]
        elif self.weight == 16:
            return assets.images["Sulphur"]
        elif self.weight == 11:
            return assets.images["Sodium"]
        elif self.weight == 26:
            return assets.images["Iron"]
        elif self.weight == 30:
            return assets.images["Zinc"]
        elif self.weight == 56:
            return assets.images["Barium"]
        elif self.weight == 36:
            return assets.images["Krypton"]
        return assets.images["movingblob"]
    def update(self, rooms=None, corridor_tiles=None):
        # update rect for collision checks
        self.rect = rl.Rectangle(self.x - self.radius / 2, self.y - self.radius / 2,
                                self.radius, self.radius)

        px, py = self.display.player.x, self.display.player.y
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        self.cooldown_timer -= 1
        if self.cooldown_timer <= 0 and dist <= self.shooting_range + 5:
            self.shootin = True
            self.img = assets.images["Bullet_Bad_Create"]
            self.num_of_frames = int(self.img.height / self.img.width)
            self.frame_width = int(self.img.width)
            self.frame_height = int(self.img.height / self.num_of_frames)
            self.current_frame = 0
            self.frame_timer = 0.0
            self.frame_duration = 0.08
            self.cooldown_timer = 70  # naprawione: używaj cooldown_timer

        if dist == 0:
            return

        # remember previous position so we can prevent leaving corridors
        old_x, old_y = self.x, self.y

        if self.shooting_range < dist <= self.detection_radius:
            nx = dx / dist
            ny = dy / dist
            self.x += nx * self.speed
            self.y += ny * self.speed

            self.frame_timer += rl.get_frame_time()
            while self.frame_timer >= self.frame_duration:
                self.frame_timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_of_frames

        if self.shootin:
            # print(self.current_frame)
            if self.current_frame == self.num_of_frames - 9:
                self.game.music_manager.play_sound(assets.sounds["Plum"])
            if self.current_frame == self.num_of_frames - 1:
                self.shoot()
                self.shootin = False
                self.img = self.get_sprite()
                self.num_of_frames = int(self.img.height / self.img.width)
                self.frame_width = int(self.img.width)
                self.frame_height = int(self.img.height / self.num_of_frames)
                self.current_frame = 0
                self.frame_timer = 0.0
                self.frame_duration = 0.08

        # postępuj klatkami także podczas animacji strzału
        if self.current_frame != 0 or self.shootin:
            self.frame_timer += rl.get_frame_time()
            while self.frame_timer >= self.frame_duration:
                self.frame_timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_of_frames
                if self.current_frame == 0:
                    self.frame_timer = 0.0
                    break
        else:
            self.current_frame = 0
            self.frame_timer = 0.0

        # tile logic: prevent leaving corridor tiles unless entering a room
        tile_size = 16
        if corridor_tiles is not None:

            old_tile = (int(old_x) // tile_size, int(old_y) // tile_size)
            new_tile = (int(self.x) // tile_size, int(self.y) // tile_size)

            was_in_corridor = old_tile in corridor_tiles if old_tile is not None else False
            now_in_corridor = new_tile in corridor_tiles if new_tile is not None else False

            entering_room = False
            if rooms and new_tile is not None:
                for room in rooms:
                    # allow entering room background tiles
                    if new_tile in room.background_tiles():
                        entering_room = True
                        break

            # if we started in corridor and tried to move to a non-corridor tile that is not a room, revert
            if was_in_corridor and (not now_in_corridor) and (not entering_room):
                self.x, self.y = old_x, old_y

        # resolve wall/gate collisions like Atom
        self._resolve_wall_collisions(rooms, 16, corridor_tiles)

        for player_bullet in self.display.player_bullets:
            if rl.check_collision_circles(rl.Vector2(self.x, self.y), self.radius / 2,
                                          rl.Vector2(player_bullet.x, player_bullet.y), player_bullet.radius / 2):
                self.take_damage(player_bullet.damage)
                self.display.player_bullets.remove(player_bullet)
                self.game.music_manager.play_sound(assets.sounds["shot"])


    def shoot(self):
        b = bullet.Bullet(self.display, self.x, self.y - 5, 0, 0, 10, "player")
        self.display.enemy_bullets.append(b)
        self.cooldown_timer = 375

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()
    def render(self):
        # print('rendering enemy', self.x, self.y)
        scale = 10 / float(self.frame_width)
        src = rl.Rectangle(0.0, float(self.frame_height * self.current_frame),
                           float(self.frame_width), float(self.frame_height))
        dst_w = float(self.frame_width) * scale
        dst_h = float(self.frame_height) * scale
        dst_x = float(self.x) - dst_w / 2.0
        dst_y = float(self.y) - dst_h / 2.0
        dst = rl.Rectangle(dst_x, dst_y, dst_w, dst_h)
        origin = rl.Vector2(0.0, 0.0)
        angle = 0
        rl.draw_texture_pro(self.img, src, dst, origin, angle, rl.WHITE)


    def die(self):
        a = app.atom.Atom(self.display, self.weight, self.display.player, self.x * 16, self.y * 16)
        if not self.room == None:
            self.room.busy = 2
        if self.display.player.hp != self.display.player.max_hp:
            self.display.player.hp += 10
            self.display.player.current_HP_frame = int(self.display.player.hp / self.display.player.max_hp * 10) - 1
        self.display.player.friends.append(a)
        self.game.atomic_masses.append(self.weight)
        try:
            self.display.enemies.remove(self)
            self.display.game_objects.remove(self)
            del self
        except:
            pass

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
