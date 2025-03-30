#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\infoWindow.py
import sys
import types
import blue
import log
import dogma.data
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveicon
import evetypes
import expertSystems.client
import globalConfig
import localization
import trinity
import uthread
import utillib
from caching.memoize import Memoize
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.lib.const import DAY
from carbon.common.script.sys.service import ROLE_GML
from carbon.common.script.util.format import FmtDateTimeInterval
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import uiconst
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.tabGroup import TabGroup
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.color import Color
from characterdata.bloodlines import get_bloodline_description
from characterdata.factions import get_faction, get_faction_description
from controltowerresources.data import get_resources_for_tower_by_purpose
from entosis.entosisConst import EVENT_TYPE_TCU_DEFENSE, EVENT_TYPE_IHUB_DEFENSE
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.entries.button import ButtonEntry
from eve.client.script.ui.control.entries.divider import DividerEntry
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.moreIcon import MoreIcon
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.inflight.shipModuleButton.attributeValueRowContainer import AttributeValueRowContainer
from eve.client.script.ui.services.menuSvcExtras import openFunctions
from eve.client.script.ui.shared import medalribbonranks
from eve.client.script.ui.shared.bountyWindow import PlaceBountyUtilMenu
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SHOWINFO
from eve.client.script.ui.shared.cloneGrade.omegaCloneIcon import OmegaCloneIcon
from eve.client.script.ui.shared.cloneGrade.omegaCloneOverlayIcon import OmegaCloneOverlayIcon
from eve.client.script.ui.shared.fittingScreen.ghostShipIcon import GhostShipIconSimple, GetSimulateLabelPath
from eve.client.script.ui.shared.fittingScreen.tryFit import GhostFitShip
from eve.client.script.ui.shared.industry.views.containersMETE import ContainerTE, ContainerME
from eve.client.script.ui.shared.info.infoUtil import GetEffectIconIdAndLabelID, GetIconAndLabelForChargeSize, GetUsedWithText, GetWeaonSystemIconForTypeID
from eve.client.script.ui.shared.info.panels.PanelSkinMaterial import PanelSkinMaterial
from eve.client.script.ui.shared.info.panels.PanelSovConstellation import PanelSovConstellation
from eve.client.script.ui.shared.info.panels.panelAgents import PanelAgents
from eve.client.script.ui.shared.info.panels.panelDescription import PanelDescription
from eve.client.script.ui.shared.info.panels.panelFactionalWarfare import PanelFactionalWarfare
from eve.client.script.ui.shared.info.panels.panelFighterAbilities import PanelFighterAbilities
from eve.client.script.ui.shared.info.panels.panelFitting import PanelFitting
from eve.client.script.ui.shared.info.panels.panelGateIcons import PanelGateIcons
from eve.client.script.ui.shared.info.panels.panelRequirements import PanelRequirements
from eve.client.script.ui.shared.info.panels.panelShipAvailableSkinLicenses import PanelShipAvailableSkinLicenses
from eve.client.script.ui.shared.info.panels.panelSkinLicense import PanelSkinLicense
from eve.client.script.ui.shared.info.panels.panelSov import PanelSov
from eve.client.script.ui.shared.info.panels.panelStandings import PanelStandings
from eve.client.script.ui.shared.info.panels.panelTraits import PanelTraits
from eve.client.script.ui.shared.info.panels.panelUsedWith import PanelUsedWith
from eve.client.script.ui.shared.info.panels.panelWarHQ import WarHQ
from eve.client.script.ui.shared.info.panels.planetaryProduction import PanelPlanetaryProduction
from eve.client.script.ui.shared.info.panels.planetaryProductionPlanet import PanelPlanetaryProductionPlanet
from eve.client.script.ui.shared.maps import maputils
from eve.client.script.ui.shared.neocom.skillConst import COLOR_UNALLOCATED_1
from eve.client.script.ui.shared.planet import planetCommon
from eve.client.script.ui.shared.planet.planetSchematicItemEntry import PlanetSchematicItemEntry
from eve.client.script.ui.shared.portraitWindow.portraitWindow import PortraitWindow
from eve.client.script.ui.shared.preview import PreviewContainer
from eve.client.script.ui.shared.skins.buyButton import SkinLicenseBuyButtonAur
from eve.client.script.ui.shared.skins.uiutil import GetMaterialDragData
from eve.client.script.ui.shared.stateFlag import FlagIconWithState, GetRelationShipFlag
from eve.client.script.ui.shared.statusIcon import StatusIcon
from eve.client.script.ui.shared.vgs.button import BuyButtonAurSmall
from eve.client.script.ui.station.agents.agentConversationIcon import AgentConversationIcon
from eve.client.script.ui.station.agents.agentDialogueUtil import GetAgentNameAndLevel
from eve.client.script.ui.station.insurance.insuranceTooltip import LoadInfoInsuranceTooltip
from eve.client.script.ui.util import uix
from eve.client.script.ui.util.linkUtil import IsLink
from eve.client.script.util.contractutils import GetCorpseName
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.idCheckers import IsNPCCorporation
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import ExceptionEater, UserError
from eveformat.client import location
from eveservices.menu import GetMenuService, StartMenuService
from evestations.data import get_station_operation_description
from fastcheckout.client.purchasepanels.purchaseButton import PurchaseButton
from fastcheckout.const import FROM_INFO_WINDOW
from fighters.client import GetSquadronClassResPath, GetSquadronClassTooltip
from fsdBuiltData.common.iconIDs import GetIconFile
from fsdBuiltData.common.planet import get_schematic_ids_for_pin_type_id
from inventorycommon.const import groupCapsule, groupSupercarrier, groupTitan
from menu import MenuLabel
from npcs.npccorporations import get_corporation_faction_id
from npcs.npccorporations import get_npc_corporation_description, get_npc_corporation
from solarsysteminterference.client.ui import GetInterferenceBandLabel
from solarsysteminterference.util import SystemCanHaveInterference
from typematerials.data import get_type_materials_by_id
from .baseInfoWindow import BaseInfoWindow
from .infoConst import *
from .panels.panelCertificateSkills import PanelCertificateSkills
from .panels.panelIndustry import PanelIndustry
from .panels.panelItemIndustry import PanelItemIndustry
from .panels.panelMastery import PanelMastery
from .panels.panelMutatorUsedWith import PanelMutatorUsedWith
from .panels.panelNotes import PanelNotes
from .panels.panelRequiredFor import PanelRequiredFor
from .panels.panelVariations import PanelVariations
ICONSIZE_OMEGA = 24
MINWIDTH = 325
MINHEIGHTREGULAR = 280
MINHEIGHTMEDAL = 480

