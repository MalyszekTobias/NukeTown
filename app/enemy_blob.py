import math
import pyray as rl
from app import assets
from app import bullet

class EnemyBlob:
    def __init__(self, game, x, y, health, weight):
        self.weight = weight
        self.health = health
        self.game = game
        self.x, self.y = x, y
        self.speed = 0.55
        self.detection_radius = 100
        self.img = self.get_sprite()
        self.shooting_range = 26

        self.num_of_frames = int(self.img.height / self.img.width)
        self.frame_width = int(self.img.width)
        self.frame_height = int(self.img.height / self.num_of_frames)
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.08
        self.cooldown_timer = 0


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
    def update(self):
        px, py = self.game.player.x, self.game.player.y
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        self.cooldown_timer -= 1
        if self.cooldown_timer <= 0 and dist <= self.shooting_range:
            self.shoot()
        if dist == 0:
            return

        if self.shooting_range < dist <= self.detection_radius:
            nx = dx / dist
            ny = dy / dist
            self.x += nx * self.speed
            self.y += ny * self.speed

            self.frame_timer += rl.get_frame_time()
            while self.frame_timer >= self.frame_duration:
                self.frame_timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_of_frames
        else:
            if self.current_frame != 0:
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

    def shoot(self):
        b = bullet.Bullet(self.game, self.x, self.y, 0, 0, "player")
        self.game.enemy_bullets.append(b)
        self.cooldown_timer = 375

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()
    def render(self):
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
        self.game.enemy_blobs.remove(self)
        del self