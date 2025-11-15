import pyray as rl
from app import assets
class Bullet:
    def __init__(self, game, x, y, velRight, velUp, target):
        self.game = game
        self.x, self.y = x, y
        self.speed = 0.5
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


    def update(self):
        dt = rl.get_frame_time()
        self.frame_timer += dt
        while self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_of_frames
        if self.target == "enemy":
            self.x += self.velRight
            self.y += self.velUp
        else:
            self.lifespan -= 1
            x, y = self.game.player.x, self.game.player.y
            if self.x < x:
                self.x += self.speed
            elif self.x > x:
                self.x -= self.speed
            if self.y < y:
                self.y += self.speed
            elif self.y > y:
                self.y -= self.speed
            if self.lifespan <= 0:
                self.game.enemy_bullets.remove(self)
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
