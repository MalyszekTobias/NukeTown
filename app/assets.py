import pyray as rl

shaders = {}
models = {}
images = {}

def load():
    shaders["bloom"] = rl.load_shader("", "app/assets/shaders/bloom.fs")
    models["shiba"] = rl.load_model("app/assets/models/blackrat_free_glb/blackrat.glb")
    images["Jeff"] = rl.load_texture("app/assets/images/Jeff.png")