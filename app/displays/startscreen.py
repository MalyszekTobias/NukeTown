from itertools import count

import pyray as rl
from app.displays.base import BaseDisplay
from app.ui import button, text
import itertools, math
from app import sprite


class StartDisplay(BaseDisplay):

    def __init__(self, game):
        super().__init__(game)
        self.button_to_2dgame = button.Button(self.game, self.game.width//4, self.game.height//2 + 100, 150, 50, "BEGIN", 50, rl.WHITE, (rl.GRAY[0], rl.GRAY[0],rl.GRAY[0], 0), rl.RED, rl.RED)
        self.buttons = [self.button_to_2dgame]
        self.focus_index = 0
        self.jumping_mascot = sprite.Jumping_sprite_test(self)
        self.fader = itertools.cycle(self.color_cycle())
        self.start = False
        self.speed = 25
        self.counter = 0
        self.text_x = 100

    def render(self):


        if self.start:
            self.counter += 1
            self.button_to_2dgame.move_out(self.speed)
            self.jumping_mascot.move_out(self.speed)
            self.text_x -= self.speed

        if self.counter >= 77:
            self.game.change_display(self.game.chapter2_display)




        r, g, b = next(self.fader)
        self.jumping_mascot.tint = (r, g, b, 255)
        text.draw_text('NUKE TOWN', self.text_x, self.game.height // 2 - 100, 200, (r, g, b, 255))
        self.button_to_2dgame.text_color = (r, g, b, 255)
        for b in self.buttons:
            b.draw()

        super().render()

    def color_cycle(self):
        period = 5000
        t = 0
        while True:
            # red goes 0 → 255 → 0
            red = int((math.sin((t * 2 * math.pi / period) + math.pi/2) + 1) * 127.5)

            green = 255
            blue = 0

            yield (red, green, blue)
            t += 1



    def update(self):
        super().update()
        if self.game.gamepad_enabled:
            y = getattr(self.game, "left_joystick_y", 0.0)
            if y < -self.game.gamepad_deadzone:
                self.focus_index = max(0, self.focus_index - 1)
            elif y > self.game.gamepad_deadzone:
                self.focus_index = min(len(self.buttons) - 1, self.focus_index + 1)
        else:
            self.focus_index = -1
        for i, b in enumerate(self.buttons):
            b.update(focused=(i == self.focus_index))
        if self.button_to_2dgame.is_clicked:
            self.start = True
