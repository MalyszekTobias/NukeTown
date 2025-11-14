import pyray as rl
from app.displays.base import BaseDisplay
from app.ui import button
class StartDisplay(BaseDisplay):

    def __init__(self, game):
        super().__init__(game)
        self.button_to_2dgame = button.Button(self.game, 200, 100, 100, 100, "click to enter 2dgame", 20, rl.WHITE, rl.GRAY, rl.GREEN, rl.RED)
        self.buttons = [self.button_to_2dgame]
        self.focus_index = 0

    def render(self):
        super().render()
        rl.draw_fps(10, 10)
        for b in self.buttons:
            b.draw()

    def update(self):
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
            self.game.change_display(self.game.twodgame)
