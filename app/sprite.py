from app import assets
import pyray as rl

class Sprite:
    def __init__(self, display, scaleXframewidth=5):
        self.display = display
        self.game = display.game
        self.scaleXframewidth = scaleXframewidth
        self.num_of_frames = int(self.img.height / self.img.width)
        self.frame_width = int(self.img.width)
        self.frame_height = int(self.img.height / self.num_of_frames)
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.08
        self.x = 0
        self.y = 0
        self.gameHeight = self.game.height
        self.gameWidth = self.game.width

        self.display.game_objects.append(self)


    def update(self):

        dt = rl.get_frame_time()
        self.frame_timer += dt
        while self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_of_frames
            if self.current_frame == 0:
                self.frame_timer = 0.0
                break

    def render(self):
        scale = self.scaleXframewidth / float(self.frame_width)

        src = rl.Rectangle(0.0, float(self.frame_height * self.current_frame),
                           float(self.frame_width), float(self.frame_height))
        dst_w = float(self.frame_width) * scale
        dst_h = float(self.frame_height) * scale
        dst_x = float(self.x) - dst_w / 2.0
        dst_y = float(self.y) - dst_h / 2.0
        dst = rl.Rectangle(dst_x, dst_y, dst_w, dst_h)
        origin = rl.Vector2(0.0, 0.0)
        angle = 0

        rl.draw_texture_pro(self.img, src, dst, origin, angle, rl.WHITE)
