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
        print(self.img.width, self.img.height)
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
        self.target_x = None
        self.target_y = None

    def get_sprite(self):
        if self.weight in [0, 92]:
            return assets.images["movingblob"]
        elif self.weight == 1:
            print("Loading Hydrogen sprite")
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
        if self.leader == None:
            scale = 14.0 / float(self.frame_width)
        else:
            scale = 6.0 / float(self.frame_width)

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
                for friend in self.game.player.friends:
                    friend.set_destination(15)
        rl.draw_texture_pro(self.img, src, dst, origin, angle, rl.WHITE)

    def set_destination(self, radius):
        x = rl.get_random_value(- radius, radius)
        y = rl.get_random_value(- radius, radius)
        self.target_x = self.leader.x + x
        self.target_y = self.leader.y + y