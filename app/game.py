import pyray as rl

from app.displays import startscreen, main_display,crafting, chapter1, pause, chapter2, main_display2, cutscene
from app import assets

from app import music


class Game:
    def __init__(self):
        self.width, self.height = 1920, 1080
        self.stop=False
        rl.set_config_flags(rl.ConfigFlags.FLAG_VSYNC_HINT)
        rl.set_config_flags(rl.ConfigFlags.FLAG_MSAA_4X_HINT)
        rl.init_window(self.width, self.height, "raylib template?")
        rl.toggle_fullscreen()
        rl.set_exit_key(rl.KeyboardKey.KEY_NULL)
        rl.set_target_fps(rl.get_monitor_refresh_rate(rl.get_current_monitor()))

        self.draw_loading_screen("Topopisy Inc. Presents")

        self.music_manager = music.MusicManager()
        assets.load()

        self.light_shader = assets.shaders["lights"]
        self.base_display = startscreen.StartDisplay(self)
        self.crafting_display = crafting.Crafting_Menu(self)
        self.chapter1_display = chapter1.Chapter1(self)
        self.chapter2_display = chapter2.Chapter2(self)
        self.cutscene_display = cutscene.Cutscene(self)
        self.best_craft = 1

        self.atomic_masses = [1,1,1,1,36,56]
        self.twodgame = main_display.MainDisplay(self)
        self.display2 = main_display2.MainDisplay2(self)
        self.chapter2=False
        self.current_display = self.base_display
        self.pause_menu = pause.Menu(self)
        self.crafting = False
        self.gamepad_id = 0
        self.gamepad_deadzone = 0.25
        self.gamepad_enabled = False


    def draw_loading_screen(self, message: str = "Loading…"):
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)
        font_size = 40
        text_width = rl.measure_text(message, font_size)
        x = (self.width - text_width) // 2
        y = self.height // 2 - font_size // 2
        rl.draw_text(message, x, y, font_size, rl.RAYWHITE)
        rl.end_drawing()

    def update_gamepad_status(self):
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
        rl.end_drawing()

    def update(self):
        self.current_display.update()
        self.update_gamepad_status()
        self.update_joystick()
        try:
            self.music_manager.update()
        except Exception:
            pass


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