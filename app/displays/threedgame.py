import pyray as rl
from app.displays.base import BaseDisplay
from app.cameras import threedcamera


class ThreeDGameDisplay(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        self.cube_pos = [0.0, 1.0, 0.0]
        self.speed = 10
        self.camera = threedcamera.Camera(
            self.cube_pos[0], self.cube_pos[1], self.cube_pos[2],
            (0, 6, 8),
            3.0,
            60.0
        )
        self.delta_time = 0

        self.texture =  rl.load_render_texture(game.width, game.height)
        rl.set_texture_filter(self.texture.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.bloom_shader = self.game.bloom_shader
        self.shader_resolution_location = rl.get_shader_location(self.bloom_shader, "resolution")
        self.shader_time_location = rl.get_shader_location(self.bloom_shader, "time")

        res = rl.ffi.new("float[2]", [float(self.game.width), float(self.game.height)])
        rl.set_shader_value(self.bloom_shader, self.shader_resolution_location, res,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)


    def update(self):
        self.delta_time = rl.get_frame_time()
        self.camera.update_target(self.cube_pos[0], self.cube_pos[1], self.cube_pos[2], self.delta_time)

        t = rl.ffi.new("float *", float(rl.get_time()))
        rl.set_shader_value(self.bloom_shader, self.shader_time_location, t,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        if not self.game.gamepad_enabled:
            if rl.is_key_down(rl.KeyboardKey.KEY_W):
                self.cube_pos[2] -= self.speed * self.delta_time
            if rl.is_key_down(rl.KeyboardKey.KEY_S):
                self.cube_pos[2] += self.speed * self.delta_time
            if rl.is_key_down(rl.KeyboardKey.KEY_A):
                self.cube_pos[0] -= self.speed * self.delta_time
            if rl.is_key_down(rl.KeyboardKey.KEY_D):
                self.cube_pos[0] += self.speed * self.delta_time
        else:
            self.cube_pos[0] += self.game.left_joystick_x * self.speed * self.delta_time
            self.cube_pos[2] += self.game.left_joystick_y * self.speed * self.delta_time

    def render(self):
        rl.begin_texture_mode(self.texture)

        super().render()

        self.camera.begin_mode()

        rl.draw_grid(40, 1.0)
        pos = rl.Vector3(self.cube_pos[0], self.cube_pos[1], self.cube_pos[2])
        rl.draw_cube(pos, 1.0, 1.0, 1.0, rl.RED)
        rl.draw_cube_wires(pos, 1.0, 1.0, 1.0, rl.BLACK)

        self.camera.end_mode()

        rl.end_texture_mode()
        rl.begin_shader_mode(self.bloom_shader)

        src = rl.Rectangle(0.0, 0.0,
                           float(self.texture.texture.width),
                           -float(self.texture.texture.height))
        dst = rl.Rectangle(0.0, 0.0, float(self.game.width), float(self.game.height))
        rl.draw_texture_pro(self.texture.texture, src, dst, rl.Vector2(0.0, 0.0), 0.0, rl.WHITE)

        rl.end_shader_mode()

        rl.draw_fps(10, 10)
        if self.game.gamepad_enabled:
            rl.draw_text(f"Gamepad X: {self.game.left_joystick_x:.2f}  Y: {self.game.left_joystick_y:.2f}", 10, 130, 20,
                         rl.YELLOW)

