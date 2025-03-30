#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\moonmining\autoMoonMining\client\auto_moon_miner_service.py
from carbon.common.script.sys.service import Service
from caching import Memoize

class AutoMoonMinerService(Service):
    __guid__ = 'svc.autoMoonMiner'
    __displayname__ = 'Auto Moon Miner Service'
    __notifyevents__ = ['ProcessSessionReset']

    @Memoize(5)
    def get_mining_details(self, solar_system_id, structure_id):
        return self.remote_service.RequestMiningDetails(solar_system_id, structure_id)

    @Memoize
    def get_mining_cycle_output(self, solar_system_id, structure_id):
        return self.remote_service.RequestMiningCycleOutput(solar_system_id, structure_id)

    @property
    def remote_service(self):
        return sm.RemoteSvc('autoMoonMining')

    def ProcessSessionReset(self):
        self.get_mining_details.clear_memoized()
        self.get_mining_cycle_output.clear_memoized()
