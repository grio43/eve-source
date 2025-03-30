#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetEditModeContainer.py
import blue
import eveicon
import evetypes
import inventorycommon
import localization
from bannedwords.client import bannedwords
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.lib.const import ixLocationID
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst, Align
from carbonui.button.group import ButtonGroup
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from dogma.const import attributePlanetRestriction
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.planet import planetConst
from eve.client.script.ui.shared.planet.colonyTemplateWindow import ColonyTemplateWindow
from eve.client.script.ui.shared.planet.planetUtil import iconsByGroupID, IsSerenity
from eve.client.script.ui.shared.planet.templatePreviewWindow import TemplatePreviewWindow
from eve.client.script.ui.shared.planet.templateSavingUtil import ConfirmExportWnd, SaveToLocalFile
from eveplanet.client.templates.templateConst import TemplatePinDataDictKeys, TemplateLinkDataDictKeys, TemplateRouteDataDictKeys, TemplateDictKeys
from eve.common.script.planet.planetUtil import CMDCTRSTRING
from eve.common.lib import appConst
from eve.common.script.sys.eveCfg import InShipInSpace
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
try:
    import json
except ImportError:
    import simplejson as json

ICON_SIZE = 24
TYPE_PLACELINK = -1
TYPE_DECOMMISSION = -3
tooltipByGroupID = {appConst.groupExtractionControlUnitPins: GetByLabel('UI/PI/BuildTooltips/ECU'),
 appConst.groupProcessPins: GetByLabel('UI/PI/BuildTooltips/ProcessorCommonText'),
 appConst.groupStoragePins: GetByLabel('UI/PI/BuildTooltips/Storage'),
 appConst.groupSpaceportPins: GetByLabel('UI/PI/BuildTooltips/Launchpad'),
 appConst.groupPlanetaryLinks: GetByLabel('UI/PI/BuildTooltips/Link'),
 appConst.groupCommandPins: GetByLabel('UI/PI/BuildTooltips/CommandCenter')}

