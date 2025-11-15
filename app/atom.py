# app/atom.py
import math

import pyray as rl
import app
from app import assets, sprite

class Atom(sprite.Sprite):
    def __init__(self, display, weight, leader, x, y, scaleXframewidth=6):

        self.x = x
        self.y = y
        self.weight = weight
        self.leader = leader
        self.img = self.get_sprite()
        self.radius = 10
        super().__init__(display, scaleXframewidth)
        self.rect = rl.Rectangle(0, 0, self.radius, self.radius)

        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.clicked = False
        self.velUp = 0
        self.velRight = 0
        self.maxSpeed = 0.5
        self.acceleration = 0.012
        self.run_tilt = 4
        self.target_x = None
        self.target_y = None
        self.cooldown = 0
        self.shootin = False
        # Distance beyond which follower atoms skip collisions to save perf and avoid snagging far away
        self._collision_disable_distance = 40.0

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
        return assets.images.get("movingblob")
    def movement(self):
        if self.up and self.velUp < self.maxSpeed:
            self.velUp += self.acceleration
        if self.velUp > 0 and not self.up:
            if self.velUp >= self.acceleration:
                self.velUp -= self.acceleration
            else:
                self.velUp = 0

        if self.down and self.velUp > -self.maxSpeed:
            self.velUp -= self.acceleration
        if self.velUp < 0 and not self.down:
            if self.velUp <= -self.acceleration:
                self.velUp += self.acceleration
            else:
                self.velUp = 0

        if self.right and self.velRight < self.maxSpeed:
            self.velRight += self.acceleration
        if self.velRight > 0 and not self.right:
            if self.velRight >= self.acceleration:
                self.velRight -= self.acceleration
            else:
                self.velRight = 0

        if self.left and self.velRight > -self.maxSpeed:
            self.velRight -= self.acceleration
        if self.velRight < 0 and not self.left:
            if self.velRight <= -self.acceleration:
                self.velRight += self.acceleration
            else:
                self.velRight = 0

        self.y -= self.velUp



        self.x += self.velRight

    def _is_far_from_player(self):
        """Return True if this atom (when follower) is far enough from player to skip collisions."""
        # Only followers (leader set) get their collisions disabled by distance.
        if self.leader is None:
            return False
        try:
            px, py = self.display.player.x, self.display.player.y
        except Exception:
            return False
        dx = self.x - px
        dy = self.y - py
        return (dx * dx + dy * dy) > (self._collision_disable_distance * self._collision_disable_distance)

    def update(self, rooms = None, corridor_tiles = None):
        self.rect = rl.Rectangle(self.x - self.radius / 2, self.y - self.radius / 2,
                                self.radius, self.radius)
        if self.leader is None:
            if not self.game.gamepad_enabled:
                self.up = rl.is_key_down(rl.KeyboardKey.KEY_W)
                self.down = rl.is_key_down(rl.KeyboardKey.KEY_S)
                self.left = rl.is_key_down(rl.KeyboardKey.KEY_A)
                self.right = rl.is_key_down(rl.KeyboardKey.KEY_D)
            else:
                self.up = self.game.left_joystick_y < -self.game.gamepad_deadzone
                self.down = self.game.left_joystick_y > self.game.gamepad_deadzone
                self.left = self.game.left_joystick_x < -self.game.gamepad_deadzone
                self.right = self.game.left_joystick_x > self.game.gamepad_deadzone
        self.cooldown -= 1
        if rl.is_mouse_button_pressed(0):
            if self.cooldown <= 0:
                self.shootin = True
                self.img = assets.images["Bullet_Good_Create"]
                self.num_of_frames = int(self.img.height / self.img.width)
                self.frame_width = int(self.img.width)
                self.frame_height = int(self.img.height / self.num_of_frames)
                self.current_frame = 0
                self.frame_timer = 0.0
                self.frame_duration = 0.08
                self.cooldown = 70
        elif self.target_x != None and self.target_y != None:
            if self.x < self.target_x:
                self.right = True
                self.left = False
            elif self.x > self.target_x:
                self.left = True
                self.right = False
            if self.y > self.target_y:
                self.up = True
                self.down = False
            elif self.y < self.target_y:
                self.down = True
                self.up = False

            if abs(self.x - self.target_x) < 8:
                self.left = False
                self.right = False
            if abs(self.y - self.target_y) < 8:
                self.up = False
                self.down = False

        # remember previous position so we can prevent leaving corridors
        old_x, old_y = self.x, self.y

        self.movement()

        # tile logic: prevent leaving corridor tiles unless entering a room
        tile_size = 16
        # Skip corridor constraints when far from player (followers only)
        far_from_player = self._is_far_from_player()
        if corridor_tiles is not None and not far_from_player:

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
                # cancel velocities so we don't push against the boundary
                self.velUp = 0
                self.velRight = 0
                # stop movement inputs so atom won't immediately try again
                self.up = self.down = self.left = self.right = False

        dt = rl.get_frame_time()
        moving = any((self.up, self.down, self.left, self.right)) or abs(self.velUp) > 1e-6 or abs(self.velRight) > 1e-6
        if self.shootin:
            self.frame_timer += dt
            while self.frame_timer >= self.frame_duration:
                self.frame_timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_of_frames
            if self.leader == None and self.current_frame == self.num_of_frames - 9:
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
        else:
            if moving:
                self.frame_timer += dt
                while self.frame_timer >= self.frame_duration:
                    self.frame_timer -= self.frame_duration
                    self.current_frame = (self.current_frame + 1) % self.num_of_frames
            else:
                # If we're mid-animation, continue advancing frames until we wrap back to frame 0,
                # then stop there. If already at frame 0, keep it idle.
                if self.current_frame != 0:
                    self.frame_timer += dt
                    while self.frame_timer >= self.frame_duration:
                        self.frame_timer -= self.frame_duration
                        self.current_frame = (self.current_frame + 1) % self.num_of_frames
                        if self.current_frame == 0:
                            self.frame_timer = 0.0
                            break
                else:
                    self.current_frame = 0
                    self.frame_timer = 0.0
        # Skip wall/gate collision resolution when far from player (followers only)
        if not far_from_player:
            self._resolve_wall_collisions(rooms, 16, corridor_tiles)

    def _resolve_wall_collisions(self, rooms, tile_size, corridor_tiles=None):
        """Rect vs rect: push atom out of first colliding wall rect."""
        if not rooms:
            return
        ax, ay, aw, ah = self.rect.x, self.rect.y, self.rect.width, self.rect.height

        # Check room wall collisions
        for room in rooms:
            for (wx, wy, ww, wh) in room.collision_rects(tile_size, corridor_tiles):
                # AABB overlap test
                if ax < wx + ww and ax + aw > wx and ay < wy + wh and ay + ah > wy:
                    # compute penetration depths on each side
                    pen_left = (ax + aw) - wx
                    pen_right = (wx + ww) - ax
                    pen_top = (ay + ah) - wy
                    pen_bottom = (wy + wh) - ay
                    # choose smallest penetration axis
                    min_pen = min(pen_left, pen_right, pen_top, pen_bottom)
                    if min_pen == pen_left:
                        # push atom left
                        ax -= pen_left
                    elif min_pen == pen_right:
                        ax += pen_right
                    elif min_pen == pen_top:
                        ay -= pen_top
                    else:  # pen_bottom
                        ay += pen_bottom
                    # write back center from rect
                    self.x = ax + aw / 2
                    self.y = ay + ah / 2
                    return

        # Check closed gate collisions
        try:
            mp = getattr(self.display, 'map', None)
            if mp and getattr(mp, 'gates', None):
                for gate in mp.gates.values():
                    if not gate.is_open:
                        wx, wy, ww, wh = gate.collision_rect()
                        # AABB overlap test
                        if ax < wx + ww and ax + aw > wx and ay < wy + wh and ay + ah > wy:
                            # compute penetration depths on each side
                            pen_left = (ax + aw) - wx
                            pen_right = (wx + ww) - ax
                            pen_top = (ay + ah) - wy
                            pen_bottom = (wy + wh) - ay
                            # choose smallest penetration axis
                            min_pen = min(pen_left, pen_right, pen_top, pen_bottom)
                            if min_pen == pen_left:
                                ax -= pen_left
                            elif min_pen == pen_right:
                                ax += pen_right
                            elif min_pen == pen_top:
                                ay -= pen_top
                            else:  # pen_bottom
                                ay += pen_bottom
                            # write back center from rect
                            self.x = ax + aw / 2
                            self.y = ay + ah / 2
                            return
        except Exception:
            pass

    def render(self):

        if self.x == 0 and self.y == 0:
            self.x = self.display.player.x
            self.y = self.display.player.y
        if self.leader == None:
            scale = (self.scaleXframewidth + 8) / float(self.frame_width)
        else:
            scale = self.scaleXframewidth / float(self.frame_width)

        src = rl.Rectangle(0.0, float(self.frame_height * self.current_frame),
                           float(self.frame_width), float(self.frame_height))
        dst_w = float(self.frame_width) * scale
        dst_h = float(self.frame_height) * scale
        dst_x = float(self.x) - dst_w / 2.0
        dst_y = float(self.y) - dst_h / 2.0
        dst = rl.Rectangle(dst_x, dst_y, dst_w, dst_h)
        origin = rl.Vector2(0.0, 0.0)
        angle = 0
        if self.velRight > 0:
            angle = self.run_tilt
        elif self.velRight < 0:
            angle = -self.run_tilt
        if self.leader == None:
            if self.velRight > 0.09 or self.velRight < -0.09 or self.velUp > 0.09 or self.velUp < -0.09:
                for friend in self.display.player.friends:
                    friend.set_destination(15)
        rl.draw_texture_pro(self.img, src, dst, origin, angle, rl.WHITE)
        rl.draw_rectangle_lines(int(self.rect.x), int(self.rect.y), int(self.rect.width), int(self.rect.height), rl.RED)

    def shoot(self):
        mouse_pos = rl.get_mouse_position()
        world_pos = rl.get_screen_to_world_2d(mouse_pos, self.display.camera.camera)
        mouse_x, mouse_y = world_pos.x, world_pos.y
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        vel_right = (dx / dist)
        vel_up = (dy / dist)
        bullet = app.bullet.Bullet(self.display, self.x, self.y - 5, vel_right, vel_up, self.weight, "enemy")
        self.display.player_bullets.append(bullet)


    def set_destination(self, radius):
        x = rl.get_random_value(- radius, radius)
        y = rl.get_random_value(- radius, radius)
        self.target_x = self.leader.x + x
        self.target_y = self.leader.y + y

