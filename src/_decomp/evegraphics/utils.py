#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\utils.py
import evetypes
import fsdBuiltData.common.graphicIDs as fsdGraphicIDs
import fsdBuiltData.common.graphicMaterialSets as materialSets

def IsValidSOFDNA(dna):
    sp = dna.split(':')
    if len(sp) < 3:
        return False
    return True


def BuildSOFDNAFromTypeID(typeID, materialSetID = None, multiHullTypeIDList = None):
    if typeID is None:
        return
    if not evetypes.Exists(typeID):
        return
    sofBuildClass = evetypes.GetSofBuildClassOrNone(typeID)
    multiHullGraphicIDList = None
    if multiHullTypeIDList is not None:
        multiHullGraphicIDList = [ evetypes.GetGraphicID(t) for t in multiHullTypeIDList ]
    return BuildSOFDNAFromGraphicID(evetypes.GetGraphicID(typeID), materialSetID=materialSetID, sofBuildClass=sofBuildClass, multiHullGraphicIDList=multiHullGraphicIDList)


def CombineSOFHullName(gfxIDList):
    hullNameList = [ fsdGraphicIDs.GetSofHullName(fsdGraphicIDs.GetGraphic(g)) for g in gfxIDList ]
    if None in hullNameList:
        return
    hullNameList.sort()
    return ';'.join(hullNameList)


def CombineSOFDNA(sofHullName, sofFactionName, sofRaceName, sofAddition = None):
    dna = sofHullName + ':' + sofFactionName + ':' + sofRaceName
    if sofAddition is not None:
        dna += ':' + sofAddition
    return dna


def BuildSOFDNAFromGraphicID(graphicID, materialSetID = None, sofBuildClass = None, multiHullGraphicIDList = None):
    if graphicID is None:
        return
    graphicInfo = fsdGraphicIDs.GetGraphic(graphicID)
    if graphicInfo is None:
        return
    if materialSetID is None:
        materialSetID = fsdGraphicIDs.GetSofMaterialSetID(graphicInfo)
    if multiHullGraphicIDList is not None:
        hull = CombineSOFHullName(multiHullGraphicIDList)
    else:
        hull = CombineSOFHullName([graphicID])
    faction = fsdGraphicIDs.GetSofFactionName(graphicInfo)
    race = fsdGraphicIDs.GetSofRaceName(graphicInfo)
    dnaAddition = None
    if hull is None or faction is None or race is None:
        return
    materialSet = materialSets.GetGraphicMaterialSet(materialSetID)
    if materialSet is not None:
        faction = materialSets.GetSofFactionName(materialSet, faction)
        dnaAddition = 'material?' + materialSets.GetMaterial1(materialSet) + ';' + materialSets.GetMaterial2(materialSet) + ';' + materialSets.GetMaterial3(materialSet) + ';' + materialSets.GetMaterial4(materialSet)
        resPathInsert = materialSets.GetResPathInsert(materialSet)
        if resPathInsert is not None:
            dnaAddition += ':respathinsert?' + resPathInsert
        sofPatternName = materialSets.GetSofPatternName(materialSet)
        if sofPatternName is not None:
            dnaAddition += ':pattern?' + sofPatternName + ';' + materialSets.GetCustomMaterial1(materialSet) + ';' + materialSets.GetCustomMaterial2(materialSet)
    layouts = fsdGraphicIDs.GetSofLayoutNames(graphicInfo)
    if layouts is not None:
        addition = 'layout?' if dnaAddition is None else ':layout?'
        if len(layouts) > 0:
            addition += ';'.join(layouts)
            dnaAddition = addition if dnaAddition is None else dnaAddition + addition
    if sofBuildClass is not None:
        if dnaAddition is None:
            dnaAddition = 'class?' + str(sofBuildClass)
        else:
            dnaAddition += ':class?' + str(sofBuildClass)
    return CombineSOFDNA(hull, faction, race, dnaAddition)


def RemapDirtLevel(dirtLevel0To100):

    def lerp(min, max, f):
        return (max - min) * f + min

    if dirtLevel0To100 < 50:
        currentDirtLevel = lerp(-2.0, 0.0, dirtLevel0To100 / 50.0)
    else:
        currentDirtLevel = lerp(0.0, 0.7, (dirtLevel0To100 - 50) / 50.0)
    if currentDirtLevel == 0.55:
        currentDirtLevel = None
    return currentDirtLevel


def CalcDirtLevelFromAge(lastCleanTimeStamp):
    import blue
    dirtTimeDiff = blue.os.TimeDiffInMs(lastCleanTimeStamp, blue.os.GetWallclockTime())
    dirtTimeDiff = max(dirtTimeDiff, 0.0)
    msInWeek = 604800000.0
    dirtTimeDiffInWeeks = dirtTimeDiff / msInWeek
    dirtLevel = 0.7 - 1.0 / (pow(dirtTimeDiffInWeeks, 0.65) + 1.0 / 2.7)
    return dirtLevel


class DummyGroup(object):

    def __init__(self, **kwargs):
        self._d = kwargs

    def Get(self, key, default = None):
        return self._d.get(key, default)

    def Set(self, key, val):
        self._d[key] = val


def GetDnaFromResPath(respath):
    lowerCaseResPath = respath.lower()
    prefix = 'res:/dx9/model/ship/'
    if not lowerCaseResPath.startswith(prefix):
        raise RuntimeError
    lowerCaseResPath = lowerCaseResPath[len(prefix):]
    parts = lowerCaseResPath.split('/')
    if len(parts) < 4:
        raise RuntimeError
    race = parts[0]
    if len(parts) == 5:
        faction = parts[3]
        ship = parts[4]
        ship = ship.replace('_' + faction, '')
    else:
        faction = race + 'base'
        ship = parts[3]
    ship = ship.split('.')[0]
    dna = '%s:%s:%s' % (ship, faction, race)
    return dna


def GetCorrectEffectPath(effectPath, model):
    if getattr(model, 'isAnimated', False):
        return effectPath.replace('.red', '_skinned.red')
    return effectPath
