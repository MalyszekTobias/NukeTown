import pyray as rl

shaders = {}
models = {}
images = {}
sounds = {}
font = None

def load():
    global font
    shaders["bloom"] = rl.load_shader("", "app/assets/shaders/bloom.fs")
    images["Jeff"] = rl.load_texture("app/assets/images/Jeff.png")
    images["movingblob"] = rl.load_texture("app/assets/Spritesheets/Uranek_jump.png")
    images["Floor_Default"] = rl.load_texture("app/assets/images/Floor_Default.png")
    images["Floor_Cracked"] = rl.load_texture("app/assets/images/Floor_Cracked.png")
    images["Floor_flower_1"] = rl.load_texture("app/assets/images/Floor_Flower_1.png")
    images["Floor_flower_2"] = rl.load_texture("app/assets/images/Floor_Flower_2.png")
    images["Floor_flower_3"] = rl.load_texture("app/assets/images/Floor_Flower_3.png")
    images["Hydrogen"] = rl.load_texture("app/assets/Spritesheets/Hydrogen.png")
    images["Helium"] = rl.load_texture("app/assets/Spritesheets/Helium.png")
    images["Oxygen"] = rl.load_texture("app/assets/Spritesheets/Oxygen_Walk.png")
    images["Sulphur"] = rl.load_texture("app/assets/Spritesheets/Sulphur.png")
    images["Sodium"] = rl.load_texture("app/assets/Spritesheets/Sodium.png")
    images["Iron"] = rl.load_texture("app/assets/Spritesheets/Iron.png")
    images["Zinc"] = rl.load_texture("app/assets/Spritesheets/Zinc.png")
    images["Barium"] = rl.load_texture("app/assets/Spritesheets/Barrium.png")
    images["Krypton"] = rl.load_texture("app/assets/Spritesheets/Cobalt_jump.png")
    images["Bullet_Good"] = rl.load_texture("app/assets/Spritesheets/Bullet_Good.png")
    images["Bullet_Good_Explode"] = rl.load_texture("app/assets/Spritesheets/Bullet_Good_Explode.png")
    images["Bullet_Bad"] = rl.load_texture("app/assets/Spritesheets/Bullet_Bad.png")
    images["Bullet_Bad_Explode"] = rl.load_texture("app/assets/Spritesheets/Bullet_Bad_Explode.png")
    images["Bullet_Bad_Create"] = rl.load_texture("app/assets/Spritesheets/Bullet_Bad_Create.png")
    images["Bullet_Good_Create"] = rl.load_texture("app/assets/Spritesheets/Bullet_Good_Create.png")
    # images["Elektrownia"] = rl.load_texture("app/assets/Spritesheets/Komin.png")
    images["Wall_horizontal"] = rl.load_texture("app/assets/images/Wall_1.png")
    images["Wall_vertical"] = rl.load_texture("app/assets/images/Wall_2.png")
    images["Elektrownia"] = rl.load_texture("app/assets/Spritesheets/Komin.png")
    images["Oxygen_Standby"] = rl.load_texture("app/assets/images/Oxygen_Standby.png")
    images["Hydrogen_Standby"] = rl.load_texture("app/assets/images/Hydrogen_Standby.png")
    images["Helium_Standby"] = rl.load_texture("app/assets/images/Helium_Standby.png")
    images["Sodium_Standby"] = rl.load_texture("app/assets/images/Sodium_Standby.png")
    images["Barium_Standby"] = rl.load_texture("app/assets/images/Barium_Standby.png")
    images["Zinc_Standby"] = rl.load_texture("app/assets/images/Zinc_Standby.png")
    images["Sulphur_Standby"] = rl.load_texture("app/assets/images/Sulphur_Standby.png")
    images["Iron_Standby"] = rl.load_texture("app/assets/images/Iron_Standby.png")
    images["Krypton_Standby"] = rl.load_texture("app/assets/images/Cobalt_Stand.png")
    images["Wall_corner"] = rl.load_texture("app/assets/images/Corner.png")
    images["Table"] = rl.load_texture("app/assets/images/Table.png")
    images["Tablica"] = rl.load_texture("app/assets/images/Tablica.png")
    images["Tablica_Fatass"] = rl.load_texture("app/assets/images/Tablica_Fatass.png")
    images["Taskbar"] = rl.load_texture("app/assets/images/Taskbar.png")
    images["Uranium_Standby"]=rl.load_texture("app/assets/images/MC_Standby.png")
    font = rl.load_font('app/assets/Fonts/Chernobyl.otf')

    sounds["shot"] = rl.load_sound("app/assets/Sounds/roblox-death-sound-effect.mp3")