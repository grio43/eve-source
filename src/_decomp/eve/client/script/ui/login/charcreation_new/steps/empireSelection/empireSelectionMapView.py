#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\empireSelectionMapView.py
import math
from collections import defaultdict
import geo2
import evecamera
import trinity
import uthread
from carbonui import uiconst
from carbonui.uianimations import animations
from characterdata import schools
from eve.client.script.ui import eveColor
from eve.client.script.ui.login.charcreation_new import charCreationSignals
from eve.client.script.ui.login.charcreation_new.steps.empireSelection import empireSelectionConst
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionConst import FACTIONSELECT_ANIMATION_DURATION, ENTRY_ANIMATION_DURATION
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionMapViewFilter import EmpireSelectionMapFilter
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectipMapViewNavigation import EmpireSelectionMapViewNavigation
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.schoolBracket import SchoolBracket
from eve.client.script.ui.shared.mapView.mapView import MapView
from eve.client.script.ui.shared.maps import mapcommon
from eve.common.lib import appConst
from operations.common.warpSites import GetOperationSites

class EmpireSelectionMapView(MapView):
    mapViewID = 'EmpireSelectionMapView'
    mapFilterID = mapcommon.STARMODE_FACTIONEMPIRE
    cameraID = evecamera.CAM_EMPIRESELECTIONMAP
    default_bgColor = eveColor.BLACK

    def ApplyAttributes(self, attributes):
        super(EmpireSelectionMapView, self).ApplyAttributes(attributes)
        self.animEntry = attributes.animEntry
        self.connect_signals()
        self.bracketsByFactionID = None

    def Close(self, *args, **kwds):
        try:
            self.disconnect_signals()
        finally:
            super(EmpireSelectionMapView, self).Close(*args, **kwds)

    def connect_signals(self):
        charCreationSignals.onEmpireFactionSelected.connect(self.OnEmpireFactionSelected)
        charCreationSignals.onStepSwitched.connect(self.OnStepSwitched)

    def disconnect_signals(self):
        charCreationSignals.onEmpireFactionSelected.disconnect(self.OnEmpireFactionSelected)
        charCreationSignals.onStepSwitched.disconnect(self.OnStepSwitched)

    def OnStepSwitched(self, oldStepID, newStepID):
        for brackets in self.bracketsByFactionID.values():
            for bracket in brackets:
                animations.FadeOut(bracket, duration=0.6)

        self.camera.AnimZoomIn()

    def InitCameraFocus(self, zoomToItem = True, mapFilterID = None):
        duration = ENTRY_ANIMATION_DURATION if self.animEntry else None
        uthread.new(self.camera.AnimEntry, self.GetCenterOfMassForAllFactions(), duration)

    def LayoutChangeCompleted(self, changedSolarSystems):
        super(EmpireSelectionMapView, self).LayoutChangeCompleted(changedSolarSystems)
        if not self.bracketsByFactionID:
            self.ConstructBrackets()

    def OnEmpireFactionSelected(self, factionID):
        uthread.new(self.LookAtFaction, factionID)

    def ConstructBrackets(self):
        self.bracketsByFactionID = defaultdict(list)
        for raceID, schoolIDs in schools.get_all_schools_by_race().iteritems():
            for schoolID in schoolIDs:
                factionID = appConst.factionByRace.get(raceID, None)
                if factionID:
                    bracket = self._ConstructBracket(schoolID, factionID)
                    self.bracketsByFactionID[factionID].append(bracket)

    def _ConstructBracket(self, schoolID, factionID):
        systemID = GetOperationSites().get_solarsystem_id_from_school(schoolID)
        if systemID:
            system = self.layoutHandler.nodesBySolarSystemID.get(systemID, None)
            return SchoolBracket(parent=self.infoLayer, scene=self.scene, curveSet=self.sceneContainer.bracketCurveSet, system=system, schoolID=schoolID, factionID=factionID)

    def ConstructMapNavigation(self):
        self.mapNavigation = EmpireSelectionMapViewNavigation(parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL, mapView=self)

    def _LoadAllMarkers(self):
        pass

    def _GetDefaultInterestID(self):
        return None

    def ReconstructMyLocationMarker(self):
        pass

    def ShowMyHomeStation(self):
        pass

    def LoadAllJumpBridges(self):
        pass

    def GetActiveFilter(self):
        return EmpireSelectionMapFilter()

    def ConstructStarfield(self):
        self.mapScene.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
        self.mapScene.starfield.maxDist = 500
        self.mapScene.starfield.minDist = 100

    def IsAbstractModeActive(self):
        return False

    def GetCenterOfMassForFaction(self, factionID):
        positions = [ bracket.GetPosition() for bracket in self.bracketsByFactionID[factionID] ]
        return self._GetCenterOfMass(positions)

    def GetCenterOfMassForAllFactions(self):
        starNodes = self.layoutHandler.nodesBySolarSystemID.values()
        positions = [ starNode.position for starNode in starNodes if starNode.system.factionID in empireSelectionConst.EMPIRE_FACTIONIDS ]
        return self._GetCenterOfMass(positions)

    def _GetCenterOfMass(self, positions):
        center = (0, 0, 0)
        for position in positions:
            center = geo2.Vec3Add(center, position)

        return geo2.Vec3Scale(center, 1.0 / len(positions))

    def LookAtFaction(self, factionID):
        atPos = self.GetCenterOfMassForFaction(factionID)
        eyePos = geo2.Vec3Add(atPos, geo2.Vec3Scale(self.camera.GetLookAtDirection(), 22000))
        animations.StopAllAnimations(self.camera)
        animations.MorphVector3(self.camera, 'atPosition', self.camera.atPosition, atPos, duration=FACTIONSELECT_ANIMATION_DURATION)
        animations.MorphVector3(self.camera, 'eyePosition', self.camera.eyePosition, eyePos, duration=FACTIONSELECT_ANIMATION_DURATION, sleep=True)
        animations.MorphScalar(self.camera, 'yaw', self.camera.yaw, self.camera.yaw + 2 * math.pi, duration=500.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