class PlanetEditModeContainer(ContainerAutoSize):
    default_name = 'planetEditMode'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_HIDDEN
    __notifyevents__ = ['OnEditModeChanged',
     'OnEditModeBuiltOrDestroyed',
     'OnPlanetCommandCenterDeployedOrRemoved',
     'OnItemChange',
     'OnSessionChanged',
     'OnPlanetUIStateChanged']
    COLOR_ENABLED = (1.0, 1.0, 1.0, 1.0)
    COLOR_DISABLED = (0.7, 0.7, 0.7, 0.8)

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.activeBuildEntry = None
        self.entriesByTypeID = {}
        self.exportClipboardBtn = None
        self.exportFileBtn = None
        self.buildContainer = ContainerAutoSize(parent=self, name='buildContainer', align=uiconst.TOTOP)
        self.CreateLayout()
        sm.RegisterNotify(self)

    def CreateLayout(self):
        isCommandCenterPresent = self.IsCommandCenterPresent()
        groupIDs = self._GetPinGroupIDs(isCommandCenterPresent)
        for groupID in groupIDs:
            typeIDs = self.GetStructuresForGroup(groupID)
            for typeID in typeIDs:
                self._ConstructPlacePinEntry(groupID, typeID)

        if isCommandCenterPresent:
            self._ConstructToolEntries()
        self._ConstructTemplateButtons()

    def _GetPinGroupIDs(self, isCommandCenterPresent):
        if isCommandCenterPresent:
            return [appConst.groupExtractionControlUnitPins,
             appConst.groupProcessPins,
             appConst.groupStoragePins,
             appConst.groupSpaceportPins]
        else:
            return [appConst.groupCommandPins]

    def _ConstructToolEntries(self):
        self.entriesByTypeID[TYPE_PLACELINK] = PlaceLinkEntry(parent=self.buildContainer, padTop=8)
        self.entriesByTypeID[TYPE_DECOMMISSION] = DecommissionEntry(parent=self.buildContainer)

    def _ConstructTemplateButtons(self):
        self.templateButtonGroup = ButtonGroup(parent=self.buildContainer, align=Align.TOTOP, orientation=uiconst.VERTICAL, top=8)
        if self.IsCommandCenterPresent():
            self.exportFileBtn = self.templateButtonGroup.AddButton(label=GetByLabel('UI/PI/ExportToFile'), func=lambda *args: self.SaveTemplateToFile(), texturePath=eveicon.export)
        self.templateButtonGroup.AddButton(label=GetByLabel('UI/PI/ShowTemplateWindow'), func=self.ShowTemplateWindow, texturePath=eveicon.open_window)

    def UpdateButtons(self, inEditMode):
        if self.exportClipboardBtn is not None:
            if inEditMode:
                self.exportClipboardBtn.Disable()
            else:
                self.exportClipboardBtn.Enable()
        if self.exportFileBtn is not None:
            if inEditMode:
                self.exportFileBtn.Disable()
            else:
                self.exportFileBtn.Enable()

    def _ConstructPlacePinEntry(self, groupID, typeID):
        isDisabledHint = self.GetBuildEntryDisabledHint(groupID, typeID)
        entry = PlacePinEntry(parent=self.buildContainer, typeID=typeID, isDisabledHint=isDisabledHint)
        self.entriesByTypeID[typeID] = entry

    def IsCommandCenterPresent(self):
        commandPinObject = sm.GetService('planetUI').GetCurrentPlanet().GetCommandCenterForCharacter(session.charid)
        isCommandCenterPresent = commandPinObject is not None and not commandPinObject.IsInEditMode()
        return isCommandCenterPresent

    def GetStructuresForGroup(self, groupID):
        planetTypeID = sm.GetService('planetUI').typeID
        godma = sm.GetService('godma')
        structureIDs = set()
        for typeID in evetypes.GetTypeIDsByGroup(groupID):
            typeRestriction = godma.GetTypeAttribute(typeID, attributePlanetRestriction)
            if typeRestriction and int(typeRestriction) != planetTypeID:
                continue
            if not evetypes.IsPublished(typeID):
                continue
            structureIDs.add(typeID)

        return sorted(structureIDs, key=evetypes.GetBasePrice)

    def GetBuildEntryDisabledHint(self, groupID, typeID):
        if groupID == appConst.groupCommandPins:
            planetID = sm.GetService('planetUI').planetID
            planetSolarSystemID = sm.GetService('map').GetPlanetInfo(planetID).solarSystemID
            if not InShipInSpace() or session.solarsystemid != planetSolarSystemID:
                return localization.GetByLabel('UI/PI/Common/CannotBuildLocation')
            planetRows = sm.GetService('planetSvc').GetMyPlanets()
            skillSvc = sm.GetService('skills')
            if len(planetRows) > 0:
                interplanetaryConsolidationSkillLevel = skillSvc.GetEffectiveLevel(appConst.typeInterplanetaryConsolidation) or 0
                if interplanetaryConsolidationSkillLevel < len(planetRows):
                    if interplanetaryConsolidationSkillLevel < 5:
                        hint = localization.GetByLabel('UI/PI/Common/CannotBuildMaxColoniesTrain', skillName=evetypes.GetName(appConst.typeInterplanetaryConsolidation))
                    else:
                        hint = localization.GetByLabel('UI/PI/Common/CannotBuildMaxColonies')
                    return hint
            skillsRequired = skillSvc.GetRequiredSkills(typeID)
            for skillTypeID, requiredLevel in skillsRequired.iteritems():
                myLevel = skillSvc.GetEffectiveLevel(skillTypeID) or 0
                if myLevel < requiredLevel:
                    hint = localization.GetByLabel('UI/PI/Common/CannotBuildSkillNeeded', skillName=evetypes.GetName(skillTypeID), skillLevel=int(requiredLevel))
                    return hint

            if session.shipid is None:
                hint = localization.GetByLabel('UI/PI/Common/CannotBuildNoCommandCenter', typeName=evetypes.GetName(typeID))
                return hint
            inv = sm.GetService('invCache').GetInventoryFromId(session.shipid)
            commandCenterID = None
            if inv:
                invList = inv.List(inventorycommon.const.flagSpecializedCommandCenterHold)
                invList.extend(inv.List(inventorycommon.const.flagCargo))
                invList.extend(inv.List(inventorycommon.const.flagColonyResourcesHold))
                for item in invList:
                    if item.typeID == typeID:
                        commandCenterID = item.itemID
                        break

            if commandCenterID is None:
                hint = localization.GetByLabel('UI/PI/Common/CannotBuildNoCommandCenter', typeName=evetypes.GetName(typeID))
                return hint

    def OnPlanetCommandCenterDeployedOrRemoved(self):
        self.ResetBuildbuttons()

    def OnPlanetUIStateChanged(self, state, oldState):
        typeID = self._GetTypeIDByState(state)
        for _typeID, entry in self.entriesByTypeID.iteritems():
            if typeID == _typeID:
                entry.Select()
            else:
                entry.Deselect()

    def _GetTypeIDByState(self, state):
        if state == planetConst.STATE_BUILDPIN:
            return sm.GetService('planetUI').myPinManager.newPinType
        if state in (planetConst.STATE_CREATELINKSTART, planetConst.STATE_CREATELINKEND):
            return TYPE_PLACELINK
        if state == planetConst.STATE_DECOMMISSION:
            return TYPE_DECOMMISSION

    def OnItemChange(self, item, change, location):
        locationIdx = ixLocationID
        if session.shipid not in (item[locationIdx], change.get(locationIdx, 'No location change')):
            return
        if evetypes.GetGroupID(item.typeID) == appConst.groupCommandPins:
            self.ResetBuildbuttons()

    def ResetBuildbuttons(self):
        animations.FadeOut(self.buildContainer, duration=0.25, sleep=True)
        if not self or self.destroyed:
            return
        self.buildContainer.Flush()
        self.activeBuildEntry = None
        self.entriesByTypeID = {}
        self.CreateLayout()
        blue.pyos.synchro.SleepWallclock(300)
        if not self or self.destroyed:
            return
        animations.FadeIn(self.buildContainer, duration=0.25, sleep=True)

    def SaveTemplateToFile(self):
        jsonText = self._GetJsonInfoToStore('UI/PI/SaveNewTemplate', 'UI/PI/SaveTemplate')
        if jsonText is None:
            return
        self.ShowTemplateWindow()
        SaveToLocalFile(jsonText, encoding='unicode-escape')

    def CopyTemplateToClipboard(self):
        jsonText = self._GetJsonInfoToStore('UI/PI/CopyToClipboard', 'UI/PI/CopyToClipboard')
        if jsonText is None:
            return
        blue.pyos.SetClipboardData(jsonText)
        ShowQuickMessage(localization.GetByLabel('UI/PI/Copied'))

    def _GetJsonInfoToStore(self, captionPath, okPath):
        if not self.Verify_No_CmdCtr_Link():
            return
        if sm.GetService('planetUI').inEditMode:
            ShowQuickMessage(localization.GetByLabel('UI/PI/CannotExportWhileEditing'))
            return
        defaultNote = u'{0} {1}'.format(cfg.eveowners.Get(session.charid).name, FmtDate(blue.os.GetSimTime()))
        wnd = ConfirmExportWnd.Open(defaultNote=defaultNote, captionPath=captionPath, okPath=okPath)
        wnd.SetParent(uicore.layer.planet)
        wnd.ShowDialog(modal=True)
        retval = wnd.result
        if retval is None:
            return
        note = retval.get('note', '')
        bannedwords.check_words_allowed(note)
        if IsSerenity():
            retval.get('note', '')
            includeCmdCtr = retval.get('includeCmdCtr', False)
        else:
            includeCmdCtr = False
        planetID = sm.GetService('planetUI').planetID
        if not planetID:
            ShowQuickMessage(localization.GetByLabel('UI/PI/FailedTosave'))
            return
        planet = sm.GetService('planetSvc').GetClientPlanet(planetID)
        pins = planet.colony.colonyData.pins
        links = planet.colony.colonyData.links
        routes = planet.colony.colonyData.routes
        pinIDs = {}
        cmdCtrLvl = planet.colony.colonyData.level
        pinExtracted = []
        linkExtracted = []
        routeExtracted = []
        if includeCmdCtr:
            self.ExtractCmdCenterPin(pinExtracted, pinIDs, pins)
        self.ExtractNormalPins(pinExtracted, pinIDs, pins)
        for link in links.values():
            linkExtracted.append({TemplateLinkDataDictKeys.Source: pinIDs[link.endpoint1.id],
             TemplateLinkDataDictKeys.Destination: pinIDs[link.endpoint2.id],
             TemplateLinkDataDictKeys.Level: link.level})

        for route in routes.values():
            path = []
            for node in route.path:
                path.append(pinIDs[node])

            routeExtracted.append({TemplateRouteDataDictKeys.Path: path,
             TemplateRouteDataDictKeys.ItemType: route.GetType(),
             TemplateRouteDataDictKeys.ItemQuantity: route.GetQuantity()})

        fullOutput = {TemplateDictKeys.Comments: note if note is not None else '',
         TemplateDictKeys.CmdCenterLV: cmdCtrLvl,
         TemplateDictKeys.PlanetType: planet.GetPlanetTypeID(),
         TemplateDictKeys.Diameter: planet.radius * 2 / 1000,
         TemplateDictKeys.PinData: pinExtracted,
         TemplateDictKeys.LinkData: linkExtracted,
         TemplateDictKeys.RouteData: routeExtracted}
        jsonText = json.dumps(obj=fullOutput, sort_keys=True).decode('unicode-escape')
        return jsonText

    def Verify_No_CmdCtr_Link(self):
        planet = sm.GetService('planetUI').GetCurrentPlanet()
        links = planet.colony.colonyData.links
        for link in links.itervalues():
            if link.endpoint1.id == planet.colony.colonyData.commandPin.id or link.endpoint2.id == planet.colony.colonyData.commandPin.id:
                sm.GetService('gameui').MessageBox(text=localization.GetByLabel('UI/PI/LinkWithCmdCtrNotAvailable'), buttons=uiconst.OK, icon=uiconst.INFO)
                return False

        return True

    def ExtractNormalPins(self, pinExtracted, pinIDs, pins):
        anotherCounter = 1
        for pin in pins.itervalues():
            if pin.IsCommandCenter():
                continue
            pinExtracted.append(self._GetPinInfo(pin))
            pinIDs[pin.id] = anotherCounter
            anotherCounter += 1

    def ExtractCmdCenterPin(self, pinExtracted, pinIDs, pins):
        for pin in pins.itervalues():
            if not pin.IsCommandCenter():
                continue
            pinExtracted.append(self._GetPinInfo(pin))
            pinIDs[pin.id] = CMDCTRSTRING
            return

    def _GetPinInfo(self, pin):
        products = pin.GetProducts()
        pinInfo = {TemplatePinDataDictKeys.PinTypeID: pin.typeID,
         TemplatePinDataDictKeys.Lat: round(pin.latitude, 5),
         TemplatePinDataDictKeys.Longi: round(pin.longitude, 5),
         TemplatePinDataDictKeys.Product: products.keys()[0] if products else None,
         TemplatePinDataDictKeys.ExtractorHeadCount: pin.GetNumHeads() if pin.IsExtractor() else 0}
        return pinInfo

    def ShowTemplateWindow(self, *args):
        instance = ColonyTemplateWindow.GetIfOpen()
        if instance:
            instance.Close()
        wnd = TemplatePreviewWindow.GetIfOpen()
        if wnd:
            wnd.Close()
        ColonyTemplateWindow.Open(target=self)

    def OnSessionChanged(self, isRemote, sess, change):
        self.ResetBuildbuttons()

    def Close(self, *args):
        instance = ColonyTemplateWindow.GetIfOpen()
        if instance:
            instance.Close()
            ColonyTemplateWindow.Open(target=None)
        super(type(self), self).Close()


