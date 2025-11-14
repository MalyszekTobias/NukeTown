import pyray as rl

from app.displays import startscreen, twodgame
from app import assets


class Game:
    def __init__(self):
        self.width, self.height = 800, 600
        rl.init_window(self.width, self.height, "raylib template?")
        rl.set_exit_key(rl.KeyboardKey.KEY_NULL)
        assets.load()
        self.bloom_shader = assets.shaders["bloom"]
        self.base_display = startscreen.StartDisplay(self)
        self.twodgame = twodgame.TwoDGameDisplay(self)
        self.current_display = self.base_display

        # controller
        self.gamepad_id = 0
        self.gamepad_deadzone = 0.25
        self.gamepad_enabled = False

    def update_gamepad_status(self):
        # Detect availability each frame (hot-plug support)
        self.gamepad_enabled = rl.is_gamepad_available(self.gamepad_id)

    def change_display(self, display):
        self.current_display = display

    def loop(self):
        while not rl.window_should_close():
            self.update()
            self.render()

    def render(self):
        rl.begin_drawing()
        self.current_display.render()
        #debug thingy
        rl.draw_text(str(self.current_display), 10, 100, 20, rl.WHITE)
        rl.end_drawing()

    def update(self):
        self.update_gamepad_status()
        self.update_joystick()
        self.current_display.update()

    def update_joystick(self):
        if self.gamepad_enabled:
            self.left_joystick_x = rl.get_gamepad_axis_movement(self.gamepad_id, rl.GamepadAxis.GAMEPAD_AXIS_LEFT_X)
            self.left_joystick_y = rl.get_gamepad_axis_movement(self.gamepad_id, rl.GamepadAxis.GAMEPAD_AXIS_LEFT_Y)
            self.right_joystick_x = rl.get_gamepad_axis_movement(self.gamepad_id, rl.GamepadAxis.GAMEPAD_AXIS_RIGHT_X)
            self.right_joystick_y = rl.get_gamepad_axis_movement(self.gamepad_id, rl.GamepadAxis.GAMEPAD_AXIS_RIGHT_Y)
            if abs(self.left_joystick_x) < self.gamepad_deadzone:
                self.left_joystick_x = 0.0
            if abs(self.left_joystick_y) < self.gamepad_deadzone:
                self.left_joystick_y = 0.0
            if abs(self.right_joystick_x) < self.gamepad_deadzone:
                self.right_joystick_x = 0.0
            if abs(self.right_joystick_y) < self.gamepad_deadzone:
                self.right_joystick_y = 0.0