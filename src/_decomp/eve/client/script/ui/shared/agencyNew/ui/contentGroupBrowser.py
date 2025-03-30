#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupBrowser.py
import math
import eveicon
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
from eve.client.script.ui.shared.agencyNew import agencySignals
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupProvider import GetContentGroup
from eve.client.script.ui.shared.agencyNew.ui.breadcrumbLabel import BreadcrumbLabel
from localization import GetByLabel

class ContentGroupBrowser(Container):
    default_name = 'ContentGroupBrowser'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        agencySignals.on_content_group_selected.connect(self.OnContentGroupSelected)
        agencySignals.on_content_pieces_invalidated.connect(self.OnContentPiecesInvalidated)
        self.contentPage = None
        self.isLoading = False
        self.pendingSelection = None
        self.history = HistoryBuffer()
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN)
        self.ConstructHeaderContainer()
        self.ConstructNavigationButtons()
        self.ConstructBreadcrumbLabel()
        self.ConstructTopBracket()
        self.ConstructBottomBracket()
        self.contentPageCont = Container(name='contentPageCont', parent=self, align=uiconst.TOALL)
        self.UpdateNavigationButtons()

    def ConstructBreadcrumbLabel(self):
        breadCrumbLabelContainer = ContainerAutoSize(name='breadCrumbLabelContainer', parent=self.headerContainer, align=uiconst.TOLEFT, left=16)
        self.breadcrumbLabel = BreadcrumbLabel(parent=breadCrumbLabelContainer, align=uiconst.CENTERLEFT, height=32)

    def ConstructHeaderContainer(self):
        self.headerContainer = Container(name='headerContainer', parent=self, align=uiconst.TOTOP, height=32, padding=(0, 0, 0, 16))

    def ConstructTopBracket(self):
        ruleContainer = Container(name='ruleContainer', parent=self, align=uiconst.TOTOP, height=5, state=uiconst.UI_DISABLED)
        StretchSpriteHorizontal(parent=ruleContainer, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/agency/hDecoExpand.png', height=5, rightEdgeSize=5, leftEdgeSize=5)
        Sprite(parent=ruleContainer, align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/agency/hDecoMiddle.png', width=286, height=4, top=1)

    def ConstructBottomBracket(self):
        ruleContainer = Transform(name='ruleContainer', parent=self, align=uiconst.TOBOTTOM, height=5, rotation=math.pi, padBottom=15, state=uiconst.UI_DISABLED)
        StretchSpriteHorizontal(parent=ruleContainer, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/agency/hDecoExpand.png', height=5, rightEdgeSize=5, leftEdgeSize=5)
        Sprite(parent=ruleContainer, align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/agency/hDecoMiddle.png', width=286, height=4, top=1)

    def ConstructNavigationButtons(self):
        navButtonCont = ContainerAutoSize(name='navigationButtonCont', parent=self.headerContainer, align=uiconst.TOLEFT)
        self.backBtn = ButtonIcon(name='goBackBtn', parent=ContainerAutoSize(parent=navButtonCont, align=uiconst.TOLEFT), align=uiconst.CENTER, pos=(0, 0, 24, 24), iconSize=16, texturePath=eveicon.navigate_back, func=self.OnBack, hint=GetByLabel('UI/Control/EveWindow/Previous'))
        self.forwardBtn = ButtonIcon(name='goForwardBtn', parent=ContainerAutoSize(parent=navButtonCont, align=uiconst.TOLEFT), align=uiconst.CENTER, pos=(0, 0, 24, 24), iconSize=16, texturePath=eveicon.navigate_forward, func=self.OnForward, hint=GetByLabel('UI/Control/EveWindow/Next'))

    def OnContentGroupSelected(self, contentGroupID, itemID = None, appendHistory = True, *args, **kwargs):
        if self.isLoading:
            if kwargs.get('setPending', False):
                self.pendingSelection = (contentGroupID,
                 itemID,
                 appendHistory,
                 args,
                 kwargs)
            return
        self.isLoading = True
        try:
            contentGroupID, itemID = self.GetValidatedContentGroupIDItemID(contentGroupID, itemID)
            self._LoadContentGroup(appendHistory, contentGroupID, itemID, **kwargs)
        finally:
            self.isLoading = False

        if self.pendingSelection:
            contentGroupID, itemID, appendHistory, args, kwargs = self.pendingSelection
            self.pendingSelection = None
            self.OnContentGroupSelected(contentGroupID, itemID, appendHistory, *args, **kwargs)

    def _LoadContentGroup(self, appendHistory, contentGroupID, itemID = None, **kwargs):
        self.breadcrumbLabel.UpdateContentGroup(contentGroupID, itemID)
        animations.FadeOut(self.contentPageCont, duration=0.1, sleep=True)
        if self.contentPage:
            self.contentPageCont.Flush()
            self.loadingWheel.Show()
        if appendHistory:
            self.history.Append((contentGroupID, itemID))
        self.UpdateNavigationButtons()
        self.contentPage = self.ConstructContentPage(contentGroupID, itemID, **kwargs)
        self._SetFocusIfWindowIsActive()
        animations.FadeIn(self.contentPageCont, duration=0.1)
        self.loadingWheel.Hide()

    def _SetFocusIfWindowIsActive(self):
        if uicore.registry.GetActive() == uicore.registry.GetTopLevelWindowAboveItem(self):
            uicore.registry.SetFocus(self.contentPage)

    def UpdateNavigationButtons(self):
        if self.history.IsBackEnabled():
            self.backBtn.Enable()
        else:
            self.backBtn.Disable()
        if self.history.IsForwardEnabled():
            self.forwardBtn.Enable()
        else:
            self.forwardBtn.Disable()

    def ConstructContentPage(self, contentGroupID, itemID = None, **kwargs):
        contentGroup = GetContentGroup(contentGroupID, itemID)
        if not contentGroup:
            return
        cls = contentGroup.GetContentPageClass()
        contentPage = cls(parent=self.contentPageCont, contentGroup=contentGroup, itemID=itemID, **kwargs)
        contentPage.uniqueUiName = contentGroupConst.get_content_group_name(contentGroupID)
        return contentPage

    def OnBack(self):
        if not self.history.IsBackEnabled():
            return
        contentGroupID, itemID = self.history.GoBack()
        self._TriggerOnContentGroupSelectedSignal(contentGroupID, itemID, True)

    def _TriggerOnContentGroupSelectedSignal(self, contentGroupID, itemID, browsingHistory = False):
        contentGroupID, itemID = self.GetValidatedContentGroupIDItemID(contentGroupID, itemID, browsingHistory)
        if contentGroupID is None:
            return
        agencySignals.on_content_group_selected(contentGroupID, itemID=itemID, appendHistory=False)

    def GetValidatedContentGroupIDItemID(self, contentGroupID, itemID, browsingHistory = False):
        if contentGroupID:
            contentGroup = GetContentGroup(contentGroupID, itemID)
            if contentGroup:
                if contentGroup.IsEnabled():
                    if browsingHistory and not contentGroup.CanLoadFromHistory():
                        return (None, None)
                    return (contentGroupID, itemID)
                else:
                    return self.GetValidatedContentGroupIDItemID(contentGroup.GetParentID(), None)
        return (contentGroupConst.contentGroupHome, None)

    def OnForward(self):
        if not self.history.IsForwardEnabled():
            return
        contentGroupID, itemID = self.history.GoForward()
        self._TriggerOnContentGroupSelectedSignal(contentGroupID, itemID, True)

    def OnContentPiecesInvalidated(self, contentGroupID = None):
        if self.history.IsEmpty():
            return
        currContentGroupID, itemID = self.history.GetCurrent()
        if contentGroupID is None or contentGroupID == currContentGroupID:
            self._TriggerOnContentGroupSelectedSignal(currContentGroupID, itemID)

    def Close(self):
        super(ContentGroupBrowser, self).Close()
        agencySignals.on_content_group_selected.disconnect(self.OnContentGroupSelected)
