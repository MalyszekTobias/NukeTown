# app/player.py
import pyray as rl
from app.atom import Atom

class Player(Atom):
    def __init__(self, game, weight=0):
        super().__init__(game, weight, None)
        self.friends = []
        self.x = 300
        self.y = 200


    def spawn_friend(self, weight):
        friend = Atom(self.game, weight, self)
        friend.x = self.x + rl.get_random_value(-5, 5)
        friend.y = self.y + rl.get_random_value(-5, 5)
        self.friends.append(friend)