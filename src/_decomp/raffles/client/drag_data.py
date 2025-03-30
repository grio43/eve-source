#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\drag_data.py
from raffles.client import texture
from raffles.client.link import get_raffle_link

class RaffleDragData(object):

    def __init__(self, raffle):
        self._raffle = raffle
        self.raffleID = raffle.raffle_id
        self.typeID = raffle.type_id
        self.itemID = raffle.item_id

    def get_link(self):
        return get_raffle_link(self._raffle)

    def LoadIcon(self, icon, dad, iconSize):
        icon.LoadIcon(texture.drag_icon)
