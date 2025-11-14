import pyray as rl
import app
from app import assets

class Player:
    def __init__(self, game):
        self.game = game
        self.img = assets.images["Jeff"]
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
        self.maxSpeed = 0.12
        self.acceleration = 0.0002
        self.gameHeight = self.game.height
        self.gameWidth = self.game.width
        self.hpHeight = 30

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

    def render(self):
        scale = 20 / float(self.img.width)

        rl.draw_texture_ex(self.img, rl.Vector2(float(self.x), float(self.y)), 0.0,
                           scale, rl.WHITE)