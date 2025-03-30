#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageEpicArcs.py
import uthread
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold, EveCaptionMedium
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from carbonui.control.section import Section
from eve.client.script.ui.shared.epicArcs.epicArcChapterCont import EpicArcChapters
from localization import GetByLabel
from eve.client.script.ui.control.statefulButton import StatefulButton

class ContentPageEpicArcs(SingleColumnContentPage):
    default_name = 'ContentPageEpicArcs'

    def ApplyAttributes(self, attributes):
        self.epicArcCont = None
        super(ContentPageEpicArcs, self).ApplyAttributes(attributes)

    def _ConstructBaseLayout(self):
        pass

    def OnCardSelected(self, selectedCard):
        super(ContentPageEpicArcs, self).OnCardSelected(selectedCard)
        if self.epicArcCont:
            self.epicArcCont.Close()
        contentPiece = selectedCard.contentPiece
        self.epicArcCont = EpicArcInfoContainer(parent=self, contentPiece=contentPiece, align=uiconst.TOLEFT, width=450, padLeft=10)


class EpicArcInfoContainer(Section):
    default_name = 'EpicArcInfoContainer'
    default_headerText = GetByLabel('UI/Agents/MissionTypes/EpicArc')

    def ApplyAttributes(self, attributes):
        super(EpicArcInfoContainer, self).ApplyAttributes(attributes)
        self.contentPiece = attributes.contentPiece
        EveCaptionMedium(parent=self, align=uiconst.TOTOP, text=self.contentPiece.GetEpicArcName())
        EveLabelMedium(parent=self, align=uiconst.TOTOP, text=self.contentPiece.GetEpicArcFlavorLine(), padTop=4, opacity=0.5)
        EveLabelMediumBold(parent=self, align=uiconst.TOTOP, text=self.contentPiece.GetNumMissionsCompletedText(), padTop=4)
        self.ConstructButtonContainer()
        scrollCont = ScrollContainer(parent=self, padTop=4)
        chapters = EpicArcChapters(parent=scrollCont, contentPiece=self.contentPiece)
        uthread.new(scrollCont.ScrollToVertical, chapters.GetCurrentChapterPosFraction())

    def ConstructButtonContainer(self):
        buttonRowCont = Container(name='buttonRowContainer', parent=self, align=uiconst.TOBOTTOM, height=30, padTop=10)
        self.primaryButton = StatefulButton(parent=buttonRowCont, align=uiconst.CENTERRIGHT, iconAlign=uiconst.TORIGHT, label=self.contentPiece.GetButtonLabel(), func=self.contentPiece.GetButtonFunction(), texturePath=self.contentPiece.GetButtonTexturePath(), controller=self.contentPiece)
