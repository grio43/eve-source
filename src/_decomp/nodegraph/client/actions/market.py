#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\market.py
from .base import Action

def set_sell_items_read_only(is_read_only):
    from eve.client.script.ui.shared.market.accessControl import MarketAccessControl
    MarketAccessControl().is_sell_items_read_only = is_read_only


class BlockSellWindow(Action):
    atom_id = 468

    def start(self, **kwargs):
        super(BlockSellWindow, self).start(**kwargs)
        set_sell_items_read_only(is_read_only=True)

    def stop(self):
        set_sell_items_read_only(is_read_only=False)


class UnblockSellWindow(Action):
    atom_id = 469

    def start(self, **kwargs):
        super(UnblockSellWindow, self).start(**kwargs)
        set_sell_items_read_only(is_read_only=False)
