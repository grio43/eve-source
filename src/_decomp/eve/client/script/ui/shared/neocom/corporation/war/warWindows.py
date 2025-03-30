#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warWindows.py
import carbonui.const as uiconst
import evewar.util as warUtil
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.button.group import ButtonGroup
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionSmall
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel

class BaseNegotiationWnd(Window):
    __guid__ = 'BaseNegotiationWnd'
    __notifyevents__ = []
    default_windowID = 'BaseNegotiationWnd'
    default_width = 450
    default_height = 282
    default_minSize = (default_width, default_height)

    def __init__(self, **kwargs):
        self.war = None
        self.isRequest = None
        self.isAllyRequest = None
        self.warID = None
        self.attackerID = None
        self.defenderID = None
        self.requesterID = None
        self.warNegotiation = None
        self.warCont = None
        self.requesterLabel = None
        self.offerLabel = None
        self.negotiationIcon = None
        self.windowTitle = None
        self.warLabel = None
        self.btnGroup = None
        self.myCont = None
        self.offerAmount = None
        self.requestText = None
        super(BaseNegotiationWnd, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.war = war = attributes.war
        self.isRequest = attributes.Get('isRequest', False)
        self.isAllyRequest = attributes.Get('isAllyRequest', False)
        if self.isRequest:
            self.warID = war.warID
            self.attackerID = war.declaredByID
            self.defenderID = war.againstID
            self.requesterID = attributes.Get('requesterID', None)
        else:
            warNegotiation = attributes.get('warNegotiation', None)
            self.warNegotiation = warNegotiation or sm.GetService('war').GetWarNegotiation(attributes.warNegotiationID)
            self.warID = self.warNegotiation.warID
            self.attackerID = self.warNegotiation.declaredByID
            self.defenderID = self.warNegotiation.againstID
            self.requesterID = self.warNegotiation.ownerID1
        self.ConstructLayout()
        self.LoadNegotiation()

    def ConstructLayout(self):
        mainContPadding = (const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         0)
        mainCont = Container(parent=self.sr.main, align=uiconst.TOALL, padding=mainContPadding)
        headerCont = Container(name='headerCont', parent=mainCont, align=uiconst.TOTOP, height=45)
        self.warCont = Container(name='warCont', parent=mainCont, align=uiconst.TOTOP, height=40, padTop=6)
        self.requesterLabel = EveLabelMedium(name='requesterLabel', text='', parent=self.warCont, padLeft=38, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, top=2)
        self.offerLabel = EveLabelMedium(name='offerLabel', text='', parent=self.warCont, padLeft=38, align=uiconst.TOTOP)
        self.negotiationIcon = Sprite(parent=headerCont, align=uiconst.TOPLEFT, pos=(0, 4, 32, 32))
        self.windowTitle = EveCaptionSmall(text='', parent=headerCont, align=uiconst.TOTOP, padLeft=38)
        self.warLabel = EveLabelMedium(name='warLabel', text='', parent=headerCont, align=uiconst.TOTOP, padLeft=38, state=uiconst.UI_NORMAL)
        self.btnGroup = ButtonGroup(parent=mainCont, btns=[], height=20)
        self.myCont = Container(parent=mainCont, align=uiconst.TOALL, padLeft=2, padRight=2)
        self.offerAmount = SingleLineEditInteger(setvalue=self.GetBaseIskValue(), parent=self.myCont, align=uiconst.TOBOTTOM, maxValue=100000000000L, hintText=GetByLabel('UI/Corporations/Wars/OfferInISK'))
        self.requestText = EditPlainText(setvalue='', parent=self.myCont, align=uiconst.TOALL, padBottom=4, hintText=GetByLabel('UI/Corporations/Wars/Reasonforoffer'), maxLength=400)
        self.SetCaption(self.GetWndCaption())
        self.moreInfoIcon = MoreInfoIcon(left=0, top=-1, parent=headerCont, idx=0, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.moreInfoIcon.display = False
        self.moreInfoIcon.hint = self.GetMoreInfoHint()

    def LoadNegotiation(self):
        attackerName, attackerInfo = self.GetEntityInfo(self.attackerID)
        defenderName, defenderInfo = self.GetEntityInfo(self.defenderID)
        self.windowTitle.text = self.GetText()
        self.moreInfoIcon.display = True
        self.moreInfoIcon.left = self.windowTitle.padLeft + self.windowTitle.textwidth + 6
        self.warLabel.text = GetByLabel('UI/Corporations/Wars/InWarAvsB', attackerName=attackerName, attackerInfo=attackerInfo, defenderName=defenderName, defenderInfo=defenderInfo)
        GetLogoIcon(itemID=self.requesterID, parent=self.warCont, acceptNone=False, align=uiconst.TOPLEFT, size=32, state=uiconst.UI_NORMAL, left=2, top=2)
        self.requesterLabel.text = self.GetRequesterText()
        if self.isRequest:
            self.requesterLabel.top = 8
            self.offerLabel.display = False
            self.btnGroup.AddButton(GetByLabel('UI/Common/Buttons/Submit'), self.SubmitRequest, (), 84, 0, 1, 0)
            self.btnGroup.AddButton(GetByLabel('UI/Common/Buttons/Cancel'), self.CloseByUser, (), 84, 0, 0, 0)
        else:
            offerDescription = self.warNegotiation.description
            self.requestText.SetValue(offerDescription)
            self.offerLabel.text = self.GetOfferText()
            self.offerAmount.display = False
            self.requestText.readonly = True
            entityID = session.allianceid or session.corpid
            if entityID == self.warNegotiation.ownerID1:
                self.btnGroup.AddButton(GetByLabel('UI/Common/Buttons/Close'), self.CloseByUser, (), 84, 0, 1, 0)
                self.btnGroup.AddButton(GetByLabel('UI/Corporations/Wars/RetractAllyOffer'), self.RetractWarAllyOffer, (), 84, 0, 1, 0)
            elif entityID == self.warNegotiation.ownerID2:
                self.btnGroup.AddButton(GetByLabel('UI/Corporations/Wars/AcceptOffer'), self.AcceptOffer, (), 84, 0, 1, 0)
                self.btnGroup.AddButton(GetByLabel('UI/Corporations/Wars/DeclineOffer'), self.DeclineOffer, (), 84, 0, 0, 0)
        iconPath, iconID = self.GetWndIconAndPath()
        self.icon = iconID
        self.negotiationIcon.LoadIcon(iconPath)

    def IsDefender(self):
        myID = session.corpid if session.allianceid is None else session.allianceid
        if self.defenderID == myID:
            return True
        return False

    @staticmethod
    def GetEntityInfo(entityID):
        entityName = cfg.eveowners.Get(entityID).name
        if idCheckers.IsCorporation(entityID):
            entityLinkType = const.typeCorporation
        elif idCheckers.IsAlliance(entityID):
            entityLinkType = const.typeAlliance
        else:
            entityLinkType = const.typeFaction
        return (entityName, ('showinfo', entityLinkType, entityID))

    def GetWndIconAndPath(self):
        raise NotImplementedError

    def GetOfferAmountText(self):
        raise NotImplementedError

    def GetText(self):
        raise NotImplementedError

    def GetWndCaption(self):
        raise NotImplementedError

    def GetRequesterText(self):
        raise NotImplementedError

    def GetOfferText(self):
        raise NotImplementedError

    def SubmitRequest(self):
        message = self.requestText.GetValue()
        iskValue = float(self.offerAmount.GetValue())
        try:
            self._SubmitRequest(iskValue, message)
        finally:
            self.CloseByUser()

    @staticmethod
    def ShowInfo(itemID, typeID):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def _SubmitRequest(self, iskValue, message):
        raise NotImplementedError

    def AcceptOffer(self):
        try:
            self._AcceptOffer()
        finally:
            self.CloseByUser()

    def _AcceptOffer(self):
        raise NotImplementedError

    def DeclineOffer(self):
        try:
            self._DeclineOffer()
        finally:
            self.CloseByUser()

    def _DeclineOffer(self):
        raise NotImplementedError

    def RetractWarAllyOffer(self):
        try:
            self._RetractWarAllyOffer()
        finally:
            self.CloseByUser()

    def _RetractWarAllyOffer(self):
        raise NotImplementedError

    def GetBaseIskValue(self):
        raise NotImplementedError

    def GetMoreInfoHint(self):
        raise NotImplementedError


class WarSurrenderWnd(BaseNegotiationWnd):
    __guid__ = 'form.WarSurrenderWnd'
    default_windowID = 'warSurrenderWnd'

    def GetWndIconAndPath(self):
        return ('res:/UI/Texture/Icons/Surrender_64.png', 'ui_1337_64_5')

    def _AcceptOffer(self):
        if self.isRequest:
            sm.GetService('war').CreateSurrenderNegotiation(self.warID, float(self.offerAmount.GetValue()))
        else:
            sm.GetService('war').AcceptSurrender(self.warNegotiation.warNegotiationID)

    def _DeclineOffer(self):
        sm.GetService('war').DeclineSurrender(self.warNegotiation.warNegotiationID)

    def GetOfferAmountText(self):
        return GetByLabel('UI/Corporations/Wars/SurrenderFee')

    def GetWndCaption(self):
        return GetByLabel('UI/Corporations/Wars/Surrender')

    def GetText(self):
        return GetByLabel('UI/Corporations/Wars/SurrenderOffer')

    def _SubmitRequest(self, iskValue, message):
        sm.GetService('war').CreateSurrenderNegotiation(self.warID, iskValue, message)

    def GetRequesterText(self):
        requesterName, requesterInfo = self.GetEntityInfo(self.requesterID)
        return GetByLabel('UI/Corporations/Wars/OffersSurrender', requesterName=requesterName, requesterInfo=requesterInfo)

    def GetOfferText(self):
        return GetByLabel('UI/Corporations/Wars/OfferAmountInISK', amount=self.warNegotiation.iskValue)

    def GetBaseIskValue(self):
        return 0.0

    def GetMoreInfoHint(self):
        return GetByLabel('UI/Corporations/Wars/MoreInfoSurrender')


class WarAssistanceOfferWnd(BaseNegotiationWnd):
    __guid__ = 'form.WarAssistanceOfferWnd'
    default_windowID = 'warAssistanceOfferWnd'
    __notifyevents__ = ['OnWarChanged']

    def __init__(self, **kwargs):
        self.originalIskValue = None
        super(WarAssistanceOfferWnd, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        self.originalIskValue = attributes.get('iskValue', 0)
        BaseNegotiationWnd.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)

    def OnWarChanged(self, war, ownerIDs, change):
        if self.destroyed:
            return
        if war is not None and war.warID == self.warID and self.warNegotiation:
            self.offerLabel.text = self.GetOfferText()

    def GetOfferText(self):
        entityID = session.allianceid or session.corpid
        if entityID == self.warNegotiation.ownerID2:
            war = sm.GetService('war').GetWars(self.defenderID)[self.warID]
            baseCostFunc = sm.GetService('corp').GetAllyBaseCost
            concordFee = warUtil.GetAllyCostToConcord(war, baseCostFunc)
            if concordFee > 0:
                totalIsk = concordFee + self.warNegotiation.iskValue
                return GetByLabel('UI/Corporations/Wars/AllyOfferWithFee', concordFee=FmtISK(concordFee), iskTotal=FmtISK(totalIsk))
        return GetByLabel('UI/Corporations/Wars/MercenaryOfferDetailed', amount=self.warNegotiation.iskValue)

    def GetBaseIskValue(self):
        return self.originalIskValue

    def _AcceptOffer(self, *args):
        if not self.isRequest:
            sm.GetService('war').AcceptAllyNegotiation(self.warNegotiation.warNegotiationID)

    def _SubmitRequest(self, iskValue, message):
        sm.GetService('war').CreateWarAllyOffer(self.warID, iskValue, self.defenderID, message)

    def _DeclineOffer(self, *args):
        sm.GetService('war').DeclineAllyOffer(self.warNegotiation.warNegotiationID)

    def _RetractWarAllyOffer(self):
        sm.GetService('war').RetractWarAllyOffer(self.warNegotiation.warNegotiationID)

    def GetWndIconAndPath(self):
        return ('res:/UI/Texture/Icons/Mercenary_64.png', 'ui_1337_64_4')

    def GetOfferAmountText(self):
        return GetByLabel('UI/Corporations/Wars/MercenaryFee')

    def GetText(self):
        if self.isRequest:
            return GetByLabel('UI/Corporations/Wars/OfferAssistance')
        else:
            return GetByLabel('UI/Corporations/Wars/AllyOffer')

    def GetWndCaption(self):
        return GetByLabel('UI/Corporations/Wars/Allies')

    def GetRequesterText(self):
        requesterName, requesterInfo = self.GetEntityInfo(self.requesterID)
        if self.requesterID in (self.attackerID, self.defenderID):
            return GetByLabel('UI/Corporations/Wars/RequestsAnAlly', requesterName=requesterName, requesterInfo=requesterInfo)
        elif self.isRequest:
            return GetByLabel('UI/Corporations/Wars/OffersToAlly', requesterName=requesterName, requesterInfo=requesterInfo)
        else:
            return GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=requesterName, info=requesterInfo)

    def GetMoreInfoHint(self):
        return GetByLabel('UI/Corporations/Wars/MoreInfoAlly')


class HeaderClear(Header):
    __guid__ = 'listentry.HeaderClear'

    def __init__(self, **kwargs):
        self.clearButton = None
        super(HeaderClear, self).__init__(**kwargs)

    def Startup(self, *args):
        Header.Startup(self, *args)
        self.clearButton = ButtonIcon(name='removeButton', parent=self, align=uiconst.TORIGHT, width=16, iconSize=16, texturePath='res:/UI/Texture/Icons/73_16_210.png')

    def Load(self, node):
        Header.Load(self, node)
        self.clearButton.func = node.func
