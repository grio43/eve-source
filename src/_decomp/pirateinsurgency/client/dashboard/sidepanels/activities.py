#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\sidepanels\activities.py
import eveicon
from carbonui import uiconst, ButtonFrameType, Density
import carbonui
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupPirateIncursionsGuide, contentGroupPirateIncursions
from localization import GetByLabel

class Activities(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(Activities, self).ApplyAttributes(attributes)

    def ConstructLayout(self):
        self.Flush()
        cont = Container(parent=self, align=uiconst.TOALL, padding=(16, 0, 16, 0))
        carbonui.TextBody(parent=cont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/spreadOrPreventCorruption'))
        learnMore = Button(parent=cont, align=uiconst.TOTOP, label=GetByLabel('UI/PirateInsurgencies/learnMore'), frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, density=Density.COMPACT, padTop=16, func=self.OpenInsurgencyGuide)
        learnMore.icon = eveicon.open_window
        findContent = Button(parent=cont, align=uiconst.TOTOP, label=GetByLabel('UI/PirateInsurgencies/findObjectives'), frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, density=Density.COMPACT, padTop=12, func=self.OpenInsurgencySystems)
        findContent.icon = eveicon.open_window

    def OpenInsurgencyGuide(self, *args):
        sm.GetService('agencyNew').OpenWindow(contentGroupID=contentGroupPirateIncursionsGuide)

    def OpenInsurgencySystems(self, *args):
        sm.GetService('agencyNew').OpenWindow(contentGroupID=contentGroupPirateIncursions)
