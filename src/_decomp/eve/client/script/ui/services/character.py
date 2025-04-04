#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\character.py
import colorsys
import random
import types
import locks
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_CONTENT
from carbon.common.script.util.commonutils import GetAttrs
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.paperDoll.paperDollSculpting import PaperDollSculpting
from eve.client.script.paperDoll.paperDollSpawnWrappers import PaperDollManager
from eve.client.script.ui.login.charcreation.eveDollRandomizer import EveDollRandomizer
from eve.common.script.util import paperDollUtil
import log
import blue
import charactercreator.const as ccConst
import eve.client.script.ui.login.charcreation.ccUtil as ccUtil
import telemetry
import geo2
import uthread
import evegraphics.settings as gfxsettings
from carbonui.uicore import uicore
from eveprefs import prefs, boot
import charactercreator.client.animparams as animparams
from eve.common.script.paperDoll.paperDollDefinitions import BODY_CATEGORIES, ConvertDNAForDB, DOLL_EXTRA_PARTS, GENDER, HAIR_CATEGORIES, HEAD_CATEGORIES, ModifierRow, SEPERATOR_CHAR
from eve.common.script.util.paperDollBloodLineAssets import bloodlineAssets
WEIGHT_MODIFIER_PATH = ['bodyshapes/fatshape']
MUSCLE_MODIFIER_PATH = ['bodyshapes/muscularshape']
POTBELLY_PATH = ['bodyshapes/abs_forwardshape']
THIN_MODIFIER_PATH = ['bodyshapes/thinshape']
CATEGORY_NAMES = [HEAD_CATEGORIES.FACEMODIFIERS, DOLL_EXTRA_PARTS.BODYSHAPES, DOLL_EXTRA_PARTS.UTILITYSHAPES]
WEIGHT_BREAK_DOWNS = [('weightUpDown', 'up', 'down'), ('weightLeftRight', 'left', 'right'), ('weightForwardBack', 'forward', 'back')]

