import pyray as rl
from app.displays.base import BaseDisplay
from app.cameras import twodcamera
from app import assets


class TwoDGameDisplay(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        self.square_pos = [200, 200]
        self.speed = 200
        self.delta_time = rl.get_frame_time()
        self.camera = twodcamera.Camera(self.game.width, self.game.height, self.square_pos[0], self.square_pos[1], 3)

        self.texture =  rl.load_render_texture(game.width, game.height)
        rl.set_texture_filter(self.texture.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.jeff_image = assets.images["Jeff"]

        self.bloom_shader = self.game.bloom_shader
        self.shader_resolution_location = rl.get_shader_location(self.bloom_shader, "resolution")
        self.shader_time_location = rl.get_shader_location(self.bloom_shader, "time")

        res = rl.ffi.new("float[2]", [float(self.game.width), float(self.game.height)])
        rl.set_shader_value(self.bloom_shader, self.shader_resolution_location, res,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)



    def render(self):
        rl.begin_texture_mode(self.texture)

        super().render()

        self.camera.begin_mode()

        rl.draw_fps(10, 10)
        # rl.draw_rectangle(int(self.square_pos[0]), int(self.square_pos[1]), 20, 20, rl.RED)
        scale = 20.0 / float(self.jeff_image.width)
        rl.draw_texture_ex(self.jeff_image, rl.Vector2(float(self.square_pos[0]), float(self.square_pos[1])), 0.0,
                           scale, rl.WHITE)

        self.camera.end_mode()
        rl.end_texture_mode()

        #shader stuff
        rl.begin_shader_mode(self.bloom_shader)

        src = rl.Rectangle(0.0, 0.0,
                           float(self.texture.texture.width),
                           -float(self.texture.texture.height))
        dst = rl.Rectangle(0.0, 0.0, float(self.game.width), float(self.game.height))
        rl.draw_texture_pro(self.texture.texture, src, dst, rl.Vector2(0.0, 0.0), 0.0, rl.WHITE)

        rl.end_shader_mode()
        if self.game.gamepad_enabled:
            rl.draw_text(f"Gamepad X: {self.game.left_joystick_x:.2f}  Y: {self.game.left_joystick_y:.2f}", 10, 130, 20, rl.YELLOW)


    def update(self):
        self.delta_time = rl.get_frame_time()
        self.camera.update_target(self.square_pos[0], self.square_pos[1], self.delta_time)

        t = rl.ffi.new("float *", float(rl.get_time()))
        rl.set_shader_value(self.bloom_shader, self.shader_time_location, t,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

        if not self.game.gamepad_enabled:
            if rl.is_key_down(rl.KeyboardKey.KEY_W):
                self.square_pos[1] -= self.speed * self.delta_time
            if rl.is_key_down(rl.KeyboardKey.KEY_S):
                self.square_pos[1] += self.speed * self.delta_time
            if rl.is_key_down(rl.KeyboardKey.KEY_A):
                self.square_pos[0] -= self.speed * self.delta_time
            if rl.is_key_down(rl.KeyboardKey.KEY_D):
                self.square_pos[0] += self.speed * self.delta_time
        else:
            self.square_pos[0] += self.game.left_joystick_x * self.speed * self.delta_time
            self.square_pos[1] += self.game.left_joystick_y * self.speed * self.delta_time


