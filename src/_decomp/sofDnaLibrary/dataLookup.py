#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sofDnaLibrary\dataLookup.py
import re
from evegraphics.utils import BuildSOFDNAFromGraphicID
from sofDnaLibrary.data import GetSkins, GetMaterials, GetGraphicIDs, GetTypes, GetMaterialSets

def DnaMatch(dna, hullQuery, factionQuery, raceQuery):
    if dna is None:
        return False
    combinedQuery = '%s:%s:%s.*' % (hullQuery, factionQuery, raceQuery)
    match = re.match('^%s$' % combinedQuery, dna, re.IGNORECASE)
    return match is not None


def Matches(actualValue, queryValue):
    if actualValue is None:
        return False
    if actualValue.lower() == queryValue.lower():
        return True
    match = re.match('^%s$' % queryValue, actualValue)
    return match is not None


def GetSkinnedDnaForDnaQuery(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    skins = GetSkins()
    types = GetTypes()
    matchingDnaStrings = {}
    for skin, skinInfo in skins.iteritems():
        for typeID in skinInfo.types:
            graphicID = types[typeID].graphicID
            dna = BuildSOFDNAFromGraphicID(graphicID, int(skinInfo.skinMaterialID))
            if DnaMatch(dna, hullQuery, factionQuery, raceQuery):
                graphicIDStrings = matchingDnaStrings.get(graphicID, [])
                graphicIDStrings.append(dna)
                matchingDnaStrings[graphicID] = graphicIDStrings

    return matchingDnaStrings


def GetDefaultDnaStringsForDnaQuery(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    matchingDnaStrings = {}
    for graphicID in GetGraphicIDs():
        dna = BuildSOFDNAFromGraphicID(graphicID)
        if DnaMatch(dna, hullQuery, factionQuery, raceQuery):
            matchingDnaStrings[graphicID] = dna

    return matchingDnaStrings
