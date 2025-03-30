#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\empireSelectionMapViewFilter.py
import random
from carbonui.util.color import Color
from eve.client.script.ui.login.charcreation_new.steps.empireSelection import empireSelectionConst
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.filters.baseMapFilterBinary import BaseMapFilterBinary
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
from eve.common.lib import appConst
from operations.common.warpSites import GetOperationSites

class EmpireSelectionMapFilter(BaseMapFilterBinary):
    spriteEffectPath = 'res:/Texture/Particle/empireSelectMap1.png'

    def __init__(self, filterID = None, itemID = None):
        super(EmpireSelectionMapFilter, self).__init__(filterID, itemID)
        self.schoolSystemIDs = [ GetOperationSites().get_solarsystem_id_from_school(schoolID) for schoolID in empireSelectionConst.ICONS_BY_SCHOOLID.keys() ]

    def _ConstructDataBySolarSystemID(self):
        ret = {}
        for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
            if solarSystem.factionID in appConst.factionsEmpires:
                ret[solarSystemID] = solarSystem

        return ret

    def GetStarColorAffected(self, solarSystemID):
        solarSystem = self.dataBySolarSystemID[solarSystemID]
        color = self.GetAffectedColor(solarSystem)
        if solarSystemID in self.schoolSystemIDs:
            color = Color(*color).SetOpacity(1.5).SetBrightness(1.0).SetSaturation(0.1).GetRGBA()
        return color

    def GetAffectedColor(self, solarSystem):
        color = Color(*empireSelectionConst.COLOR_BY_FACTIONID[solarSystem.factionID])
        saturation = 0.4 + random.random() * 0.2
        hue = color.GetHue()
        color.SetHSB(hue, saturation, 1.0)
        color.SetOpacity(0.5 + 0.2 * random.random())
        return color.GetRGBA()

    def GetStarColorUnaffected(self, solarSystemID):
        return (1.0, 1.0, 1.0, 1.5)

    def GetStarSizeAffected(self, solarSystemID):
        if solarSystemID in self.schoolSystemIDs:
            return mapViewConst.STAR_SIZE_AFFECTED * 15.0
        else:
            return mapViewConst.STAR_SIZE_AFFECTED * (2.0 + 10.0 * random.random())

    def GetStarSizeUnaffected(self):
        return mapViewConst.STAR_SIZE_AFFECTED

    def GetLineColor(self, solarSystemID):
        if self.IsAffected(solarSystemID):
            return self.GetStarColorAffected(solarSystemID)
        else:
            return (1.0, 1.0, 1.0, 0.3)
