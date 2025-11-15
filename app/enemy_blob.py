import math
import pyray as rl
from app import assets
from app import bullet, sprite

class EnemyBlob(sprite.Sprite):
    def __init__(self, display, x, y, health, weight, scaleXframe=10):

        self.weight = weight
        self.health = health

        self.scaleXframe = scaleXframe
        self.img = self.get_sprite()
        super().__init__(display, self.scaleXframe)
        self.x, self.y = x, y
        self.speed = 0.55
        self.detection_radius = 100
        self.shittin = False

        self.shooting_range = 26


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
        px, py = self.display.player.x, self.display.player.y
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        self.cooldown_timer -= 1
        if self.cooldown_timer <= 0 and dist <= self.shooting_range + 5:
            self.shittin = True
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

        if self.shooting_range < dist <= self.detection_radius and not self.shittin:
            nx = dx / dist
            ny = dy / dist
            self.x += nx * self.speed
            self.y += ny * self.speed

            self.frame_timer += rl.get_frame_time()
            while self.frame_timer >= self.frame_duration:
                self.frame_timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_of_frames

        if self.shittin:
            print(self.current_frame)
            if self.current_frame == self.num_of_frames - 9:
                self.game.music_manager.play_sound(assets.sounds["Plum"])
            if self.current_frame == self.num_of_frames - 1:
                self.shoot()
                self.shittin = False
                self.img = self.get_sprite()
                self.num_of_frames = int(self.img.height / self.img.width)
                self.frame_width = int(self.img.width)
                self.frame_height = int(self.img.height / self.num_of_frames)
                self.current_frame = 0
                self.frame_timer = 0.0
                self.frame_duration = 0.08

        # postępuj klatkami także podczas animacji strzału
        if self.current_frame != 0 or self.shittin:
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
        b = bullet.Bullet(self.display, self.x, self.y - 5, 0, 0, "player")
        self.display.enemy_bullets.append(b)
        self.cooldown_timer = 375

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        self.display.enemy_blobs.remove(self)
        self.display.objects.remove(self)
        del self