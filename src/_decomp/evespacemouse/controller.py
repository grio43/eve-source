#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evespacemouse\controller.py
import math
import geo2

def Lerp(t, v1, v2):
    return (1 - t) * v1 + t * v2


def VectorClamp(source_vector, clamp_vector):
    v = geo2.Vector(tuple([ (v if abs(v) <= abs(cv) else math.copysign(cv, v)) for v, cv in zip(source_vector, clamp_vector) ]))
    return v


def VecMul(v1, v2, scale = 1.0):
    return geo2.Vector(tuple([ v1_component * v2_component * scale for v1_component, v2_component in zip(v1, v2) ]))


class SpaceMouseController(object):
    VELOCITY_RANGE = (100, 10000)
    ANGULAR_VELOCITY_RANGE = (math.pi / 8.0, math.pi / 6.0)
    ACCELERATION_TIME_RANGE = (3.0, 0.5)
    ANGULAR_ACCELERATION_TIME_RANGE = (3.5, 0.5)
    VELOCITY_UNIT_VECTOR = (1.0, 0.5, -1.0)
    ANGULAR_VELOCITY_UNIT_VECTOR = (0.4, 1)

    def __init__(self, speed_coefficient, acceleration_coefficient):
        self.current_velocity = geo2.Vector(0, 0, 0)
        self.current_angular_velocity = geo2.Vector(0, 0)
        self.max_velocity = geo2.Vector(0, 0, 0)
        self.max_angular_velocity = geo2.Vector(0, 0)
        self.translation_acceleration_time = 0.0
        self.angular_acceleration_time = 0.0
        self.last_translation = geo2.Vector(0, 0, 0)
        self.last_rotation = geo2.Vector(0, 0)
        self.velocity_length = 0.0
        self.angular_velocity_length = 0.0
        self.SetAccelerationCoefficient(acceleration_coefficient)
        self.SetSpeedCoefficient(speed_coefficient)
        self.current_translation_input = geo2.Vector(0, 0, 0)
        self.current_rotation_input = geo2.Vector(0, 0)

    def Stop(self):
        self.current_velocity = geo2.Vector(0, 0, 0)
        self.current_angular_velocity = geo2.Vector(0, 0)

    def GetInfo(self):
        text = '\nmax velocity (%2.7f, %2.7f, %2.7f)m/s' % tuple(self.max_velocity)
        text += '\nmax angular velocity (%2.7f, %2.7f)rad/s' % tuple(self.max_angular_velocity)
        text += '\nacceleration %2.7f m/s2' % (self.max_velocity[0] / self.translation_acceleration_time)
        text += '\nangular acceleration %2.7f rad/s2' % (self.max_angular_velocity[1] / self.angular_acceleration_time)
        text += '\nacceleration time %2.7f s' % self.translation_acceleration_time
        text += '\nangular acceleration time %2.7f s' % self.angular_acceleration_time
        text += '\ncurrent translation velocity (%2.7f, %2.7f, %2.7f)m/s' % tuple(self.current_velocity)
        text += '\ncurrent angular velocity (%2.7f, %2.7f)rad/s' % tuple(self.current_angular_velocity)
        text += '\nvelocity length %2.7f' % self.velocity_length
        text += '\nangular velocity length %2.7f' % self.angular_velocity_length
        text += '\nlast translation (%2.7f, %2.7f, %2.7f)m' % tuple(self.last_translation)
        text += '\nlast rotation (%2.7f, %2.7f)rad' % tuple(self.last_rotation)
        text += '\ncurrent translation input (%2.7f, %2.7f, %2.7f)' % tuple(self.current_translation_input)
        text += '\ncurrent rotation input (%2.7f, %2.7f)' % tuple(self.current_rotation_input)
        return text

    def SetAccelerationCoefficient(self, acceleration_coefficient):
        acceleration_coefficient = min(1.0, max(0.01, acceleration_coefficient))
        self.translation_acceleration_time = Lerp(acceleration_coefficient, *self.ACCELERATION_TIME_RANGE)
        self.angular_acceleration_time = Lerp(acceleration_coefficient, *self.ANGULAR_ACCELERATION_TIME_RANGE)

    def SetSpeedCoefficient(self, speed_coefficient):
        speed_coefficient = min(1.0, max(0.01, speed_coefficient))
        self.max_velocity = geo2.Vec3Scale(self.VELOCITY_UNIT_VECTOR, Lerp(speed_coefficient, *self.VELOCITY_RANGE))
        self.max_angular_velocity = geo2.Vec2Scale(self.ANGULAR_VELOCITY_UNIT_VECTOR, Lerp(speed_coefficient, *self.ANGULAR_VELOCITY_RANGE))

    def CalculateTranslationAndRotation(self, dt, acceleration, angular_acceleration):
        acceleration = geo2.Vector(acceleration)
        angular_acceleration = geo2.Vector(angular_acceleration[0], angular_acceleration[1])
        self.current_translation_input = acceleration
        self.current_rotation_input = angular_acceleration
        if geo2.Vec3LengthSq(acceleration) == 0.0 and geo2.Vec2LengthSq(angular_acceleration) == 0.0 and self.velocity_length == 0.0 and self.angular_velocity_length == 0.0:
            return ((0, 0, 0), (0, 0))
        acceleration = VecMul(acceleration, self.max_velocity, 1.0 / self.translation_acceleration_time)
        angular_acceleration = VecMul(angular_acceleration, self.max_angular_velocity, 1.0 / self.angular_acceleration_time)
        self.current_velocity = geo2.Vec3Add(self.current_velocity, geo2.Vec3Scale(acceleration, dt))
        self.current_angular_velocity = geo2.Vec2Add(self.current_angular_velocity, geo2.Vec2Scale(angular_acceleration, dt))
        self.current_velocity = geo2.Vec3Scale(self.current_velocity, max(0.0, 1.0 - 0.5 * dt / self.translation_acceleration_time))
        self.current_angular_velocity = geo2.Vec2Scale(self.current_angular_velocity, max(0.0, 1.0 - 0.5 * dt / self.angular_acceleration_time))
        self.current_velocity = VectorClamp(self.current_velocity, self.max_velocity)
        self.current_angular_velocity = VectorClamp(self.current_angular_velocity, self.max_angular_velocity)
        self.velocity_length = geo2.Vec3Length(self.current_velocity)
        self.angular_velocity_length = geo2.Vec2Length(self.current_angular_velocity)
        if self.velocity_length < 0.1:
            self.current_velocity = geo2.Vector(0, 0, 0)
            self.velocity_length = 0.0
        if self.angular_velocity_length < 0.001:
            self.current_angular_velocity = geo2.Vector(0, 0)
            self.angular_velocity_length = 0.0
        self.last_rotation = geo2.Vec2Scale(self.current_angular_velocity, dt)
        self.current_velocity = geo2.Vec3Transform(self.current_velocity, geo2.MatrixRotationQuaternion(geo2.QuaternionRotationSetYawPitchRoll(-self.last_rotation[1], -self.last_rotation[0], 0.0)))
        self.last_translation = geo2.Vec3Scale(self.current_velocity, dt)
        return (self.last_translation, self.last_rotation)
