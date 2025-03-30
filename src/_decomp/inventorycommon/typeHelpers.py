#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventorycommon\typeHelpers.py
from contrabandtypes.data import get_contraband_type
try:
    import eve.common.script.sys.eveCfg
    fsdDustIcons = eve.common.script.sys.eveCfg.CfgFsdDustIcons
    _averageMarketPrice = eve.common.script.sys.eveCfg.CfgAverageMarketPrice
except (ImportError, AttributeError):
    fsdDustIcons = []
    sounds = None
    _averageMarketPrice = None

import evetypes
from inventorycommon import const
from fsdBuiltData.common.soundIDs import GetSound as GetSoundFromSoundID
import fsdBuiltData.common.graphicIDs as fsdGraphicIDs
import fsdBuiltData.common.iconIDs as fsdIconIDs
import logging
log = logging.getLogger(__name__)

def GetGraphic(typeID):
    try:
        return fsdGraphicIDs.GetGraphic(evetypes.GetGraphicID(typeID))
    except IOError as e:
        raise e
    except Exception:
        pass


def GetGraphicFile(typeID):
    return fsdGraphicIDs.GetGraphicFile(evetypes.GetGraphicID(typeID), '')


def GetIcon(typeID):
    if typeID >= const.minDustTypeID:
        return fsdDustIcons().get(typeID, None)
    return fsdIconIDs.GetIcon(evetypes.GetIconID(typeID))


def GetIconFile(typeID, icon_size = 64):
    texture_path = None
    if evetypes.IsRenderable(typeID):
        texture_path = sm.GetService('photo').ExistsInCacheOrRenders(typeID, icon_size, None, None)
    if not texture_path:
        texture_path = fsdIconIDs.GetIconFile(evetypes.GetIconID(typeID), '')
    return texture_path or ''


def GetHoloIconPath(typeID):
    try:
        g = GetGraphic(typeID)
        return fsdGraphicIDs.GetIconFolder(g) + '/' + fsdGraphicIDs.GetSofHullName(g) + '_isis.png'
    except Exception:
        typeString = typeID if typeID is not None else 'None'
        exceptionMsg = 'Failed to find respath to the holographic icon for typeID: %s' % typeString
        log.exception(exceptionMsg)
        return


def GetSound(typeID):
    try:
        soundID = evetypes.GetSoundID(typeID)
        return GetSoundFromSoundID(soundID)
    except Exception:
        pass


def GetIllegality(typeID):
    contrabandType = get_contraband_type(typeID)
    if contrabandType is None:
        return {}
    return {fID:contraband for fID, contraband in contrabandType.factions.iteritems()}


def GetIllegalityInFaction(typeID, factionID):
    contrabandType = get_contraband_type(typeID)
    if contrabandType is None:
        return
    return contrabandType.factions.get(factionID, None)


def GetAdjustedAveragePrice(typeID):
    try:
        return _averageMarketPrice()[typeID].adjustedPrice
    except KeyError:
        return None


def GetAveragePrice(typeID):
    try:
        if typeID in (79785,):
            return 1000
        return _averageMarketPrice()[typeID].averagePrice
    except KeyError:
        return None
