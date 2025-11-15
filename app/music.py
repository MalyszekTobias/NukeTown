import os
import glob
import pyray as rl


class MusicManager:

    # default expected paths (may be overridden by discovery)
    MUSIC1_DEFAULT = "app/assets/Sounds/Doom Eternal OST - The Only Thing They Fear Is You (Mick Gordon) [Doom Eternal Theme].mp3"
    MUSIC2_DEFAULT = "app/assets/Sounds/Terraria Music - Day.mp3"
    #https://pixabay.com/music/upbeat-game-minecraft-gaming-background-music-402451/

    def __init__(self):
        try:
            rl.init_audio_device()
        except Exception:
            pass

        paths = []
        for p in (MusicManager.MUSIC1_DEFAULT, MusicManager.MUSIC2_DEFAULT):
            if os.path.exists(p):
                paths.append(p)

        if len(paths) < 2:
            found = glob.glob(os.path.join("app", "assets", "Sounds", "*.mp3"))
            for f in found:
                if f not in paths:
                    paths.append(f)
                if len(paths) >= 2:
                    break

        self._m1 = None
        self._m2 = None
        self.current = None
        # volume in range 0.0 - 1.0
        self.volume = 1

        try:
            if len(paths) > 0:
                self._m1 = rl.load_music_stream(paths[0])
            if len(paths) > 1:
                self._m2 = rl.load_music_stream(paths[1])
        except Exception:
            self._m1 = None
            self._m2 = None

    def play_music1(self):
        if not self._m1:
            return
        self._play(self._m1)

    def play_music2(self):
        if not self._m2:
            return
        self._play(self._m2)

    def _play(self, music):
        try:
            if self.current and self.current != music:
                rl.stop_music_stream(self.current)
        except Exception:
            pass

        self.current = music
        try:
            rl.play_music_stream(self.current)
            try:
                rl.set_music_volume(self.current, float(self.volume))
            except Exception:
                try:
                    rl.set_master_volume(float(self.volume))
                except Exception:
                    pass
        except Exception:
            pass

    def play_sound(self, sound):
        rl.play_sound(sound)

    def stop(self):
        try:
            if self.current:
                rl.stop_music_stream(self.current)
        except Exception:
            pass
        self.current = None

    def set_volume(self, volume: float):
        try:
            v = float(volume)
        except Exception:
            return
        self.volume = v

        try:
            if self.current:
                try:
                    rl.set_music_volume(self.current, float(self.volume))
                except Exception:
                    try:
                        rl.set_master_volume(float(self.volume))
                    except Exception:
                        pass
        except Exception:
            pass

    def update(self):
        if not self.current:
            return
        try:
            rl.update_music_stream(self.current)
            if hasattr(rl, "is_music_playing"):
                try:
                    if not rl.is_music_playing(self.current):
                        rl.play_music_stream(self.current)
                        try:
                            rl.set_music_volume(self.current, float(self.volume))
                        except Exception:
                            try:
                                rl.set_master_volume(float(self.volume))
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass

    def unload(self):
        try:
            if self._m1:
                rl.unload_music_stream(self._m1)
                self._m1 = None
            if self._m2:
                rl.unload_music_stream(self._m2)
                self._m2 = None
        except Exception:
            pass
        try:
            rl.close_audio_device()
        except Exception:
            pass
