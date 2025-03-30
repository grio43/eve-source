#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\entries\structureEntryMyCorp.py
from collections import defaultdict
import evetypes
import gametime
from carbon.common.lib.const import SEC
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.primitives.container import Container
import structures
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate, FmtAmt
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.control.window import Window
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.structure.structureIcon import StructureIcon
from eve.client.script.ui.control.eveLabel import Label, EveLabelSmall, EveLabelMedium
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.station.stationServiceConst import UPWELL_STANDARD_SERVICES, serviceDataByNameID
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureBrowser.browserUIConst import ALL_SERVICES
from eve.client.script.ui.structure.structureBrowser.controllers.reinforceTimersBundle import GetDayAndHourText, ReinforcementBundle
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from eve.client.script.ui.structure.structureBrowser.entries.structureEntry import StructureServiceIconMyCorp
from eve.client.script.ui.structure.structureBrowser.structureState import StructureStateIcon
from eve.common.script.sys.idCheckers import IsDockableStructure
from eve.common.script.util.structuresCommon import MAX_STRUCTURE_BIO_LENGTH
from eveservices.scheduling import GetSchedulingService
import inventorycommon.const as invConst
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from localization import GetByLabel
import carbonui.const as uiconst
from localization.formatters import FormatTimeIntervalShortWritten
from structures.types import IsFlexStructure
from utillib import KeyVal
import blue
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from menu import MenuLabel
HEIGHT = 48
ICONSIZE = 20
LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)
STATE_ICON_SIZE = 30
UPKEEP_TEXTURE_PATH = 'res:/UI/Texture/classes/StructureBrowser/bolt.png'

