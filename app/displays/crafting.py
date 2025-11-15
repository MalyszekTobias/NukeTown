from email.mime import image
import copy
# from zipimport import alt_path_sep
import time
from app.displays.main_display import MainDisplay
from app.displays.main_display2 import MainDisplay2
from app.ui import text
from app import sprite
import pyray as rl
from app.displays.base import BaseDisplay
from app.cameras import twodcamera
from app import assets

class Crafting_Menu(BaseDisplay):

    def __init__(self, game):

        super().__init__(game)
        self.square_pos = [0, 0]
        self.end_chapter_1=False
        self.speed = 200
        self.delta_time = rl.get_frame_time()

        self.texture = rl.load_render_texture(game.width, game.height)
        rl.set_texture_filter(self.texture.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
        self.mouse_down = True
        self.current_atom=None

        self.translator = {"H": "hydrogen", "He": "helium", "O": "oxygen", "Na": "sodium", "Ba": "barium",
                           "Kr": "krypton", "Zn": "zinc", "S": "sulphur", "Fe": "iron","U":"uranium"}
        self.crafting = False

        self.objects = []
        # a=GameObject(self,assets.images["Jeff"],0,0,10,10)
        # t1=TextObject(self,'aaa',0,0,100,rl.WHITE)
        self.table = Table(self, self.game.width // 2, 0, self.game.width // 2, self.game.height)
        self.inventory=Inventory({"oxygen":2,"hydrogen":2,"zinc":3,"sodium":2,"krypton":10,"barium":11,"sulphur":67,"iron":11,"helium":1000},self,0,0,100,200)
        # self.inventory=Inventory({},self,0,0,100,200)
        # self.oxygen1=Atom(self,assets.images["Oxygen_Standby"] ,1000,100,100,100,"O",8,40)
        self.atom_bar=Atom_Bar(self,self.game.width//2,0,self.game.width//2,100)

    def render(self):
        # print(self.square_pos)
        super().render()
        # self.table.update()

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


        if rl.is_key_pressed(rl.KeyboardKey.KEY_C) or rl.is_gamepad_button_pressed(self.game.gamepad_id, rl.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_UP) or rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
            self.table.clear()
            self.game.current_display = self.game.twodgame
            self.game.crafting = False
            self.game.atomic_masses=[]
            self.trans={"oxygen":8,"hydrogen":1,"zinc":30,"sodium":11,"krypton":36,"barium":56,"sulphur":16,"iron":26,"helium":2,"uranium":92}
            for obj in self.game.twodgame.player.friends:
                self.game.twodgame.game_objects.remove(obj)
            self.game.twodgame.player.friends=[]
            for x in self.inventory.inv.keys():
                for y in range(self.inventory.inv[x]):
                    self.game.atomic_masses.append(self.trans[x])
            for mass in self.game.atomic_masses:
                self.game.twodgame.player.spawn_friend(mass)
            if self.end_chapter_1:

                self.end_chapter_1=False
                self.game.twodgame=self.game.display2
                self.game.chapter2=True
                self.game.stop=True
                self.game.change_display(self.game.chapter2_display)


        if rl.is_mouse_button_pressed(0):
            self.mouse_down=True
            self.mouse=rl.get_mouse_position()
            # print(self.mouse.x,self.mouse.y)
            a=False
            self.from_bar=False
            for x in self.atom_bar.atom_images.keys():
                obj=self.atom_bar.atom_images[x]
                if self.collision(obj,self.mouse):
                    if self.inventory.inv[x]>=1:
                        self.current_atom_name=x
                        self.current_atom=Atom(self,obj.image,0,0,obj.w,obj.h,obj.name,obj.mass,obj.font_w)
                        a=True
                        self.from_bar=True

            if not a:
                b=False
                self.from_bar=False
                for obj in self.table.atoms:
                    if self.collision(obj,self.mouse):

                        self.current_atom = obj
                        self.current_atom_name = obj.name
                        b=True
                if not b:
                    if self.collision(self.table.fuse_ram,self.mouse):
                        self.table.do_fusion()
                    elif self.collision(self.table.clear_ram,self.mouse):
                        self.table.clear()
        if rl.is_mouse_button_down(0):

            if self.mouse_down and self.current_atom is not None:
                # for obj in self.objects:
                    # print(obj)
                self.mouse=rl.get_mouse_position()
                # print(self.mouse.x,self.mouse.y)
                self.current_atom.x=int(self.mouse.x)-50
                self.current_atom.y=int(self.mouse.y)-50
                self.current_atom.update()




        if rl.is_mouse_button_released(0):
            if self.current_atom!=None:
                self.mouse_down = False
                a = False
                for atom in self.atom_bar.atom_images.values():
                    if self.rect_collision(atom, self.current_atom):
                        self.current_atom.delete()
                        if not self.from_bar:
                            self.table.atoms.remove(self.current_atom)
                        a = True
                        if self.from_bar==False:
                            try:
                                self.inventory.inv[self.translator[self.current_atom_name]] += 1
                            except:
                                self.inventory.inv[self.translator[self.current_atom_name]] = 1
                            self.atom_bar.update()
                        break
                if not a:
                    if self.from_bar:
                        self.inventory.inv[self.current_atom_name] -= 1
                        self.table.protons+=self.current_atom.mass
                    a = False
                    if self.from_bar:
                        self.table.atoms.append(self.current_atom)
                self.current_atom = None
                self.current_atom_name = None

    def collision(self,obj1,mouse):
        if (obj1.x<mouse.x<obj1.x+obj1.w) :
            if (obj1.y<mouse.y<obj1.y+obj1.h):
                return True
        return False
    def rect_collision(self,obj1,obj2):
        if (obj1.x<obj2.x<obj1.x+obj1.w) or (obj1.x<obj2.x+obj2.w<obj1.x+obj1.w):
            if (obj1.y < obj2.y < obj1.h + obj1.y) or (obj1.y < obj2.y + obj2.h < obj1.y + obj1.h):
                return True

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
    def __str__(self):
        return f"obiekt o pozycji {self.x,self.y,self.w,self.h} i obrazku {self.image}"
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
        text.draw_text_with_border(self.text,self.x,self.y,self.w,self.color,)
    def delete(self):
        self.display.objects.remove(self)
    def __str__(self):
        return f"obiekt o pozycji {self.x,self.y,self.w} text"
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
        # rl.draw_rectangle_lines(self.x,self.y,self.w,self.h,rl.WHITE,)
        pass
    def delete(self):
        self.display.objects.remove(self)
    def __str__(self):
        return f"obiekt o pozycji {self.x,self.y,self.w,self.h} rect"

class Inventory():
    def __init__(self,inv,display,x,y,w,h):
        self.display = display
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.display.objects.append(self)
        self.inv=inv
        self.atom_images={}
        self.tablica_image=assets.images["Tablica_big"]
        self.src=rl.Rectangle(0,0,235,32)
        self.display.objects.append(self)
    def add_element(self,atom,amount):
        if atom in self.inv:
            self.inv[atom] += amount
        else:
            self.inv[atom] = amount
    def draw(self):
        i = 0
        rl.draw_texture_pro(self.tablica_image, self.src,
                            rl.Rectangle(self.x, self.y + 100 + (i - 1) * 100, self.display.game.width // 2 - 240, 100),
                            (0, 0), 0, rl.WHITE)
        text.draw_text_with_border("Inventory", self.x+20, self.y+8, self.w, rl.WHITE)


        for atom in self.inv:
            i+=1

            rl.draw_texture_pro(self.tablica_image,self.src,rl.Rectangle(self.x,self.y+100+(i-1)*100,self.display.game.width // 2 - 240,100),(0, 0), 0, rl.WHITE)
            text.draw_text_with_border(f"{atom}: {self.inv[atom]}", self.x+20, self.y+8 + self.w * i, self.w, rl.WHITE)
        for xi in range(10 - len(self.inv)):
            i += 1
            rl.draw_texture_pro(self.tablica_image, self.src,
                                rl.Rectangle(self.x, self.y + 100 + (i - 1) * 100, self.display.game.width // 2 - 240,
                                             100),
                                (0, 0), 0, rl.WHITE)
            i += 1
            rl.draw_texture_pro(self.tablica_image, self.src,
                                rl.Rectangle(self.x, self.y + 100 + (i - 1) * 100, self.display.game.width // 2 - 240,
                                             100),
                                (0, 0), 0, rl.WHITE)
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


    def update(self):
        self.image_object.square_pos[0], self.image_object.square_pos[1] = self.x-50,self.y-60
        self.image_object.x,self.image_object.y,self.image_object.w,self.image_object.h=self.x-50,self.y-60,self.w,self.h
        self.name_text.x,self.name_text.y=self.x,self.y-3
        self.mass_text.x,self.mass_text.y=self.x+self.w-self.font_w//2,self.y+self.h-self.font_w+9
        self.rect.x,self.rect.y=self.x,self.y
        self.hitboxes = rl.Rectangle(self.x, self.y, self.w, self.h)
    def delete(self):
        self.image_object.delete()
        self.name_text.delete()
        self.mass_text.delete()
        self.rect.delete()


class Atom_Bar():
    def __init__(self,display,x,y,w,h):
        self.display = display
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.inv=self.display.get_inv()
        self.atom_images={}
        self.bar=GameObject(display,assets.images["Taskbar"],x-240,y,w,h,256)
        atom_properites={"hydrogen":['H',1,assets.images["Hydrogen_Standby"]],"helium":['He',2,assets.images["Helium_Standby"]],"oxygen":['O',8,assets.images["Oxygen_Standby"]],"sodium":['Na',11,assets.images["Sodium_Standby"]],"iron":['Fe',26,assets.images["Iron_Standby"]],"zinc":['Zn',30,assets.images["Zinc_Standby"]],"barium":['Ba',56,assets.images["Barium_Standby"]],"krypton":['Kr',36,assets.images["Krypton_Standby"]],"sulphur":['S',16,assets.images["Sulphur_Standby"]],"uranium":["U",92,assets.images["Uranium_Standby"]]}
        i=0
        for a in self.inv.keys():
            # print(a)
            i += 1
            self.atom_images[a]=Atom(self.display, atom_properites[a][2], x + self.w-i*100-40-(i-1)*16, y+9, 100, 100, atom_properites[a][0], atom_properites[a][1], 40)

    def update(self):
        for i in self.atom_images.values():
            try:
                i.delete()
            except:
                pass
        self.inv = self.display.get_inv()
        self.atom_images = {}
        atom_properites = {"hydrogen": ['H', 1, assets.images["Hydrogen_Standby"]],
                           "helium": ['He', 2, assets.images["Helium_Standby"]],
                           "oxygen": ['O', 8, assets.images["Oxygen_Standby"]],
                           "sodium": ['Na', 11, assets.images["Sodium_Standby"]],
                           "iron": ['Fe', 26, assets.images["Iron_Standby"]],
                           "zinc": ['Zn', 30, assets.images["Zinc_Standby"]],
                           "barium": ['Ba', 56, assets.images["Barium_Standby"]],
                           "krypton": ['Kr', 36, assets.images["Krypton_Standby"]],
                           "sulphur": ['S', 16, assets.images["Sulphur_Standby"]],"uranium":["U",92,assets.images["Uranium_Standby"]]}
        i = 0
        for a in self.inv.keys():
            # print(a)
            i += 1
            self.atom_images[a] = Atom(self.display, atom_properites[a][2], self.x + self.w-i*100-40-(i-1)*16, self.y+9, 100, 100,
                                       atom_properites[a][0], atom_properites[a][1], 40)





class Table():
    def __init__(self,display,x,y,w,h):
        self.display = display
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.protons=0
        self.atoms=[]
        self.rect=Rect(display,x,y,w-1,h-1)
        self.font=90

        self.table_object=GameObject(self.display,assets.images["Table"],x-412,y-500,w,h,15)
        self.fuse_text = TextObject(display, 'Fuse', x + w - int(2.5 * self.font)+20, y + h - self.font+7, self.font,
                                    rl.WHITE)
        self.fuse_ram = Rect(self.display, x + w - int(2.5 * self.font), y + h - self.font, int(2.5 * self.font) - 1,
                             self.font - 1)

        self.clear_text = TextObject(display,"Clear", x-230, y+7 + h - self.font, self.font,
                                     rl.WHITE)
        self.clear_ram = Rect(self.display, x-239, y + h - self.font, int(3 * self.font) - 1,
                              self.font - 1)
        self.atom_properites = {"hydrogen": ['H', 1, assets.images["Hydrogen_Standby"]],
                           "helium": ['He', 2, assets.images["Helium_Standby"]],
                           "oxygen": ['O', 8, assets.images["Oxygen_Standby"]],
                           "sodium": ['Na', 11, assets.images["Sodium_Standby"]],
                           "iron": ['Fe', 26, assets.images["Iron_Standby"]],
                           "zinc": ['Zn', 30, assets.images["Zinc_Standby"]],
                           "barium": ['Ba', 56, assets.images["Barium_Standby"]],
                           "krypton": ['Kr', 36, assets.images["Krypton_Standby"]],
                           "sulphur": ['S', 16, assets.images["Sulphur_Standby"]],
                            "uranium":["U",92,assets.images["Uranium_Standby"]]}
        self.translator={"H":"hydrogen","He":"helium","O":"oxygen","Na":"sodium","Ba":"barium","Kr":"krypton","Zn":"zinc","S":"sulphur","Fe":"iron","U":"uranium"}
        self.values=[[1,"hydrogen"],[2,"helium"],[8,"oxygen"],[11,"sodium"],[16,"sulphur"],[26,"iron"],[30,"zinc"],[36,"krypton"],[56,"barium"],[92,"uranium"]]
    def update(self):
        if self.display.end_chapter_1==False:
                if self.display.inventory.inv['uranium']>=9:
                    self.fuse_text.text = "Start the chain reaction"
                    self.fuse_text.w = 70
                    self.fuse_ram.w = 70
                    measure=rl.measure_text(self.fuse_text.text,self.fuse_text.w)
                    self.fuse_text.x=self.x+self.w-measure-15
                    self.fuse_ram.x=self.x+self.w-measure-15
                else:

                    self.fuse_text.text="Not enough uranium"
                    self.fuse_text.w = 70
                    self.fuse_ram.w = 70
                    measure=rl.measure_text(self.fuse_text.text,self.fuse_text.w)
                    self.fuse_text.x=self.x+self.w-measure-15
                    self.fuse_ram.x=self.x+self.w-measure-15
    def do_fusion(self):
        if type(self.display.game.twodgame)==MainDisplay:
            if self.display.end_chapter_1 == False:
                if self.protons == 92:
                    if self.display.end_chapter_1 == False:
                        self.display.game.change_display(self.display.game.cutscene_display)
                        self.display.game.change_display(self.display.game.cutscene_display)
                    self.display.end_chapter_1 = True

                if self.protons > 92:
                    print('nope')
                elif len(self.atoms) > 1:
                    a = True
                    i = len(self.values) - 1
                    while a:

                        if self.protons >= self.values[i][0]:
                            if self.values[i][0] > self.display.game.best_craft:
                                self.display.game.best_craft = self.values[i][0]
                            self.clear_before_fusion()
                            self.atoms.append(
                                Atom(self.display, self.atom_properites[self.values[i][1]][2], self.x + self.w // 2,
                                     self.y + self.h // 2, 100, 100, self.atom_properites[self.values[i][1]][0],
                                     self.atom_properites[self.values[i][1]][1], 40))
                            self.protons = self.atom_properites[self.values[i][1]][1]
                            break
                        i -= 1
        else:
            print('xxx')
            if self.display.inventory.inv['uranium'] >= 9:
                self.display.game.change_display(self.display.game.ending)

        # self.clear()
    def clear(self):
        for atom in self.atoms:
            print(atom.name)
            try:
                self.display.inventory.inv[self.translator[atom.name]]+=1
            except:
                self.display.inventory.inv[self.translator[atom.name]] = 1
                # self.display.inventory.update()
                self.display.atom_bar.update()

            atom.delete()

        self.atoms=[]
        self.protons=0
    def clear_before_fusion(self):
        for atom in self.atoms:
            print(atom.name)

            atom.delete()

        self.atoms=[]
        self.protons=0