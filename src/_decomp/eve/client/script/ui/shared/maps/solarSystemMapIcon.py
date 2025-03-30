#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\solarSystemMapIcon.py
import collections
import geo2
import carbonui.const as uiconst
import inventorycommon
import trinity
from carbonui.primitives import vectorarc
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.common.lib import appConst
from eve.client.script.ui.shared.maps.map2D import Map2D
SIZE_DOTS = 6
DRAW_REGIONS = 1
DRAW_CONSTELLATIONS = 2
DRAW_SOLARSYSTEMS = 3
DRAW_SOLARSYSTEM_INTERIOR = 4
FLIPMAP = -1
Map2DCelestialItemInfoType = collections.namedtuple('Map2DItemInfoType', ['itemID',
 'typeID',
 'orbitID',
 'orbitIndex',
 'celestialIndex',
 'locationID',
 'groupID',
 'x',
 'y',
 'z'])

def GetMap2DItemsForSolarSystem(solarSystemID):
    items = []
    try:
        solarSystemItems = cfg.mapSolarSystemContentCache[solarSystemID]
    except (IndexError, KeyError):
        return []

    for stargateID, stargate in solarSystemItems.stargates.iteritems():
        items.append(Map2DCelestialItemInfoType(itemID=stargateID, orbitID=1, orbitIndex=1, locationID=solarSystemID, celestialIndex=0, groupID=appConst.groupStargate, typeID=stargate.typeID, x=stargate.position.x, y=stargate.position.y, z=stargate.position.z))

    for planetID, planet in solarSystemItems.planets.iteritems():
        items.append(Map2DCelestialItemInfoType(itemID=planetID, orbitID=1, orbitIndex=1, locationID=solarSystemID, celestialIndex=planet.celestialIndex, groupID=appConst.groupPlanet, typeID=planet.typeID, x=planet.position.x, y=planet.position.y, z=planet.position.z))
        asteroidBelts = getattr(planet, 'asteroidBelts', {})
        for asteroidBeltID, asteroidBelt in asteroidBelts.iteritems():
            items.append(Map2DCelestialItemInfoType(itemID=asteroidBeltID, orbitID=planetID, orbitIndex=1, celestialIndex=planet.celestialIndex, locationID=solarSystemID, groupID=9, typeID=asteroidBelt.typeID, x=asteroidBelt.position.x, y=asteroidBelt.position.y, z=asteroidBelt.position.z))

        npcStations = getattr(planet, 'npcStations', {})
        for npcStationID, npcStation in npcStations.iteritems():
            items.append(Map2DCelestialItemInfoType(itemID=npcStationID, orbitID=planetID, orbitIndex=1, celestialIndex=planet.celestialIndex, locationID=solarSystemID, groupID=appConst.groupStation, typeID=npcStation.typeID, x=npcStation.position.x, y=npcStation.position.y, z=npcStation.position.z))

        moons = getattr(planet, 'moons', {})
        for moonID, moon in moons.iteritems():
            items.append(Map2DCelestialItemInfoType(itemID=moonID, orbitID=planetID, orbitIndex=1, locationID=solarSystemID, celestialIndex=planet.celestialIndex, groupID=appConst.groupMoon, typeID=moon.typeID, x=moon.position.x, y=moon.position.y, z=moon.position.z))
            asteroidBelts = getattr(moon, 'asteroidBelts', {})
            for asteroidBeltID, asteroidBelt in asteroidBelts.iteritems():
                items.append(Map2DCelestialItemInfoType(itemID=asteroidBeltID, orbitID=moonID, orbitIndex=1, celestialIndex=planet.celestialIndex, locationID=solarSystemID, groupID=9, typeID=asteroidBelt.typeID, x=asteroidBelt.position.x, y=asteroidBelt.position.y, z=asteroidBelt.position.z))

            npcStations = getattr(moon, 'npcStations', {})
            for npcStationID, npcStation in npcStations.iteritems():
                items.append(Map2DCelestialItemInfoType(itemID=npcStationID, orbitID=planetID, orbitIndex=1, celestialIndex=planet.celestialIndex, locationID=solarSystemID, groupID=appConst.groupStation, typeID=npcStation.typeID, x=npcStation.position.x, y=npcStation.position.y, z=npcStation.position.z))

    return items


