#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\textImporting\textToTypeIDFinder.py
from textImporting import CleanAndStripText, GetNameFunc
SEARCH_LOCALIZED = 1
SEARCH_ENGLISH = 2
SEARCH_BOTH = 3

class TextToTypeIDFinder(object):

    def __init__(self, typeIDs, usingDefaultLanguage = True):
        self.typeIDs = typeIDs
        self.englishNamesToTypeIDs = self.GetTypesByLowerName(typeIDs)
        if usingDefaultLanguage:
            self.localizedNamesToTypeIDs = {}
        else:
            self.localizedNamesToTypeIDs = self.GetTypesByLowerName(typeIDs, localized=True)
        self.typeIDsToEnglishName = None
        self.typeIDsToLocalizedName = None

    def GetTypesByLowerName(self, typeIDs, localized = False):
        nameFunc = GetNameFunc(localized)
        return {CleanAndStripText(nameFunc(typeID)).lower():typeID for typeID in typeIDs}

    def GetLowerNameByTypeID(self, typeIDs, localized = False):
        nameFunc = GetNameFunc(localized)
        return {typeID:CleanAndStripText(nameFunc(typeID)).lower() for typeID in typeIDs}

    def GetTypeIDFromEitherLangage(self, potentialName):
        typeID = self._GetTypeIDFromName(potentialName)
        if typeID:
            return typeID
        return self._GetTypeIDFromNameLocalized(potentialName)

    def GetTypeIDFromName(self, potentialName, localized = False):
        try:
            if localized:
                return self._GetTypeIDFromNameLocalized(potentialName)
            return self._GetTypeIDFromNameLocalized(potentialName)
        except KeyError:
            return None

    def _GetTypeIDFromName(self, potentialName):
        try:
            return self.englishNamesToTypeIDs[potentialName]
        except KeyError:
            return None

    def _GetTypeIDFromNameLocalized(self, potentialName):
        try:
            return self.localizedNamesToTypeIDs[potentialName]
        except KeyError:
            return None

    def FindTypeIDsWithPartialMatch(self, searchText, searchWhat):
        if searchWhat == SEARCH_BOTH:
            self.PrimeTypeIDToNameDict(True)
            self.PrimeTypeIDToNameDict(False)
            typeDicts = [self.typeIDsToLocalizedName, self.typeIDsToEnglishName]
        elif searchWhat == SEARCH_LOCALIZED:
            self.PrimeTypeIDToNameDict(True)
            typeDicts = [self.typeIDsToLocalizedName]
        else:
            self.PrimeTypeIDToNameDict(False)
            typeDicts = [self.typeIDsToEnglishName]
        foundTypeIDs = set()
        for eachDictToUse in typeDicts:
            for typeID, typeName in eachDictToUse.iteritems():
                if typeName.find(searchText) != -1:
                    foundTypeIDs.add(typeID)

        return foundTypeIDs

    def PrimeTypeIDToNameDict(self, isLocalized):
        if isLocalized:
            if self.typeIDsToLocalizedName is not None:
                return
            self.typeIDsToLocalizedName = self.GetLowerNameByTypeID(self.typeIDs, isLocalized)
        else:
            if self.typeIDsToEnglishName is not None:
                return
            self.typeIDsToEnglishName = self.GetLowerNameByTypeID(self.typeIDs, isLocalized)
