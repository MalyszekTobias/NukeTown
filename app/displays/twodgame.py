import pyray as rl
from app.displays.base import BaseDisplay
from app.cameras import twodcamera
from app import assets, map, room
from app.ui import text


class TwoDGameDisplay(BaseDisplay):
    def __init__(self, game, player, enemies):
        self.game = game
        self.player = player
        self.enemies = enemies
        super().__init__(game)
        self.delta_time = rl.get_frame_time()
        self.camera = twodcamera.Camera(self.game.width, self.game.height, 0, 0, 3)
        self.enemy_blobs = []

        self.texture =  rl.load_render_texture(game.width, game.height)
        rl.set_texture_filter(self.texture.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.jeff_image = assets.images["Jeff"]

        self.bloom_shader = self.game.bloom_shader
        self.shader_resolution_location = rl.get_shader_location(self.bloom_shader, "resolution")
        self.shader_time_location = rl.get_shader_location(self.bloom_shader, "time")

        self.map = map.Map()
        self.map.add_room(room.Room(10, 10, 5, 5))
        self.map.add_room(room.Room(20, 15, 17, 100))
        self.map.add_room(room.Room(20, -1, 10, 10))
        self.map.connect_rooms()

        self.crafting=False
        res = rl.ffi.new("float[2]", [float(self.game.width), float(self.game.height)])
        rl.set_shader_value(self.bloom_shader, self.shader_resolution_location, res,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        self.start_zoom = self.camera.camera.zoom
        self.intro = True
        self._intro_tolerance = 0.01
        self.camera.camera.zoom = 100.0  # start zoomed in

    def draw_minimap(self):
        if not getattr(self.map, "rooms", None):
            return

        size = 300
        margin = 10
        x = self.game.width - size - margin
        y = margin
        padding = 4
        content_size = size - padding * 2

        # compute map bounds
        min_x = min((r.x for r in self.map.rooms), default=0)
        max_x = max((r.x + r.width for r in self.map.rooms), default=1)
        min_y = min((r.y for r in self.map.rooms), default=0)
        max_y = max((r.y + r.height for r in self.map.rooms), default=1)

        map_w = max(1, max_x - min_x)
        map_h = max(1, max_y - min_y)
        scale = min(content_size / map_w, content_size / map_h)

        # background + border
        rl.draw_rectangle(x-5, y-5, size+10, size+10, rl.DARKGRAY)
        rl.draw_rectangle(x, y, size, size, rl.BLACK)

        # draw rooms
        for rm in self.map.rooms:
            rx = x + padding + int((rm.x - min_x) * scale)
            ry = y + padding + int((rm.y - min_y) * scale)
            rw = max(1, int(rm.width * scale))
            rh = max(1, int(rm.height * scale))
            rl.draw_rectangle(rx, ry, rw, rh, rl.WHITE)
            rl.draw_rectangle_lines(rx, ry, rw, rh, rl.GRAY)
        tile_size = self.map.tile_size
        player_map_x = float(self.player.x) / float(tile_size)
        player_map_y = float(self.player.y) / float(tile_size)
        # draw player
        px = x + padding + int((player_map_x - min_x) * scale)
        py = y + padding + int((player_map_y - min_y) * scale)
        rl.draw_circle(px, py, 3, rl.GREEN)

    def render(self):

        super().render()

        self.camera.begin_mode()
        self.map.draw()
        self.camera.end_mode()

        # 2) Render only the player (and any bloom-only elements) into the render texture
        rl.begin_texture_mode(self.texture)
        # clear the render texture to transparent so only player pixels contribute to bloom
        rl.clear_background((0, 0, 0, 0))
        self.camera.begin_mode()
        for friend in self.player.friends:
            friend.render()
        for e in self.enemies:
            e.render()
        self.player.render()
        self.camera.end_mode()
        rl.end_texture_mode()

        # 3) Apply bloom shader to the render texture (this draws the bloomed player on top of the map)
        rl.begin_shader_mode(self.bloom_shader)
        src = rl.Rectangle(0.0, 0.0,
                           float(self.texture.texture.width),
                           -float(self.texture.texture.height))
        dst = rl.Rectangle(0.0, 0.0, float(self.game.width), float(self.game.height))
        rl.draw_texture_pro(self.texture.texture, src, dst, rl.Vector2(0.0, 0.0), 0.0, rl.WHITE)
        rl.end_shader_mode()

        # 4) UI / minimap (no bloom)
        self.draw_minimap()
        rl.draw_fps(10, 10)
        if self.game.gamepad_enabled:
            text.draw_text(f"Gamepad X: {self.game.left_joystick_x:.2f}  Y: {self.game.left_joystick_y:.2f}", 10, 130, 20,
                         rl.YELLOW, )

    def update(self):
        if self.game.music_manager.current is None:
            self.game.music_manager.play_music2()
        self.delta_time = rl.get_frame_time()

        if self.intro:
            self.camera.zoom_intro(self.delta_time)
            # stop the intro once the camera zoom reaches (close enough to) the target
            if abs(self.camera.camera.zoom - self.camera.target_zoom) < 0.01:
                self.intro = False

        self.camera.update_target(self.player.x, self.player.y, self.delta_time)

        t = rl.ffi.new("float *", float(rl.get_time()))
        rl.set_shader_value(self.bloom_shader, self.shader_time_location, t,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

        for fellow in self.player.friends:
            fellow.update()
        for enemy in self.enemies:
            enemy.update()

        self.player.update(self.map.rooms, self.map.corridor_tiles)

        for friend in self.player.friends:
            friend.update(self.map.rooms, self.map.corridor_tiles)

        if rl.is_key_pressed(rl.KeyboardKey.KEY_C) or rl.is_gamepad_button_pressed(self.game.gamepad_id, rl.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_UP):
            if self.game.crafting==False:
                self.game.crafting = True
                self.game.current_display = self.game.crafting_display
                self.game.current_display = self.game.crafting_display
                if self.game.music_manager.current != 1:
                    print(self.game.music_manager.current)
                    self.game.music_manager.play_music1()





