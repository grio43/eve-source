#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\npsStationTaxModifier.py
from brennivin.itertoolsext import FrozenDict
from caching import Memoize
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import npcStationTaxModifierLoader
except ImportError:
    npcStationTaxModifierLoader = None

WAR_FACTION_ID = 'warFactionID'

class NpcStationTaxModifiersByStationID(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/npcStationTaxModifier.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/npcStationTaxModifier.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/npcStationTaxModifier.fsdbinary'
    __loader__ = npcStationTaxModifierLoader


@Memoize
def _GetTaxModifierInfoByStationID():
    return FrozenDict(NpcStationTaxModifiersByStationID.GetData())


def GetTaxModifierForStation(stationID, warFactionID):
    modifier = 1.0
    modifierInfoForStation = _GetTaxModifierInfoByStationID().get(int(stationID), None)
    if modifierInfoForStation is None:
        return modifier
    if warFactionID:
        modifier *= _GetModifierForWarFactionID(modifierInfoForStation, warFactionID)
    return modifier


def _GetModifierForWarFactionID(modifierInfoForStation, warFactionID):
    defaultModifier = 1.0
    taxInfoForWarFactionID = modifierInfoForStation.get('warFactionID')
    if not taxInfoForWarFactionID:
        return defaultModifier
    for k, v in taxInfoForWarFactionID.taxModifierByValue.iteritems():
        if k == warFactionID:
            return v

    return defaultModifier
