# app/player.py
import pyray as rl
from app.atom import Atom
from app import assets

class Player(Atom):
    def __init__(self, game, weight=0):
        super().__init__(game, weight, None)
        self.friends = []
        self.x = 200
        self.y = 200


    def spawn_friend(self, weight):
        friend = Atom(self.game, weight, self)
        friend.x = self.x + rl.get_random_value(-5, 5)
        friend.y = self.y + rl.get_random_value(-5, 5)
        self.friends.append(friend)

    def update(self, rooms = None, corridor_tiles = None):
        super().update()
        for enemy_bullet in self.game.enemy_bullets:
            if rl.check_collision_circles(rl.Vector2(self.x, self.y), self.radius / 2,
                                          rl.Vector2(enemy_bullet.x, enemy_bullet.y), enemy_bullet.radius / 2):
                self.game.enemy_bullets.remove(enemy_bullet)
                self.game.music_manager.play_sound(assets.sounds["shot"])
