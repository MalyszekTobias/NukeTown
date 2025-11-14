import pyray as rl

shaders = {}
models = {}
images = {}

def load():
    shaders["bloom"] = rl.load_shader("", "app/assets/shaders/bloom.fs")
    images["Jeff"] = rl.load_texture("app/assets/images/Jeff.png")
    images["movingblob"] = rl.load_texture("app/assets/Spritesheets/Uranek_jump.png")
    images["Floor_Default"] = rl.load_texture("app/assets/images/Floor_Default.png")
    images["Floor_Cracked"] = rl.load_texture("app/assets/images/Floor_Cracked.png")
    images["Floor_flower_1"] = rl.load_texture("app/assets/images/Floor_Flower_1.png")
    images["Floor_flower_2"] = rl.load_texture("app/assets/images/Floor_Flower_2.png")
    images["Floor_flower_3"] = rl.load_texture("app/assets/images/Floor_Flower_3.png")
    images["Hydrogen"] = rl.load_texture("app/assets/images/Spritesheets/Hydrogen.png")
    images["Helium"] = rl.load_texture("app/assets/images/Spritesheets/Helium.png")
    images["Oxygen"] = rl.load_texture("app/assets/images/Spritesheets/Oxygen_Walk.png")
    images["Sulphur"] = rl.load_texture("app/assets/images/Spritesheets/Sulphur.png")
    images["Sodium"] = rl.load_texture("app/assets/images/Spritesheets/Sodium.png")
    images["Iron"] = rl.load_texture("app/assets/images/Spritesheets/Iron.png")
    images["Zinc"] = rl.load_texture("app/assets/images/Spritesheets/Zinc.png")
    images["Barium"] = rl.load_texture("app/assets/images/Spritesheets/Barrium.png")
    images["Krypton"] = rl.load_texture("app/assets/images/Spritesheets/Cobalt_jump.png")