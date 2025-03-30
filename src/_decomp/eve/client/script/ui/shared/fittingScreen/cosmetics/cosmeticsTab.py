#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\cosmetics\cosmeticsTab.py
from carbonui.control.tab import Tab

class CosmeticsTab(Tab):

    def OnClick(self, *args):
        if self.callback:
            shouldContinue = self.callback(*args)
            if shouldContinue:
                super(CosmeticsTab, self).OnClick(*args)
        else:
            super(CosmeticsTab, self).OnClick(*args)
