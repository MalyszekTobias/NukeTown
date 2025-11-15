import pyray as rl

import app.enemy_blob
from app.atom import Atom
from app import assets

class Player(Atom):
    def __init__(self, game, weight=0):
        super().__init__(game, weight, None, 200, 200)
        self.friends = []
        self.x = 200
        self.y = 200
        self.hp = 100
        self.hpHeight = 20


    def spawn_friend(self, weight):
        friend = Atom(self.display, weight, self, self.x, self.y)
        friend.x = self.x + rl.get_random_value(-5, 5)
        friend.y = self.y + rl.get_random_value(-5, 5)
        self.friends.append(friend)

    def update(self, rooms = None, corridor_tiles = None):
        super().update(rooms, corridor_tiles)
        print(self.game.best_craft)
        for room in rooms:
            if room.busy == 0:
                if rl.check_collision_recs(self.rect, room.one_collision_rect(16)):
                    room.busy = 1
                    if not self.game.chapter2:
                        e = app.enemy_blob.EnemyBlob(self.display, (room.x + room.width / 2) * 16,
                                                     16 * (room.y + room.height / 2), 10, self.get_weight_of_spawned(), room=room)
                        self.display.enemies.append(e)

            elif room.busy == 2:
                if not rl.check_collision_recs(self.rect, room.one_collision_rect(16)):
                    room.busy = 0

        for enemy_bullet in self.display.enemy_bullets:
            if rl.check_collision_circles(rl.Vector2(self.x, self.y), self.radius / 2,
                                          rl.Vector2(enemy_bullet.x, enemy_bullet.y), enemy_bullet.radius / 2):
                self.hp -= enemy_bullet.damage
                self.display.enemy_bullets.remove(enemy_bullet)
                self.game.music_manager.play_sound(assets.sounds["shot"])
        try:
            if rl.is_key_pressed(rl.KeyboardKey.KEY_E) or rl.is_gamepad_button_pressed(self.game.gamepad_id, rl.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_LEFT):
                mp = getattr(self.display, 'map', None)
                if mp and getattr(mp, 'gates', None):
                    for g in mp.gates.values():
                        try:
                            if g.can_interact(self):
                                g.interact(self)
                                break
                        except Exception:
                            pass
        except Exception:
            pass
    def get_weight_of_spawned(self):
        weights = [1, 2, 8, 11, 16, 26, 30, 36, 56, 92]
        i = weights.index(self.game.best_craft)
        return weights[i-1] if i > 0 else weights[0]