# app/book.py
import pyray as rl
from app import assets

class Book:
    # Class variable to store flavour texts loaded from file
    flavour_texts = []

    @classmethod
    def load_flavour_texts(cls):
        """Load flavour texts from the Flavour.txt file."""
        if not cls.flavour_texts:  # Only load once
            try:
                with open('app/assets/Flavour/Flavour.txt', 'r', encoding='utf-8') as f:
                    cls.flavour_texts = [line.strip() for line in f.readlines() if line.strip()]
            except Exception as e:
                print(f"Error loading flavour texts: {e}")
                # Fallback texts if file can't be loaded
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
        """
        Create a book at position (x, y) with a specific book_id.

        Args:
            display: The game display object
            x: X position in world coordinates
            y: Y position in world coordinates
            book_id: Unique identifier for this book (1-8)
            interaction_radius: Distance within which player can interact
        """
        # Load flavour texts if not already loaded
        if not Book.flavour_texts:
            Book.load_flavour_texts()

        self.display = display
        self.x = x
        self.y = y
        self.book_id = book_id
        self.interaction_radius = interaction_radius
        self.size = 4  # Size for rendering

        # Get the flavour text for this book (book_id 1 = index 0, etc.)
        text_index = book_id - 1
        if 0 <= text_index < len(Book.flavour_texts):
            self.flavour_text = Book.flavour_texts[text_index]
        else:
            self.flavour_text = f"Book {book_id} - No text available"

        # Try to load paper texture, fallback to simple rectangle if not available
        self.texture = assets.images.get("Paper")

        # Animation properties for 5 frames, each 1024x1024
        self.num_of_frames = 5
        self.frame_width = 1024
        self.frame_height = 1024
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.3  # Slow animation - 0.3 seconds per frame

        # Add to display's game objects
        self.display.game_objects.append(self)

    def can_interact(self, player):
        """Check if player is close enough to interact with this book."""
        try:
            dx = self.x - player.x
            dy = self.y - player.y
            distance = (dx * dx + dy * dy) ** 0.5
            return distance <= self.interaction_radius
        except Exception:
            return False

    def render(self):
        """Draw the book on the map with animation."""
        if self.texture:
            # Calculate source rectangle for current frame (vertical sprite sheet)
            src = rl.Rectangle(
                0.0,
                float(self.frame_height * self.current_frame),
                float(self.frame_width),
                float(self.frame_height)
            )
            # Destination rectangle
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
            # Fallback: draw a simple rectangle
            rl.draw_rectangle(
                int(self.x - self.size / 2),
                int(self.y - self.size / 2),
                int(self.size),
                int(self.size),
                rl.BROWN
            )

    def update(self):
        """Update animation frame."""
        dt = rl.get_frame_time()
        self.frame_timer += dt
        while self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_of_frames
            if self.current_frame == 0:
                self.frame_timer = 0.0
                break