class SolarSystemMapIcon(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fillSize = 0.8
        self.solarSystemID = None

    def Draw(self, solarSystemID, size):
        self.solarSystemID = solarSystemID
        mapitems = GetMap2DItemsForSolarSystem(solarSystemID)
        self.DrawSolarsystem(mapitems, size)

    def DrawSolarsystem(self, mapitems, size):
        if not len(mapitems):
            return
        planets = []
        stargates = []
        asteroidbelts = []
        for item in mapitems:
            if item.groupID == appConst.groupPlanet:
                planets.append(item)
            elif item.groupID == appConst.groupStargate:
                stargates.append(item)
            elif item.groupID == appConst.groupAsteroidBelt:
                asteroidbelts.append(item)

        cords = {}
        self.size = size
        maxdist = self._GetMaxDistance(mapitems)
        self.sizefactor = size / 2 / maxdist * self.fillSize
        self._DrawSun()
        for i, item in enumerate(planets):
            self._DrawPlanet(cords, item)

        for orbit in planets:
            if orbit.itemID in cords:
                self._DrawOrbit(cords, orbit)

        for item in stargates:
            self._DrawStargate(cords, item)

    def _DrawSun(self):
        star = cfg.mapSolarSystemContentCache[self.solarSystemID].star
        gfx = inventorycommon.typeHelpers.GetGraphic(star.typeID)
        if hasattr(gfx, 'emissiveColor') and gfx.emissiveColor:
            color = tuple(gfx.emissiveColor)
        else:
            color = (1, 1, 1, 1)
        size = self.size * 0.4
        Sprite(parent=self, align=uiconst.CENTER, width=size, height=size, texturePath='res:/UI/Texture/shared/circularGradient2.png', state=uiconst.UI_DISABLED, color=color, opacity=0.03, blendMode=trinity.TR2_SBM_ADD)

    def _GetMaxDistance(self, mapitems):
        for item in mapitems:
            pos = (item.x, 0.0, item.z)
            maxdist = geo2.Vec3Length(pos)

        return maxdist

    def _DrawStargate(self, cords, item):
        x = FLIPMAP * self.sizefactor * item.x + self.size / 2 + 6
        y = self.sizefactor * item.z + self.size / 2
        radius = 1
        Sprite(parent=self, align=uiconst.TOPLEFT, left=x - 4, top=self.size - y - 4, width=SIZE_DOTS, height=SIZE_DOTS, texturePath='res:/UI/Texture/classes/graph/point.png', state=uiconst.UI_DISABLED, color=self.GetColorByGroupID(appConst.groupStargate))
        cords[item.itemID] = (x, self.size - y, radius)

    def _DrawOrbit(self, cords, orbit):
        x, y, radius = cords[orbit.itemID]
        center = self.size / 2
        frompos = geo2.Vector(float(center), 0.0, float(center))
        topos = geo2.Vector(float(x), 0.0, float(y))
        diff = topos - frompos
        rad = int(geo2.Vec3Length(diff))
        vectorarc.VectorArc(parent=self, align=uiconst.TOPLEFT, radius=rad, fill=False, left=center, lineWidth=1, top=center, width=self.size, height=self.size, color=self.GetColorByGroupID(appConst.groupPlanet), spriteEffect=trinity.TR2_SFX_FILL_AA)

    def _DrawPlanet(self, cords, item):
        pos = (item.x, 0.0, item.z)
        x = FLIPMAP * pos[0] * self.sizefactor + self.size / 2
        y = pos[2] * self.sizefactor + self.size / 2
        radius = 1
        cords[item.itemID] = (x, self.size - y, radius)
        Sprite(parent=self, align=uiconst.TOPLEFT, left=x - 4, top=self.size - y - 4, width=SIZE_DOTS, height=SIZE_DOTS, texturePath='res:/UI/Texture/classes/graph/point.png', state=uiconst.UI_DISABLED, color=self.GetColorByGroupID(appConst.groupPlanet))

    def GetChilds(self, parentID, childs, i):
        i += 1
        if i == 20 or len(childs) > 1000:
            return childs
        _childs = [ child for child in self.mapitems if child.orbitID == parentID and child not in childs ]
        if len(_childs):
            childs += _childs
            for granchild in _childs:
                childs = self.GetChilds(granchild.itemID, childs, i)

        return childs

    def GetColorByGroupID(self, groupID):
        col = {appConst.groupAsteroidBelt: (0, 0, 1),
         appConst.groupPlanet: (0.53, 0.53, 0.53),
         appConst.groupStargate: (0, 0.53, 0),
         appConst.groupStation: (1, 0.2, 0.2)}.get(groupID, (0.6, 0.6, 0.6))
        return col


class _MapIcon(Container):
    default_clipChildren = True
    map_level = None

    def __init__(self, location_id, size = 64, lineColors = None, dotColor = None, dotSizeMultiplier = None, **kwargs):
        super(_MapIcon, self).__init__(width=size, height=size, **kwargs)
        ssmap = Map2D()
        ssmap.Draw([location_id], self.map_level, self.map_level + 1, size - 4, self, lineColors=lineColors, dotColor=dotColor, dotSizeMultiplier=dotSizeMultiplier)


class ConstellationMapIcon(_MapIcon):
    map_level = 2


class RegionMapIcon(_MapIcon):
    map_level = 1