class InfoWindow(BaseInfoWindow):
    __guid__ = 'form.infowindow'
    __notifyevents__ = ['OnBountyPlaced', 'OnSkillsChanged']
    default_width = 500
    default_height = 600
    default_name = 'infoWindow'
    default_windowID = 'infowindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/info.png'
    default_scope = uiconst.SCOPE_INGAME

    def ConstructLayout(self):
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, padBottom=8, clipChildren=True)
        self.toparea = Container(name='toparea', parent=self.topParent, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.mainiconparent = Container(name='mainiconparent', parent=self.toparea, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, padRight=8)
        self.techicon = Sprite(name='techIcon', parent=self.mainiconparent, align=uiconst.RELATIVE, left=0, width=16, height=16, idx=0)
        self.fighterClassIcon = Sprite(parent=self.mainiconparent, name='fighterClass', align=uiconst.TOPRIGHT, left=0, width=16, height=16, idx=0)
        self.cloneStateOverlay = None
        self.mainicon = Container(name='mainicon', parent=self.mainiconparent, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
        self.mainiconparent.OnMouseEnter = self.OnMainIconParentMouseEnter
        self.mainiconparent.OnMouseExit = self.OnMainIconParentMouseExit
        self.mainiconparent.LoadTooltipPanel = self.MainIconParentLoadTooltipPanel
        self.topRightContent = ContainerAutoSize(name='topRightContent', align=uiconst.TOTOP, parent=self.toparea, callback=self.OnTopRightContResized, alignMode=uiconst.TOTOP)
        self.captioncontainer = ContainerAutoSize(name='captioncontainer', parent=self.topRightContent, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, padRight=48)
        self.subinfolinkcontainer = Container(name='subinfolinkcontainer', parent=self.topRightContent, align=uiconst.TOTOP, padTop=8, clipChildren=True)
        self.therestcontainer = ContainerAutoSize(name='therestcontainer', parent=self.topRightContent, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=8)
        self.moreIcon = MoreIcon(parent=self.topRightContent, align=uiconst.BOTTOMRIGHT, left=4, top=4)
        self.moreIcon.LoadTooltipPanel = self.LoadMoreTooltipPanel
        self.moreIcon.display = False
        self.goForwardBtn = ButtonIcon(name='goForwardBtn', parent=self.toparea, align=uiconst.TOPRIGHT, top=-4, left=-4, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_forward, func=self.OnForward, hint=localization.GetByLabel('UI/Control/EveWindow/Next'))
        self.goBackBtn = ButtonIcon(name='goBackBtn', parent=self.toparea, align=uiconst.TOPRIGHT, top=-4, left=20, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_back, func=self.OnBack, hint=localization.GetByLabel('UI/Control/EveWindow/Previous'))
        self.mainContentCont = Container(name='mainContentCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))

    def ConstructSubtabs(self, tabgroup, subtabs, tabname):
        subtabgroup = []
        sublisttype = None
        for sublisttype, _, _ in subtabs:
            subitems = self.data[sublisttype]['items']
            subtabname = self.data[sublisttype]['name']
            if len(subitems):
                subtabgroup.append([subtabname,
                 self.scroll,
                 self,
                 (sublisttype, None)])

        if subtabgroup:
            _subtabs = TabGroup(name='%s_subtabs' % tabname.lower(), parent=self.mainContentCont, idx=0, tabs=subtabgroup, groupID='infowindow_%s' % sublisttype, autoselecttab=0)
            tabgroup.append([tabname,
             self.scroll,
             self,
             ('selectSubtab', None, _subtabs),
             _subtabs])

    def ConstructCustomTab(self, tabgroup, tabType, tabName):
        name = localization.GetByLabel(tabName)
        panel = self.GetPanelByTabType(tabType)
        if panel:
            tabgroup.append([name,
             panel,
             self,
             (tabType, panel.Load)])
        else:
            func = self.GetDynamicTabLoadMethod(tabType)
            if func:
                tabgroup.append([name,
                 self.scroll,
                 self,
                 (tabType, func)])

    def ConstructMainTabs(self, widthRequirements, tabNumber, selectTabType = None):
        tabgroup = []
        for listtype, subtabs, tabName in INFO_TABS:
            items = self.data[listtype]['items']
            tabname = self.data[listtype]['name']
            text = self.data[listtype].get('text', None)
            if text:
                tabgroup.append([tabname,
                 self.descedit,
                 self,
                 ('readOnlyText', None, text)])
            elif len(items):
                tabgroup.append([tabname,
                 self.scroll,
                 self,
                 (listtype, None)])
            elif listtype in self.dynamicTabs:
                self.ConstructCustomTab(tabgroup, listtype, tabName)
            if subtabs:
                self.ConstructSubtabs(tabgroup, subtabs, tabname)
            if selectTabType is not None and listtype == selectTabType:
                tabNumber = len(tabgroup) - 1

        if len(tabgroup):
            autoSelectTab = tabNumber is None and selectTabType is None
            tabGroupID = 'infowindow_%s' % self.infoType
            self.maintabs = TabGroup(name='maintabs', parent=self.mainContentCont, idx=0, tabs=tabgroup, groupID=tabGroupID, autoselecttab=autoSelectTab, analyticID=tabGroupID)
            if not autoSelectTab:
                self.maintabs.SelectByIdx(tabNumber)
            self.SetUniqueUiNamesForTabs(self.maintabs)

    def ConstructBottomButtons(self, widthRequirements):
        if self.data[DATA_BUTTONS] and session.charid:
            Line(parent=self.mainContentCont, align=uiconst.TOBOTTOM, weight=1, opacity=0.1, idx=0, padTop=8)
            btns = ButtonGroup(parent=self.mainContentCont, padTop=8, btns=self.data[DATA_BUTTONS], button_size_mode=ButtonSizeMode.DYNAMIC, line=False, idx=0)
            totalBtnWidth = 0
            for btn in btns.children[0].children:
                totalBtnWidth += btn.width

            widthRequirements.append(totalBtnWidth)

    def ConstructWindowHeader(self):
        self.ConstructHeaderCaptionAndSubCaption()
        self.mainicon.state = uiconst.UI_DISABLED
        if self.IsType(TYPE_CHARACTER) and self.itemID:
            self.ConstructHeaderCharacter()
        elif self.IsType(TYPE_STRUCTURE):
            self.ConstructHeaderStructure()
        elif self.IsType(TYPE_SHIP):
            self.ConstructHeaderShip()
        elif self.typeID and sm.GetService('godma').GetType(self.typeID).agentID:
            self.ConstructHeaderShip()
        elif self.IsType(TYPE_ENTITY):
            self.ConstructHeaderShip()
            self.ConstructNpcCorpLogo()
        elif self.IsType(TYPE_MEDAL, TYPE_RIBBON) and self.abstractinfo is not None:
            self.ConstructHeaderMedalOrRibbon()
        elif self.IsType(TYPE_CORPORATION):
            self.ConstructHeaderCorporation()
        elif self.IsType(TYPE_ALLIANCE):
            self.ConstructHeaderAlliance()
        elif self.IsType(TYPE_FACTION):
            self.ConstructHeaderFaction()
        elif self.IsType(TYPE_SKILL) and session.charid:
            self.ConstructHeaderSkill()
        elif self.IsType(TYPE_BLUEPRINT):
            self.ConstructHeaderBlueprint()
        elif self.IsType(TYPE_SKINLICENSE):
            self.ConstructHeaderSkinLicense()
        elif self.IsType(TYPE_ENTOSISNODE):
            self.ConstructHeaderEntosisNode()
        elif self.IsType(TYPE_COMMANDNODEBEACON):
            self.ConstructHeaderCommandNodeBeacon()
        elif self.IsType(TYPE_PLEX):
            self.ConstructHeaderPlex()
        elif self.IsType(TYPE_SKILLINJECTOR):
            self.ConstructHeaderSkillInjector()
        elif self.IsType(TYPE_SKILLEXTRACTOR):
            self.ConstructHeaderSkillExtractor()
        elif self.IsDynamicItem():
            self.ConstructHeaderDynamicItem()
        elif self.IsOmegaItem():
            self.omegaIcon = OmegaCloneIcon(parent=self.subinfolinkcontainer, pos=(0,
             0,
             ICONSIZE_OMEGA,
             ICONSIZE_OMEGA), origin=ORIGIN_SHOWINFO, reason=self.typeID)
            self.subinfolinkcontainer.height = ICONSIZE_OMEGA
        if self.IsType(TYPE_MODULE, TYPE_STRUCTURE_MODULE):
            self.ConstructHeaderModule()
        elif self.IsType(TYPE_CHARGE):
            self.ConstructHeaderCharge()

    def ConstructHeaderCaptionAndSubCaption(self):
        if self.captionText:
            eveLabel.EveLabelMedium(name='caption', text=self.captionText, parent=self.captioncontainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
            self.captioncontainer.height = 30
            if self.subCaptionText:
                alpha = 0
                if self.IsType(TYPE_SKILL):
                    labelType = eveLabel.EveLabelSmall
                    alpha = 0.6
                else:
                    labelType = eveLabel.EveLabelMedium
                if IsLink(self.subCaptionText):
                    lblState = uiconst.UI_NORMAL
                else:
                    lblState = uiconst.UI_DISABLED
                lbl = labelType(name='subCaption', text=self.subCaptionText, parent=self.captioncontainer, align=uiconst.TOTOP, tabs=[84], state=lblState)
                if alpha != 0:
                    lbl.SetAlpha(alpha)

    def ConstructNpcCorpLogo(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark:
            slimItem = ballpark.GetInvItem(self.itemID)
            if slimItem and slimItem.ownerID and idCheckers.IsNPCCorporation(slimItem.ownerID):
                self.GetNpcCorpLogo(slimItem.ownerID)

    def ConstructHeaderCharacter(self):
        corpid = None
        corpAge = None
        charStartDate = None
        allianceid = None
        charinfo = None
        corpCharInfo = None
        security = None
        if not idCheckers.IsNPC(self.itemID):
            parallelCalls = []
            parallelCalls.append((sm.RemoteSvc('charMgr').GetPublicInfo3, (self.itemID,)))
            parallelCalls.append((sm.GetService('corp').GetInfoWindowDataForChar, (self.itemID, 1)))
            parallelCalls.append((sm.GetService('crimewatchSvc').GetCharacterSecurityStatus, (self.itemID,)))
            charinfo, corpCharInfo, security = uthread.parallel(parallelCalls)
        if charinfo is not None:
            charinfo = charinfo[0]
            self.data[TAB_BIO]['text'] = charinfo.description
            charStartDate = charinfo.startDateTime
            if getattr(charinfo, 'medal1GraphicID', None):
                eveIcon.Icon(icon='res:/ui/Texture/WindowIcons/corporationdecorations.png', parent=self.mainicon, left=70, top=80, size=64, align=uiconst.RELATIVE, idx=0)
        if corpCharInfo:
            corpid = corpCharInfo.corpID
            allianceid = corpCharInfo.allianceID
            self.corpID = corpid
            self.allianceID = allianceid
            titleList = []
            if corpCharInfo.title:
                titleList.append(corpCharInfo.title)
            for index in xrange(1, 17):
                titleText = getattr(corpCharInfo, 'title%s' % index, None)
                if titleText:
                    titleList.append(titleText)

            if len(titleList):
                title = localization.formatters.FormatGenericList(titleList)
                text = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/InfoWindow/CorpTitle', title=title), parent=self.captioncontainer, align=uiconst.TOTOP)
                if text.height > 405:
                    text.height = 405
        if not idCheckers.IsNPC(self.itemID):
            secText = localization.GetByLabel('UI/InfoWindow/SecurityStatusOfCharacter', secStatus=security)
            eveLabel.EveLabelSmall(text=secText, parent=self.therestcontainer, align=uiconst.TOTOP)
            standing = sm.GetService('standing').GetStanding(eve.session.corpid, self.itemID)
            if standing is not None:
                standingText = localization.GetByLabel('UI/InfoWindow/CorpStandingOfCharacter', corpStanding=standing)
                eveLabel.EveLabelSmall(text=standingText, parent=self.therestcontainer, align=uiconst.TOTOP)
            showWantedSprite = False
            bountyOwnerIDs = (self.itemID, corpid, allianceid)
            bountyAmount = self.GetBountyAmount(*bountyOwnerIDs)
            if bountyAmount > 0 and security <= -5:
                showWantedSprite = True
            bountyAmounts = self.GetBountyAmounts(*bountyOwnerIDs)
            charBounty = 0
            corpBounty = 0
            allianceBounty = 0
            if len(bountyAmounts):
                for ownerID, value in bountyAmounts.iteritems():
                    if idCheckers.IsCharacter(ownerID):
                        charBounty = value
                    elif idCheckers.IsCorporation(ownerID):
                        corpBounty = value
                    elif idCheckers.IsAlliance(ownerID):
                        allianceBounty = value

            bountyHint = localization.GetByLabel('UI/Station/BountyOffice/BountyHint', charBounty=FmtISK(charBounty, 0), corpBounty=FmtISK(corpBounty, 0), allianceBounty=FmtISK(allianceBounty, 0))
            self.Wanted(bountyAmount, True, showWantedSprite, ownerIDs=bountyOwnerIDs, hint=bountyHint)
        if idCheckers.IsNPC(self.itemID):
            agentInfo = sm.GetService('agents').GetAgentByID(self.itemID)
            if agentInfo:
                corpid = agentInfo.corporationID
            else:
                corpid = sm.RemoteSvc('corpmgr').GetCorporationIDForCharacter(self.itemID)
        if corpid:
            corpLogo = self.GetCorpLogo(corpid, parent=self.subinfolinkcontainer)
            corpLogo.padRight = 4
            self.subinfolinkcontainer.height = 64
            if not idCheckers.IsNPC(self.itemID) and corpid:
                tickerName = cfg.corptickernames.Get(corpid).tickerName
                eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/InfoWindow/MemberOfCorp', corpName=cfg.eveowners.Get(corpid).name, tickerName=tickerName), parent=self.subinfolinkcontainer, align=uiconst.TOTOP, top=0, left=0)
                if charStartDate is not None:
                    eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/InfoWindow/MemberFor', timePeriod=FmtDateTimeInterval(charStartDate, blue.os.GetWallclockTime(), 'day')), parent=self.subinfolinkcontainer, align=uiconst.TOBOTTOM, left=4)
                uthread.new(self.ShowRelationshipIcon, self.itemID, corpid, allianceid)
            if charinfo is not None:
                militiaFactionID = charinfo.militiaFactionID
                if not idCheckers.IsNPC(self.itemID) and (allianceid or militiaFactionID):
                    if militiaFactionID:
                        fwSubinfoCont = Container(name='fwSubinfoCont', parent=self.therestcontainer, align=uiconst.TOTOP, height=16, idx=0, clipChildren=True)
                        fwiconCont = Container(name='subinfo', parent=fwSubinfoCont, align=uiconst.TOLEFT, width=20)
                        fwicon = Sprite(name='fwIcon', parent=fwiconCont, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Icons/FW_Icon_Small.png', pos=(-2, 0, 20, 20))
                        fwicon.OnClick = sm.GetService('cmd').OpenMilitia
                        factionText = localization.GetByLabel('UI/FactionWarfare/MilitiaAndFaction', factionName=cfg.eveowners.Get(militiaFactionID).name)
                        factionLabel = eveLabel.EveLabelSmall(text=factionText, parent=fwSubinfoCont, align=uiconst.TOLEFT, top=4)
                        fwSubinfoCont.height = max(factionLabel.textheight + 2 * factionLabel.top, fwicon.height)
                    if allianceid:
                        allianceSubinfoCont = Container(name='allianceSubinfoCont', parent=self.therestcontainer, align=uiconst.TOTOP, height=16, idx=0, clipChildren=True)
                        text = cfg.eveowners.Get(allianceid).name
                        subinfoText = eveLabel.EveLabelSmall(text=text, parent=allianceSubinfoCont, align=uiconst.TOLEFT, top=4)
                        allianceSubinfoCont.height = subinfoText.textheight + 2 * subinfoText.top
                    Line(parent=self.therestcontainer, align=uiconst.TOTOP, padBottom=1, idx=0)
        if sm.GetService('agents').IsAgent(self.itemID):
            AgentConversationIcon(parent=self.subinfolinkcontainer, align=uiconst.TOPRIGHT, agentID=self.itemID)

    def ConstructHeaderStructure(self):
        if self._IsSimulatable():
            iconCont = Container(name='iconCont', parent=self.therestcontainer, align=uiconst.TOTOP, height=42, padBottom=2)
            self.ConstructSimulateBtn(iconCont)

    def _GetShipOwnerID(self):
        if not self.itemID:
            return
        if self.itemID == session.shipid:
            return session.charid
        if session.stationid and eveCfg.GetActiveShip() == self.itemID:
            return session.charid
        if self.typeID and sm.GetService('godma').GetType(self.typeID).agentID:
            return sm.GetService('godma').GetType(self.typeID).agentID
        if session.solarsystemid is not None:
            return sm.GetService('michelle').GetCharIDFromShipID(self.itemID)

    def ConstructHeaderShip(self):
        self.subinfolinkcontainer.height = 42
        shipOwnerID = self._GetShipOwnerID()
        if shipOwnerID:
            btn = Icon(parent=self.subinfolinkcontainer, width=42, height=42, hint=localization.GetByLabel('UI/InfoWindow/ClickForPilotInfo'), align=uiconst.CENTERLEFT)
            btn.OnClick = (self.ReconstructInfoWindow, cfg.eveowners.Get(shipOwnerID).typeID, shipOwnerID)
            btn.LoadIconByTypeID(cfg.eveowners.Get(shipOwnerID).typeID, itemID=shipOwnerID, ignoreSize=True)
        left = 54 if shipOwnerID else 0
        if self.groupID == groupCapsule or self.IsType(TYPE_ENTITY) or self.IsType(TYPE_CELESTIAL):
            return
        skills = sm.GetService('skills').GetRequiredSkills(self.typeID).items()
        texturePath, hint = sm.GetService('skills').GetRequiredSkillsLevelTexturePathAndHint(skills, typeID=self.typeID)
        skillSprite = Sprite(name='skillSprite', parent=self.subinfolinkcontainer, align=uiconst.CENTERLEFT, pos=(left,
         0,
         33,
         33), texturePath=texturePath, hint=hint)
        skillSprite.OnClick = lambda *args: self.maintabs.ShowPanelByName(localization.GetByLabel('UI/InfoWindow/TabNames/Requirements'))
        masterySprite = Sprite(name='masterySprite', parent=self.subinfolinkcontainer, align=uiconst.CENTERLEFT, pos=(left + 36,
         0,
         45,
         45))
        masterySprite.OnClick = lambda *args: self.maintabs.ShowPanelByName(localization.GetByLabel('UI/InfoWindow/TabNames/Mastery'))
        shipMasteryLevel = sm.GetService('certificates').GetCurrCharMasteryLevel(self.typeID)
        texturePath = sm.GetService('certificates').GetMasteryIconForLevel(shipMasteryLevel)
        if shipMasteryLevel == 0:
            hint = localization.GetByLabel('UI/InfoWindow/MasteryNone')
        else:
            hint = localization.GetByLabel('UI/InfoWindow/MasteryLevel', masteryLevel=shipMasteryLevel)
        masterySprite.SetTexturePath(texturePath)
        masterySprite.hint = hint
        left += 84
        if self.IsOmegaItem():
            self.omegaIcon = OmegaCloneIcon(parent=self.subinfolinkcontainer, unlockedWithExpertSystems=self.isUnlockedWithExpertSystem, align=uiconst.CENTERLEFT, pos=(left,
             0,
             ICONSIZE_OMEGA,
             ICONSIZE_OMEGA), origin=ORIGIN_SHOWINFO, reason=self.typeID)
            left += ICONSIZE_OMEGA + 6
        if expertSystems.is_expert_systems_enabled():
            expertSystemIcon = expertSystems.AssociatedExpertSystemIcon(parent=self.subinfolinkcontainer, align=uiconst.CENTERLEFT, left=left, type_id=self.typeID, on_click=lambda : self.maintabs.ShowPanelByName(localization.GetByLabel('UI/InfoWindow/TabNames/Requirements')))
            left += expertSystemIcon.width + 6
        if sm.GetService('info').IsItemSimulated(self.itemID):
            return
        iconCont = None
        if self._IsSimulatable():
            iconCont = Container(name='iconCont', parent=self.therestcontainer, align=uiconst.TOTOP, height=42)
            self.ConstructSimulateBtn(iconCont)
        if self.itemID:
            insuranceParent = self.ConstructInsuranceIcon()
            if insuranceParent:
                if iconCont:
                    padLeft = 12
                else:
                    iconCont = Container(name='iconCont', parent=self.therestcontainer, align=uiconst.TOTOP, height=32)
                    padLeft = 0
                insuranceParent.padLeft = padLeft
                insuranceParent.SetParent(iconCont)

    def ConstructSimulateBtn(self, parentCont):
        sidePad = 0
        btnSize = 42
        simulateCont = Container(name='simulateCont', parent=parentCont, align=uiconst.TOLEFT, width=42 + 2 * sidePad)
        simulateBtn = GhostShipIconSimple(name='simulateBtn', parent=simulateCont, itemID=self.itemID, typeID=self.typeID, invItem=self.rec, align=uiconst.TOPLEFT, pos=(sidePad,
         0,
         btnSize,
         btnSize))

    def ConstructInsuranceIcon(self):
        if self.groupID in (groupTitan, groupSupercarrier):
            return
        bp = sm.GetService('michelle').GetBallpark()
        isMine = False
        if bp is not None and not session.structureid:
            slimItem = bp.GetInvItem(self.itemID)
            if slimItem is not None:
                if slimItem.ownerID in (session.corpid, session.charid):
                    isMine = True
            elif not session.solarsystemid:
                isMine = True
        if isMine or bp is None or session.structureid:
            contract = sm.GetService('insurance').GetContractForShip(self.itemID)
            price = sm.GetService('insurance').GetInsurancePrice(self.typeID)
            if price <= 0:
                return
            status = StatusIcon.STATUS_OK
            if contract and contract.ownerID in (session.corpid, session.charid):
                timeDiff = contract.endDate - blue.os.GetWallclockTime()
                days = timeDiff / DAY
                if days < 5:
                    status = StatusIcon.STATUS_CAUTION
            else:
                status = StatusIcon.STATUS_WARNING
            insuranceParent = Container(name='insuranceParent', align=uiconst.TOLEFT, width=32)
            insuranceIcon = StatusIcon(name='insuranceIcon', parent=insuranceParent, state=uiconst.UI_NORMAL, status=status, texturePath='res:/ui/Texture/WindowIcons/insurance.png')
            insuranceIcon.LoadTooltipPanel = lambda tooltipPanel, *args: LoadInfoInsuranceTooltip(tooltipPanel, self.typeID, contract)
            insuranceIcon.OnClick = sm.GetService('cmd').OpenInsurance
            return insuranceParent

    def ConstructHeaderMedalOrRibbon(self):
        info = sm.GetService('medals').GetMedalDetails(self.itemID).info[0]
        corpid = info.ownerID
        if corpid:
            corpLogo = self.GetCorpLogo(corpid, parent=self.subinfolinkcontainer)
            corpLogo.padRight = 4
            self.subinfolinkcontainer.height = 64
            if corpid and not idCheckers.IsNPC(corpid):
                tickerName = cfg.corptickernames.Get(corpid).tickerName
                eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/InfoWindow/MedalIssuedBy', corpName=cfg.eveowners.Get(corpid).name, tickerName=tickerName), parent=self.subinfolinkcontainer, align=uiconst.TOTOP, top=0, left=0)
            Line(parent=self.captioncontainer, align=uiconst.TOTOP, padRight=-self.captioncontainer.padRight)
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/InfoWindow/NumberOfTimesAwarded', numTimes=info.numberOfRecipients), parent=self.therestcontainer, align=uiconst.TOTOP)

    def ConstructHeaderCorporation(self):
        parallelCalls = []
        if self.corpinfo is None:
            parallelCalls.append((sm.RemoteSvc('corpmgr').GetPublicInfo, (self.itemID,)))
        else:
            parallelCalls.append((lambda : None, ()))
        parallelCalls.append((get_corporation_faction_id, (self.itemID,)))
        if self.warfactioninfo is None:
            parallelCalls.append((sm.GetService('facwar').GetCorporationWarFactionID, (self.itemID,)))
        else:
            parallelCalls.append((lambda : None, ()))
        corpinfo, factionID, warFaction = uthread.parallel(parallelCalls)
        self.warFactionID = warFaction
        self.corpinfo = self.corpinfo or corpinfo
        allianceid = self.corpinfo.allianceID
        uthread.new(self.ShowRelationshipIcon, None, self.itemID, allianceid)
        hqID, hqTypeID = self.GetCorporationHeadquarters()
        if hqID:
            hqLink = GetShowInfoLink(hqTypeID, cfg.evelocations.Get(hqID).name, hqID)
            eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/InfoWindow/HeadquartersLocation', hqLink=hqLink), parent=self.captioncontainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        memberDisp = None
        if factionID or warFaction:
            faction = cfg.eveowners.Get(factionID) if factionID else cfg.eveowners.Get(warFaction)
            eveIcon.GetLogoIcon(itemID=faction.ownerID, parent=self.subinfolinkcontainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/InfoWindow/ClickForFactionInfo'), OnClick=(self.ReconstructInfoWindow, faction.typeID, faction.ownerID), size=64, ignoreSize=True)
            self.subinfolinkcontainer.height = 64
            memberDisp = cfg.eveowners.Get(faction.ownerID).name
        if allianceid:
            alliance = cfg.eveowners.Get(allianceid)
            eveIcon.GetLogoIcon(itemID=allianceid, align=uiconst.TOLEFT, parent=self.subinfolinkcontainer, OnClick=(self.ReconstructInfoWindow, alliance.typeID, allianceid), hint=localization.GetByLabel('UI/InfoWindow/ClickForAllianceInfo'), state=uiconst.UI_NORMAL, size=64, ignoreSize=True)
            self.subinfolinkcontainer.height = 64
            memberDisp = cfg.eveowners.Get(allianceid).name
        if memberDisp is not None:
            eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/InfoWindow/MemberOfAlliance', allianceName=memberDisp), parent=self.subinfolinkcontainer, align=uiconst.TOTOP, top=4, padLeft=4)
        if warFaction is not None:
            facWarInfoCont = Container(name='facwarinfo', parent=self.subinfolinkcontainer, align=uiconst.TOTOP, height=28)
            fwicon = Sprite(name='fwIcon', parent=facWarInfoCont, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Icons/FW_Icon_Large.png', pos=(2, 0, 32, 32), hint=localization.GetByLabel('UI/Commands/OpenFactionalWarfare'))
            fwicon.OnClick = sm.GetService('cmd').OpenMilitia
            eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/FactionWarfare/MilitiaAndFaction', factionName=cfg.eveowners.Get(warFaction).name), parent=facWarInfoCont, align=uiconst.CENTERLEFT, left=38)
        if not idCheckers.IsNPC(self.itemID):
            wanted = False
            if not self.corpinfo.deleted:
                bountyOwnerIDs = (self.itemID, allianceid)
                bountyAmount = self.GetBountyAmount(*bountyOwnerIDs)
                if bountyAmount > 0:
                    wanted = True
                bountyAmounts = self.GetBountyAmounts(*bountyOwnerIDs)
                corpBounty = 0
                allianceBounty = 0
                if len(bountyAmounts):
                    for ownerID, value in bountyAmounts.iteritems():
                        if idCheckers.IsCorporation(ownerID):
                            corpBounty = value
                        elif idCheckers.IsAlliance(ownerID):
                            allianceBounty = value

                bountyHint = localization.GetByLabel('UI/Station/BountyOffice/BountyHintCorp', corpBounty=FmtISK(corpBounty, 0), allianceBounty=FmtISK(allianceBounty, 0))
                self.Wanted(bountyAmount, False, wanted, ownerIDs=bountyOwnerIDs, hint=bountyHint)

    def ConstructHeaderAlliance(self):
        if self.allianceinfo is None:
            self.allianceinfo = sm.GetService('alliance').GetAlliancePublicInfo(self.itemID)
        warFactionID = self.allianceinfo.warFactionID
        self.warFactionID = warFactionID
        if warFactionID is not None:
            fwicon = Sprite(name='fwIcon', parent=self.subinfolinkcontainer, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Icons/FW_Icon_Large.png', pos=(2, 0, 32, 32), hint=localization.GetByLabel('UI/Commands/OpenFactionalWarfare'))
            fwicon.OnClick = sm.GetService('cmd').OpenMilitia
            eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/FactionWarfare/MilitiaAndFaction', factionName=cfg.eveowners.Get(warFactionID).name), parent=self.subinfolinkcontainer, align=uiconst.CENTERLEFT, left=38)
            self.subinfolinkcontainer.height = 32
        uthread.new(self.ShowRelationshipIcon, None, None, self.itemID)
        if not self.allianceinfo.deleted:
            bountyOwnerIDs = (self.itemID,)
            bountyAmount = self.GetBountyAmount(*bountyOwnerIDs)
            wanted = bountyAmount > 0
            self.Wanted(bountyAmount, False, wanted, ownerIDs=bountyOwnerIDs)

    def ConstructHeaderFaction(self):
        faction = get_faction(self.itemID)
        hqSolarSystemID = faction.solarSystemID
        hqLink = GetShowInfoLink(const.typeSolarSystem, cfg.evelocations.Get(hqSolarSystemID).name, hqSolarSystemID)
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/InfoWindow/HeadquartersLocation', hqLink=hqLink), parent=self.captioncontainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)

    def ConstructHeaderSkill(self):
        self.moreIcon.display = True
        uicore.uilib.tooltipHandler.RefreshTooltipForOwner(self.moreIcon)
        cont = Container(name='skillLevelCont', parent=self.therestcontainer, align=uiconst.TOTOP, height=12)
        SkillBar(parent=cont, align=uiconst.TOLEFT, height=0, skillID=self.typeID)
        if self.IsOmegaItem():
            iconCont = Container(name='iconCont', parent=cont, align=uiconst.TOLEFT, width=ICONSIZE_OMEGA, padLeft=5)
            self.omegaIcon = OmegaCloneIcon(parent=iconCont, align=uiconst.CENTER, pos=(0,
             0,
             ICONSIZE_OMEGA,
             ICONSIZE_OMEGA), origin=ORIGIN_SHOWINFO, reason=self.typeID)

    def ConstructHeaderBlueprint(self):
        self.subinfolinkcontainer.padTop = 0
        bpData = self.GetBlueprintData()
        bpInfoCont = Container(name='copyInfoCont', parent=self.therestcontainer, align=uiconst.TOTOP, height=32)
        if not bpData.IsAncientRelic():
            if bpData.original:
                text = localization.GetByLabel('UI/Industry/OriginalInfiniteRuns')
            elif not bpData.runsRemaining or bpData.runsRemaining <= 0:
                text = localization.GetByLabel('UI/Industry/Copy')
            else:
                text = localization.GetByLabel('UI/Industry/CopyRunsRemaining', runsRemaining=bpData.runsRemaining)
            Label(parent=self.captioncontainer, align=uiconst.TOTOP, text=text)
        if bpData.IsAncientRelic() or bpData.IsReactionBlueprint():
            return
        self.containerME = ContainerME(parent=bpInfoCont, align=uiconst.TOPLEFT, pos=(0, 0, 71, 30))
        self.containerME.SetValue(bpData.materialEfficiency)
        self.containerTE = ContainerTE(parent=bpInfoCont, align=uiconst.TOPLEFT, pos=(80, 0, 71, 30))
        self.containerTE.SetValue(bpData.timeEfficiency)
        if self.IsOmegaItem():
            OmegaCloneIcon(parent=bpInfoCont, align=uiconst.TOPLEFT, pos=(160,
             0,
             ICONSIZE_OMEGA,
             ICONSIZE_OMEGA), origin=ORIGIN_SHOWINFO, reason=self.typeID)

    def ConstructHeaderSkinLicense(self):
        buttonCont = ContainerAutoSize(parent=self.therestcontainer, align=uiconst.TOTOP)
        SkinLicenseBuyButtonAur(parent=buttonCont, align=uiconst.TOPLEFT, types=[self.typeID], logContext='SkinLicenseInfoWindow')

    def ConstructHeaderPlex(self):
        buttonCont = ContainerAutoSize(parent=self.therestcontainer, align=uiconst.TOTOP)
        self.buyPlexButton = PurchaseButton(name='buyPlexButton', parent=buttonCont, align=uiconst.TOPLEFT, width=70, height=20, fontsize=12, func=lambda *args: uicore.cmd.CmdBuyPlex(logContext=FROM_INFO_WINDOW), text=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyPlex'))

    def ConstructHeaderSkillInjector(self):
        if not session.charid:
            return
        points = sm.GetService('skills').GetSkillPointAmountFromInjectors(self.typeID, quantity=1)
        text = localization.GetByLabel('UI/SkillTrading/SkillInjectorYield', points=points, charID=session.charid, color=Color.RGBtoHex(*COLOR_UNALLOCATED_1))
        EveLabelMedium(parent=self.therestcontainer, align=uiconst.TOTOP, text=text)

    def ConstructHeaderSkillExtractor(self):
        buttonCont = ContainerAutoSize(parent=self.therestcontainer, align=uiconst.TOTOP)
        BuyButtonAurSmall(parent=buttonCont, align=uiconst.TOPLEFT, types=[self.typeID])

    def ConstructHeaderModule(self):
        iconCont, left, iconSize, smallIconSize = self._GetIconSizedAndContForModuleAndCharges()
        weaponSystemCont = self._AddWeaponSystem(iconCont, iconSize, left)
        left += weaponSystemCont.width if weaponSystemCont else 0
        effectIconID, hintLabelID = GetEffectIconIdAndLabelID(self.typeID)
        if effectIconID:
            c = Container(parent=iconCont, align=uiconst.CENTERLEFT, pos=(left,
             0,
             iconSize,
             iconSize))
            hint = localization.GetByMessageID(hintLabelID) if hintLabelID else ''
            Icon(parent=c, align=uiconst.CENTER, pos=(0,
             0,
             smallIconSize,
             smallIconSize), graphicID=effectIconID, opacity=0.75, hint=hint)
            left += iconSize
        self._AddChargeSize(iconCont, smallIconSize, left)

    def ConstructHeaderCharge(self):
        iconCont, left, iconSize, smallIconSize = self._GetIconSizedAndContForModuleAndCharges()
        weaponSystemCont = self._AddWeaponSystem(iconCont, iconSize, left)
        left += weaponSystemCont.width if weaponSystemCont else 0
        chargeSizeCont = self._AddChargeSize(iconCont, smallIconSize, left)
        if not weaponSystemCont and not chargeSizeCont and not self.IsOmegaItem():
            iconCont.display = False

    def ConstructHeaderDynamicItem(self):
        if not self.itemID:
            return
        self.subinfolinkcontainer.height = 48
        self.subinfolinkcontainer.top = -8
        self.subinfolinkcontainer.padBottom = -6
        item = sm.GetService('dynamicItemSvc').GetDynamicItem(self.itemID)
        if item.characterID:
            characterName = cfg.eveowners.Get(item.characterID).name
            characterLink = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=characterName, info=('showinfo', const.typeCharacter, item.characterID))
            eveLabel.EveLabelMedium(text=(localization.GetByLabel('UI/InfoWindow/CreatedBy'), characterLink), parent=self.subinfolinkcontainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, top=2, opacity=0.4)
        iconContainer = Container(name='iconContainerForDynamicItem', parent=self.subinfolinkcontainer, align=uiconst.TOTOP, height=24, top=4)
        self.subinfolinkcontainer.iconContainerForDynamicItem = iconContainer
        mutatorIcon = ItemIcon(parent=iconContainer, align=uiconst.TOPLEFT, showOmegaOverlay=False, typeID=item.mutatorTypeID, pos=(0, 0, 24, 24))
        sourceItemIcon = ItemIcon(parent=iconContainer, align=uiconst.TOPLEFT, showOmegaOverlay=False, typeID=item.sourceTypeID, pos=(24, 0, 24, 24))
        sourceItemIcon.techIcon.state = uiconst.UI_DISABLED
        if self.IsOmegaItem():
            self.omegaIcon = OmegaCloneIcon(parent=iconContainer, pos=(60,
             0,
             ICONSIZE_OMEGA,
             ICONSIZE_OMEGA), origin=ORIGIN_SHOWINFO, reason=self.typeID)
        hint = localization.GetByLabel('UI/InfoWindow/DynamicItemCompositionHint', mutator=item.mutatorTypeID, source=item.sourceTypeID)
        mutatorIcon.GetHint = lambda : hint
        sourceItemIcon.GetHint = lambda : hint

    def ConstructHeaderCommandNodeBeacon(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return
        slimItem = ballpark.GetInvItem(self.itemID)
        if slimItem:
            sourceInfo = getattr(slimItem, 'campaign_sourceInfo', None)
            if sourceInfo:
                return self.ConstructHeaderForEntoisItems(sourceInfo)

    def ConstructHeaderEntosisNode(self):
        componentInstances = sm.GetService('info').GetComponentInstance(self.itemID)
        if not componentInstances:
            return
        instance = componentInstances.get('entosisCommandNode')
        if not instance:
            return
        return self.ConstructHeaderForEntoisItems(instance.campaign_sourceInfo)

    def ConstructHeaderForEntoisItems(self, sourceInfo):
        sourceSolarsystemID, eventTypeID, sourceID, defenderID = sourceInfo
        typeID, structureName = self.GetStructureTypeAndNameFromEventType(sourceID, eventTypeID)
        solarsytemName = cfg.evelocations.Get(sourceSolarsystemID).name
        itemLink = GetShowInfoLink(typeID, structureName, sourceID)
        solarsystemLink = GetShowInfoLink(const.typeSolarSystem, solarsytemName, sourceSolarsystemID)
        links = [itemLink, solarsystemLink]
        if defenderID:
            allianceName = cfg.eveowners.Get(defenderID).name
            allianceLink = GetShowInfoLink(const.typeAlliance, allianceName, defenderID)
            links.append(allianceLink)
        contHeight = 0
        for eachLink in links:
            label = eveLabel.EveLabelSmall(text=eachLink, parent=self.subinfolinkcontainer, align=uiconst.TOTOP, top=0, left=0, state=uiconst.UI_NORMAL)
            contHeight += label.textheight

        self.subinfolinkcontainer.height = contHeight

    def OnMainIconParentMouseExit(self):
        if self.cloneStateOverlay:
            self.cloneStateOverlay.OnMouseExit()

    def OnMainIconParentMouseEnter(self):
        if self.mainiconparent.OnClick:
            PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if self.cloneStateOverlay:
            self.cloneStateOverlay.OnMouseEnter()

    def OnTopRightContResized(self, *args):
        height = self.topRightContent.height
        self.topParent.height = max(height, self.mainiconparent.width, self.mainiconparent.height)

    def OnBack(self):
        self.UpdateHistoryData()
        infoWndID = self.history.GoBack()
        if infoWndID:
            if uicore.uilib.mouseOver != self.goBackBtn:
                self.goBackBtn.Blink()
            self.ReconstructInfoWindow(branchHistory=False, *infoWndID)

    def OnForward(self):
        self.UpdateHistoryData()
        infoWndData = self.history.GoForward()
        if infoWndData:
            if uicore.uilib.mouseOver != self.goForwardBtn:
                self.goForwardBtn.Blink()
            self.ReconstructInfoWindow(branchHistory=False, *infoWndData)

    def MainIconParentLoadTooltipPanel(self, tooltipPanel, *args):
        if self.cloneStateOverlay and sm.GetService('cloneGradeSvc').IsRestricted(self.typeID):
            self.cloneStateOverlay.LoadTooltipPanel(tooltipPanel, args)

    def ReconstructSubContainer(self):
        self.mainContentCont.Flush()
        self.scroll = Scroll(name='scroll', parent=self.mainContentCont, state=uiconst.UI_HIDDEN, padding=const.defaultPadding)
        self.scroll.ignoreTabTrimming = True
        self.descedit = EditPlainText(name='descedit', parent=self.mainContentCont, state=uiconst.UI_HIDDEN, readonly=1, linkStyle=uiconst.LINKSTYLE_SUBTLE)

    def GetMainIconDragData(self, *args):
        if not self.typeID:
            return []
        if self.IsType(TYPE_MEDAL, TYPE_RANK):
            return []
        fakeNode = Bunch()
        fakeNode.typeID = self.typeID
        if self.IsType(TYPE_CHARACTER, TYPE_CORPORATION, TYPE_ALLIANCE, TYPE_FACTION):
            fakeNode.__guid__ = 'listentry.User'
            fakeNode.itemID = self.itemID
            fakeNode.IsCharacter = self.IsType(TYPE_CHARACTER)
            fakeNode.IsCorporation = self.IsType(TYPE_CORPORATION)
            fakeNode.IsFaction = self.IsType(TYPE_FACTION)
            fakeNode.IsAlliance = self.IsType(TYPE_ALLIANCE)
            if not (fakeNode.IsCharacter or fakeNode.IsCorporation or fakeNode.IsFaction or fakeNode.IsAlliance):
                return []
            fakeNode.charID = self.itemID
            fakeNode.info = Bunch(typeID=self.typeID, name=cfg.eveowners.Get(self.itemID).name)
            return [fakeNode]
        if self.IsType(TYPE_LANDMARK):
            fakeNode.isLandMark = True
            landmark = sm.GetService('map').GetLandmark(self.itemID * -1)
            if hasattr(landmark, 'iconID'):
                fakeNode.iconNum = landmark.iconID
        if self.IsType(TYPE_CELESTIAL, TYPE_STATION, TYPE_STRUCTURE, TYPE_LANDMARK) and self.itemID:
            fakeNode.__guid__ = 'xtriui.ListSurroundingsBtn'
            fakeNode.itemID = self.itemID
            fakeNode.label = self.captionText or localization.GetByLabel('UI/Common/Unknown')
            return [fakeNode]
        if self.IsType(TYPE_CERTIFICATE):
            fakeNode.__guid__ = 'listentry.CertEntry'
            fakeNode.typeID = self.typeID
            fakeNode.certID = self.abstractinfo.certificateID
            fakeNode.level = self.abstractinfo.level
            className, grade, _ = sm.GetService('certificates').GetCertificateLabel(self.abstractinfo.certificateID)
            if fakeNode.level > 0:
                label = localization.GetByLabel('UI/InfoWindow/CertificateNameWithGrade', certificateName=className, certificateGrade=grade)
                fakeNode.label = label
            else:
                fakeNode.label = className
            return [fakeNode]
        if self.IsType(TYPE_SKINMATERIAL):
            material = sm.GetService('cosmeticsSvc').GetStaticMaterialByID(self.itemID)
            return GetMaterialDragData(material)
        if self.itemID:
            fakeNode.__guid__ = 'listentry.Item'
            fakeNode.itemID = self.itemID
            label = evetypes.GetName(self.typeID)
            fakeNode.label = label or 'Unknown'
            return [fakeNode]
        if evetypes.IsPublished(self.typeID):
            fakeNode.__guid__ = 'listentry.GenericMarketItem'
        else:
            fakeNode.__guid__ = 'uicls.GenericDraggableForTypeID'
        label = evetypes.GetName(self.typeID)
        fakeNode.label = label or 'Unknown'
        return [fakeNode]

    def ShowError(self, args):
        self.topParent.Hide()
        errorPar = Container(parent=self.sr.main, name='errorPar', align=uiconst.TOALL, left=12, top=6, width=12, height=6, state=uiconst.UI_DISABLED)
        msg = cfg.GetMessage(*args)
        title = eveLabel.CaptionLabel(text=msg.title, parent=errorPar, align=uiconst.TOTOP)
        title.name = 'errorTitle'
        Container(parent=errorPar, name='separator', align=uiconst.TOTOP, height=6)
        eveLabel.EveLabelMedium(text=msg.text, name='errorDetails', parent=errorPar, align=uiconst.TOTOP)

    def HideError(self):
        if not self.IsCollapsed():
            self.topParent.state = uiconst.UI_PICKCHILDREN
        errorPar = self.sr.main.FindChild('errorPar')
        if errorPar is not None:
            errorPar.Close()

    def UpdateWindowMinSize(self, width):
        height = MINHEIGHTREGULAR
        if self.IsType(TYPE_MEDAL):
            height = MINHEIGHTMEDAL
        self.SetMinSize([width, height])

    def GetPanelByTabType(self, tabType):
        if tabType == TAB_NOTES:
            return PanelNotes(parent=self.mainContentCont, itemID=self.itemID)
        if tabType == TAB_MASTERY:
            return PanelMastery(parent=self.mainContentCont, typeID=self.typeID)
        if tabType == TAB_CERTSKILLS:
            return PanelCertificateSkills(parent=self.mainContentCont, typeID=self.typeID, certificateID=self.abstractinfo.certificateID)
        if tabType == TAB_REQUIREDFOR:
            return PanelRequiredFor(parent=self.mainContentCont, typeID=self.typeID)
        if tabType == TAB_INDUSTRY:
            return PanelIndustry(parent=self.mainContentCont, bpData=self.GetBlueprintData())
        if tabType == TAB_ITEMINDUSTRY:
            return PanelItemIndustry(parent=self.mainContentCont, typeID=self.typeID)
        if tabType == TAB_TRAITS:
            if PanelTraits.TraitsVisible(self.typeID):
                return PanelTraits(parent=self.mainContentCont, typeID=self.typeID)
        elif tabType == TAB_REQUIREMENTS:
            if PanelRequirements.RequirementsVisible(self.typeID):
                return PanelRequirements(parent=self.mainContentCont, typeID=self.typeID)
        else:
            if tabType == TAB_FITTING:
                return PanelFitting(parent=self.mainContentCont, item=self.rec, itemID=self.itemID, typeID=self.typeID)
            if tabType == TAB_USEDWITH:
                return PanelUsedWith(parent=self.mainContentCont, typeID=self.typeID)
            if tabType == TAB_SKINLICENSE:
                return PanelSkinLicense(parent=self.mainContentCont, typeID=self.typeID)
            if tabType == TAB_SKINMATERIAL:
                return PanelSkinMaterial(parent=self.mainContentCont, typeID=self.typeID, itemID=self.itemID)
            if tabType == TAB_SHIPAVAILABLESKINLICENSES:
                return PanelShipAvailableSkinLicenses(parent=self.mainContentCont, typeID=self.typeID)
            if tabType == TAB_SOV:
                return PanelSov(parent=self.mainContentCont, solarsystemID=self.itemID)
            if tabType == TAB_SOV_CONSTELLATION:
                return PanelSovConstellation(parent=self.mainContentCont, constellationID=self.itemID)
            if tabType == TAB_FIGHTER_ABILITIES:
                return PanelFighterAbilities(parent=self.mainContentCont, itemID=self.itemID, typeID=self.typeID)
            if tabType == TAB_DESCRIPTION_DYNAMIC:
                return PanelDescription(parent=self.mainContentCont, itemID=self.itemID, typeID=self.typeID)
            if tabType == TAB_STANDINGS:
                return PanelStandings(parent=self.mainContentCont, ownerID=self.itemID)
            if tabType == TAB_AGENTS:
                return PanelAgents(parent=self.mainContentCont, ownerID=self.itemID, typeID=self.typeID, selectedLevel=self.abstractinfo.selectedLevel if self.abstractinfo else None)
            if tabType == TAB_MUTATOR_USED_WITH:
                return PanelMutatorUsedWith(parent=self.mainContentCont, typeID=self.typeID)
            if tabType == TAB_VARIATIONS:
                return PanelVariations(parent=self.mainContentCont, typeID=self.typeID)
            if tabType == TAB_PLANETARYPRODUCTION:
                return PanelPlanetaryProduction(parent=self.mainContentCont, typeID=self.typeID)
            if tabType == TAB_PLANETARYPRODUCTIONPLANET:
                return PanelPlanetaryProductionPlanet(parent=self.mainContentCont, typeID=self.typeID)
            if tabType == TAB_GATE_ICONS:
                gateIconData = self.GetGateIconData()
                if gateIconData:
                    return PanelGateIcons(parent=self.mainContentCont, gateIconData=gateIconData)
            else:
                if tabType == TAB_WARHQ:
                    return WarHQ(parent=self.mainContentCont, typeID=self.typeID, structureID=self.itemID)
                if tabType == TAB_EXPERT_SYSTEM_SKILLS and expertSystems.is_expert_systems_enabled():
                    return expertSystems.SkillsPanel(parent=self.mainContentCont, expertSystemTypeID=self.typeID)
                if tabType == TAB_EXPERT_SYSTEM_SHIPS and expertSystems.is_expert_systems_enabled():
                    return expertSystems.ShipsPanel(parent=self.mainContentCont, expertSystemTypeID=self.typeID)
                if tabType == TAB_FW:
                    return PanelFactionalWarfare(parent=self.mainContentCont, solarsystemID=self.itemID)

    def SetUniqueUiNamesForTabs(self, tabs):
        tabNamesAndPointers = [(localization.GetByLabel('UI/InfoWindow/TabNames/Variations'), pConst.UNIQUE_NAME_VARIATION_TAB)]
        pConst.SetUniqueUiNamesForTabs(tabs, tabNamesAndPointers)

    def UpdateHistoryButtons(self):
        if self.history.IsBackEnabled():
            self.goBackBtn.Enable()
        else:
            self.goBackBtn.Disable()
        if self.history.IsForwardEnabled():
            self.goForwardBtn.Enable()
        else:
            self.goForwardBtn.Disable()

    def _ReconstructInfoWindow(self, typeID, itemID = None, rec = None, parentID = None, abstractinfo = None, tabNumber = None, branchHistory = True, selectTabType = None, params = None):
        try:
            self.ShowLoad()
            self.isLoading = True
            self.HideError()
            if self.top == uicore.desktop.height:
                self.Maximize()
            if branchHistory and not self.history.IsEmpty():
                self.UpdateHistoryData()
            self.typeID = typeID
            self.itemID = itemID
            self.rec = rec
            self.parentID = parentID
            self.abstractinfo = abstractinfo
            self.isUnlockedWithExpertSystem = sm.GetService('skills').IsUnlockedWithExpertSystem(self.typeID)
            self.groupID = evetypes.GetGroupID(typeID)
            self.categoryID = evetypes.GetCategoryID(typeID)
            self.infoType = self.GetInfoWindowType()
            self.corpinfo = None
            self.allianceinfo = None
            self.warfactioninfo = None
            self.stationinfo = None
            self.plasticinfo = None
            self.corpID = None
            self.allianceID = None
            self.captionText = None
            self.subCaptionText = None
            self.omegaIcon = None
            self.ResetWindowData()
            self.maintabs = None
            self.captioncontainer.Flush()
            self.subinfolinkcontainer.Flush()
            self.therestcontainer.Flush()
            self.moreIcon.display = False
            self.subinfolinkcontainer.height = 0
            self.subinfolinkcontainer.padTop = 8
            self.subinfolinkcontainer.top = 0
            self.subinfolinkcontainer.padBottom = 0
            self.mainiconparent.GetDragData = self.GetMainIconDragData
            self.mainiconparent.isDragObject = True
            self.ReconstructSubContainer()
            self.UpdateCaption()
            self.UpdateHeaderActionMenu()
            self.UpdateWindowIcon(typeID, itemID)
            self.UpdateDescriptionCaptionAndSubCaption()
            self.ConstructWindowHeader()
            sm.GetService('info').UpdateWindowData(self, typeID, itemID, parentID=parentID)
            self.CheckConstructOwnerButtonIcon(itemID)
            if branchHistory:
                self.history.Append(self.GetHistoryData())
            self.UpdateHistoryButtons()
            widthRequirements = [MINWIDTH]
            self.ConstructMainTabs(widthRequirements, tabNumber, selectTabType)
            self.ConstructBottomButtons(widthRequirements)
            width = max(widthRequirements)
            self.UpdateWindowMinSize(width)
            self.toparea.state = uiconst.UI_PICKCHILDREN
        except BadArgs as e:
            self.ShowError(e.args)
            sys.exc_clear()
        finally:
            self.HideLoad()
            self.isLoading = False

        uicore.registry.SetFocus(self)

    def GetOwnerIDToShow(self, itemID):
        if self.IsOwned():
            slimitem = sm.GetService('michelle').GetItem(itemID)
            if slimitem is not None:
                return slimitem.ownerID
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(itemID)
            if structureInfo:
                return structureInfo.ownerID

    def CheckConstructOwnerButtonIcon(self, itemID):
        ownerID = self.GetOwnerIDToShow(itemID)
        if ownerID:
            ownerOb = cfg.eveowners.Get(ownerID)
            if ownerOb.groupID == const.groupCharacter:
                btn = Icon(parent=self.subinfolinkcontainer, pos=(0, 0, 42, 42), iconMargin=2, hint=localization.GetByLabel('UI/InfoWindow/ClickForPilotInfo'))
                btn.OnClick = (self.ReconstructInfoWindow, ownerOb.typeID, ownerID)
                btn.LoadIconByTypeID(ownerOb.typeID, itemID=ownerID, ignoreSize=True)
                self.subinfolinkcontainer.height = 42
                if self.omegaIcon:
                    self.omegaIcon.left += 45
            elif ownerOb.groupID == const.groupCorporation:
                self.GetCorpLogo(ownerID, parent=self.subinfolinkcontainer)
                self.subinfolinkcontainer.height = 64
                if self.omegaIcon:
                    self.omegaIcon.left += 67

    def IsOmegaItem(self):
        return sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(self.typeID)

    def IsDynamicItem(self):
        return sm.GetService('dynamicItemSvc').IsDynamicItem(self.typeID)

    def GetNpcCorpLogo(self, corpID):
        if len(self.subinfolinkcontainer.children) > 0:
            left = 50
        else:
            left = 4
        corpLogo = self.GetCorpLogo(corpID, parent=self.subinfolinkcontainer)
        corpLogo.left = left
        self.subinfolinkcontainer.height = 64

    def _GetShipOwnerID(self):
        if not self.itemID:
            return
        if self.itemID == session.shipid:
            return session.charid
        if session.stationid and eveCfg.GetActiveShip() == self.itemID:
            return session.charid
        if self.typeID and sm.GetService('godma').GetType(self.typeID).agentID:
            return sm.GetService('godma').GetType(self.typeID).agentID
        if session.solarsystemid is not None:
            return sm.GetService('michelle').GetCharIDFromShipID(self.itemID)

    def GetCorporationHeadquarters(self):
        hqID = None
        hqTypeID = None
        if idCheckers.IsNPCCorporation(self.corpinfo.corporationID):
            corporation = get_npc_corporation(self.corpinfo.corporationID)
            stationHQ = getattr(corporation, 'stationID')
            solarSystemHQ = getattr(corporation, 'solarSystemID')
            if stationHQ:
                stationInfo = sm.GetService('ui').GetStationStaticInfo(stationHQ)
                hqID = stationHQ
                hqTypeID = stationInfo.stationTypeID
            elif solarSystemHQ:
                hqID = corporation.solarSystemID
                hqTypeID = const.typeSolarSystem
        else:
            stationInfo = sm.GetService('ui').GetStationStaticInfo(self.corpinfo.stationID)
            if stationInfo:
                hqID = self.corpinfo.stationID
                hqTypeID = stationInfo.stationTypeID
        return (hqID, hqTypeID)

    def _GetIconSizedAndContForModuleAndCharges(self):
        iconSize = 32
        smallIconSize = 24
        if self.IsDynamicItem():
            iconContainerForDynamicItem = getattr(self.subinfolinkcontainer, 'iconContainerForDynamicItem', None)
            if iconContainerForDynamicItem and not iconContainerForDynamicItem.destroyed:
                return (iconContainerForDynamicItem,
                 86,
                 iconSize,
                 smallIconSize)
        if self.IsOmegaItem():
            iconCont = self.subinfolinkcontainer
            left = 30
        else:
            left = 0
            iconCont = Container(name='iconCont', parent=self.therestcontainer, align=uiconst.TOTOP, height=iconSize)
        return (iconCont,
         left,
         iconSize,
         smallIconSize)

    def _AddWeaponSystem(self, iconCont, iconSize, left):
        texturePath = GetWeaonSystemIconForTypeID(self.typeID)
        if texturePath:
            hintText = ''
            with ExceptionEater('infosvc: _AddWeaponSystem'):
                hintText = GetUsedWithText(self.typeID)
            c = Container(parent=iconCont, align=uiconst.CENTERLEFT, pos=(left,
             0,
             iconSize,
             iconSize))
            (Sprite(parent=c, align=uiconst.CENTER, pos=(0,
              0,
              iconSize,
              iconSize), texturePath=texturePath, opacity=0.75, saturation=0.0, spriteEffect=trinity.TR2_SFX_COLOROVERLAY, hint=hintText),)
            return c

    def _AddChargeSize(self, iconCont, iconSize, left):
        texturePath, hintText = GetIconAndLabelForChargeSize(self.typeID)
        if texturePath:
            c = Container(parent=iconCont, align=uiconst.CENTERLEFT, pos=(left,
             0,
             iconSize,
             iconSize))
            Sprite(parent=c, align=uiconst.CENTER, pos=(0,
             0,
             iconSize,
             iconSize), texturePath=texturePath, opacity=0.75, hint=hintText)
            return c

    def GetStructureTypeAndNameFromEventType(self, sourceID, eventType):
        if eventType == EVENT_TYPE_TCU_DEFENSE:
            return (const.typeTerritorialClaimUnit, evetypes.GetName(const.typeTerritorialClaimUnit))
        elif eventType == EVENT_TYPE_IHUB_DEFENSE:
            return (const.typeInfrastructureHub, evetypes.GetName(const.typeInfrastructureHub))
        else:
            stationTypeID = cfg.stations.Get(sourceID).stationTypeID
            try:
                structureName = cfg.evelocations.Get(sourceID).name
            except KeyError:
                structureName = evetypes.GetName(stationTypeID)

            return (stationTypeID, structureName)

    def GetInfoWindowType(self):
        if self.typeID in infoTypeByTypeID:
            return infoTypeByTypeID[self.typeID]
        if self.groupID in infoTypeByGroupID:
            return infoTypeByGroupID[self.groupID]
        if self.categoryID in infoTypeByCategoryID:
            return infoTypeByCategoryID[self.categoryID]
        return TYPE_UNKNOWN

    def IsType(self, *args):
        return self.infoType in args

    def IsOwned(self):
        return self.groupID in ownedGroups or self.categoryID in ownedCategories

    def UpdateCaption(self):
        if self.IsType(TYPE_BOOKMARK, TYPE_CERTIFICATE):
            caption = localization.GetByLabel('UI/InfoWindow/InfoWindowCaption', infoObject=evetypes.GetName(self.typeID))
        elif self.IsType(TYPE_SHIP, TYPE_EXPERT_SYSTEM):
            infoObject = '%s (%s)' % (evetypes.GetName(self.typeID), evetypes.GetGroupName(self.typeID))
            caption = localization.GetByLabel('UI/InfoWindow/InfoWindowCaption', infoObject=infoObject)
        elif self.IsType(TYPE_LANDMARK):
            caption = localization.GetByLabel('UI/InfoWindow/LandmarkInformationCaption')
        elif self.IsType(TYPE_SKILL):
            caption = localization.GetByLabel('UI/InfoWindow/InfoWindowCaption', infoObject=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Skill'))
        elif self.IsType(TYPE_SKINMATERIAL):
            caption = localization.GetByLabel('UI/InfoWindow/InfoWindowCaption', infoObject=localization.GetByLabel('UI/Skins/Material'))
        else:
            caption = localization.GetByLabel('UI/InfoWindow/InfoWindowCaption', infoObject=evetypes.GetGroupName(self.typeID))
        self.SetCaption(caption)

    def GetBlueprintData(self):
        if not self.itemID:
            isCopy = False
            if self.abstractinfo:
                if hasattr(self.abstractinfo, 'bpData'):
                    if hasattr(self.abstractinfo.bpData, 'original'):
                        isCopy = not self.abstractinfo.bpData.original
                elif getattr(self.abstractinfo, 'fullBlueprintData', None):
                    return self.abstractinfo.fullBlueprintData
                else:
                    if evetypes.GetCategoryID(self.typeID) == const.categoryAncientRelic:
                        isCopy = True
                    else:
                        isCopy = getattr(self.abstractinfo, 'isCopy', isCopy)
                    runsRemaining = getattr(self.abstractinfo, 'runs', None)
                    materialEfficiency = getattr(self.abstractinfo, 'materialLevel', None)
                    timeEfficiency = getattr(self.abstractinfo, 'productivityLevel', None)
                    return sm.GetService('blueprintSvc').GetBlueprintTypeCopy(self.typeID, original=not isCopy, runsRemaining=runsRemaining, materialEfficiency=materialEfficiency, timeEfficiency=timeEfficiency)

            return sm.GetService('blueprintSvc').GetBlueprintType(self.typeID, isCopy=isCopy)
        if idCheckers.IsFakeItem(self.itemID):
            return sm.GetService('blueprintSvc').GetBlueprintType(self.typeID)
        return self._GetBlueprintItem(self.itemID)

    def GetGateIconData(self):
        if self.itemID:
            bp = sm.GetService('michelle').GetBallpark()
            if bp is None:
                return
            slimItem = bp.GetInvItem(self.itemID)
            if slimItem is None:
                return
            gateData = Bunch(destinationSystemStatusIcons=slimItem.destinationSystemStatusIcons, destinationSystemOwnerID=slimItem.destinationSystemOwnerID, originSystemOwnerID=slimItem.originSystemOwnerID, destinationSystemWarning=slimItem.destinationSystemWarning, destinationSolarSystemID=slimItem.jumps[0].locationID)
            return gateData

    @Memoize(0.5)
    def _GetBlueprintItem(self, itemID):
        return sm.GetService('blueprintSvc').GetBlueprintItem(itemID)

    def UpdateWindowIcon(self, typeID, itemID):
        iWidth = iHeight = 64
        rendersize = 128
        self.mainicon.Flush()
        self.techicon.Hide()
        self.fighterClassIcon.Hide()
        self.mainiconparent.cursor = None
        self.mainiconparent.OnClick = None
        if self.IsOmegaItem() and not self.isUnlockedWithExpertSystem:
            self.cloneStateOverlay = OmegaCloneOverlayIcon(parent=self.mainicon, align=uiconst.TOALL, state=uiconst.UI_DISABLED, origin=ORIGIN_SHOWINFO, reason=self.typeID, unlockedWithExpertSystem=self.isUnlockedWithExpertSystem)
        else:
            self.cloneStateOverlay = None
        if self.IsType(TYPE_PLANET, TYPE_SHIP, TYPE_STATION, TYPE_STRUCTURE, TYPE_STARGATE, TYPE_DRONE, TYPE_FIGHTER, TYPE_ENTITY, TYPE_CELESTIAL, TYPE_RANK, TYPE_ENTOSISNODE, TYPE_COMMANDNODEBEACON):
            iWidth = iHeight = 128
            if self.groupID in (const.groupDestructibleStationServices, const.groupAbyssalEnvironment):
                iWidth = iHeight = 64
            elif self.groupID not in (const.groupRegion, const.groupConstellation, const.groupSolarSystem):
                rendersize = 256
        hasAbstractIcon = False
        if self.abstractinfo is not None:
            if self.IsType(TYPE_RANK):
                rank = medalribbonranks.Rank(name='rankicon', align=uiconst.TOPLEFT, left=3, top=2, width=iWidth, height=iHeight, parent=self.mainicon)
                rank.Startup(self.abstractinfo.warFactionID, self.abstractinfo.currentRank)
                hasAbstractIcon = True
            if self.IsType(TYPE_MEDAL, TYPE_RIBBON):
                rendersize = 256
                iWidth, iHeight = (128, 256)
                medal = medalribbonranks.MedalRibbon(name='medalicon', align=uiconst.TOPLEFT, left=3, top=2, width=iWidth, height=iHeight, parent=self.mainicon)
                medal.Startup(self.abstractinfo, rendersize)
                hasAbstractIcon = True
            if self.IsType(TYPE_CERTIFICATE):
                texturePath = 'res:/UI/Texture/icons/79_64_%s.png' % (self.abstractinfo.level + 1)
                sprite = Sprite(parent=self.mainicon, texturePath=texturePath, align=uiconst.TOALL)
                self.mainiconparent.hint = evetypes.GetDescription(const.typeCertificate)
                hasAbstractIcon = True
        if self.IsType(TYPE_FIGHTER):
            self.fighterClassIcon.Show()
            texturePath = GetSquadronClassResPath(self.typeID)
            self.fighterClassIcon.SetTexturePath(texturePath)
            self.fighterClassIcon.hint = localization.GetByLabel(GetSquadronClassTooltip(self.typeID))
        if self.IsType(TYPE_SKINMATERIAL):
            material = sm.GetService('cosmeticsSvc').GetStaticMaterialByID(itemID)
            texturePath = material.iconTexturePath
            sprite = Sprite(parent=self.mainicon, texturePath=texturePath, align=uiconst.TOALL)
        elif self.IsType(TYPE_CHARACTER):
            sprite = Sprite(parent=self.mainicon, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            sm.GetService('photo').GetPortrait(itemID, 256, sprite, allowServerTrip=True)
            iWidth = iHeight = 128
            self.mainiconparent.cursor = uiconst.UICURSOR_MAGNIFIER
            self.mainiconparent.OnClick = (self.OpenPortraitWnd, itemID)
        elif self.IsType(TYPE_CORPORATION, TYPE_FACTION, TYPE_ALLIANCE):
            if self.IsType(TYPE_CORPORATION):
                try:
                    cfg.eveowners.Get(itemID)
                except:
                    log.LogWarn('Tried to show info on bad corpID:', itemID)
                    raise BadArgs('InfoNoCorpWithID')

            eveIcon.GetLogoIcon(itemID=itemID, parent=self.mainicon, name='corplogo', acceptNone=False, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            self.mainiconparent.cursor = uiconst.UICURSOR_MAGNIFIER
            self.mainiconparent.OnClick = (self.OpenEntityWnd, itemID)
        elif self.IsType(TYPE_LANDMARK):
            landmark = sm.GetService('map').GetLandmark(itemID * -1)
            if hasattr(landmark, 'iconID'):
                sprite = Sprite(parent=self.mainicon, align=uiconst.TOALL)
                sprite.texture.resPath = GetIconFile(landmark.iconID)
                sprite.rectLeft = 64
                sprite.rectWidth = 128
                iWidth = iHeight = 128
        elif self.IsType(TYPE_BLUEPRINT) and (itemID and not idCheckers.IsFakeItem(itemID) or self.abstractinfo is not None):
            uix.GetTechLevelIcon(self.techicon, 0, typeID)
            bpData = self.GetBlueprintData()
            icon = Icon(parent=self.mainicon, align=uiconst.TOALL, size=rendersize, typeID=typeID, itemID=itemID, ignoreSize=True, isCopy=not bpData.original)
        elif itemID and evetypes.GetGroupID(typeID) in (const.groupRegion, const.groupConstellation, const.groupSolarSystem):
            from eve.client.script.ui.shared.maps.map2D import Map2D
            ssmap = Map2D()
            level = [const.groupRegion, const.groupConstellation, const.groupSolarSystem].index(evetypes.GetGroupID(typeID)) + 1
            icon = Container(parent=self.mainicon, align=uiconst.TOALL, clipChildren=True)
            ssmap.Draw([itemID], level, level + 1, rendersize, icon)
        elif self.IsType(TYPE_SHIP) and itemID and self._GetShipOwnerID():
            shipOwnerID = self._GetShipOwnerID()
            uix.GetTechLevelIcon(self.techicon, 0, typeID)
            previewContainer = PreviewContainer(parent=self.mainicon, align=uiconst.TOALL)
            uicore.animations.FadeIn(previewContainer.loadingWheel, duration=1)
            self.mainiconparent.cursor = uiconst.UICURSOR_MAGNIFIER
            self.mainiconparent.OnClick = (self.PreviewShip, None)

            def FetchAndShowAppliedSkin():
                skin_state = sm.GetService('cosmeticsSvc').GetAppliedSkinState(shipOwnerID, self.itemID)
                previewContainer.PreviewShip(self.typeID, skin_state=skin_state)
                previewContainer.AnimEntry()
                self.mainiconparent.OnClick = (self.PreviewShip, skin_state)

            uthread.new(FetchAndShowAppliedSkin)
        elif not hasAbstractIcon:
            uix.GetTechLevelIcon(self.techicon, 0, typeID)
            icon = eveIcon.Icon(parent=self.mainicon, align=uiconst.TOALL, size=rendersize, typeID=typeID, itemID=itemID, ignoreSize=True)
            if eveCfg.IsPreviewable(typeID):
                icon.typeID = typeID
                self.mainiconparent.cursor = uiconst.UICURSOR_MAGNIFIER
                self.mainiconparent.OnClick = (self.OnPreviewClick, icon)
        self.mainiconparent.width = self.mainicon.width = iWidth
        self.mainiconparent.height = self.mainicon.height = iHeight

    def GetNeocomGroupLabel(self):
        return localization.GetByLabel('UI/InfoWindow/Information')

    def UpdateHeaderActionMenu(self):
        actionMenu = self.GetActionMenu(self.itemID, self.typeID, self.rec)
        infoicon = self.sr.headerIcon
        if infoicon:
            infoicon.Hide()

    def GetMenuMoreOptions(self):
        menuData = super(InfoWindow, self).GetMenuMoreOptions()
        menuData += self.GetActionMenu(self.itemID, self.typeID, self.rec)
        return menuData

    def UpdateDescriptionCaptionAndSubCaption(self):
        capt = None
        if self.itemID in cfg.evelocations.data:
            capt = cfg.evelocations.Get(self.itemID).name
        if not capt:
            capt = evetypes.GetName(self.typeID)
        desc = evetypes.GetDescription(self.typeID)
        subCapt = ''
        if self.IsType(TYPE_LANDMARK):
            landmark = sm.GetService('map').GetLandmark(self.itemID * -1)
            capt = maputils.GetNameFromMapCache(landmark.landmarkNameID, 'landmark')
            desc = maputils.GetNameFromMapCache(landmark.descriptionID, 'landmark')
            subCapt = ''
        elif self.IsType(TYPE_RANK) and self.abstractinfo is not None:
            capt = localization.GetByLabel('UI/FactionWarfare/Rank')
            rankLabel, rankDescription = sm.GetService('facwar').GetRankLabel(self.abstractinfo.warFactionID, self.abstractinfo.currentRank)
            desc = rankDescription
            subCapt = rankLabel
        elif self.IsType(TYPE_MEDAL, TYPE_RIBBON) and self.abstractinfo is not None:
            info = sm.GetService('medals').GetMedalDetails(self.itemID).info[0]
            desc = info.description
            subCapt = info.title
        elif self.IsType(TYPE_CERTIFICATE) and self.abstractinfo is not None:
            capt, _, desc = sm.GetService('certificates').GetCertificateLabel(self.abstractinfo.certificateID)
            subCapt = ''
        elif self.IsType(TYPE_SKINMATERIAL):
            material = sm.GetService('cosmeticsSvc').GetStaticMaterialByID(self.itemID)
            capt = material.name
        elif self.IsType(TYPE_SKINLICENSE):
            if not desc.strip():
                desc = localization.GetByLabel('UI/Skins/SkinItemDescription')
        elif self.IsType(TYPE_SKILL):
            subCapt = '&gt; %s' % evetypes.GetGroupName(self.typeID)
        elif self.IsType(TYPE_CHARACTER) and self.itemID is not None:
            if sm.GetService('agents').IsAgent(self.itemID):
                agent = sm.GetService('agents').GetAgentByID(self.itemID)
                level = agent.level
                bloodlineID = agent.bloodlineID
                capt = GetAgentNameAndLevel(self.itemID, level)
                desc = get_bloodline_description(bloodlineID)
            else:
                info = sm.RemoteSvc('charMgr').GetPublicInfo3(self.itemID)
                if info:
                    bloodlineID = info[0].bloodlineID
                    capt = cfg.eveowners.Get(self.itemID).name
                    desc = get_bloodline_description(bloodlineID)
        elif self.IsType(TYPE_CORPORATION) and self.itemID is not None:
            if self.corpinfo is None:
                self.corpinfo = sm.RemoteSvc('corpmgr').GetPublicInfo(self.itemID)
                self.corpinfo.shares = sm.GetService('corp').GetCorporation(self.itemID).shares
            if IsNPCCorporation(self.corpinfo.corporationID):
                desc = get_npc_corporation_description(self.corpinfo.corporationID)
            else:
                desc = self.corpinfo.description
            if eveIcon.CheckCorpID(self.itemID):
                capt = ''
            else:
                capt = cfg.eveowners.Get(self.itemID).name
                if self.corpinfo.deleted:
                    capt = localization.GetByLabel('UI/InfoWindow/ClosedCorpOrAllianceCaption', corpOrAllianceName=cfg.eveowners.Get(self.itemID).name)
        elif self.IsType(TYPE_ALLIANCE) and self.itemID is not None:
            if self.allianceinfo is None:
                self.allianceinfo = sm.GetService('alliance').GetAlliancePublicInfo(self.itemID)
            capt = cfg.eveowners.Get(self.itemID).name
            desc = self.allianceinfo.description
            if self.allianceinfo.deleted:
                capt = localization.GetByLabel('UI/InfoWindow/ClosedCorpOrAllianceCaption', corpOrAllianceName=cfg.eveowners.Get(self.itemID).name)
        elif self.IsType(TYPE_STATION):
            if self.itemID is not None:
                if self.stationinfo is None:
                    self.stationinfo = sm.GetService('map').GetStation(self.itemID)
                if self.stationinfo is None:
                    capt = sm.GetService('ui').GetStationName(self.itemID)
                    desc = evetypes.GetDescription(self.typeID) or evetypes.GetName(self.typeID)
                else:
                    capt = self.stationinfo.stationName
                    if self.itemID < 61000000 and self.stationinfo.stationTypeID not in (12294, 12295, 12242):
                        desc = get_station_operation_description(self.stationinfo.operationID)
                    else:
                        desc = self.stationinfo.description
            else:
                desc = evetypes.GetDescription(self.typeID) or evetypes.GetName(self.typeID)
        elif self.IsType(TYPE_STRUCTURE):
            if self.itemID:
                structureInfo = sm.GetService('structureDirectory').GetStructureInfo(self.itemID)
                if structureInfo:
                    if not structureInfo.inSpace:
                        capt = '%s %s' % (localization.GetByLabel('UI/Structures/OutOfCommission'), capt)
                    capt += ' (%s)' % cfg.eveowners.Get(structureInfo.ownerID).name
                    subCapt = evetypes.GetGroupName(self.typeID) + ' - ' + evetypes.GetName(self.typeID)
        elif self.IsType(TYPE_WORMHOLE):
            slimItem = sm.StartService('michelle').GetItem(self.itemID)
            if slimItem:
                wormholeClasses = {0: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 1: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 2: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 3: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 4: 'UI/Wormholes/Classes/DangerousUnknownSpaceDescription',
                 5: 'UI/Wormholes/Classes/DangerousUnknownSpaceDescription',
                 6: 'UI/Wormholes/Classes/DeadlyUnknownSpaceDescription',
                 7: 'UI/Wormholes/Classes/HighSecuritySpaceDescription',
                 8: 'UI/Wormholes/Classes/LowSecuritySpaceDescription',
                 9: 'UI/Wormholes/Classes/NullSecuritySpaceDescription',
                 12: 'UI/Wormholes/Classes/TheraDescription',
                 13: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 14: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 15: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 16: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 17: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 18: 'UI/Wormholes/Classes/UnknownSpaceDescription',
                 25: 'UI/Wormholes/Classes/TriglavianSpaceDescription'}
                wormholeClassLabelName = wormholeClasses.get(slimItem.otherSolarSystemClass)
                wClass = localization.GetByLabel(wormholeClassLabelName)
                if slimItem.wormholeAge >= 2:
                    wAge = localization.GetByLabel('UI/InfoWindow/WormholeAgeReachingTheEnd')
                elif slimItem.wormholeAge >= 1:
                    wAge = localization.GetByLabel('UI/InfoWindow/WormholeAgeStartedDecaying')
                elif slimItem.wormholeAge >= 0:
                    wAge = localization.GetByLabel('UI/InfoWindow/WormholeAgeNew')
                else:
                    wAge = ''
                if slimItem.wormholeSize < 0.5:
                    remaining = localization.GetByLabel('UI/InfoWindow/WormholeSizeStabilityCriticallyDisrupted')
                elif slimItem.wormholeSize < 1:
                    remaining = localization.GetByLabel('UI/InfoWindow/WormholeSizeStabilityReduced')
                else:
                    remaining = localization.GetByLabel('UI/InfoWindow/WormholeSizeNotDisrupted')
                if slimItem.maxShipJumpMass == const.WH_SLIM_MAX_SHIP_MASS_SMALL:
                    maxSize = localization.GetByLabel('UI/InfoWindow/WormholeMaxShipMassSmall')
                elif slimItem.maxShipJumpMass == const.WH_SLIM_MAX_SHIP_MASS_MEDIUM:
                    maxSize = localization.GetByLabel('UI/InfoWindow/WormholeMaxShipMassMedium')
                elif slimItem.maxShipJumpMass == const.WH_SLIM_MAX_SHIP_MASS_LARGE:
                    maxSize = localization.GetByLabel('UI/InfoWindow/WormholeMaxShipMassLarge')
                elif slimItem.maxShipJumpMass == const.WH_SLIM_MAX_SHIP_MASS_VERYLARGE:
                    maxSize = localization.GetByLabel('UI/InfoWindow/WormholeMaxShipMassVeryLarge')
                else:
                    maxSize = ''
                desc = evetypes.GetDescription(self.typeID) + '<br>'
                desc = localization.GetByLabel('UI/InfoWindow/WormholeDescription', wormholeName=desc, wormholeClass=wClass, wormholeAge=wAge, remaining=remaining, maxSize=maxSize)
                capt = evetypes.GetName(self.typeID)
        elif self.IsType(TYPE_CELESTIAL, TYPE_STARGATE):
            desc = ''
            if evetypes.GetGroupID(self.typeID) in (const.groupSolarSystem, const.groupConstellation, const.groupRegion):
                locationTrace = self.GetLocationTrace(self.itemID, [])
                subCapt = evetypes.GetName(self.typeID) + '<br><br>' + locationTrace
                if self.itemID and evetypes.GetGroupID(self.typeID) == const.groupSolarSystem and SystemCanHaveInterference(self.itemID):
                    systemInterferenceSvc = sm.GetService('solarsystemInterferenceSvc')
                    interferenceBand = systemInterferenceSvc.GetSolarSystemInterferenceBand(self.itemID)
                    interferenceBandLabel = GetInterferenceBandLabel(interferenceBand)
                    interferenceLine = localization.GetByLabel('UI/InfoWindow/interferenceLevelInLocationTrace', interference=interferenceBandLabel)
                    subCapt = subCapt + '<br>' + interferenceLine
                if evetypes.GetGroupID(self.typeID) == const.groupRegion:
                    desc = self.GetGeographyDescription(cfg.mapRegionCache[self.itemID])
                elif evetypes.GetGroupID(self.typeID) == const.groupConstellation:
                    desc = self.GetGeographyDescription(cfg.mapConstellationCache[self.itemID])
                elif evetypes.GetGroupID(self.typeID) == const.groupSolarSystem:
                    desc = self.GetGeographyDescription(cfg.mapSolarSystemContentCache[self.itemID])
            if not desc:
                desc = evetypes.GetDescription(self.typeID) or evetypes.GetName(self.typeID)
            desc = desc + '<br>'
            capt = evetypes.GetName(self.typeID)
            isBeacon = evetypes.GetGroupID(self.typeID) == const.groupBeacon
            if isBeacon:
                beacon = sm.GetService('michelle').GetItem(self.itemID)
                if beacon and hasattr(beacon, 'dunDescriptionID') and beacon.dunDescriptionID:
                    desc = localization.GetByMessageID(beacon.dunDescriptionID)
            locationname = None
            if self.itemID is not None:
                try:
                    if self.itemID < const.minPlayerItem or self.rec is not None and self.rec.singleton or isBeacon:
                        locationname = cfg.evelocations.Get(self.itemID).name
                    elif self.groupID == const.groupBiomass:
                        locationname = GetCorpseName(self.itemID)
                    else:
                        locationname = evetypes.GetName(self.typeID)
                except KeyError:
                    locationname = evetypes.GetName(self.typeID)
                    sys.exc_clear()

            if locationname and locationname[0] != '@':
                capt = locationname
        elif self.IsType(TYPE_ASTEROID):
            capt = evetypes.GetName(self.typeID)
        elif self.IsType(TYPE_PLANET):
            subCapt = evetypes.GetName(self.typeID)
        elif self.IsType(TYPE_FACTION):
            capt = ''
            desc = get_faction_description(self.itemID)
        elif self.IsType(TYPE_CUSTOMSOFFICE):
            capt = evetypes.GetName(self.typeID)
            bp = sm.GetService('michelle').GetBallpark()
            slimItem = None
            if bp is not None:
                slimItem = bp.GetInvItem(self.itemID)
            if slimItem:
                capt = uix.GetSlimItemName(slimItem)
        self.data[TAB_DESCRIPTION]['text'] = desc or capt or ''
        self.captionText = capt or ''
        self.subCaptionText = subCapt or ''

    def GetLocationTrace(self, itemID, trace, recursive = 0):
        parentID = sm.GetService('map').GetParent(itemID)
        if parentID != const.locationUniverse:
            parentItem = sm.GetService('map').GetItem(parentID)
            if parentItem:
                locationLink = GetShowInfoLink(parentItem.typeID, parentItem.itemName, parentID)
                label = localization.GetByLabel('UI/InfoWindow/LocationTrace', locationType=parentItem.typeID, locationName=locationLink)
                trace += self.GetLocationTrace(parentID, [label], 1)
        if recursive:
            return trace
        else:
            trace.reverse()
            item = sm.GetService('map').GetItem(itemID)
            if item and self.groupID == const.groupSolarSystem and item.security is not None:
                sec = sm.GetService('map').GetSecurityStatus(itemID)
                label = localization.GetByLabel('UI/InfoWindow/SecurityLevelInLocationTrace', secLevel=location.security_status(sec))
                securityModifierIconText = sm.GetService('securitySvc').get_security_modifier_icon_text(itemID)
                label += securityModifierIconText
                trace += [label]
            return '<br>'.join(trace)

    def GetGeographyDescription(self, theGeography):
        if hasattr(theGeography, 'descriptionID'):
            geographyDescription = localization.GetByMessageID(theGeography.descriptionID)
            if geographyDescription:
                return geographyDescription

    def OnPreviewClick(self, obj, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        sm.GetService('preview').PreviewType(obj.typeID, itemID=getattr(obj, 'itemID', None))

    def PreviewShip(self, skin_state):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        sm.GetService('preview').PreviewType(self.typeID, skin_state=skin_state)

    def OpenPortraitWnd(self, charID, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        PortraitWindow.CloseIfOpen()
        PortraitWindow.Open(charID=charID)

    def OpenEntityWnd(self, entityID, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        EntityWindow.CloseIfOpen()
        EntityWindow.Open(entityID=entityID)

    def GetIconActionMenu(self, itemID, typeID, rec):
        return self.GetActionMenu(itemID, typeID, rec)

    def GetActionMenu(self, itemID, typeID, invItem):
        if typeID == const.typeCertificate:
            return None
        m = GetMenuService().GetMenuFromItemIDTypeID(itemID, typeID, invItem=invItem, includeMarketDetails=True).filter([localization.GetByLabel('UI/Commands/ShowInfo'),
         'UI/Commands/ShowInfo',
         'UI/Fitting/FittingWindow/SimulateShipFitting',
         'UI/Fitting/FittingWindow/SimulateStructure',
         'UI/Fitting/FittingWindow/SimulateShip'])
        if self.IsType(TYPE_CHARACTER, TYPE_CORPORATION):
            if not idCheckers.IsNPC(itemID):
                m.append((MenuLabel('UI/InfoWindow/ShowContracts'), self.ShowContracts, (itemID,)))
        if self.IsType(TYPE_CHARACTER) and not idCheckers.IsNPC(itemID) and not int(sm.GetService('machoNet').GetGlobalConfig().get('hideReportBot', 0)):
            m.append((MenuLabel('UI/InfoWindow/ReportBot'), self.ReportBot, (itemID,)))
        if self._IsSimulatable():
            labelPath = GetSimulateLabelPath(itemID, typeID, invItem)
            if itemID == session.shipid:
                m += [(MenuLabel(labelPath), sm.GetService('ghostFittingSvc').LoadCurrentShipExternal, ())]
            elif invItem:
                m += [(MenuLabel(labelPath), GhostFitShip, (invItem,))]
            else:
                m += [(MenuLabel(labelPath), openFunctions.SimulateFitting, (utillib.KeyVal(shipTypeID=typeID, fitData=[]),))]
        return m

    def _IsSimulatable(self):
        return self.typeID in evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_IS_PLAYER_PILOTABLE)

    def ReportBot(self, itemID, *args):
        if eve.Message('ConfirmReportBot', {'name': cfg.eveowners.Get(itemID).name}, uiconst.YESNO) != uiconst.ID_YES:
            return
        if itemID == session.charid:
            raise UserError('ReportBotCannotReportYourself')
        sm.RemoteSvc('userSvc').ReportBot(itemID)
        eve.Message('BotReported', {'name': cfg.eveowners.Get(itemID).name})

    def ShowContracts(self, itemID, *args):
        sm.GetService('contracts').Show(lookup=cfg.eveowners.Get(itemID).name)

    def ShowRelationshipIcon(self, itemID, corpid, allianceid):
        flag, flagHintPath = GetRelationShipFlag(itemID, corpid, allianceid)
        if not flag:
            return
        if itemID:
            pos = (4, 4, 14, 14)
            iconPos = (0, 0, 16, 16)
        else:
            pos = (4, 4, 12, 12)
            iconPos = (0, 0, 12, 12)
        icon = FlagIconWithState(parent=self.mainicon, pos=pos, state=uiconst.UI_NORMAL, align=uiconst.BOTTOMLEFT)
        flagInfo = sm.GetService('stateSvc').GetStatePropsColorAndBlink(flag)
        icon.ModifyIcon(flagInfo=flagInfo, showHint=True)
        if flagHintPath:
            icon.hint += '<br>%s' % localization.GetByLabel(flagHintPath)
            self.mainicon.state = uiconst.UI_PICKCHILDREN
        icon.ChangeIconPos(*iconPos)
        uicore.animations.FadeTo(icon.flagBackground, startVal=0.0, endVal=0.6, duration=0.3, loops=1)

    def GetCorpLogo(self, corpID, parent = None):
        logo = eveIcon.GetLogoIcon(itemID=corpID, parent=parent, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/InfoWindow/ClickForCorpInfo'), align=uiconst.TOLEFT, pos=(0, 0, 64, 64), ignoreSize=True)
        parent.height = 64
        if not idCheckers.IsNPC(corpID):
            try:
                Frame(parent=logo, color=(1.0, 1.0, 1.0, 0.1))
            except:
                pass

        logo.OnClick = (self.ReconstructInfoWindow, const.typeCorporation, corpID)
        return logo

    def Wanted(self, bounty, isChar, showSprite, isNPC = False, ownerIDs = None, hint = None):
        bountyUtilMeny = None
        if not isNPC:
            if globalConfig.IsPlayerBountyHidden(sm.GetService('machoNet')):
                return
            self.bountyOwnerIDs = (self.itemID,) if ownerIDs is None else ownerIDs
            bountyUtilMeny = PlaceBountyUtilMenu(parent=self.therestcontainer, ownerID=self.itemID, bountyOwnerIDs=self.bountyOwnerIDs)
        if showSprite:
            if isChar or isNPC:
                width = 128
                height = 34
                top = 2
            else:
                width = 64
                height = 17
                top = 1
            Sprite(name='wanted', parent=self.mainicon, idx=0, texturePath='res:/UI/Texture/wanted.png', width=width, height=height, align=uiconst.CENTERBOTTOM, hint=localization.GetByLabel('UI/InfoWindow/BountyHint', amount=FmtISK(bounty, False)), top=top)
        bountyCont = ContainerAutoSize(parent=self.therestcontainer, align=uiconst.TOTOP, padRight=bountyUtilMeny.width if bountyUtilMeny else 0)
        self.bountyLabelInfo = eveLabel.EveLabelSmall(text='', parent=bountyCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.bountyLabelInfo.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=FmtISK(bounty, False))
        if hint is not None:
            self.bountyLabelInfo.hint = hint

    def OnBountyPlaced(self, ownerID):
        if ownerID == self.itemID:
            bounty = self.GetBountyAmount(*self.bountyOwnerIDs)
            self.bountyLabelInfo.text = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=FmtISK(bounty, False))

    def OnSkillsChanged(self, skillInfoChange):
        if not self.IsType(TYPE_SKILL) or session.charid is None:
            return
        typeID = self.typeID
        if typeID in skillInfoChange:
            self.ReconstructInfoWindow(self.typeID, self.itemID)

    def GetBountyAmount(self, *ownerIDs):
        bountyAmount = sm.GetService('bountySvc').GetBounty(*ownerIDs)
        return bountyAmount

    def GetBountyAmounts(self, *ownerIDs):
        bountyAmounts = sm.GetService('bountySvc').GetBounties(*ownerIDs)
        return bountyAmounts

    def ResetWindowData(self, tabs = None):
        self.data = {}
        self.dynamicTabs = []
        self.data[DATA_BUTTONS] = []
        self._ParseTabs(INFO_TABS)

    def GetDynamicTabLoadMethod(self, tabID):
        if tabID == TAB_ALLIANCEHISTORY:
            return self.LoadAllianceHistory
        if tabID == TAB_EMPLOYMENTHISTORY:
            return self.LoadEmploymentHistory
        if tabID == TAB_DECORATIONS:
            return self.LoadDecorations
        if tabID == TAB_WARHISTORY:
            return self.LoadWarHistory
        if tabID == TAB_SCHEMATICS:
            return self.LoadProcessPinSchematics
        if tabID == TAB_PLANETCONTROL:
            return self.LoadPlanetControlInfo
        if tabID == TAB_FUELREQ:
            return self.LoadFuelRequirements
        if tabID == TAB_UPGRADEMATERIALREQ:
            return self.LoadUpgradeMaterialRequirements
        if tabID == TAB_MATERIALREQ:
            return self.LoadMaterialRequirements
        if tabID == TAB_MEMBERS:
            return self.LoadAllianceMembers

    def _ParseTabs(self, tabs):
        for listtype, subtabs, tabName in tabs:
            self.data[listtype] = {'name': localization.GetByLabel(tabName),
             'items': [],
             'subtabs': subtabs,
             'inited': 0,
             'headers': []}
            if subtabs:
                self._ParseTabs(subtabs)

    def SetActive(self, *args):
        Window.SetActive(self, *args)
        sm.GetService('info').OnActivateWnd(self)

    def Load(self, passedargs, *args):
        if type(passedargs) == types.TupleType:
            if len(passedargs) == 2:
                listtype, func = passedargs
                if func:
                    func()
                elif listtype in self.data:
                    self.scroll.Load(contentList=self.data[listtype]['items'], headers=self.data[listtype]['headers'])
            elif len(passedargs) == 3:
                listtype, func, string = passedargs
                if listtype == 'readOnlyText':
                    self.descedit.window = self
                    self.descedit.SetValue(string, scrolltotop=1)
                elif listtype == 'selectSubtab':
                    listtype, string, subtabgroup = passedargs
                    subtabgroup.AutoSelect()
        else:
            self.scroll.Clear()

    def LoadEmploymentHistory(self):
        self.LoadGeneric(TAB_EMPLOYMENTHISTORY, sm.GetService('info').GetEmploymentHistorySubContent)

    def LoadAllianceHistory(self):
        self.LoadGeneric(TAB_ALLIANCEHISTORY, sm.GetService('info').GetAllianceHistorySubContent)

    def LoadWarHistory(self):
        warFactionID = getattr(self, 'warFactionID', None)
        warHistoryFunc = lambda itemID: sm.GetService('info').GetWarHistorySubContent(itemID, warFactionID)
        self.LoadGeneric(TAB_WARHISTORY, warHistoryFunc, noContentHint=localization.GetByLabel('UI/Common/NothingFound'))

    def LoadAllianceMembers(self):
        self.LoadGeneric(TAB_MEMBERS, sm.GetService('info').GetAllianceMembersSubContent)

    def LoadUpgradeMaterialRequirements(self):
        if not self.data[TAB_UPGRADEMATERIALREQ]['inited']:
            t = sm.GetService('godma').GetType(self.typeID)
            menuFunc = lambda itemID = t.constructionType: GetMenuService().GetMenuFromItemIDTypeID(None, itemID, includeMarketDetails=True)
            upgradesIntoEntry = GetFromClass(LabelTextSides, {'line': 1,
             'label': localization.GetByLabel('UI/InfoWindow/UpgradesInto'),
             'text': evetypes.GetName(t.constructionType),
             'typeID': t.constructionType,
             'GetMenu': menuFunc})
            self.data[TAB_UPGRADEMATERIALREQ]['items'].append(upgradesIntoEntry)
            self.data[TAB_UPGRADEMATERIALREQ]['items'].append(GetFromClass(DividerEntry))
            materials = get_type_materials_by_id(t.constructionType)
            commands = []
            for material in materials:
                resourceTypeID = material.materialTypeID
                quantity = material.quantity
                menuFunc = lambda itemID = resourceTypeID: GetMenuService().GetMenuFromItemIDTypeID(None, itemID, includeMarketDetails=True)
                text = localization.formatters.FormatNumeric(quantity, useGrouping=True, decimalPlaces=0)
                le = GetFromClass(LabelTextSides, {'line': 1,
                 'label': evetypes.GetName(resourceTypeID),
                 'text': text,
                 'iconID': evetypes.GetIconID(resourceTypeID),
                 'typeID': resourceTypeID,
                 'GetMenu': menuFunc})
                commands.append((resourceTypeID, quantity))
                self.data[TAB_UPGRADEMATERIALREQ]['items'].append(le)

            if eve.session.role & ROLE_GML == ROLE_GML:
                self.data[TAB_UPGRADEMATERIALREQ]['items'].append(GetFromClass(DividerEntry))
                self.data[TAB_UPGRADEMATERIALREQ]['items'].append(GetFromClass(ButtonEntry, {'label': 'GML: Create in cargo',
                 'caption': 'Create',
                 'OnClick': sm.GetService('info').DoCreateMaterials,
                 'args': (commands, '', 1)}))
            self.data[TAB_UPGRADEMATERIALREQ]['inited'] = 1
        self.scroll.Load(fixedEntryHeight=27, contentList=self.data[TAB_UPGRADEMATERIALREQ]['items'])

    def LoadGeneric(self, label, getSubContent, noContentHint = ''):
        if not self.data[label]['inited']:
            self.data[label]['items'].extend(getSubContent(self.itemID))
            self.data[label]['inited'] = True
        self.scroll.Load(fixedEntryHeight=27, contentList=self.data[label]['items'], noContentHint=noContentHint)

    def LoadGenericType(self, label, getSubContent):
        if not self.data[label]['inited']:
            self.data[label]['items'].extend(getSubContent(self.typeID))
            self.data[label]['inited'] = True
        self.scroll.Load(fixedEntryHeight=27, contentList=self.data[label]['items'])

    def LoadFuelRequirements(self):
        if not self.data[TAB_FUELREQ]['inited']:
            purposeDict = [(1, localization.GetByLabel('UI/InfoWindow/ControlTowerOnline')),
             (2, localization.GetByLabel('UI/InfoWindow/ControlTowerPower')),
             (3, localization.GetByLabel('UI/InfoWindow/ControlTowerCPU')),
             (4, localization.GetByLabel('UI/InfoWindow/ControlTowerReinforced'))]
            cycle = sm.GetService('godma').GetType(self.typeID).posControlTowerPeriod
            commands = []
            for purposeID, caption in purposeDict:
                self.data[TAB_FUELREQ]['items'].append(GetFromClass(Header, {'label': caption}))
                resources = get_resources_for_tower_by_purpose(self.typeID, purposeID)
                if resources:
                    for row in resources:
                        extraList = []
                        if row.factionID is not None:
                            label = localization.GetByLabel('UI/InfoWindow/FactionSpace', factionName=cfg.eveowners.Get(row.factionID).name)
                            extraList.append(label)
                        if row.minSecurityLevel is not None:
                            label = localization.GetByLabel('UI/InfoWindow/SecurityLevel', secLevel=row.minSecurityLevel)
                            extraList.append(label)
                        if len(extraList):
                            t = localization.formatters.FormatGenericList(extraList)
                            extraText = localization.GetByLabel('UI/InfoWindow/IfExtraText', extraText=t)
                        else:
                            extraText = ''
                        if cycle / 3600000L == 1:
                            text = localization.GetByLabel('UI/InfoWindow/FuelRequirementPerHour', qty=row.quantity, extraText=extraText)
                        else:
                            numHours = cycle / 3600000L
                            text = localization.GetByLabel('UI/InfoWindow/FuelRequirement', qty=row.quantity, numHours=numHours, extraText=extraText)
                        menuFunc = lambda itemID = row.resourceTypeID: StartMenuService().GetMenuFromItemIDTypeID(None, itemID, includeMarketDetails=True).filter(['UI/Commands/ShowInfo'])
                        le = GetFromClass(LabelTextSides, {'line': 1,
                         'label': evetypes.GetName(row.resourceTypeID),
                         'text': text,
                         'iconID': evetypes.GetIconID(row.resourceTypeID),
                         'typeID': row.resourceTypeID,
                         'GetMenu': menuFunc})
                        commands.append((row.resourceTypeID, row.quantity))
                        self.data[TAB_FUELREQ]['items'].append(le)

            if eve.session.role & ROLE_GML == ROLE_GML:
                self.data[TAB_FUELREQ]['items'].append(GetFromClass(DividerEntry))
                self.data[TAB_FUELREQ]['items'].append(GetFromClass(ButtonEntry, {'label': 'GML: Create in cargo',
                 'caption': 'Create',
                 'OnClick': sm.GetService('info').DoCreateMaterials,
                 'args': (commands, '', 10)}))
            self.data[TAB_FUELREQ]['inited'] = 1
        self.scroll.Load(fixedEntryHeight=27, contentList=self.data[TAB_FUELREQ]['items'])

    def LoadMaterialRequirements(self):
        if not self.data[TAB_MATERIALREQ]['inited']:
            stationTypeID = sm.GetService('godma').GetType(self.typeID).stationTypeID
            materials = get_type_materials_by_id(stationTypeID)
            commands = []
            for material in materials:
                materialTypeID = material.materialTypeID
                quantity = material.quantity
                commands.append((materialTypeID, quantity))
                text = localization.GetByLabel('UI/Common/NumUnits', numItems=quantity)
                le = GetFromClass(LabelTextSides, {'line': 1,
                 'label': evetypes.GetName(materialTypeID),
                 'text': text,
                 'iconID': evetypes.GetIconID(materialTypeID),
                 'typeID': materialTypeID})
                self.data[TAB_MATERIALREQ]['items'].append(le)

            self.data[TAB_MATERIALREQ]['inited'] = 1
            if eve.session.role & ROLE_GML == ROLE_GML:
                self.data[TAB_MATERIALREQ]['items'].append(GetFromClass(DividerEntry))
                self.data[TAB_MATERIALREQ]['items'].append(GetFromClass(ButtonEntry, {'label': 'GML: Create in cargo',
                 'caption': 'Create',
                 'OnClick': sm.GetService('info').DoCreateMaterials,
                 'args': (commands, '', 1)}))
        self.scroll.Load(fixedEntryHeight=27, contentList=self.data[TAB_MATERIALREQ]['items'])

    def LoadDecorations(self):
        self.scroll.Load(contentList=[], noContentHint=localization.GetByLabel('UI/Common/NoPublicDecorations'))

    def LoadProcessPinSchematics(self):
        if not self.data[TAB_SCHEMATICS]['inited']:
            schematicItems = []
            for schematicID in get_schematic_ids_for_pin_type_id(self.typeID):
                typeID = planetCommon.GetSchematicOutput(schematicID)
                entry = GetFromClass(PlanetSchematicItemEntry, {'typeID': typeID,
                 'label': evetypes.GetName(typeID),
                 'getIcon': True})
                schematicItems.append(entry)

            self.data[TAB_SCHEMATICS]['items'] = schematicItems
            self.data[TAB_SCHEMATICS]['inited'] = 1
        self.scroll.Load(contentList=self.data[TAB_SCHEMATICS]['items'])

    def LoadPlanetControlInfo(self):
        controlLabel = TAB_PLANETCONTROL
        if not self.data[controlLabel]['inited']:
            planetID = self.itemID
            lines = []
            bp = sm.GetService('michelle').GetBallpark()
            planetItem = bp.GetInvItem(planetID) if bp is not None else None
            controller = planetItem.ownerID if planetItem is not None else None
            if controller is not None:
                pass
            requirementsText = localization.GetByLabel('UI/InfoWindow/PlanetControlRequirementHint')
            lines.append(GetFromClass(Generic, {'label': requirementsText,
             'maxLines': None}))
            self.data[controlLabel]['items'] = lines
            self.data[controlLabel]['inited'] = 1
        self.scroll.Load(contentList=self.data[controlLabel]['items'], noContentHint=localization.GetByLabel('UI/InfoWindow/PlanetNotContested'))

    def LoadMoreTooltipPanel(self, tooltipPanel, owner):
        if self.IsType(TYPE_SKILL) and session.charid:
            from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltip
            LoadSkillEntryTooltip(tooltipPanel, self.typeID)


class BadArgs(RuntimeError):

    def __init__(self, msgID, kwargs = None):
        RuntimeError.__init__(self, msgID, kwargs or {})


class EntityWindow(Window):
    __guid__ = 'form.EntityWindow'
    default_windowID = 'EntityWindow'
    default_fixedWidth = 250
    default_fixedHeight = 250
    default_isMinimizable = False
    default_isOverlayable = False
    default_isLockable = False

    def ApplyAttributes(self, attributes):
        super(EntityWindow, self).ApplyAttributes(attributes)
        entityID = attributes.entityID
        self.picParent = Container(name='picpar', parent=self.sr.main, align=uiconst.TOALL, padding=0)
        self.SetCaption(cfg.eveowners.Get(entityID).name)
        eveIcon.GetLogoIcon(entityID, parent=self.picParent, acceptNone=False, align=uiconst.CENTER, height=128, width=128, state=uiconst.UI_NORMAL)


class AttributeRowEntry(Generic):

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.sr.label.display = False
        self.rowLabel = eveLabel.EveLabelMedium(parent=self, text='', align=uiconst.TOTOP, padLeft=8, padTop=3)
        self.spriteCont = Container(parent=self, name='spriteCont', align=uiconst.TOLEFT, width=32)
        self.sprite = Sprite(parent=self.spriteCont, name='rowSprite', pos=(0, 0, 32, 32), align=uiconst.CENTER)
        self.damageContainer = AttributeValueRowContainer(parent=self, padding=(2, 2, 0, 2), align=uiconst.TOALL, height=0, doWidthAdjustments=True, loadOnStartup=False)

    def Load(self, node):
        node.selectable = False
        itemID = node.itemID
        labelText = localization.GetByLabel(node.labelPath) if node.labelPath else ''
        self.rowLabel.text = labelText
        modifiedAttributesDict = node.modifiedAttributesDict
        self.damageContainer.Load(node.attributeValues, mouseExitFunc=self.OnMouseExit, onClickFunc=node.OnClickAttr, modifiedAttributesDict=modifiedAttributesDict, itemID=itemID)
        if node.texturePath:
            self.sprite.LoadTexture(node.texturePath)
        else:
            self.spriteCont.display = False

    def GetHeight(self, *args):
        node, width = args
        node.height = 50
        return node.height

    def OnMouseExit(self, *args):
        if uicore.uilib.mouseOver.IsUnder(self):
            return
        Generic.OnMouseExit(self, *args)

    def GetMenu(self):
        return [(MenuLabel('UI/Common/Copy'), self.CopyText)]

    def CopyText(self):
        text = self.GetCopyData(self.sr.node)
        blue.pyos.SetClipboardData(text)

    @classmethod
    def GetCopyData(cls, node):
        attributeTextList = []
        for attributeID, value in node.attributeValues:
            displayName = dogma.data.get_attribute_display_name(attributeID)
            text = '%s\t%s' % (displayName, value)
            attributeTextList.append(text)

        return '\n'.join(attributeTextList)
