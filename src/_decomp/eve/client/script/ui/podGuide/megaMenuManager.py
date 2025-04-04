#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\podGuide\megaMenuManager.py
import carbonui.const as uiconst
from eve.client.script.ui.podGuide.megaMenu import MegaMenu
from carbonui.uicore import uicore

class MegaMenuManager(object):

    def ShowMegaMenu(self, options, categoryInfo, pos, openingButtonClass):
        uicore.layer.abovemain.megaMenuTest = MegaMenu(parent=uicore.layer.abovemain, megaMenuOptions=options, categoryInfo=categoryInfo, pos=pos, align=uiconst.TOPLEFT, openingButtonClass=openingButtonClass)

    def GetCurrentMegaMenu(self):
        megaMenu = getattr(uicore.layer.abovemain, 'megaMenuTest', None)
        if megaMenu and not megaMenu.destroyed:
            return megaMenu

    def CloseMegaMenu(self):
        current = self.GetCurrentMegaMenu()
        if current:
            current.Close()
