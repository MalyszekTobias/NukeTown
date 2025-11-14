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