#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerSpaceObjectRadialMenu.py
from eve.client.script.ui.shared.radialMenu.radialMenu import RadialMenuSpace
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction
from carbonui.uicore import uicore

class MapMarkerSpaceObjectRadialMenu(RadialMenuSpace):

    def SetSpecificValues(self, attributes):
        RadialMenuSpace.SetSpecificValues(self, attributes)
        self.markerObject = attributes.markerObject
        self.scanSvc = sm.GetService('directionalScanSvc')

    def LoadButtons(self, parentLayer, optionsInfo, alternate = False, startingDegree = 0, animate = False, doReset = False):
        if getattr(self, 'busyReloading', False):
            return
        self.busyReloading = True
        try:
            filteredOptions = []
            for each in optionsInfo.allWantedMenuOptions:
                if each.option1Path in ('UI/Inflight/LockTarget', 'UI/Inflight/UnlockTarget'):
                    dScanAction = SimpleRadialMenuAction(option1='UI/Inflight/Scanner/DirectionalScan', alwaysAvailable=True, func=self.DirectionalScan, funcArgs=(self.itemID,))
                    filteredOptions.append(dScanAction)
                    optionsInfo.activeSingleOptions['UI/Inflight/Scanner/DirectionalScan'] = dScanAction
                elif each.option1Path in ('UI/Inflight/OrbitObject', 'UI/Inflight/Submenus/KeepAtRange', 'UI/Inflight/LookAtObject', 'UI/Inflight/ResetCamera'):
                    filteredOptions.append(SimpleRadialMenuAction())
                else:
                    filteredOptions.append(each)

            optionsInfo.allWantedMenuOptions = filteredOptions
            parentLayer.LoadButtons(self.itemID, self.stepSize, alternate, animate, doReset, optionsInfo, startingDegree, self.GetIconTexturePath)
            self.OnGlobalMove()
        finally:
            self.busyReloading = False

    def DirectionalScan(self, itemID, *args, **kwds):
        if itemID:
            uicore.cmd.GetCommandAndExecute('OpenDirectionalScanner', toggle=False)
            markerPosition = self.markerObject.position
            self.scanSvc.ScanTowardsItem(itemID, mapPosition=markerPosition)
