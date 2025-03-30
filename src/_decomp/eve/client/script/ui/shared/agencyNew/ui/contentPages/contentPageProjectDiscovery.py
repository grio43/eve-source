#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageProjectDiscovery.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.agencyNew.ui.contentPages.baseContentPage import BaseContentPage
from carbonui.control.section import Section
from localization import GetByLabel
from projectdiscovery.client.windowclass import get_project_discovery_window_class
from projectdiscovery.client.ui.const import get_agency_title, get_agency_description, get_agency_image

class ContentPageProjectDiscovery(BaseContentPage):
    default_name = 'ContentPageProjectDiscovery'

    def _ConstructBaseLayout(self):
        self.ConstructLeftCont()
        self.ConstructRightCont()

    def ConstructLeftCont(self):
        self.leftContainer = Section(name='leftContainer', parent=self, align=uiconst.TOLEFT, width=330, headerText=GetByLabel('UI/Agency/ProjectDiscovery/Caption'))
        Label(parent=self.leftContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/ProjectDiscovery/Description'))

    def ConstructRightCont(self):
        self.rightContainer = Section(name='rightContainer', parent=self, align=uiconst.TOLEFT, width=450, headerText=GetByLabel('UI/Agency/ProjectDiscovery/CurrentProject'), padLeft=10)
        self.ConstructHeaderCont()
        cont = ContainerAutoSize(parent=self.rightContainer, align=uiconst.TOTOP, padtop=10)
        Sprite(name='projectDiscoverySprite', parent=cont, align=uiconst.CENTERTOP, texturePath=get_agency_image(), pos=(0, 0, 430, 230))
        buttonCont = Container(parent=self.rightContainer, align=uiconst.TOTOP, height=30, padTop=16)
        Button(name='openFwButton', parent=buttonCont, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/WindowIcons/projectDiscovery.png', label=GetByLabel('UI/Agency/ProjectDiscovery/OpenProjectDiscovery'), func=get_project_discovery_window_class().Open)

    def ConstructHeaderCont(self):
        iconSize = 64
        cont = ContainerAutoSize(parent=self.rightContainer, align=uiconst.TOTOP, padBottom=10, idx=0)
        Sprite(parent=cont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), texturePath='res:/UI/Texture/WindowIcons/projectDiscovery.png')
        textCont = ContainerAutoSize(parent=cont, align=uiconst.CENTERLEFT, width=300, left=iconSize + 10)
        Label(parent=textCont, align=uiconst.TOTOP, text=GetByLabel(get_agency_title()), bold=True, color=(1, 1, 1, 1))
        Label(parent=textCont, align=uiconst.TOTOP, padTop=4, text=GetByLabel(get_agency_description()))

    def ConstructLayout(self):
        pass

    def ConstructCards(self):
        pass
