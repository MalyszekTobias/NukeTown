import pyray as rl
from app import assets

class Book:
    flavour_texts = []

    @classmethod
    def load_flavour_texts(cls):
        if not cls.flavour_texts:
            try:
                with open('app/assets/Flavour/Flavour.txt', 'r', encoding='utf-8') as f:
                    cls.flavour_texts = [line.strip() for line in f.readlines() if line.strip()]
            except Exception as e:
                print(f"Error loading flavour texts: {e}")
                cls.flavour_texts = [
                    "1. Default text 1",
                    "2. Default text 2",
                    "3. Default text 3",
                    "4. Default text 4",
                    "5. Default text 5",
                    "6. Default text 6",
                    "7. Default text 7",
                    "8. Default text 8"
                ]
    def __init__(self, display, x, y, book_id, interaction_radius=3.0):

        if not Book.flavour_texts:
            Book.load_flavour_texts()

        self.display = display
        self.x = x
        self.y = y
        self.book_id = book_id
        self.interaction_radius = interaction_radius
        self.size = 4
        text_index = book_id - 1
        if 0 <= text_index < len(Book.flavour_texts):
            self.flavour_text = Book.flavour_texts[text_index]
        else:
            self.flavour_text = f"Book {book_id} - No text available"

        self.texture = assets.images.get("Paper")

        self.num_of_frames = 5
        self.frame_width = 1024
        self.frame_height = 1024
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.3

        self.display.game_objects.append(self)

    def can_interact(self, player):
        try:
            dx = self.x - player.x
            dy = self.y - player.y
            distance = (dx * dx + dy * dy) ** 0.5
            return distance <= self.interaction_radius
        except Exception:
            return False

    def render(self):
        if self.texture:
            src = rl.Rectangle(
                0.0,
                float(self.frame_height * self.current_frame),
                float(self.frame_width),
                float(self.frame_height)
            )
            dst = rl.Rectangle(
                float(self.x - self.size / 2),
                float(self.y - self.size / 2),
                float(self.size),
                float(self.size)
            )
            rl.draw_texture_pro(
                self.texture,
                src,
                dst,
                rl.Vector2(0, 0),
                0,
                rl.WHITE
            )
        else:
            rl.draw_rectangle(
                int(self.x - self.size / 2),
                int(self.y - self.size / 2),
                int(self.size),
                int(self.size),
                rl.BROWN
            )

    def update(self):
        dt = rl.get_frame_time()
        self.frame_timer += dt
        while self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_of_frames
            if self.current_frame == 0:
                self.frame_timer = 0.0
                break