class Character(Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.character'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnGraphicSettingsChanged']
    __dependencies__ = ['cacheDirectoryLimit']

    @telemetry.ZONE_METHOD
    def __init__(self):
        super(Character, self).__init__()
        self.characters = {}
        self.characterMetadata = {}
        self.index = 0
        self.sculpting = None
        self.sculptingActive = False
        self.scene = None
        self.animationBloodlineData = None
        self.preloadedResources = []
        self.cachedHairColorVariations = {}
        self.cachedEyeshadowColorVariations = {}
        self.cachedHeadTattooColorVariations = {}
        self.cachedPortraitResourcesByPath = None
        self.baseHairColors = None
        self.tuckingOptions = {}
        for k, (modifierName, locationName, subKey) in ccConst.TUCKMAPPING.iteritems():
            self.tuckingOptions[modifierName] = subKey

        self.assetsToIDs = {'male': None,
         'female': None}
        self.textureQuality = 1
        self.cachedPortraitInfo = {}
        self.modifierLocationsByName = {}
        self.modifierLocationsByKey = {}

    def lazyprop(fn):
        attr_name = '_lazy_' + fn.__name__

        @property
        def _lazyprop(self):
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)

        return _lazyprop

    @lazyprop
    def factory(self):
        factory = sm.GetService('paperDollClient').dollFactory
        factory.clothSimulationActive = False
        return factory

    @lazyprop
    def paperDollManager(self):
        pdm = PaperDollManager(self.factory)
        return pdm

    def PopulateModifierLocationDicts(self, force = False):
        if not force and len(self.modifierLocationsByKey) > 0:
            return
        self.modifierLocationsByName = {}
        self.modifierLocationsByKey = {}
        for row in cfg.paperdollModifierLocations:
            self.modifierLocationsByKey[row.modifierLocationID] = row.modifierKey
            self.modifierLocationsByName[row.modifierKey] = row.modifierLocationID

    @telemetry.ZONE_METHOD
    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.GFX_TEXTURE_QUALITY in changes:
            if len(self.characters):
                dollID = self.characters.keys()[0]
                pdc = self.characters[dollID]
                pdc.doll.buildDataManager.SetAllAsDirty()
                pdc.Update()
        if gfxsettings.GFX_CHAR_TEXTURE_QUALITY in changes:
            textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
            self.SetTextureQuality(textureQuality)
        if gfxsettings.GFX_SHADER_QUALITY in changes:
            if len(self.characters):
                dollID = self.characters.keys()[0]
                pdc = self.characters[dollID]
                pdc.doll.useFastShader = False
        if self.sculpting is not None:
            self.sculpting.SetupPickScene(doUpdate=False)

    @telemetry.ZONE_METHOD
    def PreloadItems(self, gender, items):
        return
        self.preloadedResources = []
        if gender == ccConst.GENDERID_FEMALE:
            options = self.factory.femaleOptions
        elif gender == ccConst.GENDERID_MALE:
            options = self.factory.maleOptions
        else:
            log.LogWarn('Preloading failed. Invalid gender!')
            return
        resources = []
        for cat in options:
            for item in items:
                if item in cat:
                    resources.append(options[cat])

        for paths in resources:
            for path in paths:
                try:
                    whitelist = ['.png', '.dds', '.gr2']
                    if path.lower()[-4:] in whitelist:
                        self.preloadedResources.append(blue.resMan.GetResource(path))
                except:
                    log.LogException()

    @telemetry.ZONE_METHOD
    def ClearPreloads(self):
        self.preLoadedResources = []

    def InitializeNewCharacter(self, charID, genderID, bloodlineID, raceID):
        plugList = self.GetAvailableTypesByCategory('makeup/implants', genderID, raceID)
        if len(plugList) > 0:
            self.ApplyTypeToDoll(charID, plugList[0], doUpdate=False)
        self.EnsureUnderwear(charID, genderID, raceID)
        if genderID == ccConst.GENDERID_MALE:
            self.ApplyTypeToDoll(charID, self.GetRelativePath(ccConst.BASE_HAIR_TYPE_MALE), doUpdate=False)
        else:
            self.ApplyTypeToDoll(charID, self.GetRelativePath(ccConst.BASE_HAIR_TYPE_FEMALE), doUpdate=False)
        self.SetInitialSkintype(charID, genderID, bloodlineID, raceID)
        self.RandomizeDollCategory(charID, raceID, ccConst.eyes, 0)
        self.RandomizeDollCategory(charID, raceID, ccConst.eyebrows, 0)
        self.RandomizeDollCategory(charID, raceID, ccConst.hair, 0)
        self.RandomizeDollCategory(charID, raceID, ccConst.outer, 0)
        self.RandomizeDollCategory(charID, raceID, ccConst.topmiddle, 0)
        self.RandomizeDollCategory(charID, raceID, ccConst.bottomouter, 0)
        self.RandomizeDollCategory(charID, raceID, ccConst.feet, 0)
        p, s = self.GetAvailableColorsForCategory('hair', genderID, raceID)
        primary = random.choice(p)
        secondary = random.choice(s)
        self.SetColorValueByCategory(charID, 'hair', primary, secondary, doUpdate=False)
        self.SetHairDarkness(charID, 0.5)
        self.SynchronizeHairColors(charID)

    def GetNewCharacterMetadata(self, genderID, bloodlineID):
        return utillib.KeyVal(genderID=genderID, bloodlineID=bloodlineID, types={}, typeColors={}, typeWeights={}, typeSpecularity={}, hairDarkness=0.0)

    def GetCharacterMetadataByCategory(self, charID, category):
        type_meta = {}
        if category in self.characterMetadata[charID].types:
            type_meta['types'] = self.characterMetadata[charID].types[category]
            type_meta['typeColors'] = self.characterMetadata[charID].typeColors.get(category)
            type_meta['typeSpecularity'] = self.characterMetadata[charID].typeSpecularity.get(category)
            type_meta['typeWeights'] = self.characterMetadata[charID].typeWeights.get(category)
        return type_meta

    def SetCharacterMetadataByCategory(self, charID, category, type_meta):
        if type_meta:
            self.characterMetadata[charID].types[category] = type_meta['types']
            if type_meta['typeColors']:
                self.characterMetadata[charID].typeColors[category] = type_meta['typeColors']
            if type_meta['typeSpecularity']:
                self.characterMetadata[charID].typeSpecularity[category] = type_meta['typeSpecularity']
            if type_meta['typeWeights']:
                self.characterMetadata[charID].typeWeights[category] = type_meta['typeWeights']

    def RemoveFromCharacterMetadata(self, charID, category):
        if category in self.characterMetadata[charID].types:
            self.characterMetadata[charID].types.pop(category, None)
            self.characterMetadata[charID].typeColors.pop(category, None)
            self.characterMetadata[charID].typeSpecularity.pop(category, None)
            self.characterMetadata[charID].typeWeights.pop(category, None)

    @telemetry.ZONE_METHOD
    def AddCharacterToScene(self, charID, scene, gender, bloodlineID = None, raceID = None, dna = None, position = (0.0, 0.0, 0.0), updateDoll = True, textureResolution = None, lod = None, noRandomize = False, anim = True):
        applyNewCharacterTypes = False
        if not noRandomize:
            noRandomize = prefs.GetValue('NoRandomize', 0)
        name = 'doll_%s' % charID
        if charID in self.characters:
            character = self.characters[charID]
            if hasattr(character, 'MoveToScene'):
                character.MoveToScene(scene)
            else:
                doll = character.doll
                self.characters[charID] = character = self.paperDollManager.SpawnDoll(scene, doll=doll, updateDoll=updateDoll, point=position, name=name)
        elif dna is not None:
            randomDoll = paperDollUtil.CreateRandomDollNoClothes(gender, bloodlineID, raceID, noRandomize=True)
            self.characters[charID] = character = self.paperDollManager.SpawnDoll(scene, doll=randomDoll, updateDoll=updateDoll, point=position, name=name)
        else:
            applyNewCharacterTypes = True
            randomDoll = paperDollUtil.CreateRandomDollNoClothes(gender, bloodlineID, raceID, noRandomize=noRandomize)
            self.characters[charID] = character = self.paperDollManager.SpawnDoll(scene, doll=randomDoll, updateDoll=updateDoll, point=position, name=name)
        self.characterMetadata[charID] = self.GetNewCharacterMetadata(ccUtil.PaperDollGenderToGenderID(gender), bloodlineID)
        needUpdate = False
        if character is not None:
            if lod is not None:
                character.doll.overrideLod = lod
                needUpdate = True
            if textureResolution is not None:
                character.doll.textureResolution = textureResolution
                needUpdate = True
        self.scene = scene
        if character is None:
            log.LogError('AddCharacterToScene: Character', charID, 'not created')
            return
        avatar = character.avatar
        if anim:
            network = animparams.GetParamsPerAvatar(avatar, charID)
            network.Rebuild()
        if applyNewCharacterTypes and not noRandomize:
            self.InitializeNewCharacter(charID, ccUtil.PaperDollGenderToGenderID(gender), bloodlineID, raceID)
        elif dna is not None:
            if type(dna) is list:
                self.MatchDNA(character, dna)
            else:
                self.ApplyDBRowToDoll(charID, gender, bloodlineID, raceID, dna)
            needUpdate = True
        if needUpdate and updateDoll:
            self.UpdateDoll(charID)
        return character

    @telemetry.ZONE_METHOD
    def RemoveCharacter(self, charID):
        if charID not in self.characters:
            return
        avatar = self.characters[charID].avatar
        if avatar and avatar in self.scene.dynamics:
            self.scene.dynamics.remove(avatar)
        paperDollCharacter = self.characters.pop(charID)
        self.paperDollManager.RemovePaperDollCharacter(paperDollCharacter)
        del paperDollCharacter
        del self.characterMetadata[charID]

    @telemetry.ZONE_METHOD
    def CleanCircularReferences(self):
        for each in self.characters:
            character = self.characters[each]
            if character.avatar:
                for cs in character.avatar.curveSets:
                    for bind in cs.bindings:
                        bind.copyValueCallable = None

                    del cs.bindings[:]
                    del cs.curves[:]

                del character.avatar.curveSets[:]

    @telemetry.ZONE_METHOD
    def TearDown(self):
        self.preloadedResources = []
        self.paperDollManager.ClearDolls()
        self.CleanCircularReferences()
        self.characters = {}
        sceneManager = sm.GetService('sceneManager')
        sceneManager.UnregisterScene('characterCreation')
        if self.sculpting is not None:
            self.sculpting.avatar = None
            if self.sculpting.highlightGhost is not None:
                self.sculpting.highlightGhost.avatar = None
            if self.sculpting.bodyHighlightGhost is not None:
                self.sculpting.bodyHighlightGhost.avatar = None
            self.sculpting.scene = None
            self.sculpting.pickScene = None
            self.sculpting = None
        self.scene = None

    @telemetry.ZONE_METHOD
    def GetModifierByPath(self, charID, path):
        if charID in self.characters:
            doll = self.characters[charID].doll
            return doll.GetBuildDataByResPath(path, includeFuture=True)

    @telemetry.ZONE_METHOD
    def GetModifiersByCategory(self, charID, category):
        if charID not in self.characters:
            return None
        doll = self.characters[charID].doll
        ret = []
        mods = doll.buildDataManager.GetModifiersAsList(includeFuture=True)
        for m in mods:
            resPath = m.GetResPath()
            resPathSplit = resPath.split('/')
            categSplit = category.split('/')
            match = True
            for i, each in enumerate(categSplit):
                if not (len(resPathSplit) > i and resPathSplit[i] == each):
                    match = False
                    break

            if match:
                ret.append(m)

        return ret

    @telemetry.ZONE_METHOD
    def UpdateDoll(self, charID, fromWhere = None, registerDna = True, forceUpdate = False):
        if charID not in self.characters:
            return
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        if self.sculpting:
            self.sculpting.UpdateBlendShapes([])
            if forceUpdate:
                doll.Update(self.factory, avatar)
        else:
            doll.Update(self.factory, avatar)

        def wait_t():
            while doll.IsBusyUpdating():
                blue.synchro.Yield()

            if registerDna and hasattr(uicore, 'layer'):
                uicore.layer.charactercreation.controller.TryStoreDna(doll.lastUpdateRedundant, fromWhere)
            sm.ScatterEvent('OnDollUpdated', charID, doll.lastUpdateRedundant, fromWhere)
            if hasattr(uicore, 'layer'):
                uicore.layer.charactercreation.controller.UnlockNavigation()

        if hasattr(uicore, 'layer') and uicore.layer.charactercreation.isopen:
            uthread.new(wait_t)

    @telemetry.ZONE_METHOD
    def UpdateTattoos(self, charID, doUpdate = True, paperdoll = None):
        if charID not in self.characters and not paperdoll:
            return
        if paperdoll is None:
            pdc = self.characters[charID]
        else:
            pdc = paperdoll

        def fun_t():
            while pdc.doll.IsBusyUpdating():
                blue.synchro.Yield()

            tattooModifiers = pdc.doll.buildDataManager.GetModifiersByCategory(BODY_CATEGORIES.TATTOO)
            if tattooModifiers:
                for each in tattooModifiers:
                    each.IsDirty = True

            if doUpdate:
                pdc.Update()

        uthread.new(fun_t)

    @telemetry.ZONE_METHOD
    def SetDollBloodline(self, charID, bloodlineID):
        self.characterMetadata[charID].bloodlineID = bloodlineID
        doll = self.characters[charID].doll
        gender = doll.gender
        limitPath = 'res:/Graphics/Character/Global/FaceSetup/ScultpingLimits/' + bloodlineAssets[bloodlineID] + '_' + gender + '_blendshape_limits.yaml'
        doll.buildDataManager.AddBlendshapeLimitsFromFile(limitPath)
        self.AdaptDollAnimationData(bloodlineAssets[bloodlineID], self.characters[charID].avatar, gender)

    @telemetry.ZONE_METHOD
    def ResetDoll(self, charID, bloodlineID = None):
        if bloodlineID is not None:
            self.SetDollBloodline(charID, bloodlineID)
        if self.characterMetadata[charID].bloodlineID:
            self.ApplyItemToDoll(charID, 'head', bloodlineAssets[self.characterMetadata[charID].bloodlineID], doUpdate=True)

    @telemetry.ZONE_METHOD
    def AdaptDollAnimationData(self, bloodline, avatar, gender):
        if not self.animationBloodlineData:
            animPath = 'res:/Graphics/Character/Global/FaceSetup/AnimationData.yaml'
            self.animationBloodlineData = ccUtil.LoadFromYaml(animPath)
        network = animparams.GetParamsPerAvatar(avatar)
        for param in self.animationBloodlineData[bloodline][gender]:
            try:
                paramName = 'ControlParameters|' + param
                network.SetControlParameter(paramName, self.animationBloodlineData[bloodline][gender][param])
            except:
                log.LogWarn('Invalid control parameter for bloodline: ' + param)

    @telemetry.ZONE_METHOD
    def SetCharacterWeight(self, charID, weight, doUpdate = True):
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        network = animparams.GetParamsPerAvatar(avatar, charID)
        if network is not None:
            network.SetControlParameter('ControlParameters|WeightAdjustment', weight)
        for mod in THIN_MODIFIER_PATH:
            limit = doll.buildDataManager.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is None:
                modifier = doll.AddResource(mod, 0.0, self.factory)
            if weight <= 0.5:
                modifier.weight = (1 - weight * 2.0) * multiplier
            else:
                modifier.weight = 0.0

        for mod in WEIGHT_MODIFIER_PATH:
            limit = doll.buildDataManager.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            if weight >= 0.5:
                weight = (weight - 0.5) * 2.0 * multiplier
            else:
                weight = 0.0
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is None:
                modifier = doll.AddResource(mod, weight, self.factory)
            else:
                modifier.weight = weight

        if doUpdate:
            self.UpdateTattoos(charID, doUpdate=False)
            self.UpdateDoll(charID, fromWhere='SetCharacterWeight')

    @telemetry.ZONE_METHOD
    def GetCharacterWeight(self, charID):
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        ret = []
        for mod in WEIGHT_MODIFIER_PATH:
            limit = doll.buildDataManager.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is not None:
                if modifier.weight > 0.0:
                    return 0.5 + modifier.weight * 0.5 / multiplier

        for mod in THIN_MODIFIER_PATH:
            limit = doll.buildDataManager.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is not None:
                return (1 - modifier.weight / multiplier) * 0.5

        return 0.5

    @telemetry.ZONE_METHOD
    def SetCharacterMuscularity(self, charID, weight, doUpdate = True):
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        for mod in MUSCLE_MODIFIER_PATH:
            limit = doll.buildDataManager.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is None:
                modifier = doll.AddResource(mod, 0.0, self.factory)
            modifier.weight = weight * multiplier

        if doUpdate:
            self.UpdateTattoos(charID, doUpdate=False)
            self.UpdateDoll(charID, fromWhere='SetCharacterMuscularity')

    @telemetry.ZONE_METHOD
    def GetCharacterMuscularity(self, charID):
        doll = self.characters[charID].doll
        avatar = self.characters[charID].avatar
        ret = []
        for mod in MUSCLE_MODIFIER_PATH:
            limit = doll.buildDataManager.modifierLimits.get(mod.split('/')[-1])
            multiplier = 1.0
            if limit and len(limit) == 2:
                multiplier = limit[1]
            modifier = self.GetModifierByPath(charID, mod)
            if modifier is not None:
                ret = modifier.weight / multiplier
            else:
                ret = 0.0

        return ret

    @telemetry.ZONE_METHOD
    def GetModifierByCategory(self, charID, category, getAll = False):
        modifiers = self.GetModifiersByCategory(charID, category)
        if not modifiers:
            return None
        elif getAll:
            return modifiers
        else:
            if category == HAIR_CATEGORIES.BEARD:
                for modifier in modifiers:
                    if modifier.name != 'stubble':
                        return modifier

            return modifiers[0]

    @telemetry.ZONE_METHOD
    def GetEyeshadowColors(self, genderID):
        colorVars = self.LoadEyeShadowColorVariations(genderID)
        return self.GetModifierColors(colorVars=colorVars)

    @telemetry.ZONE_METHOD
    def LoadEyeShadowColorVariations(self, genderID):
        if genderID != ccConst.GENDERID_FEMALE:
            log.LogError('LoadEyeShadowColorVariations - can only use this for females')
            return []
        cached = self.cachedEyeshadowColorVariations.get(genderID)
        if cached is not None:
            return cached
        variations = self.GetModifierColorVariation(ccConst.EYESHADOWCOLORS, ccConst.EYESHADOWCOLOR_PATHS[genderID])
        self.cachedEyeshadowColorVariations[genderID] = variations
        return variations

    @telemetry.ZONE_METHOD
    def GetHairColors(self, genderID):
        colorVars = self.LoadHairColorVariations(genderID)
        if self.baseHairColors is None:
            self.baseHairColors = [ccUtil.LoadFromYaml(ccConst.BASE_HAIR_COLOR_FEMALE), ccUtil.LoadFromYaml(ccConst.BASE_HAIR_COLOR_MALE)]
        baseColor = self.baseHairColors[genderID]
        if baseColor is None:
            log.LogWarn('Failed to load base color for hair')
            baseColor = (0.5, 0.5, 0.5, 1.0)
        return self.GetModifierColors(colorVars=colorVars)

    @telemetry.ZONE_METHOD
    def LoadHairColorVariations(self, genderID):
        if genderID is None:
            log.LogError('LoadHairColorVariations - genderID must not be None')
            return []
        cached = self.cachedHairColorVariations.get(genderID)
        if cached is not None:
            return cached
        variations = self.GetModifierColorVariation(ccConst.HAIRCOLORS, ccConst.HAIRCOLOR_PATHS[genderID])
        self.cachedHairColorVariations[genderID] = variations
        return variations

    def GetHeadTattooColors(self, genderID):
        colorVars = self.LoadHeadTattooVariations(genderID)
        return self.GetModifierColors(colorVars=colorVars)

    @telemetry.ZONE_METHOD
    def LoadHeadTattooVariations(self, genderID):
        if genderID is None:
            log.LogError('LoadHeadTattooVariations - genderID must not be None')
            return []
        cached = self.cachedHeadTattooColorVariations.get(genderID)
        if cached is not None:
            return cached
        variations = self.GetModifierColorVariation(ccConst.HEADTATTOOCOLORS, ccConst.HEADTATTOOCOLOR_PATHS[genderID])
        self.cachedHeadTattooColorVariations[genderID] = variations
        return variations

    @telemetry.ZONE_METHOD
    def GetModifierColorVariation(self, colors, path):
        variations = {}
        for each in colors:
            colorFile = path + each
            var = ccUtil.LoadFromYaml(colorFile)
            if var is not None:
                variations[each.split('.')[0]] = var
            else:
                log.LogWarn('GetModifierColorVariation - Could not load color file:', colorFile)

        return variations

    def GetModifierColors(self, colorVars):
        retColorsA = []
        retColorsBC = []
        for each in colorVars:
            color = colorVars[each]['colors']
            if color and type(color[0]) == types.TupleType:
                if each.lower().endswith('_a'):
                    displayColor = color[0]
                    r, g, b, a = displayColor
                    yiq = colorsys.rgb_to_yiq(r, g, b)
                    retColorsA.append((yiq, (each, (r,
                       g,
                       b,
                       1.0), colorVars[each])))
                elif each.lower().endswith('_bc'):
                    displayColor = color[1]
                    r, g, b, a = displayColor
                    yiq = colorsys.rgb_to_yiq(r, g, b)
                    retColorsBC.append((yiq, (each, (r,
                       g,
                       b,
                       1.0), colorVars[each])))
                else:
                    print 'Unsupported modifier color', each

        retColorsA = SortListOfTuples(retColorsA)
        retColorsBC = SortListOfTuples(retColorsBC)
        return (retColorsA, retColorsBC)

    def SetHairDarkness(self, charID, darkness):
        if darkness != self.characterMetadata[charID].hairDarkness:
            self.characterMetadata[charID].hairDarkness = darkness
            self.SynchronizeHairColors(charID)

    def GetHairDarkness(self, charID):
        return self.characterMetadata[charID].hairDarkness

    @telemetry.ZONE_METHOD
    def SynchronizeHairColors(self, charID):
        hairData = self.GetModifierByCategory(charID, ccConst.hair)
        if hairData is not None:
            colorizeData = hairData.colorizeData
            orgA, orgB, orgC = colorizeData
            newA = geo2.Vector(*orgA)
            lowA = newA * 0.2
            newA = geo2.Vec4Lerp(lowA, newA, self.characterMetadata[charID].hairDarkness)
            adjustedColor = (newA, orgB, orgC)
            for hairModifier in (ccConst.beard, ccConst.eyebrows):
                if hairModifier == ccConst.beard:
                    hms = self.GetModifierByCategory(charID, hairModifier, getAll=True)
                else:
                    hms = [self.GetModifierByCategory(charID, hairModifier)]
                if hms is None:
                    continue
                for hm in hms:
                    if hm:
                        hm.colorizeData = adjustedColor
                        hm.pattern = hairData.pattern
                        hm.patternData = hairData.patternData
                        hm.specularColorData = hairData.specularColorData
                        hm.SetColorVariation('none')

    @telemetry.ZONE_METHOD
    def GetAvailableColorsForCategory(self, categoryPath, genderID, raceID):
        if categoryPath == ccConst.hair:
            return self.GetHairColors(genderID)
        if categoryPath == ccConst.t_head:
            return self.GetHeadTattooColors(genderID)
        if genderID == ccConst.GENDERID_FEMALE and categoryPath == ccConst.eyeshadow:
            return self.GetEyeshadowColors(genderID)
        if type(genderID) is int:
            genderID = ccUtil.GenderIDToPaperDollGender(genderID)
        combined = {}
        typeData = self.GetAvailableTypesByCategory(categoryPath, genderID, raceID, getTypesOnly=True)
        for each in typeData:
            modifier = self.factory.CollectBuildData(genderID, each[0])
            combined.update(modifier.colorVariations)

        doneA = []
        doneBC = []
        retColorsA = []
        retColorsBC = []
        for colorName, colorData in combined.iteritems():
            if categoryPath.startswith(ccConst.lipstick):
                if colorName.find('_glossy') != -1 or colorName.find('_medium') != -1:
                    continue
            displayColor = colorData.get('colors') if colorData else None
            if displayColor is None:
                log.LogWarn('No colors in colorData when calling GetAvailableColorsForCategory', categoryPath, genderID)
                continue
            if type(displayColor) == types.TupleType or type(displayColor) == types.ListType:
                displayColor = colorData['colors'][0]
                r, g, b, a = displayColor
            else:
                r, g, b = displayColor
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            r, g, b = colorsys.hsv_to_rgb(h, s * 0.8, v * 0.8)
            yiq = colorsys.rgb_to_yiq(r, g, b)
            if colorName.lower().endswith('_bc'):
                if colorData['colors'] not in doneBC:
                    retColorsBC.append((yiq, (colorName, (r,
                       g,
                       b,
                       1.0), colorData)))
                    doneBC.append(colorData['colors'])
            elif colorData['colors'] not in doneA:
                retColorsA.append((yiq, (colorName, (r,
                   g,
                   b,
                   1.0), colorData)))
                doneA.append(colorData['colors'])

        retColorsA = SortListOfTuples(retColorsA)
        retColorsBC = SortListOfTuples(retColorsBC)
        return (retColorsA, retColorsBC)

    @telemetry.ZONE_METHOD
    def GetCharacterColorVariations(self, charID, category):
        colors = []
        selectedIndex = None
        modifier = self.GetModifierByCategory(charID, category)
        if modifier:
            colorVars = modifier.GetColorVariations()
            if category == ccConst.skintone:
                bloodline = self.characterMetadata[charID].bloodlineID
                bloodlineFilter = {1: 'deteis',
                 2: 'civire',
                 11: 'achura',
                 7: 'gallente',
                 8: 'intaki',
                 12: 'jinmei',
                 3: 'sebiestor',
                 4: 'brutor',
                 14: 'vherokior',
                 5: 'amarr',
                 13: 'khanid',
                 6: 'nikunni'}
                filter = bloodlineFilter[bloodline]
                newColorVars = []
                for c in colorVars:
                    if c.startswith(filter):
                        newColorVars.append(c)

                colorVars = newColorVars
            if category == ccConst.lipstick:
                newColorVars = []
                for c in colorVars:
                    if c.lower().endswith('_medium'):
                        newColorVars.append(c)

                colorVars = newColorVars
            selectedColor = modifier.GetColorizeData()
            for i, cv in enumerate(colorVars):
                c = modifier.GetColorsFromColorVariation(cv)
                if selectedColor == c:
                    selectedIndex = i
                colors.append((cv, c))

        return (colors, selectedIndex)

    def PrimePortraitResourceCache(self):
        with locks.TempLock('PrimePortraitResourceCache'):
            if self.cachedPortraitResourcesByPath is not None:
                return
            cacheDict = {}
            for eachResource in cfg.paperdollPortraitResources.rows:
                cacheDict[eachResource.resPath.lower()] = eachResource

            self.cachedPortraitResourcesByPath = cacheDict

    def GetAvailableBackgrounds(self):
        return self.GetAvailablePortraitResources('background')

    def GetAvailablePortraitResources(self, categoryName):
        availableTypeIDs = sm.GetService('cc').GetMyApparel()
        ret = []
        for eachResource in cfg.paperdollPortraitResources.rows:
            if eachResource.resourceCategoryID != categoryName:
                continue
            if eachResource.typeID is None or eachResource.typeID in availableTypeIDs:
                ret.append(eachResource)

        return ret

    def GetPortraitResourceByPath(self, path):
        self.PrimePortraitResourceCache()
        path = path.lower()
        return self.cachedPortraitResourcesByPath.get(path, None)

    @telemetry.ZONE_METHOD
    def GetAvailableTypesByCategory(self, category, gender, raceID, getTypesOnly = False, forceAllTypes = False):
        if type(gender) is int:
            gender = ccUtil.GenderIDToPaperDollGender(gender)
        types = self.factory.ListTypes(gender, category)
        ret = []
        retData = []
        resFile = blue.ResFile()
        availableTypeIDs = sm.GetService('cc').GetMyApparel()
        hasContentRole = session.role & ROLE_CONTENT or forceAllTypes
        defined_fsd_type_paths = self.GetDefinedFSDTypes()
        initialCreation = GetAttrs(uicore, 'layer', 'charactercreation', 'mode') == ccConst.MODE_FULLINITIAL_CUSTOMIZATION
        for i, each in enumerate(types):
            typeData = self.factory.GetItemType(each, gender=gender)
            if typeData is None:
                log.LogWarn('GetItemType for path returned None', each)
                continue
            assetID, assetTypeID = self.GetAssetAndTypeIDsFromPath(gender, each)
            path_parts = each.lower().split(category)
            non_fsd_resource = category + category.join(path_parts[1:]) not in defined_fsd_type_paths
            if non_fsd_resource:
                log.LogWarn("Item type doesn't exist in FSD: ", each)
                if not hasContentRole:
                    continue
            if not hasContentRole and assetTypeID is not None and (assetTypeID not in availableTypeIDs or initialCreation):
                continue
            if len(typeData) == 4:
                typeData = typeData[:-1]
            if not non_fsd_resource:
                fsdData = cfg.paperdollResources.Get(assetID)
                if fsdData:
                    empireRestrictions = fsdData.empireRestrictions
                    if empireRestrictions is not None and raceID in empireRestrictions:
                        pass
                    if raceID is None or empireRestrictions is None or empireRestrictions and raceID not in empireRestrictions:
                        ret.append(((assetTypeID is None, i), (assetID, typeData, assetTypeID)))
                        retData.append(typeData)
            else:
                ret.append(((assetTypeID is None, i), (assetID, typeData, assetTypeID)))
                retData.append(typeData)

        if getTypesOnly:
            return retData
        log.LogNotice('GetAvailableTypesByCategory -> (%s, %s, %s, %s)' % (gender,
         category,
         raceID,
         len(ret)))
        ret = SortListOfTuples(ret)
        return ret

    @telemetry.ZONE_METHOD
    def GetDefinedFSDTypes(self):
        type_path_list = []
        for resource in cfg.paperdollResources.rows:
            type_path_list.append(resource.resPath.lower())

        return type_path_list

    @telemetry.ZONE_METHOD
    def GetAvailableItemsByCategory(self, category, gender, bloodline, showVariations = False):
        if type(gender) is int:
            gender = ccUtil.GenderIDToPaperDollGender(gender)
        items = self.factory.ListOptions(gender, category, showVariations)
        self.PreloadItems(gender, items)
        return items

    @telemetry.ZONE_METHOD
    def GetCategoryFromResPath(self, resPath):
        parts = resPath.split('/')
        return '/'.join(parts[:-1])

    @telemetry.ZONE_METHOD
    def ApplyTypeToDoll(self, charID, itemType, weight = 1.0, doUpdate = True, rawColorVariation = None):
        assetTypeID = None
        if itemType is None:
            return
        self.PopulateModifierLocationDicts()
        genderID = self.characterMetadata[charID].genderID
        if type(itemType) is not tuple:
            charGender = ccUtil.GenderIDToPaperDollGender(genderID)
            itemTypeData = self.factory.GetItemType(itemType, gender=charGender)
            if itemTypeData is None:
                itemTypeLower = itemType.lower()
                if BODY_CATEGORIES.TOPINNER in itemTypeLower:
                    self.ApplyItemToDoll(charID, BODY_CATEGORIES.TOPINNER, None, removeFirst=True, doUpdate=False)
                elif BODY_CATEGORIES.BOTTOMINNER in itemTypeLower:
                    self.ApplyItemToDoll(charID, BODY_CATEGORIES.BOTTOMINNER, None, removeFirst=True, doUpdate=False)
                else:
                    log.LogError("Item type file is missing, can't be loaded", itemType)
                return
            assetID, assetTypeID = self.GetAssetAndTypeIDsFromPath(charGender, itemType)
            itemType = (assetID, itemTypeData[:3], assetTypeID)
        doll = self.characters[charID].doll
        category = self.GetCategoryFromResPath(itemType[1][0])
        modifierLocationKey = self.modifierLocationsByName.get(category, None)
        toRemove = []
        for otherCategory, otherResourceID in self.characterMetadata[charID].types.iteritems():
            if otherResourceID is None:
                continue
            otherResource = cfg.paperdollResources.Get(otherResourceID)
            if otherResource.typeID is None:
                continue
            if otherResource.clothingRemovesCategory == modifierLocationKey or otherResource.clothingRemovesCategory2 == modifierLocationKey:
                toRemove.append(otherCategory)

        for itemToRemove in toRemove:
            self.ApplyItemToDoll(charID, itemToRemove, None, removeFirst=True, doUpdate=False)

        activeMod = self.GetModifierByCategory(charID, category)
        if activeMod:
            doll.RemoveResource(activeMod.GetResPath(), self.factory)
        modifier = doll.AddItemType(self.factory, itemType[1], weight, rawColorVariation)
        self.characterMetadata[charID].types[category] = itemType[0]
        myTypeID = itemType[2]
        if myTypeID:
            resource = cfg.paperdollResources.Get(itemType[0])
            removesCategory = resource.clothingRemovesCategory
            removesCategory2 = resource.clothingRemovesCategory2
            if removesCategory is not None and removesCategory != 0 and int(removesCategory) in self.modifierLocationsByKey:
                modifierLocationName = self.modifierLocationsByKey[int(removesCategory)]
                self.ApplyItemToDoll(charID, modifierLocationName, None, removeFirst=True, doUpdate=False)
            if removesCategory2 is not None and removesCategory2 != 0 and int(removesCategory2) in self.modifierLocationsByKey:
                modifierLocationName = self.modifierLocationsByKey[int(removesCategory2)]
                self.ApplyItemToDoll(charID, modifierLocationName, None, removeFirst=True, doUpdate=False)
        if ccUtil.HasUserDefinedWeight(category):
            self.characterMetadata[charID].typeWeights[category] = weight
        if category in (ccConst.hair, ccConst.beard, ccConst.eyebrows) and assetTypeID is None:
            self.SynchronizeHairColors(charID)
        if category == ccConst.lipstick and ccConst.augm_face in self.modifierLocationsByName:
            doll.buildDataManager.SetAllAsDirty()
        if doUpdate:
            self.UpdateDoll(charID, fromWhere='ApplyTypeToDoll')
        return modifier

    @telemetry.ZONE_METHOD
    def ApplyItemToDoll(self, charID, category, name, removeFirst = False, variation = None, doUpdate = True):
        doll = self.characters[charID].doll
        modifier = None
        modifierFoundForVariationSwitch = False
        if name and variation:
            modifier = self.GetModifierByCategory(charID, category)
            if modifier and modifier.name.split(SEPERATOR_CHAR)[-1] == name:
                modifier.SetVariation(variation)
                modifierFoundForVariationSwitch = True
        if not modifierFoundForVariationSwitch:
            if removeFirst:
                if name:
                    modifier = self.GetModifierByCategory(charID, category)
                    if modifier:
                        self.RemoveFromCharacterMetadata(charID, category)
                        doll.RemoveResource(modifier.respath, self.factory)
                else:
                    modifiers = self.GetModifierByCategory(charID, category, getAll=True)
                    if modifiers:
                        self.RemoveFromCharacterMetadata(charID, category)
                        for modifier in modifiers:
                            doll.RemoveResource(modifier.respath, self.factory)

            if name:
                modifier = doll.AddResource(category + '/' + name, 1.0, self.factory, variation=variation)
            elif not removeFirst:
                modifier = self.GetModifierByCategory(charID, category)
                if modifier:
                    self.RemoveFromCharacterMetadata(charID, category)
                    doll.RemoveResource(modifier.GetResPath(), self.factory)
        if doUpdate:
            self.UpdateDoll(charID, fromWhere='ApplyItemToDoll')
        return modifier

    @telemetry.ZONE_METHOD
    def SetColorValueByCategory(self, charID, category, colorVar1, colorVar2, doUpdate = True):
        if colorVar1 is None:
            log.LogError('SetColorValue - No Color variation passed in!')
            return
        color1Value, color1Name, color2Name, variation = self.GetColorsToUse(colorVar1, colorVar2)
        modifier = self.GetModifierByCategory(charID, category)
        if not modifier:
            return
        if color1Value:
            self.characterMetadata[charID].typeColors[category] = (color1Name, None)
            modifier.SetColorizeData(color1Value)
        elif colorVar2 is not None:
            self.characterMetadata[charID].typeColors[category] = (color1Name, color2Name)
            modifier.SetColorVariationDirectly(variation)
        else:
            self.characterMetadata[charID].typeColors[category] = (color1Name, None)
            modifier.SetColorVariationDirectly(variation)
        if category == ccConst.hair:
            self.SynchronizeHairColors(charID)
        if doUpdate:
            self.UpdateDoll(charID, fromWhere='SetColorValueByCategory')

    def GetColorsToUse(self, colorVar1, colorVar2, *args):
        if colorVar1 is None:
            log.LogError('GetColorsToUse - No Color variation passed in!')
            return (None, None, None, None)
        if len(colorVar1) == 3:
            colorVar1 = (colorVar1[0], colorVar1[2])
        if colorVar2 is not None and len(colorVar2) == 3:
            colorVar2 = (colorVar2[0], colorVar2[2])
        color1Name, color1Value = colorVar1
        if type(color1Value) == types.TupleType:
            return (color1Value,
             color1Name,
             None,
             None)
        elif colorVar2 is not None:
            color2Name, color2Value = colorVar2
            variation = {}
            if color1Value:
                if color2Value and 'colors' in color1Value:
                    variation['colors'] = [color1Value['colors'][0], color2Value['colors'][1], color2Value['colors'][2]]
                if 'pattern' in color1Value:
                    variation['pattern'] = color1Value['pattern']
                if color2Value and 'patternColors' in color1Value:
                    variation['patternColors'] = [color1Value['patternColors'][0], color2Value['patternColors'][1], color2Value['patternColors'][2]]
                if 'patternColors' in color1Value:
                    variation['patternColors'] = color1Value['patternColors']
                if color2Value and 'specularColors' in color1Value:
                    variation['specularColors'] = [color1Value['specularColors'][0], color2Value['specularColors'][1], color2Value['specularColors'][2]]
            return (None,
             color1Name,
             color2Name,
             variation)
        else:
            return (None,
             color1Name,
             None,
             color1Value)

    @telemetry.ZONE_METHOD
    def SetColorSpecularityByCategory(self, charID, category, specularity, doUpdate = True):
        modifier = self.GetModifierByCategory(charID, category)
        if modifier:
            self.characterMetadata[charID].typeSpecularity[category] = specularity
            m1 = 1.0 + 0.4 * specularity
            s1 = 0.5 + 0.3 * specularity
            s2 = 0.5 - 0.2 * specularity
            modifier.SetColorVariationSpecularity([(s1,
              s1,
              s1,
              m1), (s2,
              s2,
              s2,
              1.0), (0.5, 0.5, 0.5, 1.0)])
            if doUpdate:
                self.UpdateDoll(charID, fromWhere='SetColorSpecularityByCategory')

    def GetColorSpecularityByCategory(self, charID, category):
        return self.characterMetadata[charID].typeSpecularity.get(category, 0.5)

    @telemetry.ZONE_METHOD
    def SetWeightByCategory(self, charID, category, weight, doUpdate = True):
        modifier = self.GetModifierByCategory(charID, category)
        if not modifier and charID in self.characters:
            doll = self.characters[charID].doll
            if doll.gender == GENDER.FEMALE:
                gender = 0
            else:
                gender = 1
            options = self.GetAvailableItemsByCategory(category, gender, self.characterMetadata[charID].bloodlineID)
            if options:
                name = options[0]
                modifier = doll.AddResource(category + '/' + name, 1.0, self.factory)
        if modifier:
            if ccUtil.HasUserDefinedWeight(category):
                self.characterMetadata[charID].typeWeights[category] = weight
            modifier.weight = weight
            if doUpdate:
                self.UpdateDoll(charID, 'SetWeightByCategory')

    def GetWeightByCategory(self, charID, category):
        weight = self.characterMetadata[charID].typeWeights.get(category, 0)
        sliderWeight = self.GetSliderWeight(charID, category, weight)
        return sliderWeight

    def GetTrueWeight(self, charID, category, sliderWeight):
        weight = sliderWeight
        if category in ccConst.weightLimits:
            limits = ccConst.weightLimits[category]
            color = self.characterMetadata[charID].typeColors.get(category, None)
            minMax = limits.get(color, None) or limits.get('default', None)
            if minMax:
                diff = minMax[1] - minMax[0]
                weight = minMax[0] + diff * weight
        return weight

    def GetSliderWeight(self, charID, category, trueWeight):
        weight = trueWeight
        if category in ccConst.weightLimits:
            limits = ccConst.weightLimits[category]
            color = self.characterMetadata[charID].typeColors.get(category, None)
            minMax = limits.get(color, None) or limits.get('default', None)
            diff = minMax[1] - minMax[0]
            weight = (weight - minMax[0]) / diff
        return weight

    @telemetry.ZONE_METHOD
    def SculptCallBack(self, zone, isFront):
        uicore.layer.charactercreation.controller.ChangeSculptCursor(zone, isFront)

    @telemetry.ZONE_METHOD
    def StartEditMode(self, charID, scene, camera, mode = 'sculpt', showPreview = False, callback = None, pickCallback = None, inactiveZones = [], resetAll = False, skipPickSceneReset = False, useThread = 1):
        if useThread:
            if not self.sculpting or resetAll:
                if not camera:
                    raise ValueError('Cannot start paperdoll sculpting edit mode without a camera.')
            uthread.new(self.StartEditMode_t, *(charID,
             scene,
             camera,
             mode,
             showPreview,
             callback,
             pickCallback,
             inactiveZones,
             resetAll,
             skipPickSceneReset))
        else:
            character = self.characters.get(charID, None)
            if character is None or character.doll.IsBusyUpdating():
                return
            self.StartEditMode_t(charID, scene, camera, mode, showPreview, callback, pickCallback, inactiveZones, resetAll, skipPickSceneReset)

    @telemetry.ZONE_METHOD
    def StartEditMode_t(self, charID, scene, camera, mode, showPreview, callback, pickCallback, inactiveZones, resetAll, skipPickSceneReset):
        character = self.characters.get(charID, None)
        count = 0
        while (character is None or character.doll.IsBusyUpdating()) and count < 100:
            count += 1
            blue.synchro.Yield()

        if character is None:
            return
        if not self.sculpting or resetAll:
            if self.sculpting and self.sculpting.highlightGhost:
                if self.sculpting.highlightGhost.renderStepSlot and self.sculpting.highlightGhost.renderStepSlot.object:
                    self.sculpting.highlightGhost.renderStepSlot.object.job = None
            self.sculpting = PaperDollSculpting(character.avatar, character.doll, scene, camera, self.factory, mode=mode, callback=callback, pickCallback=pickCallback, inactiveZones=inactiveZones)
        else:
            self.sculpting.Reset(character.doll, character.avatar, camera=camera, mode=mode, callback=callback, pickCallback=pickCallback, inactiveZones=inactiveZones, skipPickSceneReset=skipPickSceneReset)
        self.sculptingActive = True
        gender = character.doll.gender
        isMale = gender == 'male'
        if showPreview:
            self.sculpting.RunHighlightPreview(isMale)

    @telemetry.ZONE_METHOD
    def StopEditing(self, *args, **kwds):
        if self.sculpting is not None:
            self.sculpting.Stop()
        self.sculptingActive = False

    @telemetry.ZONE_METHOD
    def IsSculptingReady(self):
        if not self.sculpting:
            return False
        return self.sculpting.IsReady()

    @telemetry.ZONE_METHOD
    def StartPosing(self, charID, callback = None):
        avatar = self.characters[charID].avatar
        network = animparams.GetParamsPerAvatar(avatar, charID)
        uicore.layer.charactercreation.controller.StartEditMode(showPreview=False, mode='animation', callback=callback)

    @telemetry.ZONE_METHOD
    def StopPosing(self, charID):
        avatar = self.characters[charID].avatar
        network = animparams.GetParamsPerAvatar(avatar, charID)

    @telemetry.ZONE_METHOD
    def ChangePose(self, v, charID, *args):
        avatar = self.characters[charID].avatar
        network = animparams.GetParamsPerAvatar(avatar, charID)
        if network is not None:
            controlParameter = 'ControlParameters|PortraitPoseNumber'
            network.SetControlParameter(controlParameter, float(v))

    @telemetry.ZONE_METHOD
    def SetControlParametersFromList(self, params, charID):
        if charID not in self.characters:
            return
        avatar = self.characters[charID].avatar
        network = animparams.GetParamsPerAvatar(avatar, charID)
        for param in params:
            network.SetControlParameter(param[0], param[1])

    @telemetry.ZONE_METHOD
    def ResetFacePose(self, charID):
        if charID not in self.characters:
            return
        self.SetControlParametersFromList(ccConst.FACE_POSE_CONTROLPARAMS, charID)
        genderID = self.characterMetadata[charID].genderID
        avatar = self.characters[charID].avatar
        network = animparams.GetParamsPerAvatar(avatar, charID)
        if genderID == 1:
            network.SetControlParameter('ControlParameters|HeadLookTarget', (0.0, 1.6, 0.5))
        else:
            network.SetControlParameter('ControlParameters|HeadLookTarget', (0.0, 1.5, 0.5))

    @telemetry.ZONE_METHOD
    def SetTextureQuality(self, quality):
        self.textureQuality = quality
        resolution = ccConst.TEXTURE_RESOLUTIONS[quality]
        for each in self.characters:
            character = self.characters[each]
            character.doll.textureResolution = resolution
            self.UpdateDollsAvatar(character)

    @telemetry.ZONE_METHOD
    def EnableClothSimulation(self, value):
        pass

    def MatchDNA(self, character, dna):
        character.doll.MatchDNA(self.factory, dna)

    def UpdateDollsAvatar(self, character, *args):
        character.doll.Update(self.factory, character.avatar)

    def GetSculpting(self, *args):
        return self.sculpting

    def GetSculptingActive(self, *args):
        return self.sculptingActive

    @telemetry.ZONE_METHOD
    def RandomizeCharacterSculpting(self, charID, raceID = None, doUpdate = False):
        blue.synchro.Yield()
        if charID in self.characters:
            randomizer = EveDollRandomizer(self.factory)
            randomizer.gender = ccUtil.GenderIDToPaperDollGender(self.characterMetadata[charID].genderID)
            randomizer.bloodline = self.characterMetadata[charID].bloodlineID
            randomizer.race = raceID
            randomizer.SetSculptingLimits()
            blendshapeOptions = randomizer.GetBlendshapeOptions()
            randomizer.ApplyRandomizedResourcesToCharacter(charID, blendshapeOptions)
            if self.sculptingActive:
                self.sculpting.UpdateFieldsBasedOnExistingValues(self.characters[charID].doll)
            wt = self.GetCharacterWeight(charID)
            self.SetCharacterWeight(charID, wt, doUpdate=False)
            if doUpdate:
                self.UpdateDoll(charID, fromWhere='RandomizeCharacterSculpting')

    @telemetry.ZONE_METHOD
    def RandomizeCharacterGroups(self, charID, raceID, categoryList, doUpdate = False, fullRandomization = False):
        if charID in self.characters:
            doHairDarkness = False
            for category in categoryList:
                if category in (ccConst.hair, ccConst.beard, ccConst.eyebrows):
                    doHairDarkness = True
                addWeight = False
                weightFrom = 0.1
                if fullRandomization and category.startswith('makeup/'):
                    weightTo = 0.3
                else:
                    weightTo = 1.0
                doll = self.characters[charID].doll
                modifier = self.GetModifierByCategory(charID, category)
                if modifier:
                    self.RemoveFromCharacterMetadata(charID, category)
                    doll.RemoveResource(modifier.GetResPath(), self.factory)
                if category in ccConst.addWeightToCategories:
                    addWeight = True
                oddsDict = {}
                if doll.gender == 'female':
                    oddsDict = ccConst.femaleOddsOfSelectingNone.copy()
                    if fullRandomization:
                        oddsDict.update(ccConst.femaleOddsOfSelectingNoneFullRandomize)
                else:
                    oddsDict = ccConst.maleOddsOfSelectingNone.copy()
                    if fullRandomization:
                        oddsDict.update(ccConst.maleOddsOfSelectingNoneFullRandomize)
                oddsOfSelectingNone = oddsDict.get(category, None)
                self.RandomizeDollCategory(charID, raceID, category, oddsOfSelectingNone, addWeight, weightFrom, weightTo, fullRandomization)

            if doHairDarkness:
                hairDarkness = round(random.random(), 2)
                self.SetHairDarkness(charID, hairDarkness)
            if doUpdate:
                self.UpdateDoll(charID, fromWhere='RandomizeCharacterGroups')

    def RandomizeDollCategory(self, charID, raceID, category, oddsOfSelectingNone, addWeight = None, weightFrom = 0, weightTo = 1.0, fullRandomization = False):
        blue.synchro.Yield()
        randomizer = EveDollRandomizer(self.factory)
        randomizer.gender = self.characters[charID].doll.gender
        randomizer.bloodline = self.characterMetadata[charID].bloodlineID
        randomizer.race = raceID
        randomizer.fullRandomization = fullRandomization
        randomizer.AddCategoryForWhitelistRandomization(category, oddsOfSelectingNone)
        if addWeight:
            randomizer.AddPathForWeightRandomization(category, weightFrom, weightTo)
        options = randomizer.GetResources()
        randomizer.ApplyRandomizedResourcesToCharacter(charID, options)

    def SetInitialSkintype(self, charID, genderID, bloodlineID, raceID):
        allTypes = sm.GetService('character').GetAvailableTypesByCategory(ccConst.skintype, genderID, raceID)
        defaultColorName = ccConst.DEFAULSKINCOLORFORBLOODLINE.get(bloodlineID)
        skintype_for_bloodline = None
        for skintype in ccConst.SKINTYPE_TO_BLOODLINE:
            if ccConst.SKINTYPE_TO_BLOODLINE[skintype] == bloodlineID:
                skintype_for_bloodline = skintype

        if defaultColorName is None:
            return
        for eachType in allTypes:
            assetID, typeInfo, typeID = eachType
            if typeInfo[2] == defaultColorName and typeInfo[0] == skintype_for_bloodline:
                self.ApplyTypeToDoll(charID, eachType, doUpdate=False)
                return eachType

    @telemetry.ZONE_METHOD
    def GetPoseData(self):
        if self.sculpting is None:
            return
        self.sculpting.UpdateAnimation([])
        poseDataDict = self.sculpting.animationController.GetAllControlParameterValuesByName(True)
        for k in poseDataDict.keys():
            if k not in paperDollUtil.FACIAL_POSE_PARAMETERS.__dict__:
                del poseDataDict[k]

        return poseDataDict

    @telemetry.ZONE_METHOD
    def ValidateDollCustomizationComplete(self, charID):
        genderString = self.characters[charID].doll.gender
        for category, assetID in self.characterMetadata[charID].types.iteritems():
            if assetID is None:
                self.LogError('Invalid asset chosen for category ', category, '. Please make sure the asset has an associated ID.')

        dolData = self.GetCharacterAppearanceInfo(charID)
        return paperDollUtil.HasRequiredClothing(genderString, dolData.modifiers)

    def IsSingleCharacterLoaded(self, charID):
        return self.characters.get(charID) is not None

    def GetSingleCharactersDoll(self, charID):
        return self.characters[charID].doll

    def GetSingleCharactersAvatar(self, charID):
        avatar = None
        try:
            avatar = self.characters[charID].avatar
        except KeyError:
            pass

        return avatar

    def GetSingleCharacter(self, charID, *args):
        return self.characters[charID]

    def GetSingleCharactersMetadata(self, charID, *args):
        return self.characterMetadata[charID]

    def GetTypeColors(self, charID, cat):
        return self.characterMetadata[charID].typeColors.get(cat, (None, None))

    def GetAssetAndTypeIDsFromPath(self, gender, assetPath):
        if self.assetsToIDs[gender] is None:
            self.assetsToIDs[gender] = {}
            for row in cfg.paperdollResources:
                if row.resGender == (gender == GENDER.MALE):
                    self.assetsToIDs[gender][self.GetRelativePath(row.resPath).lower()] = (row.paperdollResourceID, row.typeID)

        assetPath = self.GetRelativePath(assetPath).lower()
        if assetPath in self.assetsToIDs[gender]:
            return self.assetsToIDs[gender][assetPath]
        else:
            hasContentRole = session.role & ROLE_CONTENT
            if hasContentRole:
                self.LogWarn('Asset ID', assetPath, 'does not have an associated ID!!')
            return (None, None)

    def GetCharacterAppearanceInfo(self, charID):
        dollDNA = self.characters[charID].doll.GetDNA()
        return ConvertDNAForDB(dollDNA, self.characterMetadata[charID])

    def CopyCharacterAppearanceInfoForBloodline(self, charID):
        appearanceInfo = self.GetCharacterAppearanceInfo(charID)
        appearanceInfo.sculpts = []
        for i in range(0, len(appearanceInfo.modifiers)):
            modifier = appearanceInfo.modifiers[i]
            if modifier.paperdollResourceVariation is None:
                newVariation = modifier.paperdollResourceVariation if modifier.paperdollResourceVariation is not None else 0
                appearanceInfo.modifiers[i] = ModifierRow(modifier.modifierLocationID, modifier.paperdollResourceID, newVariation)

        return appearanceInfo

    @telemetry.ZONE_METHOD
    def GetDNAFromDBRowsForEntity(self, entityID, dollDNA, gender, bloodline):
        self.ApplyDBRowToDoll(entityID, gender, bloodline, None, dollDNA)
        doll = self.GetSingleCharactersDoll(entityID)
        dna = doll.GetDNA()
        self.RemoveFromCharacterDicts(entityID, fromCharacterDict=True, fromMetadataDict=True)
        return dna

    def ConvertWeightKeyValue(self, weight, prefix, posName, negName):
        if prefix in ('thin', 'fat', 'muscular'):
            fmt = '%(prefix)sshape'
        else:
            fmt = '%(prefix)s_%(dir)sshape'
        if weight < 0.0:
            key = fmt % {'prefix': prefix,
             'dir': negName}
            return (key, abs(weight))
        if weight > 0.0:
            key = fmt % {'prefix': prefix,
             'dir': posName}
            return (key, abs(weight))
        return (None, None)

    def CachePortraitInfo(self, charID, info):
        self.cachedPortraitInfo[charID] = info

    def GetCachedPortraitInfo(self, charID):
        return self.cachedPortraitInfo.get(charID, None)

    def EnsureUnderwear(self, charID, genderID, raceID):
        doll = self.GetSingleCharactersDoll(charID)
        bottomUnderwearCount = len(doll.buildDataManager.GetModifiersByCategory(BODY_CATEGORIES.BOTTOMUNDERWEAR))
        if bottomUnderwearCount == 0:
            bottomUnderwearTypes = self.GetAvailableTypesByCategory(ccConst.bottomunderwear, genderID, raceID)
            if len(bottomUnderwearTypes) > 0:
                self.ApplyTypeToDoll(charID, bottomUnderwearTypes[0], doUpdate=False)
        if doll.gender == GENDER.FEMALE or self.IsChinaServer():
            topUnderwearCount = len(doll.buildDataManager.GetModifiersByCategory(BODY_CATEGORIES.TOPUNDERWEAR))
            if topUnderwearCount == 0:
                topUnderwearTypes = self.GetAvailableTypesByCategory(ccConst.topunderwear, genderID, raceID)
                if len(topUnderwearTypes) > 0:
                    self.ApplyTypeToDoll(charID, topUnderwearTypes[0], doUpdate=False)

    def GetRelativePath(self, resPath):
        if resPath.lower().startswith('res:'):
            for chopPart in ['Modular/Female/',
             'Modular/Male/',
             'Female/Paperdoll/',
             'Male/Paperdoll/',
             'modular/female/',
             'modular/male/',
             'female/paperdoll/',
             'male/paperdoll/']:
                startPos = resPath.find(chopPart)
                if startPos != -1:
                    chopTo = len(chopPart) + startPos
                    resPath = resPath[chopTo:]

        return resPath

    @telemetry.ZONE_METHOD
    def ApplyDBRowToDoll(self, charID, gender, bloodlineID, raceID, dbRow):
        if charID not in self.characters:
            randomDoll = paperDollUtil.CreateRandomDollNoClothes(gender, bloodlineID, raceID, noRandomize=True)
            self.characters[charID] = utillib.KeyVal(doll=randomDoll, avatar=None)
            self.characterMetadata[charID] = self.GetNewCharacterMetadata(ccUtil.PaperDollGenderToGenderID(gender), bloodlineID)
        sculptLocations = cfg.paperdollSculptingLocations
        modifierLocations = cfg.paperdollModifierLocations
        colors = cfg.paperdollColors
        colorNames = cfg.paperdollColorNames
        resources = cfg.paperdollResources
        if dbRow is None:
            self.LogError('Not applying anything to paperdoll, since dbRow is None')
            return
        for sculptRow in dbRow.sculpts:
            sculptInto = sculptLocations.GetIfExists(sculptRow.sculptLocationID)
            if sculptInto is None:
                self.LogError('Sculpting information for ', sculptRow.sculptLocationID, 'is missing from BSD, skipping sculpting location.')
                continue
            for colName, posName, negName in WEIGHT_BREAK_DOWNS:
                k, v = self.ConvertWeightKeyValue(getattr(sculptRow, colName, 0.0), sculptInto.weightKeyPrefix, posName, negName)
                if k is not None and v is not None:
                    catName = sculptInto.weightKeyCategory.lower()
                    path = SEPERATOR_CHAR.join([catName, k])
                    self.ApplyItemToDoll(charID, catName, k, doUpdate=False)
                    self.SetWeightByCategory(charID, path, v, doUpdate=False)

        modifierWeights = {}
        for colorRow in dbRow.colors:
            colorInfo = colors.GetIfExists(colorRow.colorID)
            if colorInfo is None:
                self.LogError('Color info missing for  ', colorRow.colorID)
                continue
            if colorInfo.hasWeight:
                modifierWeights[colorInfo.colorKey] = colorRow.weight

        modifierObjects = {}
        for modifierRow in dbRow.modifiers:
            modifierInfo = modifierLocations.GetIfExists(modifierRow.modifierLocationID)
            resourcesInfo = resources.GetIfExists(modifierRow.paperdollResourceID)
            if modifierInfo is None or resourcesInfo is None:
                self.LogError('Modifier or resource information missing for ', modifierRow.modifierLocationID, modifierRow.paperdollResourceID)
                continue
            weight = modifierWeights.get(modifierInfo.modifierKey, 1.0)
            if modifierRow.paperdollResourceVariation != 0 and modifierInfo.variationKey != '':
                self.ApplyItemToDoll(charID, modifierInfo.variationKey, self.tuckingOptions[modifierInfo.variationKey], removeFirst=True, variation='v%d' % modifierRow.paperdollResourceVariation if modifierRow.paperdollResourceVariation else None, doUpdate=False)
            resPath = self.GetRelativePath(resourcesInfo.resPath)
            modifierObjects[modifierInfo.modifierKey] = self.ApplyTypeToDoll(charID, resPath, weight=weight, doUpdate=False)

        genderID = ccUtil.PaperDollGenderToGenderID(gender)
        self.EnsureUnderwear(charID, genderID, raceID)
        for colorRow in dbRow.colors:
            colorInfo = colors.GetIfExists(colorRow.colorID)
            if colorInfo is None:
                self.LogError('No color info for ', colorRow.colorID)
                continue
            colorNameInfo = colorNames.GetIfExists(colorRow.colorNameA)
            if colorNameInfo is None:
                self.LogError('colorA index not in BSD data ', colorRow.colorNameA)
                continue
            colorNameA = colorNameInfo.colorName
            colorNameBC = None
            if colorRow.colorNameBC != 0:
                colorNameInfo = colorNames.GetIfExists(colorRow.colorNameBC)
                if colorNameInfo is not None:
                    colorNameBC = colorNameInfo.colorName
                else:
                    self.LogError('colorBC index not in BSD data ', colorRow.colorNameBC)
            if colorInfo.colorKey == ccConst.skintone:
                mod = self.ApplyItemToDoll(charID, ccConst.skintone, 'basic', doUpdate=False)
                skinColor = (colorNameA, mod.colorVariations[colorNameA])
                self.SetColorValueByCategory(charID, ccConst.skintone, skinColor, None, doUpdate=False)
            else:
                if colorInfo.colorKey not in modifierObjects:
                    self.LogError('%s not in modifierObjects' % colorInfo.colorKey)
                    continue
                mod = modifierObjects[colorInfo.colorKey]
                if colorNameA not in mod.colorVariations:
                    colorVarA = ('default', mod.colorVariations.get('default', None))
                else:
                    colorVarA = (colorNameA, mod.colorVariations[colorNameA])
                colorVarBC = None
                if colorInfo.hasSecondary and colorNameBC is not None:
                    colorVarBC = (colorNameBC, mod.colorVariations.get(colorNameBC, None))
                self.SetColorValueByCategory(charID, colorInfo.colorKey, colorVarA, colorVarBC, doUpdate=False)
                if colorInfo.hasGloss:
                    self.SetColorSpecularityByCategory(charID, colorInfo.colorKey, colorRow.gloss, doUpdate=False)
            if colorInfo.colorKey == ccConst.hair:
                self.SetHairDarkness(charID, dbRow.appearance.hairDarkness)
                self.SynchronizeHairColors(charID)

    def RemoveFromCharacterDicts(self, charID, fromCharacterDict = True, fromMetadataDict = True):
        if fromCharacterDict:
            self.characters.pop(charID, None)
        if fromMetadataDict:
            self.characterMetadata.pop(charID, None)

    def IsChinaServer(self):
        return boot.region == 'optic'
