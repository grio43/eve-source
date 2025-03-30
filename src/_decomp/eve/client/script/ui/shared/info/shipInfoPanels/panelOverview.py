#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelOverview.py
import blue
import eveicon
import evetypes
import localization
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.lib.const import DAY
from carbonui import Align, TextDisplay, TextHeader, TextHeadline, TextDetail, TextColor, uiconst, TextBody, AxisAlignment
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.collapsibleContainer import CollapsibleContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.shared.info.shipInfoConst import TAB_OVERVIEW, TAB_SKILLS, get_mastery_level_icon_and_message, SOUND_INSURANCE, SOUND_INSURANCE_SELECT, get_killmark_for_faction
from eve.client.script.ui.shared.info.shipInfoPanels.panelBase import PanelBase
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIcon
from eve.client.script.ui.shared.traits import TraitsContainer
from eve.client.script.ui.station.insurance.insuranceTooltip import LoadInfoInsuranceTooltip
from eve.client.script.ui.util.uix import GetTechLevelIconPathAndHint, GetTechLevelColor
from eve.common.script.util.eveFormat import FmtISK
from eveservices.xmppchat import GetChatService
from eveui import CharacterPortrait
from inventorycommon.typeHelpers import GetAveragePrice
from shipgroup import get_ship_group_name