class StructureEntryMyCorp(BaseListEntryCustomColumns):
    default_name = 'StructureEntryMyCorp'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.controller = self.node.controller
        self.slimProfileController = self.node.slimProfileController
        self.ChangeSignalConnection(connect=True)
        self.BuildUI()

    def BuildUI(self):
        self.AddProfileNameColumn()
        self.stateColumn = self.AddColumnContainer()
        self.jumpColumnLabel = self.AddColumnText()
        self.securityColumnLabel = self.AddColumnText()
        self.nameColumn = self.AddColumnContainer()
        self.servicesColumn = self.AddColumnContainer()
        self.fuelColumnLabel = self.AddColumnText()
        self.reinforcementTimeColumn = self.AddColumnContainer()
        self.AddExtraColumns()
        self.LoadUI()

    def LoadUI(self):
        self.PopulateProfileNameColumn()
        self.PopulateStateColumn()
        self.PopulateJumpColumn()
        self.PopulateSecurityColumn()
        self.PopulateNameColumn()
        self.PopulateServicesColumn()
        self.PopulateReinforcementTimeColumn()
        self.PopulateFuelColumn()
        self.PopulateExtraColumns()
        if self.controller.IsUnanchoring():
            self.opacity = 0.4

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_structure_state_changed, self.OnStructureStateChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def AddProfileNameColumn(self):
        pass

    def AddExtraColumns(self):
        structureServicesChecked = self.node.structureServicesChecked
        if structureServicesChecked == ALL_SERVICES:
            return
        for serviceName in structureServicesChecked:
            serviceData = serviceDataByNameID.get(serviceName)
            if serviceData and serviceData.serviceID == structures.SERVICE_JUMP_BRIDGE:
                columnLabel = self.AddColumnText()
                variableName = StructureEntryMyCorp.GetColumnVariableName(serviceName)
                setattr(self, variableName, columnLabel)
                break

    def PopulateProfileNameColumn(self):
        pass

    def PopulateStateColumn(self):
        self.stateColumn.Flush()
        self.upkeepLowPowerSprite = Sprite(parent=self.stateColumn, align=uiconst.TOPRIGHT, texturePath=UPKEEP_TEXTURE_PATH, state=uiconst.UI_NORMAL, pos=(4, 6, 9, 9))
        self.upkeepLowPowerSprite.SetRGBA(1, 1, 0, 0.8)
        self.upkeepLowPowerSprite.hint = GetByLabel('UI/Structures/LowPowerStructureModeHint')
        self.upkeepLowPowerSprite.display = False
        self.upkeepLowPowerSprite.DelegateEvents(self)
        self.upkeepAbandonedSprite = Sprite(parent=self.stateColumn, align=uiconst.TOPRIGHT, texturePath=UPKEEP_TEXTURE_PATH, state=uiconst.UI_NORMAL, pos=(4, 6, 9, 9))
        self.upkeepAbandonedSprite.SetRGBA(1, 0, 0, 0.8)
        self.upkeepAbandonedSprite.hint = GetByLabel('UI/Structures/AbandonedStructureModeHint')
        self.upkeepAbandonedSprite.display = False
        self.upkeepAbandonedSprite.DelegateEvents(self)
        self.structureStateIcon = StructureStateIcon(parent=self.stateColumn)
        self.structureStateIcon.DelegateEvents(self)
        self.SetStructureState()

    def SetStructureState(self):
        if self.structureStateIcon:
            self.upkeepLowPowerSprite.display = self.controller.IsLowPower()
            self.upkeepAbandonedSprite.display = self.controller.IsAbandoned()
            structureState = self.controller.GetState()
            timerEnd = self.controller.GetTimerEnd()
            self.structureStateIcon.SetStructureState(structureState, timerEnd=timerEnd)

    def PopulateNameColumn(self):
        self.nameColumn.Flush()
        name = self.controller.GetName()
        if self.controller.IsLowPower():
            name += '<br><color=0xcfffff00>%s</color>' % GetByLabel('UI/Structures/UpkeepModeLowPower')
        elif self.controller.IsAbandoned():
            name += '<br><color=0xcfff0000>%s</color>' % GetByLabel('UI/Structures/UpkeepModeAbandoned')
        size = HEIGHT - 4
        itemIcon = StructureIcon(parent=self.nameColumn, align=uiconst.CENTERLEFT, typeID=self.controller.GetTypeID(), structureID=self.controller.GetItemID(), pos=(0,
         0,
         size,
         size), state=uiconst.UI_PICKCHILDREN, name='structureIcon_%s' % name.replace('<br>', '_'), wars=self.controller.GetWars())
        label = EveLabelMedium(parent=self.nameColumn, text=name, align=uiconst.CENTERLEFT, left=HEIGHT, state=uiconst.UI_NORMAL, lineSpacing=-0.2)
        label.GetMenu = None
        label.DelegateEventsNotImplemented(self)
        if self.controller.IsUnanchoring():
            timeUntilUnanchor = self._GetTimeUntilUnanchor()
            if IsFlexStructure(self.controller.GetTypeID()):
                totalUnanchoringTime = structures.FLEX_UNANCHORING_TIME
            else:
                totalUnanchoringTime = structures.UNANCHORING_TIME
            gaugeCircular = GaugeCircular(name='gaugeCircular', parent=itemIcon, align=uiconst.CENTER, radius=16, lineWidth=4, value=1.0 - timeUntilUnanchor / float(totalUnanchoringTime * SEC), showMarker=False, idx=0, state=uiconst.UI_NORMAL, opacity=2.0)
            itemIcon.state = uiconst.UI_PICKCHILDREN
            gaugeCircular.gauge.state = uiconst.UI_DISABLED
            gaugeCircular.LoadTooltipPanel = self._LoadUnanchoringTooltipPanel

    def _LoadUnanchoringTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Structures/Browser/StructureUnanchoring'))
        diff = self._GetTimeUntilUnanchor()
        fmtDiff = FormatTimeIntervalShortWritten(diff)
        tooltipPanel.AddLabelMedium(text=fmtDiff)

    def _GetTimeUntilUnanchor(self):
        unanchorTime = self.controller.GetUnanchorTime()
        now = gametime.GetWallclockTime()
        return max(0, unanchorTime - now)

    def PopulateServicesColumn(self):
        self.servicesColumn.Flush()
        availableServices, onlineStates = self.controller.GetServicesAndOnlineStatus()
        serviceData = stationServiceConst.serviceData
        basicServicesList = sorted([ '-%s' % x.label for x in UPWELL_STANDARD_SERVICES.itervalues() ])
        basicServicesList = ['%s:' % GetByLabel('UI/Structures/UpwellStandardServices')] + basicServicesList
        basicServicesHint = '<br>'.join(basicServicesList)
        s = StructureServiceIconMyCorp(name='upwellStandardServices', parent=self.servicesColumn, texturePath='res:/UI/Texture/WindowIcons/basicServices.png', pos=(0,
         0,
         ICONSIZE,
         ICONSIZE), hintHeader=basicServicesHint, opacity=0.1 if IsFlexStructure(self.controller.GetTypeID()) else 1.0, controller=self.controller, serviceID=-1, isOffline=False)
        s.DelegateEvents(self)
        left = ICONSIZE
        for i, data in enumerate(serviceData):
            if data.name in UPWELL_STANDARD_SERVICES:
                continue
            isAvailable = self.IsThisServiceAvailable(data, availableServices)
            opacity = 1.0 if isAvailable else 0.1
            isOffline = onlineStates.get(data.serviceID, False) == structures.SERVICE_STATE_OFFLINE
            s = StructureServiceIconMyCorp(name=data.name, parent=self.servicesColumn, texturePath=data.iconID, pos=(left,
             0,
             ICONSIZE,
             ICONSIZE), hintHeader=data.label, opacity=opacity, serviceName=data.name, controller=self.controller, serviceID=data.serviceID, isOffline=isOffline)
            s.DelegateEvents(self)
            left += ICONSIZE

    def IsThisServiceAvailable(self, data, availableServices):
        if data in availableServices:
            return True
        if self.controller.GetTypeID() in structures.STRUCTURES_WITHOUT_ONLINE_SERVICES:
            return False
        return data.serviceID == stationServiceConst.serviceIDAlwaysPresent or data.serviceID in structures.ONLINE_SERVICES

    def PopulateJumpColumn(self):
        text = self.controller.GetNumJumpsText()
        self.jumpColumnLabel.text = text
        self.jumpColumnLabel.align = uiconst.CENTER
        self.jumpColumnLabel.left = 0

    def PopulateSecurityColumn(self):
        text = self.controller.GetSecurityWithColor()
        self.securityColumnLabel.text = text
        self.securityColumnLabel.align = uiconst.CENTER
        self.securityColumnLabel.left = 0

    def PopulateFuelColumn(self):
        fuelExpires = self.controller.GetFuelExpiry()
        if fuelExpires:
            text = FmtDate(fuelExpires - blue.os.GetWallclockTime(), 'ns')
        else:
            text = ''
        self.fuelColumnLabel.text = text

    def PopulateReinforcementTimeColumn(self):
        self.reinforcementTimeColumn.Flush()
        day, hour = self.controller.GetReinforcementTime()
        self.reinforcementTimeColumn.hint = ''
        dayText, hourText = GetDayAndHourText(day, hour)
        textList = [hourText]
        text = '<br>'.join(textList)
        label = Label(parent=self.reinforcementTimeColumn, text=text, align=uiconst.CENTERLEFT, left=6, state=uiconst.UI_DISABLED)
        nextDay, nextHour = self.controller.GetNextReinforcementTime()
        if None not in (nextDay, nextHour):
            texturePath = 'res:/UI/Texture/classes/StructureBrowser/notSameSchedule.png'
            hint = GetByLabel('UI/Structures/Browser/NotSameScheduleHint')
            diffSprite = Sprite(name='changeReinforceTime', parent=self.reinforcementTimeColumn, align=uiconst.CENTERRIGHT, pos=(2, 2, 16, 16), iconSize=16, texturePath=texturePath, opacity=0.75, hint=hint)
            diffSprite.DelegateEvents(self)
            self.reinforcementTimeColumn.state = uiconst.UI_NORMAL
            self.reinforcementTimeColumn.DelegateEvents(self)
            self.reinforcementTimeColumn.LoadTooltipPanel = self.ChangedReinforcementTimes

    def PopulateExtraColumns(self):
        structureServicesChecked = self.node.structureServicesChecked
        if structureServicesChecked == ALL_SERVICES:
            return
        for serviceName in structureServicesChecked:
            serviceData = serviceDataByNameID.get(serviceName)
            if serviceData and serviceData.serviceID == structures.SERVICE_JUMP_BRIDGE:
                self._PopulateLiquidOzoneColumn(serviceName)
                break

    def _PopulateLiquidOzoneColumn(self, serviceName):
        variableName = StructureEntryMyCorp.GetColumnVariableName(serviceName)
        columnLabel = getattr(self, variableName, None)
        if columnLabel:
            liquidOzone = self.controller.GetLiquidOzoneQty()
            if liquidOzone:
                text = FmtAmt(liquidOzone)
            else:
                text = ''
            columnLabel.align = uiconst.CENTERRIGHT
            columnLabel.text = text

    def ChangedReinforcementTimes(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        day, hour = self.controller.GetReinforcementTime()
        dayText, hourText = GetDayAndHourText(day, hour)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/StructureBrowser/CurrentReinforcementTimes'), colSpan=tooltipPanel.columns, bold=True)
        if dayText:
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/StructureBrowser/ReinforcementWeekday'))
            tooltipPanel.AddLabelMedium(text=dayText)
            tooltipPanel.FillRow()
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/StructureBrowser/ReinforcementTime'))
        tooltipPanel.AddLabelMedium(text=hourText)
        tooltipPanel.FillRow()
        tooltipPanel.AddSpacer(height=10, colSpan=tooltipPanel.columns)
        nextDay, nextHour = self.controller.GetNextReinforcementTime()
        nextDayText, nextHourText = GetDayAndHourText(nextDay, nextHour)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/StructureBrowser/PendingReinforcementTimes'), colSpan=tooltipPanel.columns, bold=True)
        if nextDayText:
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/StructureBrowser/ReinforcementWeekday'))
            tooltipPanel.AddLabelMedium(text=nextDayText)
            tooltipPanel.FillRow()
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/StructureBrowser/ReinforcementTime'))
        tooltipPanel.AddLabelMedium(text=nextHourText)
        tooltipPanel.FillRow()
        tooltipPanel.AddSpacer(height=10, colSpan=tooltipPanel.columns)
        nextApply = self.controller.GetGetNextApplyReinforcementTime()
        if nextApply < gametime.GetWallclockTime():
            text = GetByLabel('UI/StructureBrowser/ChangesArePending')
            tooltipPanel.AddLabelMedium(text=text, colSpan=tooltipPanel.columns)
        else:
            text = GetByLabel('UI/StructureBrowser/TakesEffect')
            date = FmtDate(nextApply)
            tooltipPanel.AddLabelMedium(text=text, colSpan=tooltipPanel.columns)
            tooltipPanel.AddLabelMedium(text=date, colSpan=tooltipPanel.columns)

    def GetDragData(self):
        nodesSelected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        data = []
        for eachNode in nodesSelected:
            k = KeyVal(__guid__='xtriui.ListSurroundingsBtn', itemID=eachNode.controller.GetItemID(), typeID=eachNode.controller.GetTypeID(), label=StripTags(eachNode.controller.GetCleanName().replace('<br>', '-')), isMyCorpStructureEntry=True)
            data.append(k)

        return data

    def GetMenu(self):
        selectedNodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        numSelectedNodes = len(selectedNodes)
        itemID = self.controller.GetItemID()
        typeID = self.controller.GetTypeID()
        m = []
        if numSelectedNodes == 1:
            if self.controller.CanUnanchor():
                m.append([MenuLabel('UI/StructureBrowser/Decommission'), sm.GetService('structureDeployment').Unanchor, [itemID, typeID]])
            elif self.controller.CanCancelUnanchor():
                m.append([MenuLabel('UI/StructureBrowser/CancelDecommission'), sm.GetService('structureDeployment').CancelUnanchor, [itemID, typeID]])
            if session.corprole & const.corpRoleStationManager and not IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                m.append([MenuLabel('UI/StructureBrowser/SetStructureDescription'), self.SetDescription, []])
            if itemID == session.shipid and self.IsSchedulingAvailableOption(typeID, itemID):
                m.append([GetByLabel('UI/Moonmining/OpenSchedulingWnd'), self.OpenSchedulingWindow, [itemID]])
        m += self._GetReinforcementTimeOptions(selectedNodes)
        if numSelectedNodes > 1:
            setProfileMenu = MenuLabel('UI/StructureBrowser/SetProfileMany', {'numSelected': numSelectedNodes})
        else:
            setProfileMenu = MenuLabel('UI/StructureBrowser/SetProfile')
            m += GetMenuService().GetMenuFromItemIDTypeID(itemID=itemID, typeID=typeID)
        m += [[setProfileMenu, ('isDynamic', self._GetProfilesMenu, (selectedNodes,))]]
        return m

    def IsSchedulingAvailableOption(self, structureTypeID, structureID):
        if evetypes.GetGroupID(structureTypeID) != invConst.groupStructureDrillingPlatform:
            return False
        return bool(sm.GetService('structureSettings').CharacterHasService(structureID, structures.SERVICE_MOONMINING))

    def OpenSchedulingWindow(self, itemID, *args):
        GetSchedulingService().OpenSchedulingWndForStructure(itemID)

    def _GetReinforcementTimeOptions(self, selectedNodes):
        nonDockableStructureControllers = [ x.controller for x in selectedNodes if not IsDockableStructure(x.controller.GetTypeID()) ]
        dockableStructureControllers = [ x.controller for x in selectedNodes if IsDockableStructure(x.controller.GetTypeID()) ]
        addPostfix = bool(nonDockableStructureControllers and nonDockableStructureControllers)
        singleLabelPath = 'UI/StructureBrowser/SetReinforcementTime'
        controllerGroups = [(dockableStructureControllers, 'UI/StructureBrowser/SetReinforcementTimeDockable' if addPostfix else singleLabelPath), (nonDockableStructureControllers, 'UI/StructureBrowser/SetReinforcementTimeNonDockable' if addPostfix else singleLabelPath)]
        m = []
        for selectedControllers, menuLabelPath in controllerGroups:
            if not selectedControllers:
                continue
            day, hour = GetMostFrequentReinforcementTime(selectedControllers)
            nDay, nHour, nextApplies, changedStructures = GetNextReinforcementTimes(selectedControllers)
            doAllStructuresHavePendingChanges = len(selectedControllers) == len(changedStructures)
            hour = hour if hour is not None else structures.DEFAULT_REINFORCE_HOUR
            day = day if day is not None else structures.DEFAULT_REINFORCE_WEEKDAY
            reinforceTimers = ReinforcementBundle(reinforceWeekday=day, reinforceHour=hour, nextReinforceWeekday=nDay, nextReinforceHour=nHour, nextReinforceApply=nextApplies)
            menuLabel = MenuLabel(menuLabelPath)
            infoOnStructures = [ (x.GetItemID(), x.GetSolarSystemID(), x.GetTypeID()) for x in selectedControllers ]
            funcArgs = (infoOnStructures,
             reinforceTimers,
             changedStructures,
             doAllStructuresHavePendingChanges)
            m += [(menuLabel, self.SetReinforcementTime, funcArgs)]

        return m

    def _GetProfilesMenu(self, selectedNodes):
        selectedStructureIDs = [ x.controller.GetItemID() for x in selectedNodes ]
        allStructureProfileController = sm.GetService('structureControllers').GetAllStructuresProfileController()
        allCorpProfiles = allStructureProfileController.GetProfiles()

        def UpdateProfileIDForStructures(profileID):
            allStructureProfileController.UpdateProfileIDForStructures(profileID, selectedStructureIDs)

        m = []
        for profileID, profileController in allCorpProfiles.iteritems():
            name = profileController.GetProfileName()
            m.append((name.lower(), (name, UpdateProfileIDForStructures, (profileID,))))

        m = SortListOfTuples(m)
        return m

    def SetDescription(self, *args):
        itemID = self.controller.GetItemID()
        structureName = GetShowInfoLink(self.controller.GetTypeID(), cfg.evelocations.Get(itemID).name, itemID)
        desc = sm.RemoteSvc('structureDirectory').GetStructureDescription(itemID)
        wnd = SetStrucureDescriptionWnd.Open(windowID='setStructureDescription_%s' % itemID, structureID=itemID, currentName=structureName, currentDesc=desc)

    def SetReinforcementTime(self, infoOnStructures, reinforceTimers, changedStructures, doAllStructuresHavePendingChanges):
        from eve.client.script.ui.structure.structureBrowser.reinforcementTimeWnd import ReinforcementTimeWnd
        wnd = ReinforcementTimeWnd.GetIfOpen()
        if wnd and not wnd.destroyed:
            wnd.LoadInfo(infoOnStructures, reinforceTimers, changedStructures, doAllStructuresHavePendingChanges)
            wnd.Maximize()
        else:
            ReinforcementTimeWnd.Open(infoOnStructures=infoOnStructures, reinforceTimers=reinforceTimers, changedStructures=changedStructures, doAllStructuresHavePendingChanges=doAllStructuresHavePendingChanges)

    def OnStructureStateChanged(self, structureID):
        self.LoadUI()

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        BaseListEntryCustomColumns.Close(self)

    @staticmethod
    def GetColumnSortValues(controller, slimProfileController, structureServicesChecked):
        ret = ((controller.GetState(), controller.IsLowPower()),
         controller.GetNumJumps(),
         controller.GetSecurity(),
         '%s %s ' % (controller.GetSystemName(), StripTags(controller.GetName()).lower()),
         len(controller.GetServices()),
         controller.GetFuelExpiry(),
         controller.GetReinforcementTime())
        if structureServicesChecked != ALL_SERVICES:
            for serviceName in structureServicesChecked:
                serviceData = serviceDataByNameID.get(serviceName)
                if serviceData and serviceData.serviceID == structures.SERVICE_JUMP_BRIDGE:
                    ret = ret + (controller.GetLiquidOzoneQty(),)
                    break

        return ret

    @staticmethod
    def GetSortValue(node, by, sortDirection, idx):
        return (node.columnSortValues[idx],) + tuple(node.columnSortValues)

    @staticmethod
    def GetHeaders(structureServicesChecked):
        extraHeaders = StructureEntryMyCorp.GetExtraHeaders(structureServicesChecked)
        return [GetByLabel('UI/Structures/Browser/HeaderState'),
         GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Common/Security'),
         GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Structures/Browser/HeaderServices'),
         GetByLabel('UI/Structures/Browser/HeaderFuel'),
         GetByLabel('UI/Structures/Browser/HeaderReinforcementTime')] + extraHeaders

    @staticmethod
    def GetExtraHeaders(structureServicesChecked):
        extraHeaders = []
        if structureServicesChecked == ALL_SERVICES:
            return []
        for serviceName in structureServicesChecked:
            serviceData = serviceDataByNameID.get(serviceName)
            if serviceData and serviceData.serviceID == structures.SERVICE_JUMP_BRIDGE:
                extraHeaders += StructureEntryMyCorp._GetLiquidOzoneHeader()
                break

        return extraHeaders

    @staticmethod
    def _GetLiquidOzoneHeader():
        header = evetypes.GetName(invConst.typeLiquidOzone)
        return [header]

    @staticmethod
    def GetDynamicHeight(node, width):
        return HEIGHT

    @staticmethod
    def GetFixedColumns():
        numServices = len({x for x in stationServiceConst.serviceData if x.name not in UPWELL_STANDARD_SERVICES})
        numServices += 1
        return {GetByLabel('UI/Structures/Browser/HeaderServices'): ICONSIZE * numServices + 2}

    @staticmethod
    def GetColWidths(node, idx = None):
        controller = node.controller
        widths = []
        getAllWidths = idx is None
        if getAllWidths or idx == 0:
            widths.append(STATE_ICON_SIZE + 10)
        if getAllWidths or idx == 1:
            jumpText = unicode(controller.GetNumJumpsText())
            widths.append(uicore.font.MeasureTabstops([(jumpText,) + LABEL_PARAMS])[0])
        if getAllWidths or idx == 2:
            securityText = unicode(controller.GetSecurity())
            widths.append(uicore.font.MeasureTabstops([(securityText,) + LABEL_PARAMS])[0])
        if getAllWidths or idx == 3:
            nameToUse = max(StripTags(controller.GetName(), ignoredTags=('br',)).split('<br>'), key=len)
            widths.append(uicore.font.MeasureTabstops([(nameToUse,) + LABEL_PARAMS])[0] + HEIGHT - 4)
        return widths

    @staticmethod
    def GetColumnVariableName(serviceName):
        return 'column_%s' % serviceName


class StructureEntryMyCorpAllProfiles(StructureEntryMyCorp):

    def AddProfileNameColumn(self):
        self.profileNameColumnLabel = self.AddColumnText()

    def PopulateProfileNameColumn(self):
        profileName = self._GetProfileName(self.slimProfileController)
        self.profileNameColumnLabel.text = profileName

    @staticmethod
    def _GetProfileName(slimProfileController):
        if slimProfileController:
            profileName = slimProfileController.GetProfileName()
        else:
            profileName = ''
        return profileName

    @staticmethod
    def GetColumnSortValues(controller, slimProfileController, structureServicesChecked):
        baseSortValues = StructureEntryMyCorp.GetColumnSortValues(controller, slimProfileController, structureServicesChecked)
        return (StructureEntryMyCorpAllProfiles._GetProfileName(slimProfileController).lower(),) + baseSortValues

    @staticmethod
    def GetHeaders(structureServicesChecked):
        baseHeaders = StructureEntryMyCorp.GetHeaders(structureServicesChecked)
        return [GetByLabel('UI/Structures/Browser/HeaderProfileName')] + baseHeaders

    @staticmethod
    def GetColWidths(node, idx = None):
        widths = []
        getAllWidths = idx is None
        if getAllWidths or idx == 0:
            profileName = StructureEntryMyCorpAllProfiles._GetProfileName(node.slimProfileController)
            widths.append(uicore.font.MeasureTabstops([(profileName,) + LABEL_PARAMS])[0])
        if getAllWidths:
            widths += StructureEntryMyCorp.GetColWidths(node, idx)
        elif idx > 0:
            widths += StructureEntryMyCorp.GetColWidths(node, idx - 1)
        return widths


class SetStrucureDescriptionWnd(Window):
    __guid__ = 'SetStrucureDescriptionWnd'
    default_width = 400
    default_height = 350
    default_minSize = (300, 200)
    default_windowID = 'setStructureDescription'
    default_maxLength = MAX_STRUCTURE_BIO_LENGTH
    default_captionLabelPath = 'UI/StructureBrowser/SetStructureDescription'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.structureID = attributes.structureID
        self.currentDesc = attributes.get('currentDesc', '')
        currentName = attributes.get('currentName', '')
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        self.maxLength = attributes.get('maxLength', self.default_maxLength)
        self.ConstructLayout()
        self.SetText(currentName, self.currentDesc)

    def SetText(self, structureName, desc):
        self.structureNameLabel.text = structureName
        self.descField.SetValue(desc)

    def ConstructLayout(self):
        cont = Container(parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        self.structureNameLabel = EveLabelMedium(name='structureName', parent=cont, text='', align=uiconst.TOTOP, top=6, padLeft=4, state=uiconst.UI_NORMAL)
        EveLabelSmall(name='titleHeader', parent=cont, text=GetByLabel('UI/InfoWindow/TabNames/Description'), align=uiconst.TOTOP, top=6, padLeft=4)
        self.descField = EditPlainText(parent=cont, padding=(4, 2, 4, 4), maxLength=self.maxLength, showattributepanel=True)

    def Confirm(self, *args):
        newDesc = self.descField.GetValue()
        newDesc.strip()
        if newDesc != self.currentDesc:
            sm.RemoteSvc('structureDirectory').SetStructureDescription(self.structureID, newDesc)
        self.Close()

    def Cancel(self, *args):
        self.CloseByUser()


def GetMostFrequentReinforcementTime(controllers):
    controllersByReinforcementTime = defaultdict(int)
    for eachController in controllers:
        reinforcementTime = eachController.GetReinforcementTime()
        if reinforcementTime != (None, None):
            controllersByReinforcementTime[reinforcementTime] += 1

    day = hour = None
    if controllersByReinforcementTime:
        day, hour = max(controllersByReinforcementTime.iterkeys(), key=lambda k: controllersByReinforcementTime[k])
    return (day, hour)


def GetNextReinforcementTimes(controllers):
    controllersByNewReinforcementTime = defaultdict(set)
    for eachController in controllers:
        nextReinforcementTime = eachController.GetNextReinforcementTime()
        if nextReinforcementTime != (None, None):
            nextApply = eachController.GetGetNextApplyReinforcementTime()
            key = nextReinforcementTime + (nextApply,)
            controllersByNewReinforcementTime[key].add((eachController.GetItemID(), eachController.GetTypeID()))

    day = hour = applyDate = None
    if not controllersByNewReinforcementTime:
        return (day,
         hour,
         applyDate,
         set())
    if len(controllersByNewReinforcementTime) == 1:
        day, hour, applyDate = controllersByNewReinforcementTime.keys()[0]
    structuresWithChangedReinforcementTimes = set.union(*controllersByNewReinforcementTime.values())
    return (day,
     hour,
     applyDate,
     structuresWithChangedReinforcementTimes)
