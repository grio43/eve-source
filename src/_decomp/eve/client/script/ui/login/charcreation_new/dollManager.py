#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\dollManager.py
import telemetry
import blue
import log
import copy
import eve.client.script.ui.login.charcreation_new.ccUtil as ccUtil
import charactercreator.const as ccConst
import evegraphics.settings as gfxsettings
from carbonui.uicore import uicore
from eve.common.script.paperDoll.paperDollDefinitions import BODY_CATEGORIES, DEFAULT_NUDE_PARTS, DESIRED_ORDER, LOD_SKIN
CLOTHING_ITEMS = (ccConst.topouter,
 ccConst.topmiddle,
 ccConst.bottomouter,
 ccConst.outer,
 ccConst.feet,
 ccConst.glasses,
 ccConst.bottommiddle,
 ccConst.mask)
ccDollManager = None

def GetCharacterCreationDollManager():
    global ccDollManager
    if ccDollManager is None:
        ccDollManager = CharacterCreationDollManager()
    return ccDollManager


class CharacterCreationDollManager(object):

    def __init__(self):
        self.characterSvc = sm.GetService('character')
        self.dolls = {}
        self._setColorsByCategory = {}
        self._setSpecularityByCategory = {}
        self._setIntensityByCategory = {}
        self.clothesOff = 0
        self.clothesStorage = {}
        self.clothesMetaStorage = {}
        self.dnaList = None
        self.lastLitHistoryBit = None

    def TearDown(self):
        self.dolls = {}

    def GetDoll(self, charID):
        return self.dolls.get(charID, None)

    def SetDoll(self, charID, doll):
        self.dolls[charID] = doll

    @telemetry.ZONE_METHOD
    def AddCharacter(self, charID, bloodlineID, raceID, genderID, scene = None, dna = None, validateColors = True, position = (0.0, 0.0, 0.0)):
        self.ResetDna()
        self.characterSvc.AddCharacterToScene(charID, scene, ccUtil.GenderIDToPaperDollGender(genderID), dna=dna, bloodlineID=bloodlineID, raceID=raceID, updateDoll=False, position=position)
        doll = self.characterSvc.GetSingleCharactersDoll(charID)
        self.dolls[charID] = doll
        while doll.IsBusyUpdating():
            blue.synchro.Yield()

        _ApplyGraphicsSettingsToDoll(doll)
        uicore.layer.charactercreation.controller.SetBloodline(charID, bloodlineID)
        self.characterSvc.SetDollBloodline(charID, bloodlineID)
        if validateColors:
            for categoryName in ccConst.COLORMAPPING.keys():
                self.UpdateColorSelectionFromDoll(categoryName)
                self.ValidateColors(categoryName)

        self.ClearDnaLog()
        self.characterSvc.UpdateDoll(charID, fromWhere='AddCharacter')

    def ResetDna(self, *args):
        self.dnaList = None
        self.lastLitHistoryBit = None

    @telemetry.ZONE_METHOD
    def ClearDnaLog(self):
        self.dnaList = []
        self.lastLitHistoryBit = None

    @telemetry.ZONE_METHOD
    def ClearDnaLogFromIndex(self, fromIndex):
        if self.dnaList:
            to = fromIndex + 1
            if to > len(self.dnaList):
                to = len(self.dnaList)
            self.dnaList = self.dnaList[:to]

    @telemetry.ZONE_METHOD
    def GetDollDNAHistory(self):
        return self.dnaList

    @telemetry.ZONE_METHOD
    def LoadDnaFromHistory(self, historyIndex):
        if len(self.characterSvc.characters) > 0:
            info = uicore.layer.charactercreation.controller.GetInfo()
            character = self.characterSvc.GetSingleCharacter(info.charID)
            if character:
                historyIndex = max(0, min(len(self.dnaList) - 1, historyIndex))
                dna, metadata = self.dnaList[historyIndex]
                metadata = copy.deepcopy(metadata)
                self.ToggleClothes(forcedValue=0, doUpdate=False)
                self.characterSvc.MatchDNA(character, dna)
                self.characterSvc.characterMetadata[info.charID] = metadata
                if self.characterSvc.GetSculptingActive():
                    sculpting = self.characterSvc.GetSculpting()
                    sculpting.UpdateFieldsBasedOnExistingValues(character.doll)
                self.characterSvc.UpdateDoll(info.charID, fromWhere='LoadDnaFromHistory', registerDna=False)
                self.characterSvc.SynchronizeHairColors(info.charID)

    def TryStoreDna(self, lastUpdateRedundant, currentIndex, charID, force = 0, allowRedundant = 0):
        if self.dnaList is not None:
            self.CheckDnaLog()
            dna = self.GetDNA(charID, getHiddenModifiers=False, getWeightless=True)
            if not allowRedundant and len(self.dnaList) > 0:
                if dna == self.dnaList[currentIndex][0]:
                    return
            currMetadata = copy.deepcopy(self.characterSvc.characterMetadata[charID])
            self.dnaList.append((dna, currMetadata))
            if lastUpdateRedundant or force:
                sm.ScatterEvent('OnHistoryUpdated')

    @telemetry.ZONE_METHOD
    def CheckDnaLog(self):
        currentStep = uicore.layer.charactercreation.controller.step
        if currentStep and currentStep.sr.historySlider:
            currentIndex, maxIndex = currentStep.sr.historySlider.GetCurrentIndexAndMaxIndex()
            if currentIndex != maxIndex:
                self.ClearDnaLogFromIndex(currentIndex)

    @telemetry.ZONE_METHOD
    def GetDNA(self, charID, getHiddenModifiers = False, getWeightless = False):
        return self.dolls[charID].GetDNA(getHiddenModifiers=getHiddenModifiers, getWeightless=getWeightless)

    @telemetry.ZONE_METHOD
    def SetItemType(self, itemType, weight = 1.0, doUpdate = True):
        info = uicore.layer.charactercreation.controller.GetInfo()
        category = self.characterSvc.GetCategoryFromResPath(itemType[1][0])
        if category in CLOTHING_ITEMS:
            if category in self.clothesStorage:
                self.clothesStorage.pop(category)
                self.clothesMetaStorage.pop(category)
            self.ToggleClothes(forcedValue=0, doUpdate=False)
        self.characterSvc.ApplyTypeToDoll(info.charID, itemType, weight=weight, doUpdate=False)
        if category in self._setColorsByCategory:
            var1, var2 = self._setColorsByCategory[category]
            self.SetColorValue(category, var1, var2, doUpdate=False)
        self.ValidateColors(category)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetItemType')

    @telemetry.ZONE_METHOD
    def SetStyle(self, category, style, variation = None, doUpdate = True):
        info = uicore.layer.charactercreation.controller.GetInfo()
        if style or variation or category in CLOTHING_ITEMS:
            self.ToggleClothes(forcedValue=0, doUpdate=False)
        self.characterSvc.ApplyItemToDoll(info.charID, category, style, removeFirst=True, variation=variation, doUpdate=False)
        if style:
            if category in self._setColorsByCategory:
                var1, var2 = self._setColorsByCategory[category]
                self.SetColorValue(category, var1, var2, doUpdate=False)
            self.ValidateColors(category)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetStyle')

    @telemetry.ZONE_METHOD
    def ClearCategory(self, category, doUpdate = True):
        self.SetStyle(category, style=None, doUpdate=doUpdate)

    def ToggleClothes(self, forcedValue = None, doUpdate = True, *args):
        valueBefore = self.clothesOff
        if forcedValue is None:
            self.clothesOff = not self.clothesOff
        else:
            self.clothesOff = forcedValue
        if valueBefore == self.clothesOff:
            return
        info = uicore.layer.charactercreation.controller.GetInfo()
        if info.charID in self.characterSvc.characters:
            character = self.characterSvc.GetSingleCharacter(info.charID)
            if self.clothesOff:
                self.RemoveClothes(character, info.charID, doUpdate=doUpdate)
            else:
                self.ReApplyClothes(character, info.charID, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def ReApplyClothes(self, character, charID, doUpdate = True):
        if not self.clothesStorage or character is None:
            return
        doll = character.doll
        bdm = doll.buildDataManager
        for category in self.clothesMetaStorage:
            self.characterSvc.SetCharacterMetadataByCategory(charID, category, self.clothesMetaStorage[category])

        modifiers = doll.SortModifiersForBatchAdding(self.clothesStorage.values())
        for modifier in modifiers:
            bdm.AddModifier(modifier)

        self.ResetClothesStorage()
        if doUpdate:
            sm.GetService('character').UpdateDollsAvatar(character)

    @telemetry.ZONE_METHOD
    def RemoveClothes(self, character, charID, doUpdate = True):
        if self.clothesStorage or character is None:
            return
        categoriesToRemove = BODY_CATEGORIES - (BODY_CATEGORIES.SKIN,
         BODY_CATEGORIES.TATTOO,
         BODY_CATEGORIES.TOPUNDERWEAR,
         BODY_CATEGORIES.BOTTOMUNDERWEAR,
         BODY_CATEGORIES.SKINTONE,
         BODY_CATEGORIES.SKINTYPE,
         BODY_CATEGORIES.SCARS)
        categoriesToRemove = list(categoriesToRemove)
        categoriesToRemove.sort(key=lambda x: -DESIRED_ORDER.index(x))
        self.ResetClothesStorage()
        bdm = character.doll.buildDataManager
        for category in categoriesToRemove:
            categoryModifiers = bdm.GetModifiersByCategory(category)
            self.StoreCharacterMetadata(category, charID)
            self.characterSvc.RemoveFromCharacterMetadata(charID, category)
            for modifier in categoryModifiers:
                if modifier.respath not in DEFAULT_NUDE_PARTS:
                    self.clothesStorage[category] = modifier
                    bdm.RemoveModifier(modifier)

        modifier = self.characterSvc.GetModifierByCategory(charID, ccConst.glasses)
        if modifier:
            self.StoreCharacterMetadata(ccConst.glasses, charID)
            self.characterSvc.RemoveFromCharacterMetadata(charID, ccConst.glasses)
            self.clothesStorage[ccConst.glasses] = modifier
            bdm.RemoveModifier(modifier)
        modifier = self.characterSvc.GetModifierByCategory(charID, ccConst.mask)
        if modifier:
            self.StoreCharacterMetadata(ccConst.mask, charID)
            self.characterSvc.RemoveFromCharacterMetadata(charID, ccConst.mask)
            self.clothesStorage[ccConst.mask] = modifier
            bdm.RemoveModifier(modifier)
        if doUpdate:
            sm.GetService('character').UpdateDollsAvatar(character)

    def ResetClothesStorage(self, *args):
        self.clothesStorage.clear()
        self.clothesMetaStorage.clear()

    def StoreCharacterMetadata(self, category, charID):
        self.clothesMetaStorage[category] = self.characterSvc.GetCharacterMetadataByCategory(charID, category)

    def UpdateColorSelectionFromDoll(self, category):
        if category not in ccConst.COLORMAPPING:
            return
        info = uicore.layer.charactercreation.controller.GetInfo()
        categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, info.genderID, info.raceID)
        if not categoryColors:
            return
        primary, secondary = categoryColors
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, category)
        if modifier:
            corPrimary = None
            corSecondary = None
            try:
                chosenPrimary, chosenSecondary = self.characterSvc.GetSingleCharactersMetadata(info.charID).typeColors[category]
                for primaryColorTuple in primary:
                    if primaryColorTuple[0] == chosenPrimary:
                        corPrimary = primaryColorTuple
                        break

                if secondary and chosenSecondary:
                    for secondaryColorTuple in secondary:
                        if secondaryColorTuple[0] == chosenSecondary:
                            corSecondary = secondaryColorTuple
                            break

            except KeyError:
                log.LogWarn('KeyError when getting Metadata for a single character in UpdateColorSelectionFromDoll', info.charID, category)

            if corPrimary is not None:
                self._setColorsByCategory[category] = (corPrimary, corSecondary)
            if category in self.characterSvc.characterMetadata[info.charID].typeWeights:
                self._setIntensityByCategory[category] = self.characterSvc.characterMetadata[info.charID].typeWeights[category]
            if category in self.characterSvc.characterMetadata[info.charID].typeSpecularity:
                self._setSpecularityByCategory[category] = self.characterSvc.characterMetadata[info.charID].typeSpecularity[category]

    @telemetry.ZONE_METHOD
    def SetColorValue(self, modifier, primaryColor, secondaryColor = None, doUpdate = True, ignoreValidate = False):
        self._setColorsByCategory[modifier] = (primaryColor, secondaryColor)
        info = uicore.layer.charactercreation.controller.GetInfo()
        self.characterSvc.SetColorValueByCategory(info.charID, modifier, primaryColor, secondaryColor, doUpdate=False)
        if ccUtil.HasUserDefinedSpecularity(modifier):
            specValue = self._setSpecularityByCategory.setdefault(modifier, 0.5)
            self.SetColorSpecularity(modifier, specValue, doUpdate=False)
        if ccUtil.HasUserDefinedWeight(modifier):
            defaultIntensity = ccConst.defaultIntensity.get(modifier, 0.5)
            intensityValue = self._setIntensityByCategory.setdefault(modifier, defaultIntensity)
            self.SetIntensity(modifier, intensityValue, doUpdate=False)
        if not ignoreValidate:
            self.ValidateColors(modifier)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetColorValue')

    @telemetry.ZONE_METHOD
    def SetColorSpecularity(self, modifier, specularity, doUpdate = True):
        self._setSpecularityByCategory[modifier] = specularity
        info = uicore.layer.charactercreation.controller.GetInfo()
        self.characterSvc.SetColorSpecularityByCategory(info.charID, modifier, specularity, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetIntensity(self, modifier, value, doUpdate = True):
        info = uicore.layer.charactercreation.controller.GetInfo()
        if modifier == ccConst.muscle:
            self.characterSvc.SetCharacterMuscularity(info.charID, value, doUpdate=doUpdate)
        elif modifier == ccConst.weight:
            self.characterSvc.SetCharacterWeight(info.charID, value, doUpdate=doUpdate)
        else:
            self._setIntensityByCategory[modifier] = value
            self.characterSvc.SetWeightByCategory(info.charID, modifier, value, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def ValidateColors(self, category):
        if category not in ccConst.COLORMAPPING:
            return
        info = uicore.layer.charactercreation.controller.GetInfo()
        categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, info.genderID, info.raceID)
        if not categoryColors:
            return
        primary, secondary = categoryColors
        hasValidColor = False
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, category)
        if modifier:
            currentColor = modifier[0].GetColorizeData()
            if secondary:
                if modifier[0].metaData.numColorAreas > 1:
                    for primaryColorTuple in primary:
                        primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                        pA, pB, pC = primaryColorValue['colors']
                        for secondaryColorTuple in secondary:
                            secondaryColorName, secondaryDisplayColor, secondaryColorValue = secondaryColorTuple
                            srA, srB, srC = secondaryColorValue['colors']
                            if pA == currentColor[0] and srB == currentColor[1] and srC == currentColor[2]:
                                hasValidColor = True
                                if category not in self._setColorsByCategory or self._setColorsByCategory[category][1] is None:
                                    self.SetColorValue(category, primaryColorTuple, secondaryColorTuple, doUpdate=False, ignoreValidate=True)
                                break

                        if hasValidColor:
                            break

                    if not hasValidColor:
                        for primaryColorTuple in primary:
                            primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                            if primaryColorValue['colors'] == currentColor:
                                hasValidColor = True
                                self.SetColorValue(category, primaryColorTuple, secondary[0], doUpdate=False, ignoreValidate=True)
                                break

                else:
                    for primaryColorTuple in primary:
                        primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                        if primaryColorValue['colors'] == currentColor:
                            hasValidColor = True
                            if category not in self._setColorsByCategory:
                                self.SetColorValue(category, primaryColorTuple, None, doUpdate=False, ignoreValidate=True)
                            break
                    else:
                        if category in self._setColorsByCategory:
                            hasValidColor = True
            else:
                for primaryColorTuple in primary:
                    primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                    if primaryColorValue['colors'] == currentColor:
                        hasValidColor = True
                        if category not in self._setColorsByCategory:
                            self.SetColorValue(category, primaryColorTuple, None, doUpdate=False, ignoreValidate=True)
                        break

            if not hasValidColor and primary:
                if secondary:
                    var2 = secondary[0]
                else:
                    var2 = None
                self.SetColorValue(category, primary[0], var2, doUpdate=False, ignoreValidate=True)


def _ApplyGraphicsSettingsToDoll(doll):
    doll.overrideLod = LOD_SKIN
    textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
    doll.textureResolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
    if ccUtil.IsSlowMachine():
        doll.useFastShader = True
    else:
        doll.useFastShader = False
