# app/atom.py
import pyray as rl
import app
from app import assets

class Atom:
    def __init__(self, game, weight, leader):
        self.game = game
        self.weight = weight
        self.leader = leader
        self.img = self.get_sprite()
        self.num_of_frames = int(self.img.height / self.img.width)
        self.frame_width = int(self.img.width)
        self.frame_height = int(self.img.height / self.num_of_frames)
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.08
        self.radius = 40
        self.x = 100
        self.y = 100
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.clicked = False
        self.velUp = 0
        self.velRight = 0
        self.maxSpeed = 0.09
        self.acceleration = 0.002
        self.gameHeight = self.game.height
        self.gameWidth = self.game.width
        self.hpHeight = 30
        self.run_tilt = 4

    def get_sprite(self):
        if self.weight == 0:
            return assets.images["movingblob"]
        elif self.weight == 1:
            return assets.images["movingblob"]

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

        if self.velUp < 0:
            if self.y < self.gameHeight - self.radius:
                if self.y < self.gameHeight - self.radius + self.velUp:
                    self.y -= self.velUp
                else:
                    self.y = self.gameHeight - self.radius
        else:
            if self.y > self.radius + self.hpHeight:
                if self.y > self.radius + self.velUp + self.hpHeight:
                    self.y -= self.velUp
                else:
                    self.y = self.radius + self.hpHeight

        if self.velRight < 0:
            if self.x > self.radius:
                if self.x > self.radius - self.velRight:
                    self.x += self.velRight
                else:
                    self.x = self.radius
        else:
            if self.x < self.gameWidth - self.radius:
                if self.x < self.gameWidth - self.radius - self.velRight:
                    self.x += self.velRight
                else:
                    self.x = self.gameWidth - self.radius

    def update(self):
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
        self.movement()

        dt = rl.get_frame_time()
        moving = any((self.up, self.down, self.left, self.right)) or abs(self.velUp) > 1e-6 or abs(self.velRight) > 1e-6

        if moving:
            self.frame_timer += dt
            while self.frame_timer >= self.frame_duration:
                self.frame_timer -= self.frame_duration
                self.current_frame = (self.current_frame + 1) % self.num_of_frames
        else:
            self.current_frame = 0
            self.frame_timer = 0.0

    def render(self):
        scale = 20.0 / float(self.frame_width)
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
        rl.draw_texture_pro(self.img, src, dst, origin, angle, rl.WHITE)