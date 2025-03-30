#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\sovHubs\expandedSovHubEntry.py
import math
from collections import defaultdict, OrderedDict
import carbonui
import eveicon
import evetypes
import uthread
from carbonui.control.button import Button
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.mapView.markers.mapMarkerScanResult import Circle
from eve.client.script.ui.shared.sov.sovHub.editSections import TransitCont
from eve.client.script.ui.shared.sov.sovHub.fuelConts import FuelMagmaCont, FuelIceCont
from eve.client.script.ui.shared.sov.sovHub.resourceConts import PowerCont, WorkforceCont
import carbonui.const as uiconst
from eve.client.script.ui.shared.sov.threadedLoader import ThreadedLoader
from eveexceptions import ExceptionEater
from inventorycommon.const import typeSkyhook
from localization import GetByLabel
from sovereignty.client.quasarCallWrapper import DATA_NOT_AVAILABLE
from sovereignty.client.sovHub.hubUtil import GetTexturePathForUpgradeTypeList

class ExpandedSovHubEntry(SE_BaseClassCore):
    ENTRYHEIGHT = 300

    def ApplyAttributes(self, attributes):
        super(ExpandedSovHubEntry, self).ApplyAttributes(attributes)
        self.threadedLoader = ThreadedLoader('ExpandedSovHubEntry')
        self.node = attributes.node
        self.entryController = self.node.entryController
        contentCont = Container(name='contentCont', parent=self)
        topCont = Container(name='topCont', parent=contentCont, align=carbonui.Align.TOTOP, height=40, top=20, padBottom=20, padLeft=24)
        editCont = Container(name='editCont', parent=topCont, align=carbonui.Align.TORIGHT, left=10, width=30)
        self.nameLabel = carbonui.TextHeader(parent=topCont, text='', align=carbonui.Align.TOTOP, maxLines=1, autoFadeSides=30)
        self.locationLabel = carbonui.TextDetail(parent=topCont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOTOP, top=2, maxLines=1, autoFadeSides=30)
        editButton = Button(parent=editCont, label=GetByLabel('UI/Sovereignty/HubPage/EditStructure'), align=carbonui.Align.TOPRIGHT, texturePath=eveicon.open_window, func=lambda *args: self.entryController.OpenSovHubWindow())
        editCont.width = editButton.width
        lowerContentCont = Container(name='lowerContentCont', parent=contentCont, padLeft=8)
        topPad = 30
        labelTop = 150
        upgradeCont = Container(name='upgradeCont', parent=lowerContentCont, align=carbonui.Align.TOLEFT, width=145)
        carbonui.TextDetail(parent=upgradeCont, text=GetByLabel('UI/Sovereignty/HubPage/Upgrades'), color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOTOP, padLeft=16)
        self.upgradeGraph = UpgradeGraph(parent=upgradeCont, align=carbonui.Align.TOPLEFT, top=10, radius=55)
        self.upgradeLabel = carbonui.TextDetail(parent=upgradeCont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.CENTERTOP, top=labelTop)
        lavaCont = Container(name='lavaCont', parent=lowerContentCont, align=carbonui.Align.TOLEFT, width=120)
        carbonui.TextDetail(parent=lavaCont, text=GetByLabel('UI/Sovereignty/HubPage/Fuel'), color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOTOP)
        self.fuelMagmaCont = FuelMagmaCont(parent=lavaCont, align=carbonui.Align.TOPLEFT, top=topPad, hubController=self.entryController)
        self.lavaLabel = carbonui.TextDetail(parent=lavaCont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.CENTERTOP, top=labelTop)
        iceCont = Container(name='iceCont', parent=lowerContentCont, align=carbonui.Align.TOLEFT, width=120)
        self.fuelIceCont = FuelIceCont(parent=iceCont, align=carbonui.Align.TOPLEFT, top=topPad, hubController=self.entryController)
        self.iceLabel = carbonui.TextDetail(parent=iceCont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.CENTERTOP, top=labelTop)
        resourceCont = Container(parent=lowerContentCont, align=carbonui.Align.TOLEFT, width=300)
        self.powerCont = PowerCont(parent=resourceCont, align=carbonui.Align.TOTOP, gaugeHeight=4, controller=self.entryController, useLegend=False, isCompact=True, padBottom=10)
        self.workforceCont = WorkforceCont(parent=resourceCont, align=carbonui.Align.TOTOP, gaugeHeight=4, controller=self.entryController, useLegend=False, isCompact=True, padBottom=10)
        self.transitCont = TransitCont(parent=resourceCont, align=carbonui.Align.TOTOP, workforceController=self.entryController.workforceController, canEdit=False)
        skyhookCont = Container(parent=lowerContentCont, align=carbonui.Align.TOLEFT, width=100, padLeft=30)
        skyhookColor = eveColor.SMOKE_BLUE[:3] + (0.6,)
        Sprite(parent=skyhookCont, align=carbonui.Align.CENTERLEFT, pos=(0, 0, 125, 200), texturePath='res:/UI/Texture/classes/Sov/skyhook.png', color=skyhookColor, pickState=carbonui.PickState.OFF)
        self.numSkyhooks = carbonui.TextHeadline(parent=skyhookCont, text='', align=carbonui.Align.TOPLEFT, pos=(60, 60, 0, 0))
        carbonui.TextBody(parent=skyhookCont, text=evetypes.GetName(typeSkyhook), color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOPLEFT, pos=(60, 85, 0, 0))

    def Load(self, node):
        if self.destroyed:
            return
        self.nameLabel.text = self.entryController.GetHubName()
        self.locationLabel.text = self.entryController.GetLocation()
        self.threadedLoader.StartLoading(self.LoadPowerWorkforceAsync, self)
        self.threadedLoader.StartLoading(self.LoadTextAcync, self)
        self.threadedLoader.StartLoading(self.transitCont.LoadSection, self)
        self.threadedLoader.StartLoading(self.fuelMagmaCont.LoadUI, self.fuelMagmaCont)
        self.threadedLoader.StartLoading(self.fuelIceCont.LoadUI, self.fuelIceCont)
        self.threadedLoader.StartLoading(self.LoadSkyhookLabel, self)

    def LoadPowerWorkforceAsync(self):
        uthread.parallel([(self.powerCont.LoadCont, ()), (self.workforceCont.LoadCont, ())])

    def LoadTextAcync(self):
        results = uthread.parallel([(self.entryController.GetUpgradesTextLong, ()),
         (self.entryController.GetLavaText, ()),
         (self.entryController.GetIceText, ()),
         (self.entryController.GetInstalledUpgrades, ())])
        upgradeText, lavaText, iceText, installedUpgrades = results
        if self.destroyed:
            return
        self.upgradeLabel.text = upgradeText
        self.lavaLabel.text = lavaText
        self.iceLabel.text = iceText
        self.upgradeGraph.UpdatePoints(installedUpgrades)

    def LoadSkyhookLabel(self):
        numSkyhooks = self.entryController.GetNumSkyhooks()
        self.numSkyhooks.text = numSkyhooks

    def Close(self):
        with ExceptionEater('Closing ExpandedSovHubEntry'):
            self.entryController = None
        super(ExpandedSovHubEntry, self).Close()


