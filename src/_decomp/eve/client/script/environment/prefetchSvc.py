#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\prefetchSvc.py
import inventorycommon.typeHelpers
import everesourceprefetch
from carbon.common.script.sys.service import Service
from fsdBuiltData.common.graphicIDs import GetGraphicFile

class PrefetchSvc(Service):
    __guid__ = 'svc.prefetchSvc'
    __notifyevents__ = ['OnSessionChanged']

    def _AddGraphicAttribute(self, pla, attr, filesToPrefetch):
        graphic = GetGraphicFile(getattr(pla, attr))
        filesToPrefetch.add(graphic.lower())

    def GatherFilesForSolarSystem(self, ssid):
        filesToPrefetch = set()
        neighborSystemContents = cfg.mapSolarSystemContentCache[ssid]
        for stargateID, stargateInfo in neighborSystemContents.stargates.iteritems():
            graphic = inventorycommon.typeHelpers.GetGraphicFile(stargateInfo.typeID)
            filesToPrefetch.add(graphic.lower())

        for planetID, planetInfo in neighborSystemContents.planets.iteritems():
            pla = planetInfo.planetAttributes
            self._AddGraphicAttribute(pla, 'heightMap1', filesToPrefetch)
            self._AddGraphicAttribute(pla, 'heightMap2', filesToPrefetch)
            self._AddGraphicAttribute(pla, 'shaderPreset', filesToPrefetch)

        return filesToPrefetch

    def SchedulePrefetchForSystem(self, ssid):
        key = 'solarsystem_%d_statics' % ssid
        if not everesourceprefetch.KeyExists(key):
            filesToPrefetch = self.GatherFilesForSolarSystem(ssid)
            everesourceprefetch.AddFileset(key, filesToPrefetch)
        everesourceprefetch.ScheduleFront(key)

    def OnSessionChanged(self, isremote, session, change):
        if 'stationid' in change:
            stationId = change['stationid'][1]
            if stationId:
                npcStation = cfg.mapSolarSystemContentCache.npcStations.get(stationId, None)
                if npcStation:
                    self.SchedulePrefetchForSystem(npcStation.solarSystemID)
                return
        if 'solarsystemid' not in change:
            return
        ssid = change['solarsystemid'][1]
        if ssid is None:
            return
        systemInfo = cfg.mapSystemCache[ssid]
        for neighbor in systemInfo.neighbours:
            self.SchedulePrefetchForSystem(neighbor.solarSystemID)
