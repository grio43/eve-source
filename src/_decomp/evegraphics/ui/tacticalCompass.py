#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\ui\tacticalCompass.py
import math

def AddRangeCircle(instancedMesh, range):
    count = 32.0
    angle = 0.0
    medium = 74000.0
    large = 149000.0
    major = []

    def _getFalloff(range, multiplier):
        if range in major:
            multiplier *= 3
        return (multiplier * range * 10.0, multiplier * range * 20.0)

    def _addParticle(angle, multiplier):
        x = math.cos(angle) * range
        y = math.sin(angle) * range
        instancedMesh.AddParticle(position=(x, 0.0, y), falloffRange=_getFalloff(range, multiplier))

    while angle < 2 * math.pi:
        _addParticle(angle, 1.0)
        if range >= large:
            a = angle
            a += 2 * math.pi / (4.0 * count)
            _addParticle(a, 0.25)
            a += 2 * math.pi / (4.0 * count)
            _addParticle(a, 0.75)
            a += 2 * math.pi / (4.0 * count)
            _addParticle(a, 0.25)
        elif range >= medium:
            _addParticle(angle + math.pi / count, 0.25)
        angle += 2 * math.pi / count
