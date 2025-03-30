#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\radiallyAlignedMixin.py
from eve.client.script.ui.cosmetics.ship.pages.studio import studioUtil

class RadiallyAlignedMixin(object):
    _angle_deg = 0.0
    _radius = 0.0
    _radial_offset = 0.0

    def update_radial_position(self):
        self.left, self.top = studioUtil.get_radial_position(self._radius - self._radial_offset, self._angle_deg)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self.update_radial_position()

    @property
    def angle_deg(self):
        return self._angle_deg

    @angle_deg.setter
    def angle_deg(self, value):
        self._angle_deg = value
        self.update_radial_position()
