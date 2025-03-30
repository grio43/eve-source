#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\customersatisficationcont.py
import carbonui
import eveicon
import localization
import localization.settings
from carbonui import uiconst, Align
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import IsUnder
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel

class CustomerSatisficationCont(Container):
    default_name = 'CSAT'
    hasVoted = 0

    def ApplyAttributes(self, attributes):
        super(CustomerSatisficationCont, self).ApplyAttributes(attributes)
        self.tooltipPopup = None
        self.ConstructLayout()

    def ConstructLayout(self):
        leftCont = ContainerAutoSize(name='leftCont', parent=self, align=Align.TOLEFT)
        buttonCont = ContainerAutoSize(name='buttonCont', parent=leftCont, align=Align.CENTERLEFT, height=32)
        self.btnUp = SurveyButton(name='Upvote', parent=buttonCont, align=uiconst.TOLEFT, width=32, height=32, texturePath='res:/UI/Texture/classes/CSAT/up.png', iconSize=24, iconPadding=15, func=self.CastUpvote)
        self.btnDown = SurveyButton(name='Downvote', parent=buttonCont, align=uiconst.TOLEFT, width=32, height=32, texturePath='res:/UI/Texture/classes/CSAT/down.png', iconSize=24, iconPadding=15, func=self.CastDownvote)
        self.lbl = carbonui.TextBody(text=localization.GetByLabel('UI/SystemMenu/CSATQuestion'), padLeft=8, parent=self, align=uiconst.VERTICALLY_CENTERED, state=uiconst.UI_NORMAL, bold=True)

    def CastUpvote(self, *args):
        if self.hasVoted:
            self.btnDown.SetDeselected()
        sm.RemoteSvc('userSvc').CastUpvote()
        self.hasVoted = 1

    def CastDownvote(self, *args):
        if self.hasVoted:
            self.btnUp.SetDeselected()
        sm.RemoteSvc('userSvc').CastDownvote()
        self.hasVoted = 1
        if self.tooltipPopup:
            self.tooltipPopup.Close()
        self.tooltipPopup = uicore.uilib.tooltipHandler.LoadPersistentTooltip(owner=self.btnDown, customTooltipClass=CSATTooltip, parent=uicore.layer.hint)


class SurveyButton(ButtonIcon):

    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        if uicore.uilib.mouseOver is self:
            self.SetSelected()


class CSATTooltip(TooltipPersistentPanel):
    default_pointerDirection = uiconst.POINT_BOTTOM_2
    default_columns = 2
    default_state = uiconst.UI_NORMAL
    default_margin = 16
    default_cellSpacing = (8, 8)

    def ApplyAttributes(self, attributes):
        super(CSATTooltip, self).ApplyAttributes(attributes)
        self.editField = None
        self.owner = attributes.get('owner')
        self.pickState = uiconst.TR2_SPS_ON
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)

    def LoadTooltip(self, panel, owner):
        self.AddLabelMedium(align=uiconst.CENTERLEFT, width=250, text=localization.GetByLabel('UI/SystemMenu/CsatFeedbackHeader'))
        ButtonIcon(parent=self, align=uiconst.TOPRIGHT, texturePath=eveicon.close, hint=localization.GetByLabel('UI/Common/Buttons/Close'), func=self.Close, width=24, height=24, iconSize=16)
        c = Container(align=uiconst.TOTOP_NOPUSH, height=100)
        self.editField = EditPlainText(parent=c, hintText=localization.GetByLabel('UI/SystemMenu/CsatFeedbackWrite'), maxLength=1000)
        self.AddCell(cellObject=c, colSpan=self.columns)
        btn = Button(align=uiconst.CENTER, label=localization.GetByLabel('UI/SystemMenu/CsatFeedbackSend'), func=self.SendMsg)
        self.AddCell(cellObject=btn, colSpan=self.columns)

    def SendMsg(self, *args):
        feedback = self.editField.GetValue()
        sm.RemoteSvc('userSvc').CastDownvote(feedback)
        self.Close()

    def OnGlobalMouseDown(self, *args):
        if uicore.uilib.mouseOver is self or IsUnder(uicore.uilib.mouseOver, self):
            return True
        else:
            self.Close()
            return False
