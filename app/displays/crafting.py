
from app.ui import text

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




        self.crafting = False

        self.objects = []
        # a=GameObject(self,assets.images["Jeff"],0,0,10,10)
        # t1=TextObject(self,'aaa',0,0,100,rl.WHITE)
        self.inventory=Inventory({"oxygen":2,"hydrogen":2,"zinc":3,"sodium":0,"krypton":10,"barium":11},self,0,0,120,200)
        # self.oxygen1=Atom(self,assets.images["Oxygen_Standby"] ,1000,100,100,100,"O",8,40)
        self.atom_bar=Atom_Bar(self,500,0,1000,100)
        self.table=Table(self,500,500,500,500)
    def render(self):
        # print(self.square_pos)
        super().render()


        rl.draw_fps(10, 10)
        # rl.draw_rectangle(int(self.square_pos[0]), int(self.square_pos[1]), 20, 20, rl.RED)
        for obj in self.objects:
            # print('aa')
            obj.draw()


        # shader stuff

        if self.game.gamepad_enabled:
            text.draw_text(f"Gamepad X: {self.game.left_joystick_x:.2f}  Y: {self.game.left_joystick_y:.2f}", 10, 130, 20,
                         rl.YELLOW)

    def update(self):
        self.delta_time = rl.get_frame_time()


        if rl.is_key_pressed(rl.KeyboardKey.KEY_C) or rl.is_gamepad_button_pressed(self.game.gamepad_id, rl.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_UP):
            self.game.current_display = self.game.twodgame
            self.game.crafting = False

        if rl.is_mouse_button_pressed(0):
            self.mouse=rl.get_mouse_position()
            print(self.mouse.x,self.mouse.y)

            for x in self.atom_bar.atom_images.keys():
                obj=self.atom_bar.atom_images[x]
                if self.collision(obj,self.mouse):
                    if self.inventory.inv[x]>=1:
                        self.inventory.inv[x]-=1

    def collision(self,obj1,mouse):
        if (obj1.x<mouse.x<obj1.x+obj1.w) :
            if (obj1.y<mouse.y<obj1.y+obj1.h):
                return True
        return False


    def get_inv(self):
        return self.inventory.inv
class GameObject():
    def __init__(self,display,image,x,y,w,h,scale):
        self.display = display
        # if image is not None:
        #     self.image = image
        #     rl.image_resize(self.image, w, h)
        # else:
        #     self.image = None
        self.image = image
        self.scale=scale
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.square_pos = [self.x, self.y]
        self.display.objects.append(self)

    def draw(self):
        # print('bb')


        rl.draw_texture_ex(self.image, rl.Vector2(float(self.square_pos[0]), float(self.square_pos[1])), 0.0,
                           self.w/self.scale, rl.WHITE)
    def delete(self):
        self.display.objects.remove(self)
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
        # print('bb')
        text.draw_text(self.text,self.x,self.y,self.w,self.color,)
    def delete(self):
        self.display.objects.remove(self)
class Rect():
    def __init__(self,display,x,y,w,h):
        self.display = display
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.display.objects.append(self)
    def draw(self):
        # print('bb')
        rl.draw_rectangle_lines(self.x,self.y,self.w,self.h,rl.WHITE,)
    def delete(self):
        self.display.objects.remove(self)


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
        self.atom_images={}


    def add_element(self,atom,amount):
        if atom in self.inv:
            self.inv[atom] += amount
        else:
            self.inv[atom] = amount
    def draw(self):
        text.draw_text("Inventory", self.x, self.y, self.w, rl.WHITE, )
        i=0
        for atom in self.inv:
            i+=1
            text.draw_text(f"{atom}: {self.inv[atom]}",self.x,self.y+self.w*i,self.w,rl.WHITE)

class Atom():
    def __init__(self,display,image,x,y,w,h,name,mass,font_w):
        self.display = display
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font_w=font_w
        self.image = image
        self.name = name
        self.mass = mass
        self.image_object=GameObject(display,image,x-50,y-60,w,h,512)
        self.name_text=TextObject(display,self.name,x,y-3,font_w,rl.WHITE)
        self.mass_text=TextObject(display,str(self.mass),x+self.w-self.font_w//2,y+self.h-self.font_w+9,font_w,rl.WHITE)
        self.rect=Rect(display,x,y,w,h)
        self.hitboxes=rl.Rectangle(x,y,w,h)


class Atom_Bar():
    def __init__(self,display,x,y,w,h):
        self.display = display
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.inv=self.display.get_inv()
        self.atom_images={}
        atom_properites={"hydrogen":['H',1,assets.images["Hydrogen_Standby"]],"helium":['He',2,assets.images["Helium_Standby"]],"oxygen":['O',8,assets.images["Oxygen_Standby"]],"sodium":['Na',11,assets.images["Sodium_Standby"]],"iron":['Fe',26,assets.images["Iron_Standby"]],"zinc":['Zn',30,assets.images["Zinc_Standby"]],"barium":['Ba',56,assets.images["Barium_Standby"]],"krypton":['Kr',36,assets.images["Krypton_Standby"]]}
        i=0
        for a in self.inv.keys():
            print(a)
            self.atom_images[a]=Atom(self.display, atom_properites[a][2], x + self.w-i*100, y, 100, 100, atom_properites[a][0], atom_properites[a][1], 40)
            i += 1
class Table():
    def __init__(self,display,x,y,w,h):
        self.display = display
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.protons=0
        self.atoms=[]
        self.rect=Rect(display,x,y,w,h)

