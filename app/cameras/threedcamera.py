import pyray as rl

class Camera:
    def __init__(self, tx, ty, tz, offset, smooth_factor, fov):
        ox, oy, oz = offset
        self.offset = rl.Vector3(ox, oy, oz)


        self.camera = rl.Camera3D()

        target = rl.Vector3(tx, ty, tz)
        position = rl.Vector3(tx + ox, ty + oy, tz + oz)

        self.camera = rl.Camera3D(
            position,
            target,
            rl.Vector3(0.0, 1.0, 0.0),
            fov,
            rl.CameraProjection.CAMERA_PERSPECTIVE
        )

        self.smooth_factor = smooth_factor


    def update_target(self, tx, ty, tz, dt):
        self.camera.target = rl.Vector3(tx, ty, tz)

        desired = rl.Vector3(
            self.camera.target.x + self.offset.x,
            self.camera.target.y + self.offset.y,
            self.camera.target.z + self.offset.z
        )

        cur = self.camera.position
        t = min(1.0, self.smooth_factor * dt)
        self.camera.position = rl.Vector3(
            cur.x + (desired.x - cur.x) * t,
            cur.y + (desired.y - cur.y) * t,
            cur.z + (desired.z - cur.z) * t
        )

    def begin_mode(self):
        rl.begin_mode_3d(self.camera)

    def end_mode(self):
        rl.end_mode_3d()