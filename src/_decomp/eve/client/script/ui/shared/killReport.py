#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\killReport.py
from carbonui.primitives.frame import Frame
from collections import defaultdict
import blue
import carbonui.control.button
import eveformat.client
import evelink.client
import evetypes
import inventorycommon.const as inventoryConst
import localization
import trinity
import uthread
import utillib
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.util import bunch
from eve.client.script.ui.control import eveIcon, eveLabel, eveLoadingWheel, eveScroll
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.services.menuSvcExtras.openFunctions import SimulateFitting
from eve.client.script.ui.shared import killReportUtil
from eve.client.script.ui.util import uix
from eve.common.lib.appConst import defaultPadding, singletonBlueprintCopy
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.idCheckers import IsVoidSpaceSystem
from eve.common.script.util import eveCommonUtils
from eve.common.script.util.esiUtils import CopyESIKillmailUrlToClipboard
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem, IsFaction
from eveservices.menu import GetMenuService
from inventorycommon.util import IsSubsystemFlag
from menu import MenuLabel
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty

class KillReportWnd(Window):
    __guid__ = 'form.KillReportWnd'
    __notifyevents__ = []
    default_windowID = 'KillReportWnd'
    default_width = 650
    default_height = 640
    default_minSize = (default_width, default_height)
    default_iconNum = 'res:/UI/Texture/WindowICons/killreport.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        killmail = attributes.Get('killmail', None)
        self.windowID = attributes.windowID
        self.rawKillmail = None
        self.SetCaption(localization.GetByLabel('UI/Corporations/Wars/Killmails/KillReport'))
        self.ConstructLayout()
        self.LoadInfo(killmail)

    def ConstructLayout(self):
        topCont = Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=138, padding=defaultPadding)
        Line(parent=topCont, align=uiconst.TOBOTTOM)
        topLeftCont = Container(name='topLeftCont', parent=topCont, align=uiconst.TOLEFT, width=260, padLeft=defaultPadding)
        topRightCont = Container(name='topRightCont', parent=topCont, align=uiconst.TOALL)
        self.guyCont = Container(name='guyCont', parent=topLeftCont, align=uiconst.TOLEFT, width=128)
        self.shipCont = Container(name='shipCont', parent=topLeftCont, align=uiconst.TOLEFT, width=128)
        self.infoCont = Container(name='infoCont', parent=topRightCont, align=uiconst.TOALL, padLeft=6, padRight=4, clipChildren=True)
        victimCont = Container(name='victimCont', parent=self.infoCont, align=uiconst.TOTOP, height=68)
        victimNameCont = Container(name='victimNameCont', parent=victimCont, align=uiconst.TOTOP, height=24, clipChildren=True)
        victimCorpCont = Container(name='victimCorpCont', parent=victimCont, align=uiconst.TOALL)
        self.victimCorpLogoCont = Container(name='victimCorpLogoCont', parent=victimCorpCont, align=uiconst.TOLEFT, width=32)
        self.victimAllianceLogoCont = Container(name='victimAllianceLogoCont', parent=victimCorpCont, align=uiconst.TOLEFT, width=32)
        victimCorpTextCont = Container(name='victimCorpTextCont', parent=victimCorpCont, align=uiconst.TOALL, padLeft=defaultPadding)
        shipCont = Container(name='damageCont', parent=self.infoCont, align=uiconst.TOTOP, height=32)
        dateCont = Container(name='dateCont', parent=self.infoCont, align=uiconst.TOALL)
        self.victimName = eveLabel.EveCaptionSmall(text='', parent=victimNameCont, name='victimName', state=uiconst.UI_NORMAL)
        self.victimCorpName = eveLabel.EveLabelMedium(text='', parent=victimCorpTextCont, name='victimCorpName', align=uiconst.TOTOP, state=uiconst.UI_NORMAL, top=defaultPadding)
        self.victimAllianceName = eveLabel.EveLabelMedium(text='', parent=victimCorpTextCont, name='victimAllianceName', align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.shipName = eveLabel.EveLabelMedium(text='', parent=shipCont, name='shipName', state=uiconst.UI_NORMAL, autoFadeSides=True)
        self.killDate = eveLabel.EveLabelMedium(text='', parent=dateCont, name='killDate', autoFadeSides=True)
        self.locationName = eveLabel.EveLabelMedium(text='', parent=dateCont, name='locationName', top=14, state=uiconst.UI_NORMAL, autoFadeSides=True)
        infoCont = Container(name='infoCont', parent=self.sr.main, align=uiconst.TOALL, padding=(defaultPadding,
         0,
         defaultPadding,
         defaultPadding))
        bottomLeftCont = Container(name='bottomLeftCont', parent=infoCont, align=uiconst.TOLEFT, width=260, padLeft=defaultPadding)
        bottomRightCont = Container(name='bottomRightCont', padLeft=5, parent=infoCont, align=uiconst.TOALL)
        killersCont = Container(name='killersCont', parent=bottomLeftCont, align=uiconst.TOALL)
        self.killedOnBehalfCont = Container(name='killedOnBehalfCont', parent=killersCont, align=uiconst.TOTOP, height=90)
        eveLabel.EveLabelLarge(text=localization.GetByLabel('UI/Corporations/Wars/Killmails/KilledOnBehalf'), parent=self.killedOnBehalfCont, align=uiconst.TOTOP)
        self.behalfCont = KilledOnBehalfContainer(name='behalfCont', parent=self.killedOnBehalfCont, align=uiconst.TOTOP)
        self.killedOnBehalfCont.display = False
        self.involvedParties = eveLabel.EveLabelLarge(text='', parent=killersCont, name='involvedParties', align=uiconst.TOTOP)
        self.damageTaken = eveLabel.EveLabelMedium(text='', parent=killersCont, name='damageTaken', align=uiconst.TOTOP, color=(1.0, 0.0, 0.0))
        finalBlowCont = Container(name='finalBlowCont', parent=killersCont, align=uiconst.TOTOP, height=84, top=8)
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/Wars/Killmails/FinalBlow'), parent=finalBlowCont, align=uiconst.TOTOP)
        self.finalBlowCont = KillerContainer(name='topKiller', parent=finalBlowCont, align=uiconst.TOTOP)
        topDamageCont = Container(name='topDamageCont', parent=killersCont, align=uiconst.TOTOP, height=94, top=12)
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Corporations/Wars/Killmails/TopDamage'), parent=topDamageCont, align=uiconst.TOTOP)
        self.topDamageCont = KillerContainer(name='topDamageCont', parent=topDamageCont, align=uiconst.TOTOP)
        self.killersScrollLine = Line(parent=killersCont, align=uiconst.TOTOP, padBottom=6, state=uiconst.UI_DISABLED)
        self.killersScroll = Scroll(name='killersScroll', parent=killersCont, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        self.sr.maincontainer.padLeft = self.sr.maincontainer.padTop = 0
        self.killersScroll.HideBackground()
        self.loadingWheel = eveLoadingWheel.LoadingWheel(parent=killersCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, idx=0, top=50)
        self.loadingWheel.display = False
        itemsCont = Container(name='itemsCont', parent=bottomRightCont, align=uiconst.TOALL)
        topItemsCont = Container(name='topItemsCont', parent=itemsCont, align=uiconst.TOTOP, height=28, padBottom=defaultPadding)
        eveLabel.EveLabelLarge(text=localization.GetByLabel('UI/Corporations/Wars/Killmails/FittingAndContent'), parent=topItemsCont, name='fittingLabel', align=uiconst.TOPLEFT, top=3)
        self.buttonCont = Container(name='buttonCont', parent=itemsCont, align=uiconst.TOBOTTOM, height=50)
        LineThemeColored(parent=self.buttonCont, align=uiconst.TOTOP, colorType=uiconst.COLORTYPE_UIBASECONTRAST, blendMode=trinity.TR2_SBM_ADD)
        self.savefittingBtn = carbonui.control.button.Button(label=localization.GetByLabel('UI/Corporations/Wars/Killmails/SaveFitting'), parent=self.buttonCont, align=uiconst.CENTERLEFT, func=self.SaveFitting, top=3)
        self.simulateFittingBtn = carbonui.control.button.Button(label=localization.GetByLabel('UI/Fitting/FittingWindow/SimulateShipFitting'), parent=self.buttonCont, align=uiconst.CENTERLEFT, func=self.SimulateFitting, left=self.savefittingBtn.width + 4, top=3)
        buyAllBtn = carbonui.control.button.Button(parent=self.buttonCont, label=localization.GetByLabel('UI/Market/MarketQuote/BuyAll'), func=self.BuyAll, align=uiconst.CENTERRIGHT)
        self.buttonCont.height = self.savefittingBtn.height + 16
        bottomItemsCont = ContainerAutoSize(name='bottomItemsCont', parent=itemsCont, align=uiconst.TOBOTTOM)
        allItemsCont = Container(name='allItemsCont', parent=itemsCont, align=uiconst.TOALL)
        self.itemsScroll = eveScroll.Scroll(name='itemsScroll', parent=allItemsCont)
        totalLossCont = Container(name='totalLossCont', parent=bottomItemsCont, align=uiconst.TOTOP, height=40, padRight=8)
        eveLabel.EveLabelLarge(text=localization.GetByLabel('UI/Corporations/Wars/Killmails/TotalWorth'), parent=totalLossCont, name='totalWorth', align=uiconst.CENTERLEFT, top=6)
        self.totalWorthLabel = eveLabel.EveLabelLarge(text='', parent=totalLossCont, name='totalWorthLabel', align=uiconst.CENTERRIGHT, top=6)
        self.totalPayoutCont = ContainerAutoSize(name='totalPayoutCont', parent=bottomItemsCont, align=uiconst.TOTOP, padRight=8)
        self.pendCont = Container(name='pendCont', parent=self.totalPayoutCont, align=uiconst.TOTOP, height=17)
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Corporations/Wars/Killmails/PendInsurance'), parent=self.pendCont, name='totalLoss', align=uiconst.BOTTOMLEFT)
        self.pendLabel = eveLabel.EveLabelSmall(text='', parent=self.pendCont, name='pendLabel', align=uiconst.BOTTOMRIGHT, color=(1.0, 0.0, 0.0))
        self.lpCont = Container(name='lpCont', parent=self.totalPayoutCont, align=uiconst.TOTOP, height=17)
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Corporations/Wars/Killmails/LPPaidOut'), parent=self.lpCont, name='totalLP', align=uiconst.BOTTOMLEFT)
        self.totalLPLabel = eveLabel.EveLabelSmall(text='', parent=self.lpCont, name='totalLPLabel', align=uiconst.BOTTOMRIGHT, color=(0.0, 1.0, 0.0))
        self.lpCont.display = False
        self.bountyCont = Container(name='bountyCont', parent=self.totalPayoutCont, align=uiconst.TOTOP, height=17, display=False)
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Corporations/Wars/Killmails/BountyPaidOut'), parent=self.bountyCont, name='totalBounty', align=uiconst.BOTTOMLEFT)
        self.totalBountyLabel = eveLabel.EveLabelSmall(text='', parent=self.bountyCont, name='totalBountyLabel', align=uiconst.BOTTOMRIGHT, color=(0.0, 1.0, 0.0))
        self.bountyCont.display = False
        self.totalSpacer = Container(name='totalSpacer', parent=self.totalPayoutCont, align=uiconst.TOTOP, height=12)

    def LoadInfo(self, killmail):
        uthread.new(self.LoadInfo_thread, killmail)

    def LoadInfo_thread(self, killmail):
        self.guyCont.Flush()
        self.shipCont.Flush()
        self.victimAllianceLogoCont.Flush()
        self.victimCorpLogoCont.Flush()
        self.rawKillmail = killmail
        self.killmail = self.FormatKillMail(killmail)
        killmail = self.killmail
        self.attackers, self.items = eveCommonUtils.GetKillMailInfo(self.rawKillmail)
        self.orignalItems = [ x.copy() for x in self.items ]
        isCapsule = evetypes.GetGroupID(killmail.victimShipTypeID) == inventoryConst.groupCapsule
        isShip = evetypes.GetCategoryID(killmail.victimShipTypeID) == inventoryConst.categoryShip
        self.buttonCont.display = False
        self.savefittingBtn.display = False
        self.simulateFittingBtn.display = False
        if len(self.items):
            if isCapsule:
                self.buttonCont.display = True
            elif isShip:
                self.buttonCont.display = True
                self.savefittingBtn.display = True
                self.simulateFittingBtn.display = True
        if idCheckers.IsCharacter(killmail.victimCharacterID):
            victim = eveIcon.Icon(parent=self.guyCont, align=uiconst.TOPRIGHT, size=128, idx=0)
            sm.GetService('photo').GetPortrait(killmail.victimCharacterID, 128, victim)
            victim.OnClick = (self.OpenPortrait, killmail.victimCharacterID)
            victimHint = cfg.eveowners.Get(killmail.victimCharacterID).name
            dragHint = localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingIconHint')
        else:
            victim = eveIcon.GetLogoIcon(itemID=killmail.victimCorporationID, parent=self.guyCont, acceptNone=False, align=uiconst.TOPRIGHT, height=128, width=128, state=uiconst.UI_NORMAL)
            victim.OnClick = (self.ShowInfo, killmail.victimCorporationID, inventoryConst.typeCorporation)
            victimHint = cfg.eveowners.Get(killmail.victimCorporationID).name
            dragHint = localization.GetByLabel('UI/Corporations/Wars/DragToShare')
        victim.GetDragData = self.GetKillDragData
        victim.hint = '%s<br>%s' % (victimHint, dragHint)
        ship = eveIcon.Icon(parent=self.shipCont, align=uiconst.TOPRIGHT, size=128, typeID=killmail.victimShipTypeID)
        ship.OnClick = (self.OpenPreview, killmail.victimShipTypeID)
        ship.GetDragData = self.GetKillDragData
        shipTechIcon = Sprite(name='techIcon', parent=self.shipCont, width=16, height=16, idx=0)
        uix.GetTechLevelIcon(shipTechIcon, 0, killmail.victimShipTypeID)
        ship.hint = '%s<br>%s' % (evetypes.GetName(killmail.victimShipTypeID), localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FittingIconHint'))
        victimCorpName = cfg.eveowners.Get(killmail.victimCorporationID).name
        victimCorpLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=victimCorpName, info=('showinfo', inventoryConst.typeCorporation, killmail.victimCorporationID))
        self.victimCorpName.text = victimCorpLabel
        victimCorpLogo = eveIcon.GetLogoIcon(itemID=killmail.victimCorporationID, parent=self.victimCorpLogoCont, acceptNone=False, align=uiconst.TOPRIGHT, height=32, width=32, state=uiconst.UI_NORMAL)
        victimCorpLogo.OnClick = (self.ShowInfo, killmail.victimCorporationID, inventoryConst.typeCorporation)
        victimCorpLogo.hint = victimCorpName
        victimCorpLogo.SetSize(32, 32)
        victimCorpNameTop = defaultPadding * 2
        self.victimAllianceName.display = True
        if killmail.victimAllianceID:
            victimAllianceName = cfg.eveowners.Get(killmail.victimAllianceID).name
            victimAllianceLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=victimAllianceName, info=('showinfo', inventoryConst.typeAlliance, killmail.victimAllianceID))
            self.victimAllianceName.text = victimAllianceLabel
            victimAllianceLogo = eveIcon.GetLogoIcon(itemID=killmail.victimAllianceID, parent=self.victimAllianceLogoCont, acceptNone=False, align=uiconst.TOPRIGHT, height=32, width=32)
            victimAllianceLogo.OnClick = (self.ShowInfo, killmail.victimAllianceID, inventoryConst.typeAlliance)
            victimAllianceLogo.hint = victimAllianceName
            victimCorpNameTop = 0
        elif killmail.victimFactionID:
            victimFactionName = cfg.eveowners.Get(killmail.victimFactionID).name
            victimFactionLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=victimFactionName, info=('showinfo', inventoryConst.typeFaction, killmail.victimFactionID))
            self.victimAllianceName.text = victimFactionLabel
            victimAllianceLogo = eveIcon.GetLogoIcon(itemID=killmail.victimFactionID, parent=self.victimAllianceLogoCont, acceptNone=False, align=uiconst.TOPRIGHT, height=32, width=32)
            victimAllianceLogo.OnClick = (self.ShowInfo, killmail.victimFactionID, inventoryConst.typeFaction)
            victimAllianceLogo.hint = victimFactionName
            victimAllianceLogo.SetSize(32, 32)
            victimCorpNameTop = 0
        else:
            self.victimAllianceName.text = ''
            self.victimAllianceName.display = False
            victimAllianceLogo = Sprite(texturePath='res:/UI/Texture/defaultAlliance.dds', parent=self.victimAllianceLogoCont, align=uiconst.TOPLEFT, width=32, height=32, state=uiconst.UI_NORMAL)
            victimAllianceLogo.hint = localization.GetByLabel('UI/PeopleAndPlaces/OwnerNotInAnyAlliance', corpName=victimCorpName)
            victimAllianceLogo.SetAlpha(0.2)
        self.victimCorpName.top = victimCorpNameTop
        self.killDate.text = FmtDate(killmail.killTime, 'ss')
        self.locationName.text = self.GetLocation(killmail.solarSystemID)
        shipName = evetypes.GetName(killmail.victimShipTypeID)
        shipGroupID = evetypes.GetGroupID(killmail.victimShipTypeID)
        shipGroupName = evetypes.GetGroupNameByGroup(shipGroupID)
        shipLabel = localization.GetByLabel('UI/Corporations/Wars/Killmails/ShipInfo', showInfoName=shipName, info=('showinfo', killmail.victimShipTypeID), groupName=shipGroupName)
        if idCheckers.IsCharacter(killmail.victimCharacterID):
            victimName = cfg.eveowners.Get(killmail.victimCharacterID).name
            victimNameLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=victimName, info=('showinfo', inventoryConst.typeCharacter, killmail.victimCharacterID))
            self.victimName.text = victimNameLabel
            self.shipName.text = shipLabel
        else:
            self.victimName.text = shipLabel
            self.shipName.text = ''
        self.damageTaken.text = localization.GetByLabel('UI/Corporations/Wars/Killmails/TotalDamage', damage=killmail.victimDamageTaken)
        if killmail.iskLost:
            worthText = eveformat.isk(killmail.iskLost, fraction=False)
        else:
            worthText = localization.GetByLabel('UI/Common/Unknown')
        self.totalWorthLabel.text = worthText
        if self.rawKillmail.iskDestroyed is not None:
            lossText = eveformat.isk(self.rawKillmail.iskDestroyed, fraction=False)
        else:
            lossText = localization.GetByLabel('UI/Common/Unknown')
        self.pendLabel.text = lossText
        if self.rawKillmail.bountyClaimed:
            bountyText = eveformat.isk(self.rawKillmail.bountyClaimed, fraction=False)
            self.totalBountyLabel.text = bountyText
            self.bountyCont.display = True
        else:
            bountyText = None
            self.bountyCont.display = False
        if self.rawKillmail.loyaltyPoints is not None and self.rawKillmail.loyaltyPoints > 0:
            LPText = localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=eveformat.number(self.rawKillmail.loyaltyPoints, decimal_places=0))
            self.totalLPLabel.text = LPText
            self.lpCont.display = True
        else:
            LPText = None
            self.lpCont.display = False
        if bountyText is None and LPText is None:
            self.totalPayoutCont.display = False
        else:
            self.totalPayoutCont.display = True
        self._LoadItemsToScrollPanel(self.itemsScroll, self.GetItems())
        self.GetAttackers()
        self.DrawKillers()
        isKilledOnBehalf = False
        self.IsKilledOnBehalf(isKilledOnBehalf)

    def _LoadItemsToScrollPanel(self, scrollPanel, items):
        entries = []
        for slots, label, iconID in (('hiSlots', 'UI/Corporations/Wars/Killmails/HighPowerSlots', 293),
         ('medSlots', 'UI/Corporations/Wars/Killmails/MediumPowerSlots', 294),
         ('lowSlots', 'UI/Corporations/Wars/Killmails/LowPowerSlots', 295),
         ('rigs', 'UI/Corporations/Wars/Killmails/RigSlots', 3266),
         ('subSystems', 'UI/Corporations/Wars/Killmails/SubSystemSlots', 3756),
         ('deed', 'UI/Corporations/Wars/Killmails/DeedSlot', 2224)):
            entries.extend(self._GetListEntriesForSlot(items[slots], label, iconID))

        for flag, label, iconID in ((inventoryConst.flagDroneBay, 'UI/Corporations/Wars/Killmails/DroneBay', 76), (inventoryConst.flagCargo, 'UI/Corporations/Wars/Killmails/CargoBay', 71), (inventoryConst.flagImplant, 'UI/Corporations/Wars/Killmails/Implants', 2224)):
            entries.extend(self._GetListEntriesForFlag(items['other'], flag, label, iconID))

        otherItems = []
        for flagID, items2 in items['other'].iteritems():
            if flagID in (inventoryConst.flagDroneBay, inventoryConst.flagCargo, inventoryConst.flagImplant):
                continue
            for item in items2:
                otherItems.extend(self._GetListEntriesForItem(item))

        if len(otherItems):
            entries.append(GetFromClass(ItemsHeader, {'label': 'Other',
             'iconID': 71}))
            entries.extend(otherItems)
        scrollPanel.Load(contentList=entries, headers=[], noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'))

    def _GetListEntriesForSlot(self, items, label, iconID):
        if not len(items):
            return []
        entries = [GetFromClass(ItemsHeader, {'label': localization.GetByLabel(label),
          'iconID': iconID})]
        itemsByTypeID = {}
        for item in items:
            if item.typeID not in itemsByTypeID:
                itemsByTypeID[item.typeID] = item
            else:
                itemsByTypeID[item.typeID].qtyDestroyed += item.qtyDestroyed
                itemsByTypeID[item.typeID].qtyDropped += item.qtyDropped

        for item in itemsByTypeID.itervalues():
            entries.extend(self._GetListEntriesForItem(item))

        return entries

    def _GetListEntriesForFlag(self, items, flag, labelName, icon):
        entries = []
        if flag in items:
            label = localization.GetByLabel(labelName)
            entries.append(GetFromClass(ItemsHeader, {'label': label,
             'iconID': icon}))
            for item in items[flag]:
                entries.extend(self._GetListEntriesForItem(item))

        return entries

    def _GetListEntriesForItem(self, item, indented = False):
        entries = []
        if item.qtyDestroyed:
            destroyedData = self._MakeDestroyedEntryData(item, indented=indented)
            entries.append(GetFromClass(KillItems, destroyedData))
            if item.contents:
                for containerItem in item.contents:
                    entries.extend(self._GetListEntriesForItem(containerItem, indented=True))

        if item.qtyDropped:
            droppedData = self._MakeDroppedEntryData(item, indented=indented)
            entries.append(GetFromClass(KillItems, droppedData))
            if item.contents:
                for containerItem in item.contents:
                    entries.extend(self._GetListEntriesForItem(containerItem, indented=True))

        return entries

    def _MakeDroppedEntryData(self, item, indented = False):
        data = utillib.KeyVal()
        data.typeID = item.typeID
        data.qtyDestroyed = None
        data.qtyDropped = item.qtyDropped
        data.singleton = item.singleton
        data.flag = item.flag
        data.indented = indented
        return data

    def _MakeDestroyedEntryData(self, item, indented = False):
        data = utillib.KeyVal()
        data.typeID = item.typeID
        data.qtyDestroyed = item.qtyDestroyed
        data.qtyDropped = None
        data.singleton = item.singleton
        data.flag = item.flag
        data.indented = indented
        return data

    def DrawKillers(self):
        self.killersScroll.Clear()
        killmail = self.killmail
        topKiller = utillib.KeyVal()
        topKiller.killerID = killmail.finalCharacterID
        topKiller.killerCorporationID = killmail.finalCorporationID
        topKiller.killerAllianceID = killmail.finalAllianceID
        topKiller.killerShipTypeID = killmail.finalShipTypeID
        topKiller.killerWeaponTypeID = killmail.finalWeaponTypeID
        topKiller.killerSecurityStatus = killmail.finalSecurityStatus
        topKiller.killerDamageDone = killmail.finalDamageDone
        topKiller.killerFactionID = killmail.finalFactionID
        try:
            topKiller.percentage = float(killmail.finalDamageDone) / float(killmail.victimDamageTaken) * 100
        except ZeroDivisionError:
            topKiller.percentage = 0.0

        involvedParties = 1
        self.finalBlowCont.LoadInfo(topKiller)
        highestDamage, restOfAttackers = self.GetAttackers()
        if highestDamage.characterID:
            if topKiller.killerID != int(highestDamage.characterID):
                involvedParties += 1
        involvedParties += len(restOfAttackers)
        self.involvedParties.text = localization.GetByLabel('UI/Corporations/Wars/Killmails/InvolvedParties', parties=involvedParties)
        topDamage = self.GetKiller(highestDamage)
        self.topDamageCont.LoadInfo(topDamage)
        if len(restOfAttackers):
            self.loadingWheel.display = True
            self.killersScroll.display = True
            self.killersScrollLine.display = True
            idsToPrime = set()
            for k in restOfAttackers:
                if k.characterID:
                    idsToPrime.add(int(k.characterID))
                if k.corporationID:
                    idsToPrime.add(int(k.corporationID))
                if k.allianceID:
                    idsToPrime.add(int(k.allianceID))

            cfg.eveowners.Prime(idsToPrime)
            self.loadingWheel.display = False
            scrollList = []
            for killer in restOfAttackers:
                if self.destroyed:
                    break
                killerInfo = self.GetKiller(killer)
                entry = GetFromClass(KillContainerEntry, {'killer': killerInfo})
                scrollList.append(entry)

            self.killersScroll.Load(contentList=scrollList)
        else:
            self.killersScroll.display = False
            self.killersScrollLine.display = False

    def GetKiller(self, killer):
        killerInfo = utillib.KeyVal()
        if killer.characterID:
            killerInfo.killerID = int(killer.characterID)
        else:
            killerInfo.killerID = None
        killerInfo.killerCorporationID = killer.corporationID
        killerInfo.killerAllianceID = killer.allianceID
        if killer.shipTypeID:
            killerInfo.killerShipTypeID = int(killer.shipTypeID)
        else:
            killerInfo.killerShipTypeID = None
        if killer.weaponTypeID:
            killerInfo.killerWeaponTypeID = int(killer.weaponTypeID)
        else:
            killerInfo.killerWeaponTypeID = None
        killerInfo.killerSecurityStatus = killer.secStatusText
        killerInfo.killerDamageDone = killer.damageDone
        killerInfo.killerFactionID = killer.factionID
        try:
            killerInfo.percentage = float(killer.damageDone) / float(self.killmail.victimDamageTaken) * 100
        except ZeroDivisionError:
            killerInfo.percentage = 0

        return killerInfo

    def GetLocation(self, solarSystemID):
        if IsAbyssalSpaceSystem(solarSystemID) or IsVoidSpaceSystem(solarSystemID):
            return localization.GetByLabel('UI/Abyss/AbyssalDepths')
        solarSystem = cfg.mapSystemCache[solarSystemID]
        constellationID = solarSystem.constellationID
        regionID = solarSystem.regionID
        return u'{solar_system} {security_status} &lt; {constellation} &lt; {region}'.format(solar_system=evelink.location_link(solarSystemID), security_status=eveformat.solar_system_security_status(solarSystemID), constellation=evelink.location_link(constellationID), region=evelink.location_link(regionID))

    def FormatKillMail(self, killmail):
        km = utillib.KeyVal()
        km.killID = killmail.killID
        km.killTime = killmail.killTime
        km.solarSystemID = killmail.solarSystemID
        km.moonID = killmail.moonID
        km.victimCharacterID = killmail.victimCharacterID
        km.victimCorporationID = killmail.victimCorporationID
        km.victimFactionID = killmail.victimFactionID
        km.victimAllianceID = killmail.victimAllianceID
        km.victimShipTypeID = killmail.victimShipTypeID
        km.victimDamageTaken = killmail.victimDamageTaken
        km.finalCharacterID = killmail.finalCharacterID
        km.finalCorporationID = killmail.finalCorporationID
        km.finalAllianceID = killmail.finalAllianceID
        km.finalShipTypeID = killmail.finalShipTypeID
        km.finalWeaponTypeID = killmail.finalWeaponTypeID
        km.finalSecurityStatus = killmail.finalSecurityStatus
        km.finalDamageDone = killmail.finalDamageDone
        km.finalFactionID = killmail.finalFactionID
        km.warID = killmail.warID
        km.iskLost = killmail.iskLost or None
        return km

    def GetAttackers(self):
        self.attackers.sort(reverse=True)
        highestDamage = self.attackers[0][1]
        try:
            restOfAttackers = [ attacker for damage, attacker in self.attackers[1:] if not attacker.finalBlow ]
        except IndexError:
            restOfAttackers = []

        return (highestDamage, restOfAttackers)

    def IsKilledOnBehalf(self, isKilledOnBehalf):
        killRightSupplied = self.rawKillmail.killRightSupplied
        if killRightSupplied is not None:
            self.killedOnBehalfCont.display = True
            charID = killRightSupplied
            publicInfo = sm.GetService('corp').GetInfoWindowDataForChar(killRightSupplied)
            corpID = publicInfo.corpID
            allianceID = publicInfo.allianceID
            self.behalfCont.LoadInfo(charID, corpID, allianceID, None)
        else:
            self.killedOnBehalfCont.display = False

    def GetItems(self):
        ret = {'hiSlots': [],
         'medSlots': [],
         'lowSlots': [],
         'rigs': [],
         'subSystems': [],
         'deed': [],
         'other': defaultdict(list)}
        for item in self.items:
            loc = self.GetRack(item.flag)
            if loc is None:
                ret['other'][item.flag].append(item)
            else:
                ret[loc].append(item)

        return ret

    def GetRack(self, flagID):
        if inventoryConst.flagHiSlot0 <= flagID <= inventoryConst.flagHiSlot7:
            return 'hiSlots'
        if inventoryConst.flagMedSlot0 <= flagID <= inventoryConst.flagMedSlot7:
            return 'medSlots'
        if inventoryConst.flagLoSlot0 <= flagID <= inventoryConst.flagLoSlot7:
            return 'lowSlots'
        if inventoryConst.flagRigSlot0 <= flagID <= inventoryConst.flagRigSlot7:
            return 'rigs'
        if IsSubsystemFlag(flagID):
            return 'subSystems'
        if flagID == inventoryConst.flagStructureDeed:
            return 'deed'

    def OpenPreview(self, typeID, *args):
        if eveCfg.IsPreviewable(typeID):
            sm.GetService('preview').PreviewType(typeID)

    def OpenPortrait(self, charID, *args):
        from eve.client.script.ui.shared.portraitWindow.portraitWindow import PortraitWindow
        PortraitWindow.CloseIfOpen()
        PortraitWindow.Open(charID=charID)

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def SaveFitting(self, *args):
        sm.GetService('fittingSvc').DisplayFittingFromItems(self.rawKillmail.victimShipTypeID, self.orignalItems)

    def SimulateFitting(self, *args):
        fitting = sm.GetService('fittingSvc').GetFittingFromItems(self.rawKillmail.victimShipTypeID, self.items)
        SimulateFitting(fitting)

    def BuyAll(self, *args):
        buyDict = defaultdict(int)
        for eachItem in self.orignalItems:
            qty = getattr(eachItem, 'stacksize', None)
            if qty is None:
                qty = getattr(eachItem, 'qtyDropped', 0) + getattr(eachItem, 'qtyDestroyed', 0)
            buyDict[int(eachItem.typeID)] += qty

        if evetypes.GetGroupID(self.rawKillmail.victimShipTypeID) != inventoryConst.groupCapsule:
            buyDict[self.rawKillmail.victimShipTypeID] = 1
        BuyMultipleTypesWithQty(buyDict)

    def GetMenuMoreOptions(self):
        menuData = super(KillReportWnd, self).GetMenuMoreOptions()
        menuData += self.GetSettingsMenu()
        return menuData

    def GetSettingsMenu(self, *args):
        m = [(MenuLabel('UI/Control/Entries/CopyKillInfo'), self.GetCombatText, ()), (MenuLabel('UI/Control/Entries/CopyExternalKillLink'), CopyESIKillmailUrlToClipboard, (self.rawKillmail,))]
        return m

    def GetCombatText(self, *args):
        killmail = eveCommonUtils.CombatLog_CopyText(self.rawKillmail)
        blue.pyos.SetClipboardData(killReportUtil.CleanKillMail(killmail))

    def GetKillDragData(self, *args):
        fakeNode = bunch.Bunch()
        fakeNode.mail = self.rawKillmail
        fakeNode.__guid__ = 'listentry.KillMail'
        return [fakeNode]


class KillItems(Generic):
    __guid__ = 'listentry.KillItems'
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.bgColor = Fill(bgParent=self, color=(0.0, 1.0, 0.0, 0.1), state=uiconst.UI_HIDDEN)
        qtyCont = Container(name='qtyCont', parent=self, align=uiconst.TORIGHT, width=80, padRight=defaultPadding)
        self.itemCont = Container(name='itemCont', parent=self, align=uiconst.TOALL, clipChildren=True)
        self.sr.label = eveLabel.EveLabelMedium(text='', parent=self.itemCont, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT)
        self.sr.qtyLabel = eveLabel.EveLabelMedium(text='', parent=qtyCont, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERRIGHT)
        iconCont = Container(parent=self.itemCont, pos=(16, 0, 24, 24), align=uiconst.CENTERLEFT)
        Sprite(bgParent=iconCont, name='background', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')
        self.sr.icon = eveIcon.Icon(parent=iconCont, pos=(0, 1, 24, 24), align=uiconst.TOPLEFT, idx=0)
        self.sr.techIcon = Sprite(name='techIcon', parent=iconCont, left=0, width=12, height=12, idx=0)

    def Load(self, node):
        Generic.Load(self, node)
        self.sr.node = node
        data = node
        if node.indented:
            self.itemCont.padLeft = 16
        self.sr.node.typeID = int(node.typeID)
        self.typeID = int(data.typeID)
        qtyDestroyed = data.qtyDestroyed
        qtyDropped = data.qtyDropped
        singleton = data.singleton
        flag = data.flag
        typeName = evetypes.GetName(self.typeID)
        isCopy = False
        if evetypes.GetCategoryID(self.typeID) == inventoryConst.categoryBlueprint:
            self.sr.icon.top = 0
            if singleton == singletonBlueprintCopy:
                isCopy = True
                typeName += ' (%s)' % localization.GetByLabel('UI/Generic/Copy').lower()
            else:
                typeName += ' (%s)' % localization.GetByLabel('UI/Generic/Original').lower()
        self.sr.label.text = typeName
        if qtyDropped > 0:
            self.bgColor.state = uiconst.UI_DISABLED
            self.sr.qtyLabel.text = eveformat.number(qtyDropped)
        else:
            self.bgColor = uiconst.UI_HIDDEN
            self.sr.qtyLabel.text = eveformat.number(qtyDestroyed)
        self.sr.techIcon.state = uiconst.UI_HIDDEN
        if self.typeID:
            self.sr.icon.state = uiconst.UI_NORMAL
            if flag == inventoryConst.flagImplant:
                self.sr.icon.LoadIcon(evetypes.GetIconID(self.typeID), ignoreSize=True)
            else:
                self.sr.icon.LoadIconByTypeID(typeID=self.typeID, size=24, ignoreSize=True, isCopy=isCopy)
            self.sr.icon.SetSize(24, 24)
            self.sr.label.left = self.height + 16
            techSprite = uix.GetTechLevelIcon(self.sr.techIcon, 1, self.typeID)
            techSprite.SetSize(12, 12)

    def GetHeight(self, *args):
        node, width = args
        node.height = 26
        return node.height

    def GetMenu(self):
        if self.typeID:
            return GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)
        return []

    def OnDblClick(self, *args):
        sm.GetService('info').ShowInfo(self.typeID)

    def GetDragData(self, *args):
        return [self.sr.node]

    @classmethod
    def GetCopyData(cls, node):
        typeID = int(node.typeID)
        typeName = evetypes.GetName(typeID)
        qty = unicode(node.qtyDestroyed or node.qtyDropped or '')
        copyText = ''
        if evetypes.GetCategoryID(typeID) == inventoryConst.categoryBlueprint:
            if node.singleton == singletonBlueprintCopy:
                copyText = localization.GetByLabel('UI/Generic/Copy')
            else:
                copyText = localization.GetByLabel('UI/Generic/Original')
        if node.qtyDestroyed:
            droppedText = localization.GetByLabel('UI/Corporations/Wars/Killmails/Destroyed')
        elif node.qtyDropped:
            droppedText = localization.GetByLabel('UI/Corporations/Wars/Killmails/Dropped')
        else:
            droppedText = ''
        return '<t>'.join([typeName,
         qty,
         copyText,
         droppedText])


class ItemsHeader(Header):
    __guid__ = 'listentry.ItemsHeader'

    def Startup(self, *args):
        Header.Startup(self, *args)
        self.sr.icon = eveIcon.Icon(parent=self, pos=(0, 0, 24, 24), align=uiconst.CENTERLEFT, idx=0, ignoreSize=True)

    def Load(self, node):
        Header.Load(self, node)
        self.sr.label.left = 30
        self.sr.icon.LoadIcon(node.iconID, ignoreSize=True)

    def GetHeight(self, *args):
        node, width = args
        node.height = 27
        return node.height


class KillerContainer(Container):
    default_height = 66
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.killerID = attributes.get('killerID', None)
        self.ConstructLayout()

    def ConstructLayout(self):
        iconCont = Container(name='iconCont', parent=self, align=uiconst.TOLEFT, width=96)
        self.killerCont = Container(name='killerCont', parent=iconCont, align=uiconst.TOLEFT, width=64, padTop=1, padBottom=1, state=uiconst.UI_NORMAL)
        self.shipCont = Container(name='shipCont', parent=iconCont, align=uiconst.TOPRIGHT, width=32, height=32, top=1)
        Sprite(bgParent=self.shipCont, name='shipBackground', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')
        self.weaponCont = Container(name='weaponCont', parent=iconCont, align=uiconst.BOTTOMRIGHT, width=32, height=32, top=1)
        Sprite(bgParent=self.weaponCont, name='weaponBackground', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')
        self.textCont = Container(name='textCont', parent=self, align=uiconst.TOALL, padLeft=defaultPadding)
        self.nameLabel = eveLabel.EveLabelSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOTOP, top=-1, state=uiconst.UI_NORMAL)
        self.corpLabel = eveLabel.EveLabelSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOTOP, top=-1, state=uiconst.UI_NORMAL)
        self.allianceLabel = eveLabel.EveLabelSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOTOP, top=-1, state=uiconst.UI_NORMAL)
        self.damageLabel = eveLabel.EveLabelSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOBOTTOM)

    def LoadInfo(self, killer):
        self.killerCont.Flush()
        self.shipCont.Flush()
        self.weaponCont.Flush()
        self.allianceLabel.text = ''
        self.damageLabel.text = ''
        nameHint = ''
        killerLogo = Sprite(parent=self.killerCont, align=uiconst.TOALL, idx=0, texturePath='res:/UI/Texture/silhouette_64.png')
        if killer.killerID:
            sm.GetService('photo').GetPortrait(killer.killerID, 64, killerLogo)
            killerLogo.OnClick = (self.ShowInfo, killer.killerID, inventoryConst.typeCharacter)
            killerLogo.hint = cfg.eveowners.Get(killer.killerID).name
        if killer.killerShipTypeID:
            shipLogo = eveIcon.Icon(parent=self.shipCont, align=uiconst.TOPRIGHT, size=32, typeID=killer.killerShipTypeID, ignoreSize=True)
            shipLogo.OnClick = (self.ShowInfo, None, killer.killerShipTypeID)
            shipTechIcon = Sprite(name='techIcon', parent=self.shipCont, width=12, height=12, idx=0)
            shipTechSprite = uix.GetTechLevelIcon(shipTechIcon, 0, killer.killerShipTypeID)
            if shipTechSprite:
                shipTechSprite.SetSize(12, 12)
            shipLogo.hint = evetypes.GetName(killer.killerShipTypeID)
        if killer.killerWeaponTypeID:
            self.weaponCont.display = True
            weaponLogo = eveIcon.Icon(parent=self.weaponCont, align=uiconst.TOPRIGHT, size=32, typeID=killer.killerWeaponTypeID, ignoreSize=True)
            weaponLogo.OnClick = (self.ShowInfo, None, killer.killerWeaponTypeID)
            techIcon = Sprite(name='techIcon', parent=self.weaponCont, width=12, height=12, idx=0)
            techSprite = uix.GetTechLevelIcon(techIcon, 0, killer.killerWeaponTypeID)
            if techSprite:
                techSprite.SetSize(12, 12)
            self.damageLabel.text = localization.GetByLabel('UI/Corporations/Wars/Killmails/DamageDone', damage=killer.killerDamageDone, percentage=killer.percentage)
            weaponLogo.hint = '%s<br>%s' % (evetypes.GetName(killer.killerWeaponTypeID), self.damageLabel.text)
        else:
            self.weaponCont.display = False
        if killer.killerID:
            self.nameLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(killer.killerID).name, info=('showinfo', inventoryConst.typeCharacter, killer.killerID))
            nameHint = '%s<br>%s' % (cfg.eveowners.Get(killer.killerID).name, cfg.eveowners.Get(killer.killerCorporationID).name)
        else:
            self.nameLabel.text = evetypes.GetName(killer.killerShipTypeID)
        showInfoType = inventoryConst.typeFaction if IsFaction(int(killer.killerCorporationID)) else inventoryConst.typeCorporation
        self.corpLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(killer.killerCorporationID).name, info=('showinfo', showInfoType, killer.killerCorporationID))
        self.allianceLabel.display = True
        if killer.killerAllianceID:
            self.allianceLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(killer.killerAllianceID).name, info=('showinfo', inventoryConst.typeAlliance, killer.killerAllianceID))
            nameHint += '<br>%s' % cfg.eveowners.Get(killer.killerAllianceID).name
        elif killer.killerFactionID:
            self.allianceLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(killer.killerFactionID).name, info=('showinfo', inventoryConst.typeFaction, killer.killerFactionID))
            nameHint += '<br>%s' % cfg.eveowners.Get(killer.killerFactionID).name
        else:
            self.allianceLabel.display = False
        killerLogo.hint = nameHint

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)


