import pyray as rl

from app.REACTOR import Reactor
from app.displays.base import BaseDisplay
from app.cameras import twodcamera
from app import assets, map, room, player, enemy_blob, atom, book
from app.ui import text


class MainDisplay(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.player = player.Player(self)
        self.delta_time = rl.get_frame_time()
        self.camera = twodcamera.Camera(self.game.width, self.game.height, 0, 0, 3)
        self.enemy_bullets = []
        self.player_bullets = []
        self.enemies = []

        for mass in self.game.atomic_masses:
            self.player.spawn_friend(mass)

        self.texture =  rl.load_render_texture(game.width, game.height)
        rl.set_texture_filter(self.texture.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.jeff_image = assets.images["Jeff"]

        # Store the reactor so we can check proximity for crafting
        self.reactor = Reactor(self)


        self.map = map.Map(self.game)
        r1=self.map.add_room(room.Room(10, 10, 7, 7))
        r2He=self.map.add_room(room.Room(20, 2, 17, 21))
        self.map.connect_two_rooms(r1, r2He, required_atom="helium")
        r3=self.map.add_room(room.Room(40, 7, 13, 11))
        self.map.connect_two_rooms(r3, r2He)
        r4=self.map.add_room(room.Room(24, -10, 9, 7))
        self.map.connect_two_rooms(r4, r2He)
        r5O = self.map.add_room(room.Room(3, -10, 9, 13))
        self.map.connect_two_rooms(r4, r5O, required_atom="oxygen")

        r6Zn = self.map.add_room(room.Room(40, -5, 11, 7))
        self.map.connect_two_rooms(r4, r6Zn, required_atom="zinc")
        r7Fe = self.map.add_room(room.Room(20, 30, 13, 13))
        self.map.connect_two_rooms(r2He, r7Fe, required_atom="iron")
        r8 = self.map.add_room(room.Room(50, 45, 11, 7))
        self.map.connect_two_rooms(r8, r7Fe)
        r9Kr = self.map.add_room(room.Room(45, 25, 15, 7))
        self.map.connect_two_rooms(r7Fe, r9Kr, required_atom="krypton")
        r10Ba = self.map.add_room(room.Room(0, 20, 13, 7))
        self.map.connect_two_rooms(r7Fe, r10Ba, required_atom="barium")
        # self.map.add_room(room.Room(20, -1, 10, 10))
        # self.map.add_room(room.Room(30, -1, 10, 10))
        # self.map.add_room(room.Room(20, 10, 5, 5))
        # self.map.connect_rooms()

        # Create 8 books scattered around different rooms
        tile_size = self.map.tile_size
        self.books = []
        # Book 1 - in r1 (starting room)
        self.books.append(book.Book(self, (12 + 3) * tile_size, (12 + 3) * tile_size, 1))
        # Book 2 - in r2He (large helium room)
        self.books.append(book.Book(self, (25 + 8) * tile_size, (10 + 10) * tile_size, 2))
        # Book 3 - in r3
        self.books.append(book.Book(self, (45 + 6) * tile_size, (10 + 5) * tile_size, 3))
        # Book 4 - in r4
        self.books.append(book.Book(self, (27 + 4) * tile_size, (-7 + 3) * tile_size, 4))
        # Book 5 - in r5O (oxygen room)
        self.books.append(book.Book(self, (6 + 4) * tile_size, (-6 + 6) * tile_size, 5))
        # Book 6 - in r6Zn (zinc room)
        self.books.append(book.Book(self, (44 + 5) * tile_size, (-2 + 3) * tile_size, 6))
        # Book 7 - in r7Fe (iron room)
        self.books.append(book.Book(self, (25 + 6) * tile_size, (35 + 6) * tile_size, 7))
        # Book 8 - in r9Kr (krypton room)
        self.books.append(book.Book(self, (50 + 7) * tile_size, (27 + 3) * tile_size, 8))

        self.crafting=False
        self.book_message = None  # Will store the book_id when showing a message

        self.start_zoom = self.camera.camera.zoom
        self.intro = True
        self._intro_tolerance = 0.01
        self.camera.camera.zoom = 100.0  # start zoomed in


        # Seed a static example light; player light will be first element and updated per-frame
        self.map.add_light(self.player.x, self.player.y, 420.0, rl.Color(150, 150, 150, 255))

        # Add a light in the center of each room
        tile_size = self.map.tile_size
        # r1
        self.map.add_light(220, 223, 600.0, rl.Color(255, 0, 0, 255))
        # r2He
        self.map.add_light((20 + 17/2) * tile_size, (2 + 21/2) * tile_size, 1500.0, rl.Color(190, 150, 200, 255))
        # r3
        self.map.add_light((40 + 13/2) * tile_size, (7 + 11/2) * tile_size, 700.0, rl.Color(200, 200, 180, 255))
        # r4
        self.map.add_light((24 + 9/2) * tile_size, (-10 + 7/2) * tile_size, 700.0, rl.Color(200, 200, 180, 255))
        # r5O
        self.map.add_light((3 + 9/2) * tile_size, (-10 + 13/2) * tile_size, 750.0, rl.Color(200, 100, 100, 255))
        # r6Zn
        self.map.add_light((40 + 11/2) * tile_size, (-5 + 7/2) * tile_size, 800.0, rl.Color(85, 160, 160, 255))
        # r7Fe
        self.map.add_light((20 + 13/2) * tile_size, (30 + 13/2) * tile_size, 850.0, rl.Color(190, 135, 80, 255))
        # r8
        self.map.add_light((50 + 11/2) * tile_size, (45 + 7/2) * tile_size, 700.0, rl.Color(200, 200, 180, 255))
        # r9Kr
        self.map.add_light((45 + 15/2) * tile_size, (25 + 7/2) * tile_size, 750.0, rl.Color(60, 90, 115, 255))
        # r10Ba
        self.map.add_light((0 + 13/2) * tile_size, (20 + 7/2) * tile_size, 700.0, rl.Color(190, 130, 91, 255))


        self.light_shader = self.game.light_shader
        self.lights_pos_loc = rl.get_shader_location(self.light_shader, "lights")
        self.lights_color_loc = rl.get_shader_location(self.light_shader, "light_colors")
        self.num_lights_loc = rl.get_shader_location(self.light_shader, "num_lights")
        self.ambient_loc = rl.get_shader_location(self.light_shader, "ambient")
        rl.set_shader_value(self.light_shader, self.ambient_loc, rl.ffi.new("float *", 0.0),
                            rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

        for i in self.map.gates:
            print(str(i))

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

        # draw corridors
        for (tile_x, tile_y) in self.map.corridor_tiles:
            cx = x + padding + int((tile_x - min_x) * scale)
            cy = y + padding + int((tile_y - min_y) * scale)
            cw = max(1, int(scale))
            ch = max(1, int(scale))
            rl.draw_rectangle(cx, cy, cw, ch, rl.DARKGRAY)

        # draw rooms
        for rm in self.map.rooms:
            rx = x + padding + int((rm.x - min_x) * scale)
            ry = y + padding + int((rm.y - min_y) * scale)
            rw = max(1, int(rm.width * scale))
            rh = max(1, int(rm.height * scale))
            rl.draw_rectangle(int(rx+scale), int(ry+scale), int(rw-(2*scale)), int(rh-(2*scale)), rl.WHITE)
            rl.draw_rectangle_lines(rx, ry, rw, rh, rl.GRAY)
        tile_size = self.map.tile_size

#debug stuff: draw lights on minimap
        for light in getattr(self.map, "lights", [])[:100]:
                lx_tiles = float(light['pos'].x) / float(tile_size)
                ly_tiles = float(light['pos'].y) / float(tile_size)
                mx = x + padding + int((lx_tiles - min_x) * scale)
                my = y + padding + int((ly_tiles - min_y) * scale)
                # small marker; don't scale with light radius to avoid clutter
                marker_r = max(1, int(max(1.5, scale)))
                rl.draw_circle(mx, my, marker_r, light['color'])


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

        for e in self.enemies:
            e.render()

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
        if self.game.gamepad_enabled:
            text.draw_text(f"Gamepad X: {self.game.left_joystick_x:.2f}  Y: {self.game.left_joystick_y:.2f}", 10, 130, 20,
                         rl.YELLOW, )
        # Interaction hint when colliding with the reactor
        try:
            if self.reactor and self.reactor.can_interact(self.player):
                text.draw_text("Press C to craft", 10, 40, 24, rl.WHITE)
        except Exception:
            pass

        # Interaction hint when near any book
        try:
            for bk in self.books:
                if bk.can_interact(self.player):
                    text.draw_text("Press E to read", 10, 70, 24, rl.WHITE)
                    break
        except Exception:
            pass

        # Display book message if one is active
        if self.book_message is not None:
            # Find the book object to get its flavour text
            book_text = f"Hello World {self.book_message}"  # Fallback
            try:
                for bk in self.books:
                    if bk.book_id == self.book_message:
                        book_text = bk.flavour_text
                        break
            except Exception:
                pass

            # Draw a semi-transparent overlay
            rl.draw_rectangle(0, 0, self.game.width, self.game.height, rl.Color(0, 0, 0, 180))
            # Draw the message box (larger for longer texts)
            box_width = 800
            box_height = 300
            box_x = (self.game.width - box_width) // 2
            box_y = (self.game.height - box_height) // 2
            rl.draw_rectangle(box_x, box_y, box_width, box_height, rl.Color(50, 50, 50, 255))
            rl.draw_rectangle_lines(box_x, box_y, box_width, box_height, rl.WHITE)

            # Draw the text with word wrapping
            text_x = box_x + 30
            text_y = box_y + 30
            text_width = box_width - 60
            text_size = 24

            # Simple word wrapping
            words = book_text.split(' ')
            current_line = ""
            y_offset = 0
            line_height = text_size + 5

            for word in words:
                test_line = current_line + word + " "
                # Approximate text width (rough estimate)
                if len(test_line) * (text_size * 0.8) > text_width:
                    if current_line:
                        text.draw_text(current_line.strip(), text_x, text_y + y_offset, text_size, rl.WHITE)
                        y_offset += line_height
                        current_line = word + " "
                else:
                    current_line = test_line

            # Draw the last line
            if current_line:
                text.draw_text(current_line.strip(), text_x, text_y + y_offset, text_size, rl.WHITE)

            # Draw close instruction at bottom
            text.draw_text("Press E to close", box_x + 30, box_y + box_height - 50, 20, rl.GRAY)

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

        for e in self.enemies:
            e.update()


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

        if (rl.is_key_pressed(rl.KeyboardKey.KEY_C) or rl.is_gamepad_button_pressed(self.game.gamepad_id, rl.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_UP)) and can_open_crafting:
            if self.game.crafting==False:
                self.game.crafting = True
                self.game.current_display = self.game.crafting_display
                self.trans = {8:"oxygen" ,  1:"hydrogen", 30:"zinc", 11:"sodium",36: "krypton", 56:"barium",
                              16:"sulphur", 26:"iron", 2:"helium", 92:"uranium"}
                self.game.crafting_display.inventory.inv={}
                for x in self.game.atomic_masses:
                    try:
                        self.game.crafting_display.inventory.inv[self.trans[x]]+=1
                    except:
                        self.game.crafting_display.inventory.inv[self.trans[x]]=1
                self.game.crafting_display.atom_bar.update()



        elif rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
            rl.draw_rectangle(self.game.width - 300 - 10, 10, 300, 300, rl.BLACK)
            rl.draw_rectangle(0, 0, 400, 200, rl.BLACK)
            self.game.change_display(self.game.pause_menu)

        # Check for E key press near books
        if rl.is_key_pressed(rl.KeyboardKey.KEY_E) or rl.is_gamepad_button_pressed(self.game.gamepad_id, rl.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_LEFT):
            # If a book message is showing, close it
            if self.book_message is not None:
                self.book_message = None
            else:
                # Check if player is near any book
                try:
                    for bk in self.books:
                        if bk.can_interact(self.player):
                            self.book_message = bk.book_id
                            break
                except Exception:
                    pass