class UpgradeGraph(Container):
    default_align = carbonui.Align.TOPLEFT
    default_width = 160
    default_height = 160

    def ApplyAttributes(self, attributes):
        super(UpgradeGraph, self).ApplyAttributes(attributes)
        self.radius = attributes.radius
        numCircles = 5
        radiusSteps = self.radius / numCircles
        self.iconCont = Container(parent=self, align=carbonui.Align.CENTER, pos=(0,
         0,
         self.width,
         self.height))
        lineCont = Container(parent=self, align=carbonui.Align.CENTER, pos=(0,
         0,
         self.width,
         self.height))
        self.onlineVectorLine = VectorLineTrace(name='onlineVectorLine', parent=lineCont, lineWidth=2.0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, align=carbonui.Align.CENTER)
        self.totalVectorLine = VectorLineTrace(name='totalVectorLine', parent=lineCont, lineWidth=1.0, width=0, height=0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, align=carbonui.Align.CENTER)
        for i in xrange(1, numCircles + 1):
            r = i * radiusSteps
            c = Container(parent=self, align=carbonui.Align.CENTER, pos=(0,
             0,
             2 * r,
             2 * r))
            circle = Circle(parent=c, radius=r, color=eveColor.TUNGSTEN_GREY, opacity=0.5, lineWidth=0.5)

    def UpdatePoints(self, upgradeDataList):
        self.iconCont.Flush()
        self.onlineVectorLine.Flush()
        self.totalVectorLine.Flush()
        if upgradeDataList == DATA_NOT_AVAILABLE:
            return
        serviceUpgrades = evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_SOVHUB_SERVICE_MODULE_UPGRADES)
        miningUpgrades = evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_SOVHUB_MINING_SITE_UPGRADES)
        combatUpgrades = evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_SOVHUB_COMBAT_SITE_UPGRADES)
        numUpgradesByTypeList = OrderedDict()
        numUpgradesByTypeList[evetypes.TYPE_LIST_SOVHUB_SERVICE_MODULE_UPGRADES] = 0
        numUpgradesByTypeList[evetypes.TYPE_LIST_SOVHUB_MINING_SITE_UPGRADES] = 0
        numUpgradesByTypeList[evetypes.TYPE_LIST_SOVHUB_COMBAT_SITE_UPGRADES] = 0
        onlineNumPerTypeList = numUpgradesByTypeList.copy()
        for upgrade in upgradeDataList:
            if upgrade.typeID in serviceUpgrades:
                typeListID = evetypes.TYPE_LIST_SOVHUB_SERVICE_MODULE_UPGRADES
            elif upgrade.typeID in miningUpgrades:
                typeListID = evetypes.TYPE_LIST_SOVHUB_MINING_SITE_UPGRADES
            elif upgrade.typeID in combatUpgrades:
                typeListID = evetypes.TYPE_LIST_SOVHUB_COMBAT_SITE_UPGRADES
            else:
                continue
            numUpgradesByTypeList[typeListID] += 1
            if upgrade.isPowerStateFunctional:
                onlineNumPerTypeList[typeListID] += 1

        maxNum = max(numUpgradesByTypeList.values())
        degreeStep = 360 / len(numUpgradesByTypeList)
        maxValue = self.radius - 3
        iconOffset = self.radius + 12
        totalVectorPoints = []
        onlineVectorPoints = []
        textureAndPos = []
        angle = 180
        for typeListID, numUpgrades in numUpgradesByTypeList.iteritems():
            angle += degreeStep
            angle_rad = math.radians(angle)
            if maxNum:
                totalProp = float(numUpgrades) / maxNum
                totalR = totalProp * maxValue
                tX = totalR * math.sin(angle_rad)
                tY = totalR * math.cos(angle_rad)
                totalVectorPoints.append((tX, tY))
                numOnline = onlineNumPerTypeList[typeListID]
                onlineProp = float(numOnline) / maxNum
                onlineR = onlineProp * maxValue
                oX = onlineR * math.sin(angle_rad)
                oY = onlineR * math.cos(angle_rad)
                onlineVectorPoints.append((oX, oY))
            texturePath = GetTexturePathForUpgradeTypeList(typeListID)
            iX = iconOffset * math.sin(angle_rad)
            iY = iconOffset * math.cos(angle_rad)
            textureAndPos.append((iX,
             iY,
             texturePath,
             typeListID))

        for pointList, vectorLine, color in ((onlineVectorPoints, self.onlineVectorLine, eveColor.CRYO_BLUE), (totalVectorPoints, self.totalVectorLine, eveColor.GUNMETAL_GREY)):
            if pointList:
                vectorLine.AddPoints(pointList, color)

        for x, y, texturePath, typeListID in textureAndPos:
            s = Sprite(parent=self.iconCont, pos=(x,
             y,
             16,
             16), align=carbonui.Align.CENTER, texturePath=texturePath, opacity=0.3)
            s.hint = evetypes.GetTypeListDisplayName(typeListID)