class KillContainerEntry(SE_BaseClassCore):
    bottomPadding = 8
    BIG_LOGO_SIZE = 64
    SMALL_LOGO_SIZE = 32

    def Startup(self, *etc):
        self.killerLogo = Sprite(parent=self, align=uiconst.TOPLEFT, pos=(0,
         1,
         self.BIG_LOGO_SIZE,
         self.BIG_LOGO_SIZE), state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/silhouette_64.png')
        shipCont = Container(name='shipCont', parent=self, align=uiconst.TOPLEFT, pos=(self.BIG_LOGO_SIZE,
         1,
         self.SMALL_LOGO_SIZE,
         self.SMALL_LOGO_SIZE))
        Sprite(bgParent=shipCont, name='shipBackground', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')
        self.shipTechIcon = Sprite(name='techIcon', parent=shipCont, width=12, height=12, idx=0)
        self.shipLogo = eveIcon.Icon(parent=shipCont, align=uiconst.TOPRIGHT, size=self.SMALL_LOGO_SIZE)
        self.weaponCont = Container(name='weaponCont', parent=self, align=uiconst.TOPLEFT, pos=(64,
         self.SMALL_LOGO_SIZE + 1,
         self.SMALL_LOGO_SIZE,
         self.SMALL_LOGO_SIZE))
        Sprite(bgParent=self.weaponCont, name='weaponBackground', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')
        self.weaponTechIcon = Sprite(name='techIcon', parent=self.weaponCont, width=12, height=12, idx=0)
        self.weaponLogo = eveIcon.Icon(parent=self.weaponCont, align=uiconst.TOPRIGHT, size=self.SMALL_LOGO_SIZE)
        textLeft = self.BIG_LOGO_SIZE + self.SMALL_LOGO_SIZE + 4
        self.nameLabel = eveLabel.EveLabelSmall(text='', parent=self, align=uiconst.TOPLEFT, pos=(textLeft,
         -1,
         0,
         0), state=uiconst.UI_NORMAL)
        self.corpLabel = eveLabel.EveLabelSmall(text='', parent=self, align=uiconst.TOPLEFT, pos=(textLeft,
         20,
         0,
         0), state=uiconst.UI_NORMAL)
        self.allianceLabel = eveLabel.EveLabelSmall(text='', parent=self, align=uiconst.TOPLEFT, pos=(textLeft,
         40,
         0,
         0), state=uiconst.UI_NORMAL)
        self.damageLabel = eveLabel.EveLabelSmall(text='', parent=self, align=uiconst.BOTTOMLEFT, pos=(textLeft,
         self.bottomPadding,
         0,
         0), state=uiconst.UI_NORMAL)

    def Load(self, node):
        killer = node.killer
        self.allianceLabel.text = ''
        self.damageLabel.text = ''
        nameHint = ''
        if killer.killerID:
            sm.GetService('photo').GetPortrait(killer.killerID, self.BIG_LOGO_SIZE, self.killerLogo)
            self.killerLogo.OnClick = (self.ShowInfo, killer.killerID, inventoryConst.typeCharacter)
            self.killerLogo.hint = cfg.eveowners.Get(killer.killerID).name
        if killer.killerShipTypeID:
            self.shipLogo.LoadIconByTypeID(killer.killerShipTypeID, ignoreSize=True)
            self.shipLogo.OnClick = (self.ShowInfo, None, killer.killerShipTypeID)
            shipTechSprite = uix.GetTechLevelIcon(self.shipTechIcon, 0, killer.killerShipTypeID)
            if shipTechSprite:
                shipTechSprite.SetSize(12, 12)
            self.shipLogo.hint = evetypes.GetName(killer.killerShipTypeID)
        if killer.killerWeaponTypeID:
            self.weaponCont.display = True
            self.weaponLogo.LoadIconByTypeID(killer.killerWeaponTypeID, ignoreSize=True)
            self.weaponLogo.OnClick = (self.ShowInfo, None, killer.killerWeaponTypeID)
            techSprite = uix.GetTechLevelIcon(self.weaponTechIcon, 0, killer.killerWeaponTypeID)
            if techSprite:
                techSprite.SetSize(12, 12)
            self.damageLabel.text = localization.GetByLabel('UI/Corporations/Wars/Killmails/DamageDone', damage=killer.killerDamageDone, percentage=killer.percentage)
            self.weaponLogo.hint = '%s<br>%s' % (evetypes.GetName(killer.killerWeaponTypeID), self.damageLabel.text)
        else:
            self.weaponCont.display = False
        if killer.killerID:
            nameText = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(killer.killerID).name, info=('showinfo', inventoryConst.typeCharacter, killer.killerID))
            self.nameLabel.text = nameText
            nameHint = '%s<br>%s' % (cfg.eveowners.Get(killer.killerID).name, cfg.eveowners.Get(killer.killerCorporationID).name)
        else:
            self.nameLabel.text = evetypes.GetName(killer.killerShipTypeID)
        self.corpLabel.top = self.nameLabel.top + self.nameLabel.textheight - 1
        showInfoType = inventoryConst.typeFaction if IsFaction(int(killer.killerCorporationID)) else inventoryConst.typeCorporation
        self.corpLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(killer.killerCorporationID).name, info=('showinfo', showInfoType, killer.killerCorporationID))
        if killer.killerAllianceID:
            self.allianceLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(killer.killerAllianceID).name, info=('showinfo', inventoryConst.typeAlliance, killer.killerAllianceID))
            nameHint += '<br>%s' % cfg.eveowners.Get(killer.killerAllianceID).name
        elif killer.killerFactionID:
            self.allianceLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(killer.killerFactionID).name, info=('showinfo', inventoryConst.typeFaction, killer.killerFactionID))
            nameHint += '<br>%s' % cfg.eveowners.Get(killer.killerFactionID).name
        self.allianceLabel.top = self.corpLabel.top + self.corpLabel.textheight - 1
        self.killerLogo.hint = nameHint

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def GetHeight(self, *args):
        node, _ = args
        node.height = KillContainerEntry.BIG_LOGO_SIZE + KillContainerEntry.bottomPadding + 2
        return node.height


