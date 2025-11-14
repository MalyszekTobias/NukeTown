import pyray as rl

shaders = {}
images = {}

def load():
    shaders["bloom"] = rl.load_shader("", "app/assets/shaders/bloom.fs")
    images["Jeff"] = rl.load_texture("app/assets/images/Jeff.png")