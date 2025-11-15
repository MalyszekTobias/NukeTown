from app.displays.base import BaseDisplay
from app.ui import text, button
import pyray as rl
from app.displays import startscreen


class Menu(BaseDisplay):
    def __init__(self, game):
        super().__init__(game)
        self.resume_button = button.Button(self.game, self.game.width/2 - rl.measure_text('RESUME', 60) /2, self.game.height/5, rl.measure_text('RESUME', 60) -24, 60, 'resume', 60, rl.BLACK, (rl.GRAY[0], rl.GRAY[1],rl.GRAY[2], 0), rl.RED, rl.RED)

        self.quit_button = button.Button(self.game, self.game.width / 2 - rl.measure_text('QUIT', 60) / 2,
                                       self.game.height / 3.5, rl.measure_text('QUIT', 60) - 24, 60, 'QUIT', 60,
                                       rl.BLACK, (rl.GRAY[0], rl.GRAY[1], rl.GRAY[2], 0), rl.RED, rl.RED)

        self.rage_quit_button = button.Button(self.game, self.game.width / 2 - rl.measure_text('RAGE QUIT', 60) / 2,
                                         self.game.height / 1.5, rl.measure_text('RAGE QUIT', 60) - 24, 60, 'RAGE QUIT', 60,
                                         rl.BLACK, (rl.GRAY[0], rl.GRAY[1], rl.GRAY[2], 0), rl.RED, rl.RED)

    def render(self):
        # super().render()
        rl.draw_rectangle(0, 0, self.game.width, self.game.height, (rl.GRAY[0], rl.GRAY[1], rl.GRAY[2], 5))
        self.resume_button.draw()
        self.quit_button.draw()
        self.rage_quit_button.draw()


    def update(self):
        super().update()
        self.resume_button.update()
        self.quit_button.update()
        self.rage_quit_button.update()
        if rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE) or self.resume_button.is_clicked:
            self.game.change_display(self.game.twodgame)

        elif self.rage_quit_button.is_clicked:
            rl.close_window()

        elif self.quit_button.is_clicked:
            self.game.base_display = startscreen.StartDisplay(self.game)
            self.game.change_display(self.game.base_display)

