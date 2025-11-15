import pyray as rl

from app.REACTOR import Reactor
from app.displays.base import BaseDisplay
from app.cameras import twodcamera
from app import assets, map, room, player, enemy_blob, atom
from app.enemy_blob import EnemyBlob
from app.ui import text
import random
import random



class MainDisplay2(BaseDisplay):

    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.player = player.Player(self)
        self.delta_time = rl.get_frame_time()
        self.camera = twodcamera.Camera(self.game.width, self.game.height, 0, 0, 3)
        self.enemy_bullets = []
        self.player_bullets=[]
        self.enemies = []


        for mass in self.game.atomic_masses:
            self.player.spawn_friend(mass)

        self.texture =  rl.load_render_texture(game.width, game.height)
        rl.set_texture_filter(self.texture.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)



        self.crafting=False
        self.map = map.Map(self.game)


        DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # 4-neighborhood grid

        def generate_spanning_tree(n):
            """Tworzy drzewo rozpinające (spójny graf bez cykli)."""
            graph = {(x, y): [] for y in range(n) for x in range(n)}
            visited = set()

            stack = [(0, 0)]
            visited.add((0, 0))

            while stack:
                x, y = stack.pop()

                dirs = DIRS[:]
                random.shuffle(dirs)

                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in visited:
                        visited.add((nx, ny))

                        graph[(x, y)].append((nx, ny))
                        graph[(nx, ny)].append((x, y))
                        stack.append((nx, ny))

            return graph

        def add_random_edges(graph, n, probability=0.05):

            for y in range(n):
                for x in range(n):
                    for dx, dy in DIRS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < n:

                            if (nx, ny) not in graph[(x, y)] and random.random() < probability:
                                graph[(x, y)].append((nx, ny))
                                graph[(nx, ny)].append((x, y))

            return graph

        def generate_loopy_connected_grid_graph(n, extra_edge_probability=0.05):

            graph = generate_spanning_tree(n)
            graph = add_random_edges(graph, n, extra_edge_probability)
            return graph


        l= 10
        g = generate_loopy_connected_grid_graph(l, extra_edge_probability=0.1)
        lista=[0 for x in range(l**2)]
        la=0


        self.rooms = [[0 for r in range(l)] for c in range(l)]
        self.rooms_checked = [[0 for r in range(l)] for c in range(l)]
        for r in range(l):
            for c in range(l):
                self.rooms[r][c] = self.map.add_room(room.Room(c * 10 + 11, r * 10 + 11, 3, 3))
                lista[la]=[r,c]
                la+=1
        for x in g.keys():
            for y in g[x]:
                self.map.connect_two_rooms_no_doors(self.rooms[x[0]][x[1]], self.rooms[y[0]][y[1]])
        samp=random.sample(lista, 50)
        print(samp)
        self.enemies2=[]
        for x in samp:
            e=EnemyBlob(self,200+x[0]*160,200+x[1]*160,100,92)
            e.speed=0
            self.enemies.append(e)



        self.start_zoom = self.camera.camera.zoom
        self.intro = True
        self._intro_tolerance = 0.01
        self.camera.camera.zoom = 100.0


        self.map.add_light(self.player.x, self.player.y, 420.0, rl.Color(255, 255, 255, 255))
        self.map.add_light(200, 200, 150.0, rl.Color(255, 0, 0, 255))
        self.map.add_light(400, 67, 670.0, rl.Color(200, 150, 5, 255))

        self.light_shader = self.game.light_shader
        self.lights_pos_loc = rl.get_shader_location(self.light_shader, "lights")
        self.lights_color_loc = rl.get_shader_location(self.light_shader, "light_colors")
        self.num_lights_loc = rl.get_shader_location(self.light_shader, "num_lights")
        self.ambient_loc = rl.get_shader_location(self.light_shader, "ambient")
        rl.set_shader_value(self.light_shader, self.ambient_loc, rl.ffi.new("float *", 0.0),
                            rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    def draw_minimap(self):
        if not getattr(self.map, "rooms", None):
            return

        size = 300
        margin = 10
        x = self.game.width - size - margin
        y = margin
        padding = 4
        content_size = size - padding * 2

        min_x = min((r.x for r in self.map.rooms), default=0)
        max_x = max((r.x + r.width for r in self.map.rooms), default=1)
        min_y = min((r.y for r in self.map.rooms), default=0)
        max_y = max((r.y + r.height for r in self.map.rooms), default=1)

        map_w = max(1, max_x - min_x)
        map_h = max(1, max_y - min_y)
        scale = min(content_size / map_w, content_size / map_h)

        rl.draw_rectangle(x-5, y-5, size+10, size+10, rl.DARKGRAY)
        rl.draw_rectangle(x, y, size, size, rl.BLACK)

        for (tile_x, tile_y) in self.map.corridor_tiles:
            cx = x + padding + int((tile_x - min_x) * scale)
            cy = y + padding + int((tile_y - min_y) * scale)
            cw = max(1, int(scale))
            ch = max(1, int(scale))
            rl.draw_rectangle(cx, cy, cw, ch, rl.DARKGRAY)

        for rm in self.map.rooms:
            rx = x + padding + int((rm.x - min_x) * scale)
            ry = y + padding + int((rm.y - min_y) * scale)
            rw = max(1, int(rm.width * scale))
            rh = max(1, int(rm.height * scale))
            rl.draw_rectangle(int(rx+scale), int(ry+scale), int(rw-(2*scale)), int(rh-(2*scale)), rl.WHITE)
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

        # Ensure first light follows player (player light)
        if self.map.lights:
            self.map.lights[0]['pos'].x = self.player.x
            self.map.lights[0]['pos'].y = self.player.y

        # Update light shader uniforms (clamp to MAX_LIGHTS from shader)
        MAX_LIGHTS = 100
        visible_lights = self.map.lights[:MAX_LIGHTS]
        num_lights = len(visible_lights)
        light_pos_data = []
        light_color_data = []
        for light in visible_lights:
            cam_pos = rl.get_world_to_screen_2d(light['pos'], self.camera.camera)
            # Invert Y-coordinate for shader
            light_pos_data.extend([cam_pos.x, self.game.height - cam_pos.y, light['radius']])
            c = light['color']
            light_color_data.extend([c.r / 255.0, c.g / 255.0, c.b / 255.0, c.a / 255.0])

        rl.set_shader_value(self.light_shader, self.num_lights_loc, rl.ffi.new("int *", num_lights),
                            rl.ShaderUniformDataType.SHADER_UNIFORM_INT)
        if num_lights > 0:
            rl.set_shader_value_v(self.light_shader, self.lights_pos_loc, rl.ffi.new("float[]", light_pos_data),
                                 rl.ShaderUniformDataType.SHADER_UNIFORM_VEC3, num_lights)
            rl.set_shader_value_v(self.light_shader, self.lights_color_loc, rl.ffi.new("float[]", light_color_data),
                                 rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4, num_lights)

        # 1) Draw the main scene (map + objects) to a texture
        rl.begin_texture_mode(self.texture)
        rl.clear_background(rl.BLACK)
        self.camera.begin_mode()
        self.map.draw()
        for obj in self.game_objects:
            obj.render()
        for b in self.player_bullets:
            b.render()
        for b in self.enemy_bullets:
            b.render()

        self.camera.end_mode()
        rl.end_texture_mode()

        # 2) Draw the scene texture to the screen using the light shader
        rl.begin_shader_mode(self.light_shader)
        src = rl.Rectangle(0.0, 0.0, float(self.texture.texture.width), -float(self.texture.texture.height))
        dst = rl.Rectangle(0.0, 0.0, float(self.game.width), float(self.game.height))
        rl.draw_texture_pro(self.texture.texture, src, dst, rl.Vector2(0.0, 0.0), 0.0, rl.WHITE)
        rl.end_shader_mode()

        # 3) UI / minimap (no shaders)
        self.draw_minimap()
        rl.draw_fps(10, 10)
        if self.game.gamepad_enabled:
            text.draw_text(f"Gamepad X: {self.game.left_joystick_x:.2f}  Y: {self.game.left_joystick_y:.2f}", 10, 130, 20,
                         rl.YELLOW, )
        # Interaction hint when colliding with the reactor
        try:
            if self.reactor and self.reactor.can_interact(self.player):
                text.draw_text("Press C to craft", 10, 40, 24, rl.WHITE)
        except Exception:
            pass
        if (rl.is_key_pressed(rl.KeyboardKey.KEY_C) or rl.is_gamepad_button_pressed(self.game.gamepad_id, rl.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_UP)):

            if self.game.crafting==False:
                if self.game.stop:
                    self.game.stop=False
                else:
                    self.game.crafting = True
                    self.game.stop = True
                    self.game.crafting_display.table.update()
                    self.game.current_display = self.game.crafting_display
                    self.trans = {8: "oxygen", 1: "hydrogen", 30: "zinc", 11: "sodium", 36: "krypton", 56: "barium",
                                  16: "sulphur", 26: "iron", 2: "helium", 92: "uranium"}
                    self.game.crafting_display.inventory.inv = {}
                    for x in self.game.atomic_masses:
                        try:
                            self.game.crafting_display.inventory.inv[self.trans[x]] += 1
                        except:
                            self.game.crafting_display.inventory.inv[self.trans[x]] = 1
                    self.game.crafting_display.atom_bar.update()

        elif rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
            rl.draw_rectangle(self.game.width - 300 - 10, 10, 300, 300, rl.BLACK)
            rl.draw_rectangle(0, 0, 400, 200, rl.BLACK)
            self.game.change_display(self.game.pause_menu)

        if rl.is_key_pressed(rl.KeyboardKey.KEY_E) or rl.is_gamepad_button_pressed(self.game.gamepad_id, rl.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_LEFT):
            if self.book_message is not None:
                self.book_message = None
            else:
                try:
                    for bk in self.books:
                        if bk.can_interact(self.player):
                            self.book_message = bk.book_id
                            break
                except Exception:
                    pass

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

        for b in self.player_bullets:
            b.update()
        for b in self.enemy_bullets:
            b.update()


        for object in self.game_objects:
            if issubclass(type(object), atom.Atom):
                # Keep corridor tiles intact, but closed gates will be treated as walls via collision rects
                object.update(self.map.rooms, self.map.corridor_tiles)
            elif isinstance(object, enemy_blob.EnemyBlob):
                # Enemy blobs also need rooms and corridor_tiles for gate/wall collision
                object.update(self.map.rooms, self.map.corridor_tiles)
            else:
                object.update()

        # Open crafting only when near the reactor
        can_open_crafting = False
        try:
            if self.reactor and hasattr(self.reactor, 'can_interact'):
                can_open_crafting = self.reactor.can_interact(self.player)
        except Exception:
            can_open_crafting = False


