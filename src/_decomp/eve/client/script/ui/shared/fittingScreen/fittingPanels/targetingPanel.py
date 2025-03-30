#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\targetingPanel.py
import math
import dogma.data as dogma_data
from dogma import const as dogmaConst
from eve.client.script.ui.shared.fittingScreen.fittingPanels.attributePanel import AttributePanel
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from localization import GetByLabel, GetByMessageID
textureByAttributeID = {dogmaConst.attributeScanResolution: 'res:/UI/Texture/classes/Fitting/StatsIcons/scanResolution.png',
 dogmaConst.attributeSignatureRadius: 'res:/UI/Texture/classes/Fitting/StatsIcons/signatureRadius.png',
 dogmaConst.attributeMaxLockedTargets: 'res:/UI/Texture/classes/Fitting/StatsIcons/maximumLockedTargets.png',
 dogmaConst.attributeScanGravimetricStrength: 'res:/UI/Texture/classes/Fitting/StatsIcons/sensorStrengthCaldari.png',
 dogmaConst.attributeScanRadarStrength: 'res:/UI/Texture/classes/Fitting/StatsIcons/sensorStrengthAmarr.png',
 dogmaConst.attributeScanMagnetometricStrength: 'res:/UI/Texture/classes/Fitting/StatsIcons/sensorStrengthGallente.png',
 dogmaConst.attributeScanLadarStrength: 'res:/UI/Texture/classes/Fitting/StatsIcons/sensorStrengthMinmatar.png'}

class TargetingPanel(AttributePanel):
    default_iconSize = 20
    attributesToShow = [('sensorStrength', dogmaConst.attributeScanResolution), (dogmaConst.attributeSignatureRadius, dogmaConst.attributeMaxLockedTargets)]

    def LoadPanel(self, initialLoad = False):
        AttributePanel.LoadPanel(self, initialLoad)
        activeShip = self.dogmaLocation.GetCurrentShipID()
        sensorStrengthAttributeID, val = self.GetSensorStrengthAttribute(activeShip)
        parentGrid = self.GetValueParentGrid()
        for eachLine in self.attributesToShow:
            for eachAttributeID in eachLine:
                if eachAttributeID == 'sensorStrength':
                    each = sensorStrengthAttributeID
                else:
                    each = eachAttributeID
                attribute = dogma_data.get_attribute(each)
                texturePath = textureByAttributeID.get(each)
                self.AddAttributeCont(attribute, parentGrid, eachAttributeID, texturePath=texturePath)

        AttributePanel.FinalizePanelLoading(self, initialLoad)

    def GetSensorStrengthAttribute(self, shipID):
        if session.shipid == shipID:
            return sm.GetService('godma').GetStateManager().GetSensorStrengthAttribute(shipID)
        else:
            dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
            return dogmaLocation.GetSensorStrengthAttribute(shipID)

    def UpdateTargetingPanel(self):
        self.SetTargetingHeader()
        self.SetScanResolutionText()
        self.SetMaxTargetsText()
        self.SetSignatureText()
        self.SetSensorStrengthElements()

    def SetTargetingHeader(self):
        maxTargetRangeInfo = self.controller.GetMaxTargetRange()
        maxRange = maxTargetRangeInfo.value / 1000.0
        text = GetByLabel('UI/Fitting/FittingWindow/TargetingHeader', maxRange=maxRange)
        coloredText = GetColoredText(isBetter=maxTargetRangeInfo.isBetterThanBefore, text=text)
        headerHint = GetByLabel('UI/Fitting/FittingWindow/TargetingHeaderHint')
        self.SetStatusText(coloredText, headerHint)

    def SetScanResolutionText(self):
        scanResolutionInfo = self.controller.GetScanResolution()
        text = GetByLabel('UI/Fitting/FittingWindow/ScanResolution', resolution=int(scanResolutionInfo.value))
        coloredText = GetColoredText(isBetter=scanResolutionInfo.isBetterThanBefore, text=text)
        self.SetLabel(scanResolutionInfo.attributeID, coloredText)

    def SetMaxTargetsText(self):
        maxTargetingInfo = self.controller.GetMaxTargets()
        maxTargets = math.ceil(maxTargetingInfo.value)
        text = GetByLabel('UI/Fitting/FittingWindow/MaxLockedTargets', maxTargets=int(maxTargets))
        coloredText = GetColoredText(isBetter=maxTargetingInfo.isBetterThanBefore, text=text)
        self.SetLabel(maxTargetingInfo.attributeID, coloredText)

    def SetSignatureText(self):
        signatureRadiusInfo = self.controller.GetSignatureRadius()
        text = GetByLabel('UI/Fitting/FittingWindow/TargetingRange', range=signatureRadiusInfo.value)
        coloredText = GetColoredText(isBetter=signatureRadiusInfo.isBetterThanBefore, text=text)
        self.SetLabel(signatureRadiusInfo.attributeID, coloredText)

    def SetSensorStrengthElements(self):
        sensorStrenghtInfos = {dogmaConst.attributeScanRadarStrength: self.controller.GetScanRadarStrength(),
         dogmaConst.attributeScanMagnetometricStrength: self.controller.GetScanMagnetometricStrength(),
         dogmaConst.attributeScanGravimetricStrength: self.controller.GetScanGravimetricStrength(),
         dogmaConst.attributeScanLadarStrength: self.controller.GetScanLadarStrength()}
        maxSensorStrenghtAttributeID, maxSensorStrengthInfo = (None, None)
        for attributeID, strengthInfo in sensorStrenghtInfos.iteritems():
            if maxSensorStrengthInfo is None or strengthInfo.value > maxSensorStrengthInfo.value:
                maxSensorStrengthInfo = strengthInfo
                maxSensorStrenghtAttributeID = attributeID

        text = GetByLabel('UI/Fitting/FittingWindow/SensorStrength', points=maxSensorStrengthInfo.value)
        coloredText = GetColoredText(isBetter=maxSensorStrengthInfo.isBetterThanBefore, text=text)
        self.SetLabel('sensorStrength', coloredText)
        maxSensor = dogma_data.get_attribute(maxSensorStrenghtAttributeID)
        iconNum = textureByAttributeID.get(maxSensorStrenghtAttributeID)
        self.LoadIcon('sensorStrength', iconNum)
        self.SetSensorTooltip(maxSensor)

    def SetSensorTooltip(self, maxSensor):
        cont = self.statsContsByIdentifier.get('sensorStrength', None)
        if cont is not None and cont.tooltipPanelClassInfo is not None:
            tooltipTitleID = maxSensor.tooltipTitleID
            if tooltipTitleID:
                tooltipTitle = GetByMessageID(tooltipTitleID)
                cont.tooltipPanelClassInfo.headerText = tooltipTitle
