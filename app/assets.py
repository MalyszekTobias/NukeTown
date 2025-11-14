import pyray as rl

shaders = {}
models = {}
images = {}

def load():
    shaders["bloom"] = rl.load_shader("", "app/assets/shaders/bloom.fs")
    images["Jeff"] = rl.load_texture("app/assets/images/Jeff.png")
    images["movingblob"] = rl.load_texture("app/assets/Spritesheets/MC_Walk.png")