# python
# file: `app/displays/threedgame.py`
import math
import pyray as rl
from app.displays.base import BaseDisplay
from app.cameras import threedcamera


class ThreeDGameDisplay(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        self.cube_pos = [0.0, 1.0, 0.0]
        self.speed = 10

        self.camera_height = 6.0
        self.camera_distance = 10.0
        self.camera_distance_min = 6.0
        self.camera_distance_max = 16.0
        self.camera_pitch_deg = 10.0
        self.pitch_min = -60.0
        self.pitch_max = 60.0
        self.pitch_sensitivity = 0.15

        # sensitivity for gamepad right stick (degrees per second)
        self.gamepad_look_sensitivity = 120.0

        self.camera = threedcamera.Camera(
            self.cube_pos[0], self.cube_pos[1], self.cube_pos[2],
            (0.0, self.camera_height, self.camera_distance),
            3.0,
            60.0
        )
        self.delta_time = 0

        self.model = rl.load_model("app/models/shiba/scene.gltf")

        self.model_scale = rl.Vector3(2.0, 2.0, 2.0)
        self.model_rot_axis = rl.Vector3(0.0, 1.0, 0.0)
        self.model_rot_deg = 0.0
        self.mouse_sensitivity = 0.2

        self.texture = rl.load_render_texture(game.width, game.height)
        rl.set_texture_filter(self.texture.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.bloom_shader = self.game.bloom_shader
        self.shader_resolution_location = rl.get_shader_location(self.bloom_shader, "resolution")
        self.shader_time_location = rl.get_shader_location(self.bloom_shader, "time")

        res = rl.ffi.new("float[2]", [float(self.game.width), float(self.game.height)])
        rl.set_shader_value(self.bloom_shader, self.shader_resolution_location, res,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)

        self.hidden_cursor = False

    def __del__(self):
        rl.enable_cursor()

    def update(self):
        self.update_cursor()
        self.delta_time = rl.get_frame_time()
        self.update_look()
        yaw_rad = math.radians(self.model_rot_deg)
        fx, fz = math.sin(yaw_rad), math.cos(yaw_rad)
        rx, rz = fz, -math.sin(yaw_rad)
        self.update_movement(fx, fz, rx, rz)
        self.update_camera(fx, fz)
        self.update_shader_time()

    def update_cursor(self):
        if not self.hidden_cursor:
            rl.disable_cursor()
            self.hidden_cursor = True

    def update_look(self):
        if not self.game.gamepad_enabled:
            mouse_delta = rl.get_mouse_delta()
            self.model_rot_deg = (self.model_rot_deg - mouse_delta.x * self.mouse_sensitivity) % 360.0

            self.camera_pitch_deg = max(
                self.pitch_min,
                min(self.pitch_max, self.camera_pitch_deg - mouse_delta.y * self.pitch_sensitivity)
            )
        else:
            rx = self.game.right_joystick_x
            ry = self.game.right_joystick_y
            look_scale = self.gamepad_look_sensitivity * self.delta_time

            self.model_rot_deg = (self.model_rot_deg - rx * look_scale) % 360.0
            self.camera_pitch_deg = max(
                self.pitch_min,
                min(self.pitch_max, self.camera_pitch_deg - ry * look_scale)
            )

    def update_movement(self, fx, fz, rx, rz):
        move_x = 0.0
        move_z = 0.0
        if not self.game.gamepad_enabled:
            if rl.is_key_down(rl.KeyboardKey.KEY_W):
                move_x += fx
                move_z += fz
            if rl.is_key_down(rl.KeyboardKey.KEY_S):
                move_x -= fx
                move_z -= fz
            if rl.is_key_down(rl.KeyboardKey.KEY_A):
                move_x += rx
                move_z += rz
            if rl.is_key_down(rl.KeyboardKey.KEY_D):
                move_x -= rx
                move_z -= rz
        else:
            # Joystick X moves along right, Y along forward
            move_x -= rx * self.game.left_joystick_x + fx * self.game.left_joystick_y
            move_z -= rz * self.game.left_joystick_x + fz * self.game.left_joystick_y

        mag = math.hypot(move_x, move_z)
        if mag > 0.0:
            move_x /= mag
            move_z /= mag
            self.cube_pos[0] += move_x * self.speed * self.delta_time
            self.cube_pos[2] += move_z * self.speed * self.delta_time

    def update_camera(self, fx, fz):
        t = (self.camera_pitch_deg - self.pitch_min) / (self.pitch_max - self.pitch_min)
        t = max(0.0, min(1.0, t))
        dynamic_dist = self.camera_distance_max * (1.0 - t) + self.camera_distance_min * t

        pitch_rad = math.radians(self.camera_pitch_deg)
        horiz_dist = dynamic_dist * math.cos(pitch_rad)
        y_off = self.camera_height + dynamic_dist * math.sin(pitch_rad)
        cam_off = rl.Vector3(-fx * horiz_dist, y_off, -fz * horiz_dist)
        self.camera.offset = cam_off

        self.camera.update_target(self.cube_pos[0], self.cube_pos[1], self.cube_pos[2], self.delta_time)

    def update_shader_time(self):
        t = rl.ffi.new("float *", float(rl.get_time()))
        rl.set_shader_value(self.bloom_shader, self.shader_time_location, t,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

    def render(self):
        rl.begin_texture_mode(self.texture)

        super().render()

        self.camera.begin_mode()

        rl.draw_grid(40, 1.0)
        pos = rl.Vector3(self.cube_pos[0], self.cube_pos[1], self.cube_pos[2])
        rl.draw_model_ex(
            self.model,
            pos,
            self.model_rot_axis,
            self.model_rot_deg,
            self.model_scale,
            rl.WHITE
        )

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

