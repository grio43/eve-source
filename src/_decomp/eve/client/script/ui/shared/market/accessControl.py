#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\accessControl.py
from typeutils import metas

class MarketAccessControl(object):
    __metaclass__ = metas.Singleton

    def __init__(self):
        self.is_sell_items_read_only = False

    def set_sell_items_read_only(self, is_read_only):
        self.is_sell_items_read_only = is_read_only
