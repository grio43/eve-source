#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageHeraldryAgents.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label, EveCaptionMedium
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from carbonui.control.section import Section
from localization import GetByLabel
from eve.client.script.ui.control.statefulButton import StatefulButton

class ContentPageHeraldryAgents(SingleColumnContentPage):
    scrollSectionWidth = 400

    def ConstructLayout(self):
        super(ContentPageHeraldryAgents, self).ConstructLayout()
        self._add_common_text()
        self._add_interaction_button()

    def _add_common_text(self):
        self.right_container = Section(name='right_container', parent=self, align=uiconst.TOLEFT, width=self.scrollSectionWidth, padLeft=10, headerText=GetByLabel('UI/Agency/MissionDetails'))
        self.title = EveCaptionMedium(parent=self.right_container, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Blurbs/HeraldryTitle'))
        self.description = Label(parent=self.right_container, align=uiconst.TOTOP, padTop=10, text=GetByLabel('UI/Agency/Blurbs/HeraldryDescription'))

    def _add_interaction_button(self):
        self.buttons_container = Container(name='buttons_container', parent=self.right_container, align=uiconst.TOTOP, padding=(0, 10, 0, 10), height=30)
        self.interaction_button = StatefulButton(name='Agency_HeraldryAgents_InteractionButton', parent=self.buttons_container, align=uiconst.CENTERRIGHT, iconAlign=uiconst.TORIGHT)

    def GetFilterContainerClass(self):
        return None

    def OnCardSelected(self, selectedCard):
        super(ContentPageHeraldryAgents, self).OnCardSelected(selectedCard)
        contentPiece = selectedCard.contentPiece
        self.interaction_button.SetController(contentPiece)
        animations.FadeTo(self.right_container, 0.0, 1.0, duration=0.3)