class BaseEditModeEntry(Container):
    default_name = 'BaseEditModeEntry'
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_height = 24

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isDisabledHint = attributes.isDisabledHint
        self.isSelected = False
        self.isEnabled = True
        self.icon = GlowSprite(parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 22, 22), texturePath=self.GetTexturePath(), state=uiconst.UI_DISABLED)
        EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, text=self.GetName(), state=uiconst.UI_DISABLED, left=26)
        self.hoverBG = ListEntryUnderlay(bgParent=self)

    def GetName(self):
        pass

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        if self.isEnabled:
            self.ClickFunc()

    def ClickFunc(self):
        pass

    def GetTexturePath(self):
        pass

    def OnMouseEnter(self, *args):
        if self.isEnabled:
            self.hoverBG.hovered = True
            if not self.isSelected:
                PlaySound(uiconst.SOUND_ENTRY_HOVER)
                self.icon.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.hoverBG.hovered = False
        if not self.isSelected:
            self.icon.OnMouseExit()

    def Select(self):
        self.isSelected = True
        self.hoverBG.Select()
        self.icon.OnMouseEnter()

    def Deselect(self):
        if self.isSelected:
            self.isSelected = False
            self.hoverBG.Deselect()
            self.icon.OnMouseExit()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.GetTooltipText(), wrapWidth=250, colSpan=2)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def GetTooltipText(self):
        return ''


