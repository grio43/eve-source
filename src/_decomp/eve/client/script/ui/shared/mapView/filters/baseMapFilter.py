#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\baseMapFilter.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.filters import mapFilterConst
from eve.client.script.ui.shared.mapView.filters.mapFilterConst import NEUTRAL_COLOR, PARTICLE_SPRITE_TEXTURE

class BaseMapFilter(object):
    name = ''
    hint = None
    color = Color.RED
    spriteEffectPath = mapFilterConst.PARTICLE_SPRITE_DATA_TEXTURE
    agencyContentGroupID = None
    spriteEffectPathNear = mapFilterConst.PARTICLE_SPRITE_TEXTURE

    def __init__(self, filterID = None, itemID = None):
        self.filterID = filterID
        self.itemID = itemID
        self.dataBySolarSystemID = self._ConstructDataBySolarSystemID()

    def GetLegend(self):
        pass

    def _ConstructDataBySolarSystemID(self):
        return {}

    def IsAffected(self, solarSystemID):
        return solarSystemID in self.dataBySolarSystemID

    @classmethod
    def GetName(cls):
        return cls.name

    @classmethod
    def GetHint(cls):
        return cls.hint

    def GetAgencyContentGroupID(self):
        return self.agencyContentGroupID

    def GetStarSize(self, solarSystemID):
        if self.IsAffected(solarSystemID):
            return self.GetStarSizeAffected(solarSystemID)
        else:
            return self.GetStarSizeUnaffected()

    def GetStarSizeAffected(self, solarSystemID):
        return mapViewConst.STAR_SIZE_STANDARD

    def GetStarSizeUnaffected(self):
        return mapViewConst.STAR_SIZE_STANDARD

    def GetLineColor(self, solarSystemID):
        return self.GetStarColorUnaffected(solarSystemID)

    def GetStarColor(self, solarSystemID):
        if self.IsAffected(solarSystemID):
            return self.GetStarColorAffected(solarSystemID)
        else:
            return self.GetStarColorUnaffected(solarSystemID)

    def GetStarColorUnaffected(self, solarSystemID):
        return NEUTRAL_COLOR

    def GetStarColorAffected(self, solarSystemID):
        return self.color

    def GetSystemHint(self, solarSystemID):
        if self.IsAffected(solarSystemID):
            return self.GetHintAffected(solarSystemID)

    def GetHintAffected(self, solarSystemID):
        numInstances = self.GetNumInstances(solarSystemID)
        if numInstances is not None:
            return str(numInstances)

    def GetSpriteEffectPath(self):
        return self.spriteEffectPath

    def GetSpriteEffectPathNear(self):
        return self.spriteEffectPathNear

    def GetSearchHandler(self):
        return None

    def GetSystemsToZoomTo(self):
        return self.GetSolarSystemIDs()

    def GetSolarSystemIDs(self):
        return self.dataBySolarSystemID.keys()

    def GetNumInstances(self, solarSystemID):
        data = self.dataBySolarSystemID.get(solarSystemID, [])
        if data is None:
            return
        elif isinstance(data, int):
            return data
        else:
            return len(data)
