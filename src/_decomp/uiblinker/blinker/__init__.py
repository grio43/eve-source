#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\blinker\__init__.py
import enum

class BlinkerType(enum.Enum):
    box = 1
    ring = 2


def get_blinker_factory(blinker_type):
    if blinker_type == BlinkerType.box:
        from .box import BoxBlinker
        return BoxBlinker.create_for
    if blinker_type == BlinkerType.ring:
        from .ring import RingBlinker
        return RingBlinker.create_for
