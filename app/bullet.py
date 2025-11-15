import math

import pyray as rl
from app import assets
class Bullet:
    def __init__(self, display, x, y, velRight, velUp, target):
        self.display = display
        self.game = display.game
        self.x, self.y = x, y
        self.speed = 0.4
        self.radius = 1
        self.velRight = velRight
        self.velUp = velUp
        self.target = target
        self.lifespan = 300
        if target == "enemy":
            self.img = assets.images["Bullet_Good"]
        else:
            self.img = assets.images["Bullet_Bad"]
        self.num_of_frames = int(self.img.height / self.img.width)
        self.frame_width = int(self.img.width)
        self.frame_height = int(self.img.height / self.num_of_frames)
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.08

    def _aim_at_player(self):
        # pobierz pozycję gracza (weź pod uwagę kamerę, jeśli istnieje)
        player_x = self.display.player.x
        player_y = self.display.player.y
        dx = player_x - self.x
        dy = player_y - self.y
        angle = math.atan2(dy, dx)
        self.velRight = math.cos(angle) * self.speed
        self.velUp = math.sin(angle) * self.speed

    def update(self):
        dt = rl.get_frame_time()
        self.frame_timer += dt
        while self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_of_frames

        self.x += self.velRight
        self.y += self.velUp
        if self.target == "player":
            self._aim_at_player()
            self.lifespan -= 1
            x, y = self.display.player.x, self.display.player.y

            if self.lifespan == 10:
                self.img = assets.images["Bullet_Bad_Explode"]
                self.num_of_frames = int(self.img.height / self.img.width)
                self.frame_width = int(self.img.width)
                self.frame_height = int(self.img.height / self.num_of_frames)
                self.current_frame = 0
                self.frame_timer = 0.0
                self.frame_duration = 0.02
            if self.frame_duration == 0.02 and self.current_frame == self.num_of_frames - 1:
                self.display.enemy_bullets.remove(self)
                del  self
                return

    def render(self):
        scale = 0.08
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
