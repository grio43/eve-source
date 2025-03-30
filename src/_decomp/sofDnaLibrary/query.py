#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sofDnaLibrary\query.py
from sofDnaLibrary.data import GetTypes
from sofDnaLibrary.dataLookup import GetSkinnedDnaForDnaQuery, GetDefaultDnaStringsForDnaQuery
import time
queryResultCache = {}

def GenerateDnaString(hull, faction, race, dnaAddition = ''):
    dna = '%s:%s:%s' % (hull, faction, race)
    if dnaAddition != '':
        dna += ':%s' % dnaAddition
    return dna


def GetSkinnedDnaStringsMatchingQuery(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    graphicIdsToDnaStrings = GetSkinnedDnaForDnaQuery(hullQuery, factionQuery, raceQuery)
    dnaStrings = []
    for graphicID, dnaList in graphicIdsToDnaStrings.iteritems():
        dnaStrings.extend(dnaList)

    return list(set(dnaStrings))


def GetDefaultDnaStringsMatchingQuery(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    return GetDefaultDnaStringsForDnaQuery(hullQuery, factionQuery, raceQuery).values()


def GetDnaStringsMatchingQuery(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    dnaString = GenerateDnaString(hullQuery, factionQuery, raceQuery)
    print "Getting dna strings that match '%s'" % dnaString
    skinnedDna = GetSkinnedDnaStringsMatchingQuery(hullQuery, factionQuery, raceQuery)
    defaultDna = GetDefaultDnaStringsMatchingQuery(hullQuery, factionQuery, raceQuery)
    dnaStrings = skinnedDna
    dnaStrings.extend(defaultDna)
    return dnaStrings


def GetDefaultDnaStringsWithTypesMatchingQuery(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    dnaString = GenerateDnaString(hullQuery, factionQuery, raceQuery)
    print "Getting dna strings that match '%s' and are linked to types" % dnaString
    defaultDnaGraphicID = GetDefaultDnaStringsForDnaQuery(hullQuery, factionQuery, raceQuery)
    dnaStrings = set()
    for typeID, typeData in GetTypes().iteritems():
        if typeData.graphicID in defaultDnaGraphicID:
            dnaStrings.add(defaultDnaGraphicID[typeData.graphicID])

    return list(dnaStrings)


if __name__ == '__main__':
    start = time.time()
    dnaResult = GetDnaStringsMatchingQuery(hullQuery='asd1_t1', raceQuery='amarr')
    print dnaResult
