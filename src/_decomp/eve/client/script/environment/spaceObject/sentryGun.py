#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\sentryGun.py
from eve.common.lib import appConst
import eve.client.script.environment.spaceObject.spaceObject as spaceObject
import eve.client.script.environment.model.turretSet as turretSet
import eveSpaceObject
import evegraphics.settings as gfxsettings
TURRET_TYPE_ID = {eveSpaceObject.gfxRaceAmarr: 462,
 eveSpaceObject.gfxRaceGallente: 569,
 eveSpaceObject.gfxRaceCaldari: 574,
 eveSpaceObject.gfxRaceMinmatar: 498,
 eveSpaceObject.gfxRaceAngel: 462,
 eveSpaceObject.gfxRaceSleeper: 4049,
 eveSpaceObject.gfxRaceJove: 4049}
TURRET_FALLBACK_TYPE_ID = 462
MATERIALIZATION_DURATION_SECONDS = 15
MATERIALIZATION_DURATION_ATTRIBUTE = 'Trig_MaterializationDuration'
MATERIALIZATION_BOOLEAN_ATTRIBUTE = 'Trig_IsMaterialized'
FORTIFICATION_UNIT_EFFECTS_BY_TYPE = {appConst.typeWebifyingFortificationUnit: 'TGFU_WEB_ON',
 appConst.typeECMFortificationUnit: 'TGFU_ECM_ON',
 appConst.typeSmartBombingFortificationUnit: 'TGFU_SMARTBOMB_ON',
 appConst.typeSensorDampeningFortificationUnit: 'TGFU_DAMP_ON',
 appConst.typeMicroJumpFieldFortificationUnit: 'TGFU_FIELDJUMP_ON'}
TYPES_THAT_NEED_DOGMA_TURRETS = [appConst.typeEDENCOMGunStar,
 appConst.typeEDENCOMHeavyGunStar,
 appConst.typeTriglavianDisintegratorWerpost,
 appConst.typeTriglavianDamagedWerpost]

def IsTriglavianFortificationUnit(typeID):
    return bool(FORTIFICATION_UNIT_EFFECTS_BY_TYPE.get(typeID, False))


def GetTriglavianFortificationUnitOnlinedEffect(typeID):
    return FORTIFICATION_UNIT_EFFECTS_BY_TYPE.get(typeID, None)


class SentryGun(spaceObject.SpaceObject):

    def __init__(self):
        spaceObject.SpaceObject.__init__(self)
        self.modules = {}
        self.fitted = False
        self.typeID = None
        self.turretTypeID = TURRET_FALLBACK_TYPE_ID

    def Assemble(self):
        self.UnSync()
        self.SetStaticRotation()
        raceName = self.typeData.get('sofRaceName', None)
        if raceName is not None:
            self.turretTypeID = TURRET_TYPE_ID.get(raceName, TURRET_FALLBACK_TYPE_ID)
        if gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            self.FitHardpoints()
        self.SetupSharedAmbientAudio()

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        if self.typeID is None:
            self.logger.warning('FitHardpoints - No typeID')
            return
        self.fitted = True
        self.modules = {}
        if self.typeID in TYPES_THAT_NEED_DOGMA_TURRETS:
            self.modules = turretSet.TurretSet.FitTurrets(self.id, self.model, shipFaction=None)
        if len(self.modules) == 0:
            ts = turretSet.TurretSet.FitTurret(self.model, self.turretTypeID, 1, self.typeData.get('sofFactionName', None))
            if ts is not None:
                self.modules[self.id] = ts

    def LookAtMe(self):
        if not self.model:
            return
        if not self.fitted:
            self.FitHardpoints()

    def Release(self):
        if self.released:
            return
        self.modules = None
        spaceObject.SpaceObject.Release(self)

    def _SetControllerVariablesForTFUsFromSlimItem(self, slimItem):
        onlined_effect = GetTriglavianFortificationUnitOnlinedEffect(slimItem.typeID)
        self.SetControllerVariable(MATERIALIZATION_DURATION_ATTRIBUTE, MATERIALIZATION_DURATION_SECONDS)
        if slimItem.poseID:
            self.SetControllerVariable(MATERIALIZATION_BOOLEAN_ATTRIBUTE, 1)
        else:
            self.SetControllerVariable(MATERIALIZATION_BOOLEAN_ATTRIBUTE, 0)
        self.SetControllerVariable(onlined_effect, slimItem.poseID > 1)

    def SetControllerVariablesFromSlimItem(self, slimItem):
        spaceObject.SpaceObject.SetControllerVariablesFromSlimItem(self, slimItem)
        if slimItem is None:
            return
        if IsTriglavianFortificationUnit(slimItem.typeID):
            self._SetControllerVariablesForTFUsFromSlimItem(slimItem)
