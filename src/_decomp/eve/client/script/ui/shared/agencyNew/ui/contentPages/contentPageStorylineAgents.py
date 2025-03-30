#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageStorylineAgents.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentPages.doubleColumnContentPage import DoubleColumnContentPage
from localization import GetByLabel

class ContentPageStorylineAgents(DoubleColumnContentPage):
    default_name = 'ContentPageStorylineAgents'
    scrollSectionWidth = agencyUIConst.LAYOUT_CONTAINER_WIDTH / 2

    def ConstructLayout(self):
        super(ContentPageStorylineAgents, self).ConstructLayout()
        self.ConstructHeaderCont()

    def _ConstructBaseLayout(self):
        self.ConstructScrollContainer()

    def ConstructHeaderCont(self):
        iconSize = 64
        cont = ContainerAutoSize(parent=self.scrollSection, align=uiconst.TOTOP, height=iconSize, padBottom=10, idx=0)
        Sprite(parent=cont, align=uiconst.TOPLEFT, pos=(0,
         0,
         iconSize,
         iconSize), texturePath='res:/UI/Texture/Classes/Agency/iconStorylineMissions_Large.png')
        Label(parent=cont, align=uiconst.TOPLEFT, text=GetByLabel('UI/Agency/StorylineAgentsHeaderText'), width=240, left=iconSize + 10)

    def ConstructFlowContainer(self):
        pass

    def _ConstructCard(self, contentPiece):
        cls = self.GetContentCardClass()
        return cls(parent=self.contentScroll, contentPiece=contentPiece, align=uiconst.TOTOP, contentGroupID=self.contentGroupID)
