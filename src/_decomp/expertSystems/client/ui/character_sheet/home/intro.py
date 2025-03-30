#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\home\intro.py
import localization
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from expertSystems.client import texture

class IntroSection(ContainerAutoSize):

    def __init__(self, on_browse, **kwargs):
        self._on_browse = on_browse
        super(IntroSection, self).__init__(alignMode=uiconst.TOTOP, minHeight=128, **kwargs)
        self.layout()

    def layout(self):
        Sprite(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT, padRight=8), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=64, height=64, texturePath=texture.badge_64)
        eveLabel.EveCaptionSmall(parent=self, align=uiconst.TOTOP, top=6, text=localization.GetByLabel('UI/ExpertSystem/IntroHeader'))
        eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, top=4, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ExpertSystems/ExpertSystemDescription'))
        Button(parent=ContainerAutoSize(parent=self, align=uiconst.TOTOP, top=16), align=uiconst.TOPLEFT, label=localization.GetByLabel('UI/ExpertSystem/BrowseExpertSystems'), fixedheight=32, sidePadding=32, func=self._on_browse, args=())
