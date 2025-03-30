#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\client\dragdata.py
from evefleet.client.link import get_fleet_link

class FleetDragData(object):

    def __init__(self, fleet_id, name = None):
        self.fleet_id = fleet_id
        self.name = name

    def get_link(self):
        return get_fleet_link(self.fleet_id, self.name)

    def LoadIcon(self, icon, parent, size):
        icon.LoadIcon('res:/UI/Texture/WindowIcons/fleet.png')