class PanelOverview(PanelBase):
    __notifyevents__ = ['OnShipInsured', 'OnSessionChanged', 'OnContactChange']

    def get_tagline(self):
        quote = evetypes.GetQuoteID(self.typeID)
        if quote:
            return localization.GetByMessageID(quote)

    def get_author(self):
        author = evetypes.GetQuoteAuthorID(self.typeID)
        if author:
            return localization.GetByMessageID(author)

    def ApplyAttributes(self, attributes):
        self.insuranceParent = None
        self._tagline = None
        self._contact_icon = None
        self.relationship_cont = None
        super(PanelOverview, self).ApplyAttributes(attributes)

    def _enable_minimized_view(self):
        if self.insuranceParent:
            self.insuranceParent.SetParent(self.basicInfoCont, idx=0)
        self.basicInfoCont.align = Align.TOTOP
        self.basicInfoCont.padBottom = 0
        self.basicInfoCont.SetParent(self.content_scroll_minimized)
        self.detailsCont.SetParent(self.content_scroll_minimized)
        if not self.traitsContainer.destroyed:
            self.traitsContainer.SetOrder(0)
        if self.masteryCont:
            self.masteryCont.height = 46
        self.nameLabel.fontsize = TextHeadline.default_fontsize
        if self._tagline:
            self._tagline.fontsize = TextHeader.default_fontsize
        if self.ownerContainer:
            self.ownerContainer.padding = (0, 6, 0, 0)

    def _enable_expanded_view(self):
        self.basicInfoCont.align = Align.TOBOTTOM
        self.basicInfoCont.padBottom = 0 if self.ownerContainer else 104
        self.basicInfoCont.SetParent(self.leftCont)
        if self.insuranceParent:
            self.insuranceParent.SetParent(self.leftCont)
        self.detailsCont.SetParent(self.infoScroll)
        if not self.traitsContainer.destroyed:
            self.traitsContainer.SetOrder(-1)
        self.nameLabel.fontsize = TextDisplay.default_fontsize
        if self._tagline:
            self._tagline.fontsize = TextHeadline.default_fontsize
        if self.masteryCont:
            self.masteryCont.height = 64
        if self.ownerContainer:
            self.ownerContainer.padding = (0, 20, 0, 20)

    def _construct_content(self):
        self.infoScroll = ScrollContainer(parent=self.rightCont, align=Align.TOALL)
        self._construct_details()
        self._construct_basic_info()
        self._construct_insurance_icon()

    def _construct_details(self):
        self.detailsCont = ContainerAutoSize(name='detailsCont', parent=self.infoScroll, align=Align.TOTOP)
        tagline = self.get_tagline()
        if tagline:
            self._tagline = TextHeadline(parent=self.detailsCont, align=Align.TOTOP, text=tagline)
        author = self.get_author()
        if author:
            TextDetail(parent=self.detailsCont, align=Align.TOTOP, text='- ' + author, color=TextColor.SECONDARY, padTop=4, padLeft=20)
        Line(parent=self.detailsCont, align=Align.TOTOP, weight=1, padTop=10 if tagline or author else 0, padBottom=10)
        descCont = CollapsibleContainer(parent=self.detailsCont, align=Align.TOTOP, collapsedHeight=78, padBottom=10)
        descCont.set_text(self._controller.get_description())
        self.traitsContainer = TraitsContainer(parent=self.detailsCont, typeID=self.typeID, padTop=10, padBottom=20, traitAttributeIcons=True, align=Align.TOTOP)

    def _construct_basic_info(self):
        self.basicInfoCont = ContainerAutoSize(parent=self.leftCont, align=Align.TOBOTTOM, alignMode=Align.TOTOP)
        self._construct_mastery_icon()
        topContainer = FlowContainer(name='topContainer', parent=self.basicInfoCont, align=Align.TOTOP, contentSpacing=(8, 8), crossAxisAlignment=AxisAlignment.CENTER)
        typeGroupContainer = ContainerAutoSize(parent=topContainer, align=Align.NOALIGN)
        Sprite(parent=typeGroupContainer, align=Align.CENTERLEFT, width=16, height=16, texturePath=sm.GetService('bracket').GetBracketIcon(self.typeID), color=TextColor.NORMAL)
        TextDetail(parent=typeGroupContainer, align=Align.CENTERLEFT, text=get_ship_group_name(self.typeID), padLeft=20, color=TextColor.SECONDARY)
        iconPath, hint = GetTechLevelIconPathAndHint(typeID=self.typeID)
        if iconPath:
            tierContainer = ContainerAutoSize(name='tierContainer', parent=topContainer, align=Align.NOALIGN, alignMode=Align.CENTERLEFT, state=uiconst.UI_DISABLED, minHeight=16)
            Sprite(name='techIcon', parent=tierContainer, align=Align.TOPLEFT, left=0, width=16, height=16, texturePath=iconPath, state=uiconst.UI_DISABLED)
            Frame(bgParent=tierContainer, color=GetTechLevelColor(typeID=self.typeID), opacity=0.5, frameConst=uiconst.FRAME_FILLED_CORNER1)
            TextDetail(parent=tierContainer, align=Align.CENTERLEFT, padLeft=16, padRight=6, text=hint, color=TextColor.NORMAL, state=uiconst.UI_DISABLED)
        self.nameContainer = ContainerAutoSize(name='nameCont', parent=self.basicInfoCont, align=Align.TOTOP)
        custom_name = self._controller.get_custom_name()
        type_name = evetypes.GetName(self.typeID)
        self.nameLabel = TextDisplay(parent=self.nameContainer, align=Align.TOTOP, text=custom_name or type_name, color=TextColor.HIGHLIGHT)
        if custom_name:
            TextHeader(parent=self.nameContainer, align=Align.TOTOP, text=type_name)
        killmarkContainer = Container(name='killmarkContainer', parent=self.basicInfoCont, align=Align.TOTOP, height=24, padTop=4, display=False)
        uthread.new(self._load_killmarks, killmarkContainer)
        self.construct_est_price()
        self._construct_pilot()

    def _construct_pilot(self):
        ownerID = self.ownerID
        self.ownerContainer = None
        if not ownerID:
            return
        if ownerID == session.charid and self.itemID != session.shipid:
            return
        self.ownerContainer = Container(name='ownerCont', parent=self.basicInfoCont, align=Align.TOTOP, height=64, padTop=20, padBottom=20)
        portraitContainer = Container(name='portraitCont', parent=self.ownerContainer, align=Align.TOLEFT, width=64, height=64)
        CharacterPortrait(parent=portraitContainer, align=Align.CENTER, size=64, character_id=ownerID, textureSecondaryPath='res:/UI/Texture/circle_full.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        infoCont = Container(name='infoCont', parent=self.ownerContainer, align=Align.TOALL, padLeft=8)
        self.allianceCont = Container(name='allianceCont', parent=infoCont, align=Align.TOBOTTOM, height=32, itemSpacing=(10, 0), state=uiconst.UI_PICKCHILDREN)
        nameCont = Container(name='nameCont', parent=infoCont, align=Align.TOALL)
        TextHeader(parent=ContainerAutoSize(parent=nameCont, align=Align.TOLEFT), align=Align.CENTERLEFT, text=cfg.eveowners.Get(ownerID).name)
        self.relationship_cont = Container(parent=ContainerAutoSize(parent=nameCont, align=Align.TOLEFT, padLeft=10), align=Align.CENTERLEFT, padTop=1, width=16, height=16)
        uthread.new(self.load_character_info)
        if ownerID != session.charid:
            isContact = sm.GetService('addressbook').IsInAddressBook(ownerID, 'contact')
            if isContact:
                hint = localization.GetByLabel('UI/PeopleAndPlaces/EditContact')
            else:
                hint = localization.GetByLabel('UI/PeopleAndPlaces/AddContact')
            self._contact_icon = ButtonIcon(name='addContactIcon', parent=ContainerAutoSize(parent=self.allianceCont, align=Align.TORIGHT, padRight=4), align=Align.CENTER, texturePath=eveicon.user_plus, pos=(0, 0, 16, 16), iconSize=16, func=lambda : sm.GetService('addressbook').AddToPersonalMulti([ownerID], 'contact', True), hint=hint)
            ButtonIcon(name='chatIcon', parent=ContainerAutoSize(parent=self.allianceCont, align=Align.TORIGHT, padRight=4), align=Align.CENTER, texturePath=eveicon.chat_bubble, pos=(0, 0, 16, 16), iconSize=16, func=lambda *args: self._on_chat_button(ownerID), hint=localization.GetByLabel('UI/Chat/StartConversation'))

    def _construct_insurance_icon(self):
        if self.insuranceParent:
            self.insuranceParent.Flush()
            self.insuranceParent.display = False
        else:
            self.insuranceParent = Container(name='insuranceParent', parent=self.leftCont, align=uiconst.TOTOP_NOPUSH, height=36, display=False)
        if not self._should_show_insurance():
            return
        contract = sm.GetService('insurance').GetContractForShip(self.itemID)
        price = sm.GetService('insurance').GetInsurancePrice(self.typeID)
        if price <= 0:
            self.insuranceParent.display = True
            return
        status = InsuranceIcon.STATUS_OK
        if contract and contract.ownerID in (session.corpid, session.charid):
            timeDiff = contract.endDate - blue.os.GetWallclockTime()
            days = timeDiff / DAY
            if days < 5:
                status = InsuranceIcon.STATUS_CAUTION
        else:
            status = InsuranceIcon.STATUS_WARNING
        insuranceIcon = InsuranceIcon(parent=self.insuranceParent, state=uiconst.UI_NORMAL, itemID=self.itemID, status=status)
        insuranceIcon.LoadTooltipPanel = lambda tooltipPanel, *args: LoadInfoInsuranceTooltip(tooltipPanel, self.typeID, contract)
        self.insuranceParent.display = True

    def _should_show_insurance(self):
        return self._controller.is_assembled and self._controller.is_owned_by_me

    def _construct_mastery_icon(self):
        self.masteryCont = None
        ownerID = self.ownerID
        if ownerID and ownerID != session.charid:
            return
        self.masteryCont = Container(name='masteryCont', parent=self.basicInfoCont, align=Align.TOTOP, height=64)
        texturePath, message, onClick = get_mastery_level_icon_and_message(self.typeID)
        masterySprite = Sprite(name='masterySprite', parent=self.masteryCont, align=Align.CENTERLEFT, height=64, width=64, texturePath=texturePath, hint=message, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.1)
        if not onClick:
            onClick = lambda *args, **kwargs: self._controller.select_tab(TAB_SKILLS)
        masterySprite.OnClick = onClick

    def _on_chat_button(self, characterID):
        GetChatService().Invite(characterID)

    def load_character_info(self):
        if self.ownerID is None:
            return
        if self.ownerID == session.charid and self.allianceCont:
            self._load_organization_logos(self.allianceCont, session.corpid, session.allianceid, session.warfactionid)
        else:
            owner_data = self._controller.get_owner_data()
            if not owner_data:
                return
            self._load_relationship()
            self._load_organization_logos(self.allianceCont, owner_data.corpID, owner_data.allianceID, owner_data.warFactionID)

    def _reload_character_info(self):
        self.allianceCont.Flush()
        self.relationship_cont.Flush()
        self.load_character_info()

    def _load_relationship(self):
        if not self.relationship_cont:
            return
        owner_data = self._controller.get_owner_data()
        if not owner_data:
            return
        flag = sm.GetService('stateSvc').CheckStates(owner_data, 'flag')
        AddAndSetFlagIcon(self.relationship_cont, flag=flag, align=Align.CENTER, width=16, height=16)

    def _load_organization_logos(self, container, corpID, allianceID, warFactionID):
        if corpID:
            corpName = cfg.eveowners.Get(corpID).name
            OwnerIcon(parent=Container(parent=container, align=Align.TOLEFT, width=24, padRight=8), align=Align.CENTER, ownerID=corpID, isSmall=True, width=24, height=24, hint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Corporation', corpName=corpName))
        if allianceID:
            allianceName = cfg.eveowners.Get(allianceID).name
            OwnerIcon(parent=Container(parent=container, align=Align.TOLEFT, width=24, padRight=8), align=Align.CENTER, ownerID=allianceID, isSmall=True, width=24, height=24, hint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Alliance', allianceName=allianceName))
        if warFactionID:
            factionName = cfg.eveowners.Get(warFactionID).name
            OwnerIcon(parent=Container(parent=container, align=Align.TOLEFT, width=24, padRight=8), align=Align.CENTER, ownerID=warFactionID, isSmall=True, width=24, height=24, hint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/FactionalWarfare', factionName=factionName))

    def _load_killmarks(self, killmarkContainer):
        if self.itemID is None or self.ownerID is None or self._controller.is_simulated:
            return
        killmarksCount = sm.RemoteSvc('shipKillCounter').GetItemKillCountPlayer(self.itemID)
        if not killmarksCount:
            return
        factionID = evetypes.GetFactionID(self.typeID)
        killmarkIcon = get_killmark_for_faction(factionID)
        Sprite(parent=killmarkContainer, state=uiconst.UI_DISABLED, align=Align.CENTERLEFT, texturePath=killmarkIcon, color=TextColor.NORMAL, width=16, height=16)
        TextBody(parent=killmarkContainer, align=Align.CENTERLEFT, padLeft=20, text=localization.GetByLabel('UI/InfoWindow/KillCount', count=killmarksCount, countColor=TextColor.NORMAL), color=TextColor.SECONDARY)
        killmarkContainer.display = True

    def construct_est_price(self):
        priceCont = Container(name='priceCont', parent=self.basicInfoCont, align=Align.TOTOP, height=24)
        labelCont = ContainerAutoSize(name='labelCont', parent=priceCont, align=Align.TOLEFT)
        TextDetail(parent=labelCont, align=Align.BOTTOMLEFT, color=TextColor.SECONDARY, text=localization.GetByLabel('UI/Inventory/EstPrice').lower())
        valueCont = Container(name='valueCont', parent=priceCont, align=Align.TOALL, padLeft=10)
        price = GetAveragePrice(self.typeID) or 0
        TextDetail(parent=valueCont, align=Align.BOTTOMLEFT, text=FmtISK(price), color=TextColor.NORMAL, padBottom=1)
        if not price:
            priceCont.Hide()

    @classmethod
    def get_name(cls):
        return localization.GetByLabel('UI/InfoWindow/TabNames/Overview')

    @classmethod
    def get_icon(cls):
        return eveicon.info

    @classmethod
    def is_visible(cls, typeID, itemID = None, rec = None):
        return True

    def get_zoom(self):
        return 0.3

    def get_tab_type(self):
        return TAB_OVERVIEW

    def OnShipInsured(self):
        self._construct_insurance_icon()

    def OnSessionChanged(self, _isRemote, _session, change):
        if not self.ownerID or self.ownerID != session.charid:
            return
        if 'corpid' in change or 'allianceid' in change or 'warfactionid' in change:
            self._reload_character_info()

    def OnContactChange(self, _contactIDs, _contactType = None):
        if not self.relationship_cont:
            return
        self.relationship_cont.Flush()
        self._load_relationship()
        isContact = sm.GetService('addressbook').IsInAddressBook(self.ownerID, 'contact')
        self._contact_icon.hint = localization.GetByLabel('UI/PeopleAndPlaces/EditContact') if isContact else localization.GetByLabel('UI/PeopleAndPlaces/AddContact')


class InsuranceIcon(Container):
    EXPANDED_WIDTH = 114
    MINIMIZED_WIDTH = 43
    COLOR_INSURED_LIGHT = (0.35, 0.65, 0.75, 0.4)
    COLOR_INSURED_DARK = (0.19, 0.34, 0.4, 0.4)
    COLOR_INSURED_TEXT = (0.35, 0.65, 0.75, 1)
    COLOR_CAUTION_LIGHT = (0.95, 0.56, 0.345, 0.8)
    COLOR_CAUTION_DARK = (0.953, 0.565, 0.345, 0.4)
    COLOR_CAUTION_TEXT = TextColor.WARNING
    COLOR_UNINSURED_LIGHT = (1, 0.27, 0.29, 0.4)
    COLOR_UNINSURED_DARK = (0.6, 0.12, 0.14, 0.4)
    COLOR_UNINSURED_TEXT = (1, 0.27, 0.29, 1)
    STATUS_OK = 1
    STATUS_CAUTION = 2
    STATUS_WARNING = 3
    COLOR_LIGHT = {STATUS_OK: COLOR_INSURED_LIGHT,
     STATUS_CAUTION: COLOR_CAUTION_LIGHT,
     STATUS_WARNING: COLOR_UNINSURED_LIGHT}
    COLOR_DARK = {STATUS_OK: COLOR_INSURED_DARK,
     STATUS_CAUTION: COLOR_CAUTION_DARK,
     STATUS_WARNING: COLOR_UNINSURED_DARK}
    COLOR_TEXT = {STATUS_OK: COLOR_INSURED_TEXT,
     STATUS_CAUTION: COLOR_CAUTION_TEXT,
     STATUS_WARNING: COLOR_UNINSURED_TEXT}
    default_align = Align.TOPRIGHT
    default_height = 36
    default_width = MINIMIZED_WIDTH

    def ApplyAttributes(self, attributes):
        self.EXPANDED_WIDTH = 114
        self.MINIMIZED_WIDTH = 43
        super(InsuranceIcon, self).ApplyAttributes(attributes)
        self.itemID = attributes.itemID
        self.status = attributes.status
        self.construct_layout()
        self.calculate_expanded_width()

    def construct_layout(self):
        self.content = Container(parent=self, align=Align.TOALL)
        self.bg_frame = Frame(parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/Button/background_cut_bottom_left.png', cornerSize=9, color=(0, 0, 0, 0.4))
        self.right_line_light = Container(parent=self.content, align=Align.TORIGHT, width=1, bgColor=self.get_color_light())
        self.right_line_dark = Container(parent=self.content, align=Align.TORIGHT, width=6, bgColor=self.get_color_dark())
        self.icon_cont = Container(parent=self.content, align=Align.TOLEFT, width=32, padLeft=2)
        Sprite(name='ship', parent=self.icon_cont, align=Align.CENTER, width=16, height=16, texturePath=eveicon.spaceship_command)
        self.shield_left = Sprite(name='shieldLeft', parent=self.icon_cont, align=Align.CENTER, width=32, height=32, texturePath='res:/UI/Texture/classes/ShipInfo/shield_left.png', color=self.get_color_light())
        self.shield_right = Sprite(name='shieldRight', parent=self.icon_cont, align=Align.CENTER, width=32, height=32, texturePath='res:/UI/Texture/classes/ShipInfo/shield_right.png', color=self.get_color_dark())
        self.text_cont = Container(parent=self.content, align=Align.TOLEFT, width=73, padLeft=2, opacity=0)
        label_cont = Container(parent=self.text_cont, align=Align.TOTOP_PROP, height=0.5, padTop=2)
        status_cont = Container(parent=self.text_cont, align=Align.TOTOP_PROP, height=0.5, padBottom=2)
        self.label = TextDetail(parent=label_cont, align=Align.CENTERLEFT, text=localization.GetByLabel('UI/Insurance/InsuranceStatusLabel'))
        self.status_label = TextDetail(parent=status_cont, align=Align.CENTERLEFT, text=self.get_status_text(), color=self.get_color_text())

    def OnMouseEnter(self, *args):
        animations.MorphScalar(self, 'width', startVal=self.ReverseScaleDpi(self.displayWidth), endVal=self.EXPANDED_WIDTH, duration=0.2)
        animations.FadeIn(self.text_cont, duration=0.2, timeOffset=0.1)
        PlaySound(SOUND_INSURANCE)

    def OnMouseExit(self, *args):
        animations.MorphScalar(self, 'width', startVal=self.ReverseScaleDpi(self.displayWidth), endVal=self.MINIMIZED_WIDTH, duration=0.2)
        animations.FadeOut(self.text_cont, duration=0.1)

    def OnClick(self, *args):
        sm.GetService('cmd').OpenInsurance()
        PlaySound(SOUND_INSURANCE_SELECT)

    def get_color_light(self):
        return self.COLOR_LIGHT[self.status]

    def get_color_dark(self):
        return self.COLOR_DARK[self.status]

    def get_color_text(self):
        return self.COLOR_TEXT[self.status]

    def get_status_text(self):
        if self.status == self.STATUS_WARNING:
            return localization.GetByLabel('UI/Insurance/InsuranceStatusUninsured')
        else:
            return localization.GetByLabel('UI/Insurance/InsuranceStatusInsured')

    def calculate_expanded_width(self):
        label_width, _ = TextBody.MeasureTextSize(self.label.text)
        status_width, _ = TextBody.MeasureTextSize(self.status_label.text)
        text_width = max(label_width, status_width) + 12
        icon_width = 32
        self.EXPANDED_WIDTH = max(self.EXPANDED_WIDTH, text_width + icon_width)
