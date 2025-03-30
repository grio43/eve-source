#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\tabGroupVertical.py
from carbonui import uiconst, fontconst
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.control.tabVertical import TabVertical

class TabGroupVertical(TabGroup):
    default_name = 'TabGroupVertical'
    default_height = 0
    default_width = 150
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_tabClass = TabVertical
    default_tabAlign = uiconst.TOTOP

    def __init__(self, **kwargs):
        super(TabGroupVertical, self).__init__(show_line=False, **kwargs)

    def UpdateSizes(self, absSize = None):
        for each in self.mytabs:
            each.state = uiconst.UI_NORMAL
