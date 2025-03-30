#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\LinkContainer.py
import eveformat
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import Label
import evetypes
import localization
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.planet.pinContainers.BasePinContainer import BasePinContainer, CaptionAndSubtext
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
import eve.common.script.util.planetCommon as planetCommon

class LinkContainer(BasePinContainer):
    default_name = 'LinkContainer'
    INFO_CONT_HEIGHT = 70
    panelIDs = [planetCommonUI.PANEL_UPGRADELINK,
     planetCommonUI.PANEL_STATS,
     planetCommonUI.PANEL_ROUTES,
     planetCommonUI.PANEL_DECOMMISSION]

    def _GetPinName(self):
        return evetypes.GetName(self.pin.typeID)

    def GetID(self):
        return self.pin.GetIDTuple()

    def PanelUpgrade(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        link = self.pin.link
        nextLevel = link.level + 1
        currentCpu = link.GetCpuUsage()
        currentPower = link.GetPowerUsage()
        nextLvlCpu = planetCommon.GetCpuUsageForLink(link.typeID, link.GetDistance(), nextLevel)
        nextLvlPower = planetCommon.GetPowerUsageForLink(link.typeID, link.GetDistance(), nextLevel)
        addlCpu = max(0, nextLvlCpu - currentCpu)
        addlPower = max(0, nextLvlPower - currentPower)
        colony = self.planetUISvc.GetCurrentPlanet().GetColony(session.charid)
        if not colony or colony.colonyData is None:
            raise RuntimeError('Unable to upgrade link - colony not set up')
        colonyCpuUsage = colony.colonyData.GetColonyCpuUsage()
        colonyCpuSupply = colony.colonyData.GetColonyCpuSupply()
        colonyPowerUsage = colony.colonyData.GetColonyPowerUsage()
        colonyPowerSupply = colony.colonyData.GetColonyPowerSupply()
        if addlPower + colonyPowerUsage > colonyPowerSupply or addlCpu + colonyCpuUsage > colonyCpuSupply:
            text = localization.GetByLabel('UI/PI/Common/LinkCannotUpgradePowerCPU', linkTypeName=evetypes.GetName(link.typeID))
            Label(parent=cont, text=text, align=uiconst.TOTOP)
            self.upgradeStatsScroll = eveScroll.Scroll(parent=cont, name='upgradeStatsScroll', align=uiconst.TOALL, padTop=4)
            self.upgradeStatsScroll.sr.id = 'planetLinkUpgradeStats'
            scrolllist = []
            strCurrentCpu = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=currentCpu)
            strNextCpu = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=nextLvlCpu)
            cpuDeficit = nextLvlCpu - (colonyCpuSupply - colonyCpuUsage)
            if cpuDeficit > 0:
                cerberusLabel = 'UI/PI/Common/TeraFlopsAmountRed'
            else:
                cerberusLabel = 'UI/PI/Common/TeraFlopsAmountGreen'
            strCpuDeficit = localization.GetByLabel(cerberusLabel, amount=max(0, cpuDeficit))
            strCurrentPower = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=currentPower)
            strNextPower = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=nextLvlPower)
            powerDeficit = nextLvlPower - (colonyPowerSupply - colonyPowerUsage)
            if powerDeficit > 0:
                cerberusLabel = 'UI/PI/Common/MegaWattsAmountRed'
            else:
                cerberusLabel = 'UI/PI/Common/MegaWattsAmountGreen'
            strPowerDeficit = localization.GetByLabel(cerberusLabel, amount=max(0, powerDeficit))
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/PI/Common/CpuUsage'),
                       strCurrentCpu,
                       strNextCpu,
                       strCpuDeficit)}))
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/PI/Common/PowerUsage'),
                       strCurrentPower,
                       strNextPower,
                       strPowerDeficit)}))
            self.upgradeStatsScroll.Load(contentList=scrolllist, headers=['',
             localization.GetByLabel('UI/Common/Current'),
             localization.GetByLabel('UI/PI/Common/UpgradeNoun'),
             localization.GetByLabel('UI/PI/Common/PowerOrCPUDeficit')])
        elif nextLevel > planetCommon.LINK_MAX_UPGRADE:
            text = localization.GetByLabel('UI/PI/Common/LinkMaxUpgradeReached', linkTypeName=evetypes.GetName(link.typeID))
            Label(parent=cont, align=uiconst.TOTOP, text=text)
        else:
            text = localization.GetByLabel('UI/PI/Common/LinkUpgradePrompt', level=nextLevel)
            self.upgradeStatsScroll = scroll = eveScroll.Scroll(parent=cont, name='UpgradeStatsScroll', align=uiconst.TOALL)
            self.upgradeStatsScroll.sr.id = 'planetLinkUpgradeStats'
            scroll.HideUnderLay()
            Frame(parent=scroll, color=(1.0, 1.0, 1.0, 0.2))
            scrolllist = []
            link = self.pin.link
            totalBandwidth = link.GetTotalBandwidth()
            nextLvlBandwidth = link.GetBandwidthForLevel(nextLevel)
            strCurrentBandwidth = totalBandwidth
            strNextLvlBandwidth = nextLvlBandwidth
            strBandwidthDelta = max(0, nextLvlBandwidth - totalBandwidth)
            strBandwidthUsage = link.GetBandwidthUsage()
            strCurrentCpu = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=currentCpu)
            strNextCpu = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=nextLvlCpu)
            strCpuDelta = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=max(0, nextLvlCpu - currentCpu))
            strCpuUsage = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=int(colonyCpuUsage))
            strCurrentPower = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=currentPower)
            strNextPower = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=nextLvlPower)
            strPowerDelta = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=max(0, nextLvlPower - currentPower))
            strPowerUsage = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=int(colonyPowerUsage))
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/Common/Current'),
                       localization.formatters.FormatNumeric(strCurrentBandwidth, decimalPlaces=1),
                       strCurrentCpu,
                       strCurrentPower)}))
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/PI/Common/UpgradeNoun'),
                       localization.formatters.FormatNumeric(strNextLvlBandwidth, decimalPlaces=1),
                       strNextCpu,
                       strNextPower)}))
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/PI/Common/ChangeNoun'),
                       localization.formatters.FormatNumeric(strBandwidthDelta, decimalPlaces=1),
                       strCpuDelta,
                       strPowerDelta)}))
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/Common/Usage'),
                       localization.formatters.FormatNumeric(strBandwidthUsage, decimalPlaces=1),
                       strCpuUsage,
                       strPowerUsage)}))
            scroll.Load(contentList=scrolllist, headers=['',
             localization.GetByLabel('UI/PI/Common/Capacity'),
             localization.GetByLabel('UI/Common/Cpu'),
             localization.GetByLabel('UI/Common/Power')])
            btns = [[localization.GetByLabel('UI/PI/Common/Upgrade'), self._UpgradeSelf, (link.endpoint1.id, link.endpoint2.id, nextLevel)]]
            Label(parent=cont, text=text, align=uiconst.TOBOTTOM, idx=0, padTop=4)
            ButtonGroup(btns=btns, parent=cont, line=False, idx=0, padTop=16)
        return cont

    def PanelDecommissionPin(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        text = localization.GetByLabel('UI/PI/Common/DecommissionLink', typeName=evetypes.GetName(self.pin.link.typeID))
        Label(parent=cont, text=text, align=uiconst.TOTOP)
        btns = [[localization.GetByLabel('UI/PI/Common/Proceed'), self._DecommissionSelf, None]]
        ButtonGroup(btns=btns, parent=cont, idx=0)
        return cont

    def LoadRouteScroll(self):
        if not self or self.destroyed:
            return
        link = self.pin.link
        scrolllist = []
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(link.endpoint1.ownerID)
        for routeID in link.routesTransiting:
            route = colony.GetRoute(routeID)
            typeID = route.GetType()
            qty = route.GetQuantity()
            typeName = evetypes.GetName(typeID)
            scrolllist.append(GetFromClass(Item, {'label': '<t>%s<t>%s<t>%s' % (typeName, qty, localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=route.GetBandwidthUsage())),
             'typeID': typeID,
             'itemID': None,
             'getIcon': True,
             'OnMouseEnter': self.OnRouteEntryHover,
             'OnMouseExit': self.OnRouteEntryExit,
             'routeID': route.routeID,
             'OnClick': self.OnRouteEntryClick}))

        self.routeScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoRoutesThroughLink'), headers=['',
         localization.GetByLabel('UI/Common/Commodity'),
         localization.GetByLabel('UI/Common/Quantity'),
         localization.GetByLabel('UI/PI/Common/CapacityUsed')])

    def OnRouteEntryHover(self, entry):
        self.planetUISvc.myPinManager.ShowRoute(entry.sr.node.routeID)

    def OnRouteEntryExit(self, entry):
        self.planetUISvc.myPinManager.StopShowingRoute(entry.sr.node.routeID)

    def OnRouteEntryClick(self, *args):
        if not self or self.destroyed:
            return
        selectedRoutes = self.routeScroll.GetSelected()
        if len(selectedRoutes) < 1:
            self.routeInfo.state = uiconst.UI_HIDDEN
            self.UpdateWindowHeight()
            return
        selectedRouteData = selectedRoutes[0]
        selectedRouteID = None
        for routeID in self.pin.link.routesTransiting:
            if routeID == selectedRouteData.routeID:
                selectedRouteID = routeID
                break

        if selectedRouteID is None:
            return
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(self.pin.link.endpoint1.ownerID)
        selectedRoute = colony.GetRoute(selectedRouteID)
        if selectedRoute is None:
            return
        sourcePin = colony.GetPin(selectedRoute.GetSourcePinID())
        self.routeInfoSource.SetSubtext(planetCommon.GetGenericPinName(sourcePin.typeID, sourcePin.id))
        destPin = colony.GetPin(selectedRoute.GetDestinationPinID())
        self.routeInfoDest.SetSubtext(planetCommon.GetGenericPinName(destPin.typeID, destPin.id))
        routeTypeID = selectedRoute.GetType()
        routeQty = selectedRoute.GetQuantity()
        self.routeInfoType.SetSubtext(localization.GetByLabel('UI/PI/Common/ItemAmount', itemName=evetypes.GetName(routeTypeID), amount=int(routeQty)))
        self.routeInfoBandwidth.SetSubtext(localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=selectedRoute.GetBandwidthUsage()))
        self.routeInfo.opacity = 0.0
        self.routeInfo.state = uiconst.UI_PICKCHILDREN
        animations.FadeIn(self.routeInfo, duration=0.125, sleep=True)

    def GetCaptionForUpgradeLevel(self, level):
        if level >= planetCommon.LINK_MAX_UPGRADE:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel10')
        elif level == 9:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel9')
        elif level == 8:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel8')
        elif level == 7:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel7')
        elif level == 6:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel6')
        elif level == 5:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel5')
        elif level == 4:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel4')
        elif level == 3:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel3')
        elif level == 2:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel2')
        elif level == 1:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel1')
        else:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel0')

    def _DecommissionSelf(self, *args):
        sm.GetService('audio').SendUIEvent('msg_pi_build_decommission_play')
        self.planetUISvc.myPinManager.RemoveLink(self.pin.GetIDTuple())

    def _UpgradeSelf(self, *args):
        self.planetUISvc.myPinManager.UpgradeLink(*args)
        self.CloseByUser()

    def _GetInfoCont(self):
        link = self.pin.link
        totalBandwidth = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=link.GetTotalBandwidth())
        bandwidthUsed = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=link.GetBandwidthUsage())
        self.totalBandwidth = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/LinkMaxCapacity'), subtext=totalBandwidth, align=uiconst.TOTOP)
        self.bandwidthUsed = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/CapacityUsed'), subtext=bandwidthUsed, align=uiconst.TOTOP)
        self.bandwidthGauge = Gauge(parent=self.infoContRight, value=link.GetBandwidthUsage() / link.GetTotalBandwidth(), color=planetCommonUI.PLANET_COLOR_BANDWIDTH, label=localization.GetByLabel('UI/PI/Common/CapacityUsed'), align=uiconst.TOTOP, padding=(0, 0, 10, 4))
        levelStr = localization.GetByLabel('UI/PI/Common/LinkUpgradeLevelAndName', upgradeLevel=eveformat.number_roman(link.level, zero_text='N/A'), upgradeLevelName=self.GetCaptionForUpgradeLevel(link.level))
        self.upgradeLevel = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/UpgradeLevel'), subtext=levelStr, align=uiconst.TOTOP)

    def _UpdateInfoCont(self):
        if not self or self.destroyed:
            return
        link = self.pin.link
        totalBandwidth = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=link.GetTotalBandwidth())
        bandwidthUsed = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=link.GetBandwidthUsage())
        self.totalBandwidth.SetSubtext(totalBandwidth)
        self.bandwidthUsed.SetSubtext(bandwidthUsed)
        levelStr = localization.GetByLabel('UI/PI/Common/LinkUpgradeLevelAndName', upgradeLevel=eveformat.number_roman(link.level, zero_text='N/A'), upgradeLevelName=self.GetCaptionForUpgradeLevel(link.level))
        self.upgradeLevel.SetSubtext(levelStr)
        self.bandwidthGauge.SetValue(link.GetBandwidthUsage() / link.GetTotalBandwidth())

    def PanelShowStats(self, *args):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.statsScroll = scroll = eveScroll.Scroll(parent=cont, name='StatsScroll', align=uiconst.TOALL)
        scrolllist = []
        link = self.pin.link
        strCpuUsage = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=int(link.GetCpuUsage()))
        scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/CpuUsage'), strCpuUsage)}))
        strPowerUsage = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=int(link.GetPowerUsage()))
        scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/PowerUsage'), strPowerUsage)}))
        scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/PI/Common/Attribute'), localization.GetByLabel('UI/Common/Value')])
        return cont