class PlacePinEntry(BaseEditModeEntry):
    default_name = 'PlacePinEntry'

    def ApplyAttributes(self, attributes):
        self.typeID = attributes.typeID
        BaseEditModeEntry.ApplyAttributes(self, attributes)

    def GetName(self):
        return evetypes.GetName(self.typeID)

    def ClickFunc(self, *args):
        sm.GetService('planetUI').myPinManager.PlacePinOnNextClick(self.typeID)

    def GetTexturePath(self):
        if self.typeID in planetConst.TYPEIDS_PROCESSORS_ADVANCED:
            return 'res:/UI/Texture/Planet/icons/processorAdvanced.png'
        elif self.typeID in planetConst.TYPEIDS_PROCESSORS_HIGHTECH:
            return 'res:/UI/Texture/Planet/icons/processorHighTech.png'
        else:
            groupID = self.GetGroupID()
            return iconsByGroupID[groupID]

    def GetGroupID(self):
        return evetypes.GetGroupID(self.typeID)

    def GetTooltipText(self):
        hint = tooltipByGroupID[self.GetGroupID()]
        if self.typeID in planetConst.TYPEIDS_PROCESSORS_BASIC:
            hint += '\n\n' + GetByLabel('UI/PI/BuildTooltips/BasicProcessor')
        elif self.typeID in planetConst.TYPEIDS_PROCESSORS_ADVANCED:
            hint += '\n\n' + GetByLabel('UI/PI/BuildTooltips/AdvancedProcessor')
        elif self.typeID in planetConst.TYPEIDS_PROCESSORS_HIGHTECH:
            hint += '\n\n' + GetByLabel('UI/PI/BuildTooltips/HighTechProcessor')
        if self.isDisabledHint:
            hint += '\n\n<color=red>%s</color>' % self.isDisabledHint
        return hint

    def GetMenu(self, *args):
        includeMarketDetails = self.GetGroupID() == appConst.groupCommandPins
        return sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=includeMarketDetails)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        BaseEditModeEntry.LoadTooltipPanel(self, tooltipPanel, *args)
        buildCost = self.GetBuildCost()
        if buildCost:
            iskPrice = FmtISK(buildCost, showFractionsAlways=False)
            label = GetByLabel('UI/PI/Common/BuildCost')
            tooltipPanel.AddLabelMedium(text='%s: <b>%s</b>' % (label, iskPrice), colSpan=2, cellPadding=(0, 12, 0, 0))
        powerUsage = self.GetPowerUsage()
        if powerUsage:
            powerTxt = GetByLabel('UI/PI/Common/MegaWattsAmount', amount=int(powerUsage))
            powerUsedTxt = GetByLabel('UI/PI/Common/PowerUsage')
            tooltipPanel.AddLabelMedium(text='%s: <b>%s</b>' % (powerUsedTxt, powerTxt), colSpan=2, cellPadding=(0, 12, 0, 0))
        cpuUsage = self.GetCpuUsage()
        if cpuUsage:
            cpuTxt = GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=int(cpuUsage))
            cpuUsedTxt = GetByLabel('UI/PI/Common/CpuUsage')
            tooltipPanel.AddLabelMedium(text='%s: <b>%s</b>' % (cpuUsedTxt, cpuTxt), colSpan=2)

    def GetBuildCost(self):
        if self.GetGroupID() == appConst.groupCommandPins:
            return None
        else:
            return evetypes.GetBasePrice(self.typeID)

    def GetPowerUsage(self):
        return sm.GetService('godma').GetTypeAttribute(self.typeID, appConst.attributePowerLoad)

    def GetCpuUsage(self):
        return sm.GetService('godma').GetTypeAttribute(self.typeID, appConst.attributeCpuLoad)


class PlaceLinkEntry(BaseEditModeEntry):
    default_name = 'PlaceLinkEntry'

    def GetName(self):
        return localization.GetByLabel('UI/PI/Common/CreateLink')

    def ClickFunc(self, *args):
        sm.GetService('planetUI').eventManager.SetStateCreateLinkStart()

    def GetTexturePath(self):
        return 'res:/UI/Texture/Planet/icons/link.png'

    def GetTooltipText(self):
        return GetByLabel('UI/PI/BuildTooltips/Link')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        BaseEditModeEntry.LoadTooltipPanel(self, tooltipPanel)
        tooltipPanel.AddSpacer(height=10)
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/PI/Common/CreateLink'), GetByLabel('UI/PI/Common/CreateLinkShortcut'))


class DecommissionEntry(BaseEditModeEntry):
    default_name = 'DecommissionEntry'

    def GetName(self):
        return localization.GetByLabel('UI/PI/Common/Decommission')

    def ClickFunc(self, *args):
        sm.GetService('planetUI').eventManager.SetStateDecommission()

    def GetTexturePath(self):
        return 'res:/UI/Texture/Planet/icons/decommission.png'

    def GetTooltipText(self):
        return GetByLabel('UI/PI/BuildTooltips/Decommission')
