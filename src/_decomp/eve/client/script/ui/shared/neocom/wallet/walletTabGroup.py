#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\walletTabGroup.py
from carbonui import uiconst
from carbonui.control.tabGroup import TabGroup

class WalletTabGroup(TabGroup):
    default_height = 0
    default_tabAlign = uiconst.TOLEFT_PROP
    default_tabSpacing = 8

    def __init__(self, **kwargs):
        super(WalletTabGroup, self).__init__(show_selection_indicator=False, **kwargs)

    def UpdateSizes(self, absSize = None):
        pass

    def _update_tab_sizes(self):
        pass
