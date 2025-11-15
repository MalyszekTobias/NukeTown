import os
import glob
import pyray as rl


class MusicManager:
    """Simple music manager that loads two music tracks and can switch between them.

    Behavior:
    - Initializes audio device on construction.
    - Attempts to load two known music files from app/assets/Sounds; falls back to finding first two .mp3 files.
    - Starts with nothing playing; call play_music1() to start the default track.
    - Call update() each frame to keep streaming and to auto-restart tracks for looping.
    """

    # default expected paths (may be overridden by discovery)
    MUSIC1_DEFAULT = "app/assets/Sounds/Doom Eternal OST - The Only Thing They Fear Is You (Mick Gordon) [Doom Eternal Theme].mp3"
    MUSIC2_DEFAULT = "app/assets/Sounds/Terraria Music - Day.mp3"

    def __init__(self):
        # initialize audio device if available
        try:
            rl.init_audio_device()
        except Exception:
            # if audio APIs aren't available in this pyray build, keep going silently
            pass

        # try explicit paths first, then fallback to first two mp3s in folder
        paths = []
        for p in (MusicManager.MUSIC1_DEFAULT, MusicManager.MUSIC2_DEFAULT):
            if os.path.exists(p):
                paths.append(p)

        if len(paths) < 2:
            found = glob.glob(os.path.join("app", "assets", "Sounds", "*.mp3"))
            # keep order but only unique
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

        # load streams if possible
        try:
            if len(paths) > 0:
                self._m1 = rl.load_music_stream(paths[0])
            if len(paths) > 1:
                self._m2 = rl.load_music_stream(paths[1])
        except Exception:
            # if load_music_stream isn't available or files fail to load, leave as None
            self._m1 = None
            self._m2 = None

    def play_music1(self):
        """Play music track 1 (if loaded)."""
        if not self._m1:
            return
        self._play(self._m1)

    def play_music2(self):
        """Play music track 2 (if loaded)."""
        if not self._m2:
            return
        self._play(self._m2)

    def _play(self, music):
        # stop current if different
        try:
            if self.current and self.current != music:
                rl.stop_music_stream(self.current)
        except Exception:
            pass

        self.current = music
        try:
            rl.play_music_stream(self.current)
            # apply current volume to the playing music stream when possible
            try:
                rl.set_music_volume(self.current, float(self.volume))
            except Exception:
                # fallback: try master volume if available
                try:
                    rl.set_master_volume(float(self.volume))
                except Exception:
                    pass
        except Exception:
            # some pyray builds might not expose these helpers; just ignore failures
            pass

    def play_sound(self, sound):
        """Play a one-off sound effect from the given file path."""
        rl.play_sound(sound)

    def stop(self):
        """Stop any currently playing music."""
        try:
            if self.current:
                rl.stop_music_stream(self.current)
        except Exception:
            pass
        self.current = None

    def set_volume(self, volume: float):
        """Set music volume (0.0 - 1.0). Applies immediately to currently playing track if possible."""
        # clamp
        try:
            v = float(volume)
        except Exception:
            return
        self.volume = v

        # apply to current music if possible
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
        """Should be called each frame to stream/update the current music and keep it looping."""
        if not self.current:
            return
        try:
            rl.update_music_stream(self.current)
            # attempt to keep it looping: if not playing, restart
            if hasattr(rl, "is_music_playing"):
                try:
                    if not rl.is_music_playing(self.current):
                        rl.play_music_stream(self.current)
                        # ensure volume is applied after restart
                        try:
                            rl.set_music_volume(self.current, float(self.volume))
                        except Exception:
                            try:
                                rl.set_master_volume(float(self.volume))
                            except Exception:
                                pass
                except Exception:
                    # if this API has a different signature, ignore
                    pass
        except Exception:
            # update_music_stream may not exist in some bindings
            pass

    def unload(self):
        """Unload music streams and close audio device."""
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