class KilledOnBehalfContainer(Container):
    default_height = 64
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.ConstructLayout()

    def ConstructLayout(self):
        Fill(bgParent=self, color=(1.0, 0.0, 0.0, 0.2))
        Frame(parent=self, color=(1.0, 0.0, 0.0, 0.2))
        iconCont = Container(name='iconCont', parent=self, align=uiconst.TOLEFT, width=96)
        self.behalfCont = Container(name='behalfCont', parent=iconCont, align=uiconst.TOLEFT, width=64, state=uiconst.UI_NORMAL)
        self.corpCont = Container(name='corpCont', parent=iconCont, align=uiconst.TOPRIGHT, width=32, height=32)
        self.allianceCont = Container(name='allianceCont', parent=iconCont, align=uiconst.BOTTOMRIGHT, width=32, height=32)
        theRestCont = Container(name='textCont', parent=self, align=uiconst.TOALL, padLeft=defaultPadding)
        self.textCont = ContainerAutoSize(parent=theRestCont, name='textCont', align=uiconst.CENTERLEFT)
        self.nameLabel = eveLabel.EveLabelSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.corpLabel = eveLabel.EveLabelSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, top=13)
        self.allianceLabel = eveLabel.EveLabelSmall(text='', parent=self.textCont, maxLines=1, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, top=26)

    def LoadInfo(self, behalfID, corpID, allianceID = None, factionID = None):
        self.behalfCont.Flush()
        self.corpCont.Flush()
        self.allianceCont.Flush()
        self.allianceLabel.text = ''
        nameHint = ''
        behalfName = cfg.eveowners.Get(behalfID).name
        corpName = cfg.eveowners.Get(corpID).name
        self.allianceLabel.display = True
        behalfLogo = Sprite(parent=self.behalfCont, align=uiconst.TOALL, idx=0, texturePath='res:/UI/Texture/silhouette_64.png')
        if behalfID:
            sm.GetService('photo').GetPortrait(behalfID, 64, behalfLogo)
            behalfLogo.OnClick = (self.ShowInfo, behalfID, inventoryConst.typeCharacter)
            behalfLogo.hint = cfg.eveowners.Get(behalfID).name
        if behalfID:
            self.nameLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(behalfID).name, info=('showinfo', inventoryConst.typeCharacter, behalfID))
            nameHint = '%s<br>%s' % (behalfName, corpName)
        corpLogo = eveIcon.GetLogoIcon(itemID=corpID, parent=self.corpCont, acceptNone=False, align=uiconst.TOPRIGHT, height=32, width=32, state=uiconst.UI_NORMAL)
        corpLogo.OnClick = (self.ShowInfo, corpID, inventoryConst.typeCorporation)
        corpLogo.hint = corpName
        corpLogo.SetSize(32, 32)
        self.corpLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=corpName, info=('showinfo', inventoryConst.typeCorporation, corpID))
        if allianceID:
            allianceName = cfg.eveowners.Get(allianceID).name
            self.allianceLabel.text = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=allianceName, info=('showinfo', inventoryConst.typeAlliance, allianceID))
            nameHint += '<br>%s' % allianceName
            allianceLogo = eveIcon.GetLogoIcon(itemID=allianceID, parent=self.allianceCont, acceptNone=False, align=uiconst.TOPRIGHT, height=32, width=32)
            allianceLogo.OnClick = (self.ShowInfo, allianceID, inventoryConst.typeAlliance)
            allianceLogo.hint = allianceName
        else:
            self.allianceLabel.text = ''
            allianceLogo = Sprite(texturePath='res:/UI/Texture/defaultAlliance.dds', parent=self.allianceCont, align=uiconst.TOPLEFT, width=32, height=32, state=uiconst.UI_NORMAL)
            allianceLogo.hint = localization.GetByLabel('UI/PeopleAndPlaces/OwnerNotInAnyAlliance', corpName=corpName)
            allianceLogo.SetAlpha(0.3)
            self.allianceLabel.display = False
        behalfLogo.hint = nameHint

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)
