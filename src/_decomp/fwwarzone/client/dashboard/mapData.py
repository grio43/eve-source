#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\mapData.py
import cPickle
import logging
import blue
from fwwarzone.client.data.warzoneMapPositionsDataLoader import get_frontlines_map_data
log = logging.getLogger(__name__)

class TestOccupationState:

    def __init__(self, occupierID, adjacencyState):
        self.adjacencyState = adjacencyState
        self.occupierID = occupierID


class _WarzoneSystemData:

    def __init__(self, position, systemId, occupationState, neighbours, territoryTexturePath, textureWidth, textureHeight, xOffset, yOffset, isNavigationSystem = False):
        self.isNavigationSystem = isNavigationSystem
        self.yOffset = yOffset
        self.xOffset = xOffset
        self.textureHeight = textureHeight
        self.textureWidth = textureWidth
        self.territoryTexturePath = territoryTexturePath
        self.neighbours = neighbours
        self.occupationState = occupationState
        self.systemId = systemId
        self.position = position


class _SystemsData:

    def __init__(self, systems, mapWidth, mapHeight):
        self.systems = systems
        self.mapWidth = mapWidth
        self.mapHeight = mapHeight


class WarzoneMapData:

    def __init__(self):
        self.occupationStates = None
        self.starMapCache = None
        self.warzonePositionCache = None
        self.RefreshOccupationStates()

    def RefreshOccupationStates(self):
        self.occupationStates = sm.GetService('fwWarzoneSvc').GetAllOccupationStates()

    def GetWarzoneSystems(self, warzoneId):
        mapCache = self._GetStarMapCache()
        warzonesPosData = self._GetWarzonePositionData()
        warzone = self.occupationStates[warzoneId]
        systems = {}
        warzoneData = warzonesPosData[warzoneId]
        positionsData = warzoneData.systems
        mapHeight = warzoneData.mapHeight
        mapWidth = warzoneData.mapWidth
        for systemId, posData in positionsData.iteritems():
            posData = positionsData[systemId]
            system = mapCache['solarSystems'][systemId]
            position = (posData.xpos, posData.ypos)
            neighbours = system['neighbours']
            texturePath = ''
            textureWidth = 0
            textureHeight = 0
            xOffset = 0
            yOffset = 0
            isNavigationSystem = False
            occupationState = None
            if posData.territorySprite is not None and systemId in warzone:
                texturePath = posData.territorySprite.territoryIconFile
                textureWidth = posData.territorySprite.imageWidth
                textureHeight = posData.territorySprite.imageHeight
                xOffset = posData.territorySprite.xOffset
                yOffset = posData.territorySprite.yOffset
                occupationState = warzone[systemId]
            else:
                isNavigationSystem = True
            systems[systemId] = _WarzoneSystemData(position, systemId, occupationState, neighbours, texturePath, textureWidth, textureHeight, xOffset, yOffset, isNavigationSystem=isNavigationSystem)

        return _SystemsData(systems, mapWidth, mapHeight)

    def _GetWarzonePositionData(self):
        if self.warzonePositionCache is None:
            self.warzonePositionCache = get_frontlines_map_data()
        return self.warzonePositionCache

    def _GetStarMapCache(self):
        if self.starMapCache is None:
            res = blue.ResFile()
            starMapResPath = 'res:/staticdata/starMapCache.pickle'
            if not res.open('%s' % starMapResPath):
                log.error('Could not load Starmap Cache data file: %s' % starMapResPath)
            else:
                try:
                    pickleData = res.Read()
                    self.starMapCache = cPickle.loads(pickleData)
                finally:
                    res.Close()

        return self.starMapCache
