#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\tutorial.py
from .base import Action

class ActivateTutorialUndockCheck(Action):
    atom_id = 243

    def start(self, **kwargs):
        super(ActivateTutorialUndockCheck, self).start(**kwargs)
        from storylines.client.airnpe import skip_air_npe
        sm.GetService('undocking').ActivateUndockCheck(undockCheck=lambda : skip_air_npe())

    def stop(self):
        super(ActivateTutorialUndockCheck, self).stop()
        sm.GetService('undocking').DeactivateUndockCheck()


class DeactivateTutorialUndockCheck(Action):
    atom_id = 244

    def start(self, **kwargs):
        super(DeactivateTutorialUndockCheck, self).start(**kwargs)
        sm.GetService('undocking').DeactivateUndockCheck()


class ActivateTutorialCloneJumpCheck(Action):
    atom_id = 248

    def start(self, **kwargs):
        super(ActivateTutorialCloneJumpCheck, self).start(**kwargs)
        from storylines.client.airnpe import skip_air_npe
        sm.GetService('clonejump').ActivateCloneJumpCheck(cloneJumpCheck=lambda : skip_air_npe())

    def stop(self):
        super(ActivateTutorialCloneJumpCheck, self).stop()
        sm.GetService('clonejump').DeactivateCloneJumpCheck()


class DeactivateTutorialCloneJumpCheck(Action):
    atom_id = 249

    def start(self, **kwargs):
        super(DeactivateTutorialCloneJumpCheck, self).start(**kwargs)
        sm.GetService('clonejump').DeactivateCloneJumpCheck()


class ActivateTutorialStargateJumpCheck(Action):
    atom_id = 447

    def __init__(self, solar_system_ids = None, **kwargs):
        super(ActivateTutorialStargateJumpCheck, self).__init__(**kwargs)
        self.solar_system_ids = solar_system_ids

    def start(self, **kwargs):
        super(ActivateTutorialStargateJumpCheck, self).start(**kwargs)
        from stargate.client.jump_checks import add_stargate_jump_check
        add_stargate_jump_check('tutorial', self._cancel_jump)

    def stop(self):
        super(ActivateTutorialStargateJumpCheck, self).stop()
        from stargate.client.jump_checks import remove_stargate_jump_check
        remove_stargate_jump_check('tutorial')

    def _cancel_jump(self, stargateID, to_solar_system_id):
        if not self.solar_system_ids:
            self.solar_system_ids = [session.solarsystemid2]
        elif not isinstance(self.solar_system_ids, (list, tuple)):
            self.solar_system_ids = [self.solar_system_ids]
        if session.solarsystemid2 not in self.solar_system_ids:
            return False
        if to_solar_system_id in self.solar_system_ids:
            return False
        from storylines.client.airnpe import skip_air_npe
        skip = skip_air_npe()
        return not skip


class DeactivateTutorialStargateJumpCheck(Action):
    atom_id = 448

    def start(self, **kwargs):
        super(DeactivateTutorialStargateJumpCheck, self).start(**kwargs)
        from stargate.client.jump_checks import remove_stargate_jump_check
        remove_stargate_jump_check('tutorial')


class ActivateTutorialHomeStationCheck(Action):
    atom_id = 456

    def __init__(self, solar_system_ids = None, **kwargs):
        super(ActivateTutorialHomeStationCheck, self).__init__(**kwargs)
        self.solar_system_ids = solar_system_ids

    def start(self, **kwargs):
        super(ActivateTutorialHomeStationCheck, self).start(**kwargs)
        import homestation.client
        homestation.Service.instance().add_confirmation_check(self._confirmation_check)

    def stop(self):
        super(ActivateTutorialHomeStationCheck, self).stop()
        import homestation.client
        homestation.Service.instance().remove_confirmation_check(self._confirmation_check)

    def _confirmation_check(self, to_station_id):
        from storylines.client.airnpe import skip_air_npe
        return skip_air_npe()
