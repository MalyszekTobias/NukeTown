import pyray as rl
from app.displays.base import BaseDisplay
from app.cameras import twodcamera
from app import assets

class Crafting_Menu(BaseDisplay):
    def __init__(self, game):

        super().__init__(game)
        self.square_pos = [0, 0]

        self.speed = 200
        self.delta_time = rl.get_frame_time()

        self.texture = rl.load_render_texture(game.width, game.height)
        rl.set_texture_filter(self.texture.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)



        self.bloom_shader = self.game.bloom_shader
        self.shader_resolution_location = rl.get_shader_location(self.bloom_shader, "resolution")
        self.shader_time_location = rl.get_shader_location(self.bloom_shader, "time")
        self.crafting = False
        res = rl.ffi.new("float[2]", [float(self.game.width), float(self.game.height)])
        rl.set_shader_value(self.bloom_shader, self.shader_resolution_location, res,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_VEC2)
        self.objects = []
        # a=GameObject(self,assets.images["Jeff"],0,0,10,10)
        # t1=TextObject(self,'aaa',0,0,100,rl.WHITE)
        self.inventory=Inventory({"oxygen":2,"hydrogen":2},self,0,0,30,200)
    def render(self):
        rl.begin_texture_mode(self.texture)
        print(self.square_pos)
        super().render()


        rl.draw_fps(10, 10)
        # rl.draw_rectangle(int(self.square_pos[0]), int(self.square_pos[1]), 20, 20, rl.RED)
        for obj in self.objects:
            print('aa')
            obj.draw()



        rl.end_texture_mode()

        # shader stuff
        rl.begin_shader_mode(self.bloom_shader)

        src = rl.Rectangle(0.0, 0.0,
                           float(self.texture.texture.width),
                           -float(self.texture.texture.height))
        dst = rl.Rectangle(0.0, 0.0, float(self.game.width), float(self.game.height))
        rl.draw_texture_pro(self.texture.texture, src, dst, rl.Vector2(0.0, 0.0), 0.0, rl.WHITE)

        rl.end_shader_mode()
        if self.game.gamepad_enabled:
            rl.draw_text(f"Gamepad X: {self.game.left_joystick_x:.2f}  Y: {self.game.left_joystick_y:.2f}", 10, 130, 20,
                         rl.YELLOW)

    def update(self):
        self.delta_time = rl.get_frame_time()

        t = rl.ffi.new("float *", float(rl.get_time()))
        rl.set_shader_value(self.bloom_shader, self.shader_time_location, t,
                            rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

        if rl.is_key_pressed(rl.KeyboardKey.KEY_C):
            self.game.current_display = self.game.twodgame
            self.game.crafting = False

        # if not self.game.gamepad_enabled:
        #     if rl.is_key_down(rl.KeyboardKey.KEY_W):
        #         self.square_pos[1] -= self.speed * self.delta_time
        #     if rl.is_key_down(rl.KeyboardKey.KEY_S):
        #         self.square_pos[1] += self.speed * self.delta_time
        #     if rl.is_key_down(rl.KeyboardKey.KEY_A):
        #         self.square_pos[0] -= self.speed * self.delta_time
        #     if rl.is_key_down(rl.KeyboardKey.KEY_D):
        #         self.square_pos[0] += self.speed * self.delta_time
        # else:
        #     self.square_pos[0] += self.game.left_joystick_x * self.speed * self.delta_time
        #     self.square_pos[1] += self.game.left_joystick_y * self.speed * self.delta_time
class GameObject():
    def __init__(self,display,image,x,y,w,h):
        self.display = display
        if image is not None:
            self.image = image
        else:
            self.image = None

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.square_pos = [self.x, self.y]
        self.display.objects.append(self)
    def draw(self):
        print('bb')
        scale = self.w
        rl.draw_texture_ex(self.image, rl.Vector2(float(self.square_pos[0]), float(self.square_pos[1])), 0.0,
                           1, rl.WHITE)
class TextObject():
    def __init__(self,display,text,x,y,w,color):
        self.display = display
        self.color=color
        self.x = x
        self.y = y
        self.w = w
        self.square_pos = [self.x, self.y]
        self.text=text
        self.display.objects.append(self)

    def draw(self):
        print('bb')
        rl.draw_text(self.text,self.x,self.y,self.w,self.color,)
class Inventory():
    def __init__(self,inv,display,x,y,w,h):
        self.display = display
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.inv={}
        self.display.objects.append(self)
        self.inv=inv
    def add_element(self,atom,amount):
        if atom in self.inv:
            self.inv[atom] += amount
        else:
            self.inv[atom] = amount
    def draw(self):
        rl.draw_text("Inventory", self.x, self.y, self.w, rl.WHITE, )
        i=0
        for atom in self.inv:
            i+=1
            rl.draw_text(f"{atom}: {self.inv[atom]}",self.x,self.y+self.w*i,self.w,rl.WHITE)

