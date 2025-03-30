#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\capitalnavigation.py
import utillib
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg
from eve.common.script.sys.eveCfg import InShipInSpace
import evetypes
from eve.client.script.ui.util import uix
from eve.client.script.ui.control import eveLabel, eveScroll
import uthread
import blue
import carbonui.const as uiconst
import localization
from eveservices.menu import GetMenuService
from menu import MenuLabel

class CapitalNav(Window):
    default_windowID = 'capitalnav'
    default_captionLabelPath = 'UI/CapitalNavigation/CapitalNavigationWindow/CapitalNavigationLabel'
    default_iconNum = 'res:/ui/Texture/WindowIcons/capitalNavigation.png'
    default_minSize = (350, 200)
    default_height = 300
    __notifyevents__ = ['OnSessionChanged']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.soldict = {}
        topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=30, clipChildren=True)
        eveLabel.EveLabelMedium(parent=topParent, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/OnlinedStarbaseMessage'))
        self.sr.scroll = eveScroll.Scroll(name='scroll', parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.settingsParent = Container(name='settingsParent', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, idx=1, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), clipChildren=1)
        maintabs = [[localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/JumpTo'),
          self.sr.scroll,
          self,
          'jumpto',
          self.sr.scroll], [localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/WithinRange'),
          self.sr.scroll,
          self,
          'inrange',
          self.sr.scroll]]
        shipID = eveCfg.GetActiveShip()
        if shipID and sm.GetService('clientDogmaIM').GetDogmaLocation().GetItem(shipID).groupID == const.groupTitan:
            maintabs.insert(1, [localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/BridgeTo'),
             self.sr.scroll,
             self,
             'bridgeto',
             self.sr.scroll])
        self.sr.maintabs = TabGroup(name='tabparent', parent=self.sr.main, idx=1, tabs=maintabs, groupID='capitaljumprangepanel')

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid' in change:
            self.sr.showing = ''
            self.sr.maintabs.ReloadVisible()

    def _OnClose(self, *args):
        self.soldict = {}

    def Load(self, args):
        self.sr.scroll.sr.id = 'capitalnavigationscroll'
        if args == 'inrange':
            self.ShowInRangeTab()
        elif args == 'jumpto':
            self.ShowJumpBridgeToTab()
        elif args == 'bridgeto':
            self.ShowJumpBridgeToTab(1)
        elif args == 'settings':
            self.ShowSettingsTab()

    def GetSolarSystemsInRange_thread(self, solarSystemID):
        shipID = eveCfg.GetActiveShip()
        if not shipID:
            return
        self.sr.scroll.Load(contentList=[], noContentHint=localization.GetByLabel('UI/Common/GettingData'))
        jumpDriveRange, consumptionType, consumptionAmount = self.GetJumpDriveInfo(shipID)
        inRange = set()
        soldict = self.soldict.get(solarSystemID, None)
        for solID, solData in cfg.mapSystemCache.iteritems():
            if session.solarsystemid2 != solID and solData.securityStatus <= const.securityClassLowSec:
                distance = uix.GetLightYearDistance(solarSystemID, solID, False)
                if distance is not None and distance <= jumpDriveRange:
                    inRange.add(solID)
            self.soldict[solarSystemID] = inRange

        scrolllist = []
        if inRange:
            for solarSystemID in inRange:
                blue.pyos.BeNice()
                if not self or self.destroyed:
                    return
                requiredQty, requiredType = self.GetFuelConsumptionForMyShip(session.solarsystemid2, solarSystemID, consumptionType, consumptionAmount)
                entry = self.GetSolarSystemBeaconEntry(solarSystemID, requiredQty, requiredType, jumpDriveRange)
                if entry:
                    scrolllist.append(entry)

        if not len(scrolllist):
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Common/NothingFound'))
        if self.sr.scroll and scrolllist and self.sr.Get('showing', None) == 'inrange':
            self.sr.scroll.ShowHint('')
            self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
             localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/SecurityColumnHeader'),
             localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/FuelColumnHeader'),
             localization.GetByLabel('UI/Common/Volume'),
             localization.GetByLabel('UI/Common/Distance'),
             localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/JumpTo')])

    def ShowInRangeTab(self):
        if not eveCfg.GetActiveShip():
            return None
        if self.sr.Get('showing', '') != 'inrange':
            self.sr.scroll.Load(contentList=[], noContentHint=localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/CalculatingStellarDistancesMessage'))
            uthread.pool('form.CapitalNav::ShowInRangeTab', self.GetSolarSystemsInRange_thread, session.solarsystemid2)
            self.sr.showing = 'inrange'

    def ShowJumpBridgeToTab(self, isBridge = False):
        showing = 'UI/CapitalNavigation/CapitalNavigationWindow/BridgeTo' if isBridge else 'UI/CapitalNavigation/CapitalNavigationWindow/JumpTo'
        if self.sr.Get('showing', '') != showing:
            scrolllist = []
            shipID = eveCfg.GetActiveShip()
            if shipID:
                jumpDriveRange, consumptionType, consumptionAmount = self.GetJumpDriveInfo(shipID)
                structureBeacons = sm.GetService('structureDirectory').GetAccessibleOnlineCynoBeaconStructures()
                structureBeaconAction = self.BridgeToStructure if isBridge else self.JumpToStructure
                for structureID, typeID, ownerID, solarSystemID, structureState, name in structureBeacons:
                    if solarSystemID == session.solarsystemid:
                        continue
                    requiredQty, requiredType = self.GetFuelConsumptionForMyShip(session.solarsystemid2, solarSystemID, consumptionType, consumptionAmount)
                    if requiredQty:
                        entry = self.GetSolarSystemBeaconEntry(solarSystemID, requiredQty, requiredType, jumpDriveRange, structureID, structureBeaconAction, typeID)
                        scrolllist.append(entry)

            headers = [localization.GetByLabel('UI/Common/Type'),
             localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
             localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/SecurityColumnHeader'),
             localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/FuelColumnHeader'),
             localization.GetByLabel('UI/Common/Volume'),
             localization.GetByLabel('UI/Common/Distance'),
             localization.GetByLabel(showing)]
            self.sr.scroll.state = uiconst.UI_NORMAL
            self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=localization.GetByLabel('UI/Common/NothingFound'))
            self.sr.showing = showing

    def JumpToStructure(self, entry, *args):
        m = []
        if entry.sr.node.itemID != session.solarsystemid2 and InShipInSpace():
            m = [(MenuLabel('UI/CapitalNavigation/CapitalNavigationWindow/JumpTo'), self._JumpToStructure, (entry.sr.node.itemID, entry.sr.node.beaconID))]
        return m

    def _JumpToStructure(self, solarSystemID, beaconID):
        GetMenuService().JumpToStructureBeacon(solarSystemID, beaconID)

    def BridgeToStructure(self, entry, *args):
        m = []
        if entry.sr.node.itemID != session.solarsystemid2 and InShipInSpace():
            m = [(MenuLabel('UI/CapitalNavigation/CapitalNavigationWindow/BridgeTo'), self._BridgeToStructure, (entry.sr.node.itemID, entry.sr.node.beaconID))]
        return m

    def _BridgeToStructure(self, solarSystemID, beaconID):
        GetMenuService().BridgeToBeaconStructure(solarSystemID, beaconID)

    def GetSolarSystemBeaconEntry(self, solarSystemID, requiredQty, requiredType, jumpDriveRange, beaconID = None, action = None, beaconTypeID = None):
        if solarSystemID is None or requiredQty is None or requiredType is None or jumpDriveRange is None:
            return
        lightYearDistance = uix.GetLightYearDistance(session.solarsystemid2, solarSystemID, False)
        solarSystemName = localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/SolarSystemName', solarSystem=solarSystemID)
        securityStatus = sm.GetService('map').GetSecurityStatus(solarSystemID)
        requiredVolume = evetypes.GetVolume(requiredType) * requiredQty
        if jumpDriveRange > lightYearDistance:
            rangeString = 'UI/CapitalNavigation/CapitalNavigationWindow/WithinRange'
        else:
            rangeString = 'UI/CapitalNavigation/CapitalNavigationWindow/NotInRange'
        label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (solarSystemName,
         localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/SecurityStatus', securityStatus=securityStatus),
         localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/FuelTypeRequired', fuelType=requiredType, requiredQty=requiredQty),
         localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/FuelVolumeRequired', requiredVolume=requiredVolume),
         localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/DistanceToSystem', lightYearDistance=lightYearDistance),
         localization.GetByLabel(rangeString))
        if beaconTypeID:
            label = '%s<t>%s' % (evetypes.GetName(beaconTypeID), label)
        data = utillib.KeyVal()
        data.label = label
        data.showinfo = 1
        data.typeID = const.typeSolarSystem
        data.itemID = solarSystemID
        data.charIndex = solarSystemName.lower()
        if beaconID and action:
            data.beaconID = beaconID
            data.GetMenu = action
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Distance'), lightYearDistance)
        data.Set('sort_%s' % localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/FuelColumnHeader'), requiredQty)
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Destination'), solarSystemName)
        data.Set('sort_%s' % localization.GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/SecurityColumnHeader'), securityStatus)
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Volume'), requiredVolume)
        return GetFromClass(Generic, data)

    def GetJumpDriveInfo(self, shipID):
        if shipID:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            jumpDriveRange = dogmaLocation.GetAttributeValue(shipID, const.attributeJumpDriveRange)
            consumptionType = dogmaLocation.GetAttributeValue(shipID, const.attributeJumpDriveConsumptionType)
            consumptionAmount = dogmaLocation.GetAttributeValue(shipID, const.attributeJumpDriveConsumptionAmount)
            return (jumpDriveRange, consumptionType, consumptionAmount)

    def GetFuelConsumptionForMyShip(self, fromSystem, toSystem, consumptionType, consumptionAmount):
        if not eveCfg.GetActiveShip():
            return (None, None)
        myDist = uix.GetLightYearDistance(fromSystem, toSystem, False)
        if myDist is None:
            return (None, None)
        consumptionAmount = myDist * consumptionAmount
        return (int(consumptionAmount), consumptionType)
