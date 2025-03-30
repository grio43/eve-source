#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\turret.py
import blue
from carbon.common.script.sys.service import Service
from eve.client.script.parklife import states as state
from inventorycommon.const import turretModuleGroups

class TurretSvc(Service):
    __exportedcalls__ = {}
    __notifyevents__ = ['OnStateChange',
     'ProcessTargetChanged',
     'OnGodmaItemChange',
     'ProcessShipEffect',
     'ProcessActiveShipChanged',
     'OnChargeBeingLoadedToModule']
    __dependencies__ = []
    __guid__ = 'svc.turret'
    __servicename__ = 'turret'
    __displayname__ = 'Turret Service'

    def Run(self, memStream = None):
        self.LogInfo('Starting Turret Service')

    def Startup(self):
        pass

    def Stop(self, memStream = None):
        pass

    def OnStateChange(self, itemID, flag, *args):
        if flag == state.targeting:
            pass
        if flag != state.activeTarget:
            return
        ship = sm.GetService('michelle').GetBall(eve.session.shipid)
        rest = len(sm.GetService('target').GetTargets()) == 0
        for turretSet in getattr(ship, 'turrets', []):
            if rest:
                turretSet.Rest()
            elif not turretSet.IsShooting():
                turretSet.SetTarget(itemID)
                turretSet.TakeAim(itemID)

    def OnGodmaItemChange(self, item, change):
        ball = sm.GetService('michelle').GetBall(eve.session.shipid)
        if ball is None:
            return
        targetSvc = sm.GetService('target')
        if targetSvc is None:
            return
        if item.groupID in turretModuleGroups:
            ball.UnfitHardpoints()
            ball.FitHardpoints()
            targets = targetSvc.GetTargets()
            if len(targets) > 0:
                for turretSet in ball.turrets:
                    turretSet.SetTargetsAvailable(True)
                    turretSet.SetTarget(targetSvc.GetActiveTargetID())

    def ProcessTargetChanged(self, what, tid, reason):
        ship = sm.GetService('michelle').GetBall(eve.session.shipid)
        if ship is None:
            return
        if not hasattr(ship, 'turrets'):
            return
        blue.synchro.Yield()
        targets = sm.GetService('target').GetTargets()
        for turretSet in ship.turrets:
            turretSet.SetTargetsAvailable(len(targets) != 0)

    def ProcessShipEffect(self, godmaStm, effectState):
        if effectState.effectName == 'online':
            ship = sm.GetService('michelle').GetBall(eve.session.shipid)
            if ship is not None:
                turret = None
                for moduleID in getattr(ship, 'modules', []):
                    if moduleID == effectState.itemID:
                        turret = ship.modules[moduleID]

                if turret is not None:
                    if effectState.active:
                        turret.Online()
                    else:
                        turret.Offline()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            try:
                ship = bp.balls[shipID]
            except KeyError:
                return

            try:
                if session.shipid == session.structureid and getattr(ship, 'fitted', False):
                    return
                ship.UnfitHardpoints()
                ship.FitHardpoints()
            except AttributeError:
                self.LogInfo("Ship didn't have attribute fitted. Probably still being initialized", shipID)

    def OnChargeBeingLoadedToModule(self, moduleIDs, chargeTypeID, reloadTime):
        ship = sm.GetService('michelle').GetBall(eve.session.shipid)
        if ship is not None:
            for launcherID in moduleIDs:
                if launcherID in ship.modules:
                    turret = ship.modules[launcherID]
                    if turret is not None:
                        turret.Reload()
