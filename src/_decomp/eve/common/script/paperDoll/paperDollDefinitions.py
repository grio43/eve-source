#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\paperDoll\paperDollDefinitions.py
import os
import blue
import paperdoll
import yaml
import cdsuc
import log
import collections
import legacy_r_drive
import walk
import utillib as util
from carbon.common.script.util.logUtil import LogMixin
MODULAR_TEST_CASES_FOLDER = 'ModularTestCases'
DUMP_MODULAR_TEST_CASES_TO_OPTIONS = False
MODIFIERNAMEFILE = 'modifiernames.yaml'
GENDER = cdsuc.EnumList('Male', 'Female')
USE_PNG = True
if hasattr(const, 'USE_PNG'):
    USE_PNG = const.USE_PNG
elif hasattr(const, 'paperdoll') and hasattr(const.paperdoll, 'USE_PNG'):
    USE_PNG = const.paperdoll.USE_PNG
GENDER_ROOT = True
BASE_GRAPHICS_FOLDER = 'Graphics'
if hasattr(const, 'BASE_GRAPHICS_FOLDER'):
    BASE_GRAPHICS_FOLDER = const.BASE_GRAPHICS_FOLDER
elif hasattr(const, 'paperdoll') and hasattr(const.paperdoll, 'BASE_GRAPHICS_FOLDER'):
    BASE_GRAPHICS_FOLDER = const.paperdoll.BASE_GRAPHICS_FOLDER
BASE_GRAPHICS_TEST_FOLDER = 'graphics_test'
PAPERDOLL_CACHE_FILE = 'res:/{0}/Character/paperDollCache.pickle'.format(BASE_GRAPHICS_FOLDER)
FEMALE_PATH_SUFFIX = 'Female/Paperdoll' if GENDER_ROOT else 'Modular/Female'
MALE_PATH_SUFFIX = 'Male/Paperdoll' if GENDER_ROOT else 'Modular/Male'
FEMALE_LOD_PATH_SUFFIX = 'Female/Paperdoll_LOD' if GENDER_ROOT else 'ModularLOD/Female'
MALE_LOD_PATH_SUFFIX = 'Male/Paperdoll_LOD' if GENDER_ROOT else 'ModularLOD/Male'
FEMALE_BASE_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_FOLDER, FEMALE_PATH_SUFFIX)
FEMALE_BASE_LOD_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_FOLDER, FEMALE_LOD_PATH_SUFFIX)
FEMALE_BASE_GRAPHICS_TEST_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_TEST_FOLDER, FEMALE_PATH_SUFFIX)
FEMALE_BASE_GRAPHICS_TEST_LOD_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_TEST_FOLDER, FEMALE_LOD_PATH_SUFFIX)
FEMALE_OPTION_FILE_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_FOLDER, FEMALE_PATH_SUFFIX) + '/FemaleOptions.yaml' if GENDER_ROOT else 'res:/{0}/Character/Modular'.format(BASE_GRAPHICS_FOLDER) + '/FemaleOptions.yaml'
MALE_BASE_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_FOLDER, MALE_PATH_SUFFIX)
MALE_BASE_LOD_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_FOLDER, MALE_LOD_PATH_SUFFIX)
MALE_BASE_GRAPHICS_TEST_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_TEST_FOLDER, MALE_PATH_SUFFIX)
MALE_BASE_GRAPHICS_TEST_LOD_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_TEST_FOLDER, MALE_LOD_PATH_SUFFIX)
MALE_OPTION_FILE_PATH = 'res:/{0}/Character/{1}'.format(BASE_GRAPHICS_FOLDER, MALE_PATH_SUFFIX) + '/MaleOptions.yaml' if GENDER_ROOT else 'res:/{0}/Character/Modular'.format(BASE_GRAPHICS_FOLDER) + '/MaleOptions.yaml'
DNA_STRINGS = cdsuc.EnumList('path', 'weight', 'decalWeight', 'colors', 'specularColors', 'pattern', 'tuck', 'decalData', 'category', 'part', 'colorVariation', 'variation')
INTERIOR_AVATAR_EFFECT_FILE_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/skinnedavatarbrdf.fx'
SKINNED_AVATAR_SINGLEPASS_DOUBLE_PATH = 'res:/graphics/effect/managed/interior/avatar/skinnedavatarbrdfsinglepassskin_double.fx'
SKINNED_AVATAR_SINGLEPASS_SINGLE_PATH = 'res:/graphics/effect/managed/interior/avatar/skinnedavatarbrdfsinglepassskin_single.fx'
SKINNED_AVATAR_EYE_SHADER = 'res:/graphics/effect/managed/interior/avatar/eyeshader.fx'
SKINNED_AVATAR_EYEWETNESS_SHADER = 'res:/graphics/effect/managed/interior/avatar/eyewetnessshader.fx'
SKINNED_AVATAR_TONGUE_SHADER = 'res:/graphics/effect/managed/interior/avatar/portraitbasic.fx'
SKINNED_AVATAR_TEETH_SHADER = 'res:/graphics/effect/managed/interior/avatar/portraitbasic.fx'
SKINNED_AVATAR_HAIR_DETAILED = 'res:/graphics/effect/managed/interior/avatar/skinnedavatarhair_detailed.fx'
SKINNED_AVATAR_CLOTH_HAIR_DETAILED = 'res:/graphics/effect/managed/interior/avatar/clothavatarhair_detailed.fx'
SKINNED_AVATAR_BRDF_LINEAR = 'res:/graphics/effect/managed/interior/avatar/skinnedavatarbrdflinear.fx'
SKINNED_AVATAR_BRDF_DOUBLE_LINEAR = 'res:/graphics/effect/managed/interior/avatar/skinnedavatarbrdfdoublelinear.fx'
SKINNED_AVATAR_GLASS_SHADER = 'res:/graphics/effect/managed/interior/avatar/glassshader.fx'
CLOTH_AVATAR_LINEAR = 'res:/graphics/effect/managed/interior/avatar/clothavatarlinear.fx'
FRESNEL_LOOKUP_MAP = 'res:/texture/global/brdflibrary.dds'
SHADERS_THAT_CAN_SWITCH_TO_FAST_SHADER_MODE = [SKINNED_AVATAR_SINGLEPASS_DOUBLE_PATH,
 SKINNED_AVATAR_SINGLEPASS_SINGLE_PATH,
 SKINNED_AVATAR_BRDF_LINEAR,
 SKINNED_AVATAR_BRDF_DOUBLE_LINEAR,
 SKINNED_AVATAR_HAIR_DETAILED,
 SKINNED_AVATAR_EYE_SHADER,
 SKINNED_AVATAR_GLASS_SHADER]
SHADERS_TO_ENABLE_DXT5N = [SKINNED_AVATAR_SINGLEPASS_DOUBLE_PATH,
 SKINNED_AVATAR_SINGLEPASS_SINGLE_PATH,
 SKINNED_AVATAR_EYEWETNESS_SHADER,
 SKINNED_AVATAR_TONGUE_SHADER,
 SKINNED_AVATAR_TEETH_SHADER,
 SKINNED_AVATAR_EYE_SHADER,
 SKINNED_AVATAR_HAIR_DETAILED,
 SKINNED_AVATAR_CLOTH_HAIR_DETAILED,
 SKINNED_AVATAR_BRDF_LINEAR,
 SKINNED_AVATAR_BRDF_DOUBLE_LINEAR,
 CLOTH_AVATAR_LINEAR]
EFFECT_PRELOAD_PATHS = ['clothavatarhair_detailed.fx',
 'clothavatarhair_detailed_dxt5n.fx',
 'SkinnedAvatar.fx',
 'SkinnedAvatarBRDF.fx',
 'SkinnedAvatarBRDFBeckmannLookup.fx',
 'SkinnedAvatarBRDFDouble.fx',
 'SkinnedAvatarBRDFDoubleLinear.fx',
 'SkinnedAvatarBRDFDoubleLinear_dxt5n.fx',
 'SkinnedAvatarBRDFDoubleLinear_fast.fx',
 'SkinnedAvatarBRDFDouble_Prepass.fx',
 'SkinnedAvatarBRDFLightmapApplication_Double.fx',
 'SkinnedAvatarBRDFLightmapApplication_Single.fx',
 'SkinnedAvatarBRDFLightmapUnwrap_Double.fx',
 'SkinnedAvatarBRDFLightmapUnwrap_Single.fx',
 'SkinnedAvatarBRDFLinear.fx',
 'SkinnedAvatarBRDFLinear_dxt5n.fx',
 'SkinnedAvatarBRDFLinear_fast.fx',
 'SkinnedAvatarBRDFSinglePassSkin_Double.fx',
 'SkinnedAvatarBRDFSinglePassSkin_Double_dxt5n.fx',
 'SkinnedAvatarBRDFSinglePassSkin_Double_fast.fx',
 'SkinnedAvatarBRDFSinglePassSkin_Single.fx',
 'SkinnedAvatarBRDFSinglePassSkin_Single_dxt5n.fx',
 'SkinnedAvatarBRDFSinglePassSkin_Single_Fast.fx',
 'SkinnedAvatarBRDF_Prepass.fx',
 'SkinnedAvatarFurShells.fx',
 'SkinnedAvatarFurShells_fast.fx',
 'SkinnedAvatarHair.fx',
 'SkinnedAvatarHair_detailed.fx',
 'SkinnedAvatarHair_detailed_dxt5n.fx',
 'SkinnedAvatarHair_detailed_fast.fx',
 'SkinnedAvatarSkin.fx',
 'SkinnedAvatar_Prepass.fx',
 'EyeShader.fx',
 'EyeShader_dxt5n.fx',
 'EyeShader_fast.fx',
 'EyeWetnessShader.fx',
 'EyeWetnessShader_dxt5n.fx',
 'PortraitBasic.fx',
 'PortraitBasic_dxt5n.fx']
TEXTURE_PRELOAD_PATHS = ['res:/Texture/Global/flatnormal.dds', 'res:/Texture/Global/50gray.dds', 'res:/Texture/Global/brdfLibrary.dds']
FEMALE_WRINKLE_FACEZONE_PREFIX = 'res://Graphics/Character/Global/FaceSetup/FaceZones.'
EYE_SHADER_REFLECTION_CUBE_PATH = 'res:/Texture/Global/EyeReflection_cube.dds'
GLASS_SHADER_REFLECTION_CUBE_PATH = 'res:/Texture/Global/GlassReflection_cube.dds'
LOD_3 = 3
LOD_2 = 2
LOD_1 = 1
LOD_0 = 0
LOD_A = -1
LOD_SKIN = -2
LOD_SCATTER_SKIN = -3
LOD_99 = 99
DIFFUSE_MAP = 0
SPECULAR_MAP = 1
NORMAL_MAP = 2
MASK_MAP = 3
MAPS = (DIFFUSE_MAP,
 SPECULAR_MAP,
 NORMAL_MAP,
 MASK_MAP)
MAPNAMES = ('DiffuseMap', 'SpecularMap', 'NormalMap', 'CutMaskMap')
RESIZABLE_MAPS = (DIFFUSE_MAP, SPECULAR_MAP, NORMAL_MAP)
FIXED_SIZE_MAPS = MASK_MAP
MAPMARKERS = ('_d', '_s', '_n', '_m')
MID_GRAY = (0.5, 0.5, 0.5, 1.0)
LIGHT_GRAY = (0.6, 0.6, 0.6, 1.0)
DARK_GRAY = (0.2, 0.2, 0.2, 1.0)
SEPERATOR_CHAR = '/'
PROJECTED_TATTOO = 'projected tattoo'
AVATAR_TYPES = cdsuc.EnumList('WodExtSkinnedObject', 'Tr2IntSkinnedObject')
DOLL_PARTS = cdsuc.EnumList('hair', 'head', 'body', 'accessories')
DOLL_EXTRA_PARTS = cdsuc.EnumList('bodyshapes', 'utilityshapes', 'dependants', 'undefined')
BODY_CATEGORIES = cdsuc.EnumList('bottominner', 'bottommiddle', 'bottomouter', 'bottomoutertucked', 'bottomtight', 'bottomunderwear', 'bottomunderweartucked', 'feet', 'feettucked', 'hands', 'handsinner', 'outer', 'scars', 'skin', 'skintone', 'skintype', 'socks', 'sockstucked', 'tattoo', 'topinner', 'topmiddle', 'toptight', 'topouter', 'topunderwear', 'topunderweartucked')
HEAD_CATEGORIES = cdsuc.EnumList('head', 'archetypes', 'makeup', 'facemodifiers')
HAIR_CATEGORIES = cdsuc.EnumList('hair', 'beard')
ACCESSORIES_CATEGORIES = cdsuc.EnumList('accessories', 'sleeveslower', 'sleevesupper')
BLENDSHAPE_CATEGORIES = cdsuc.EnumList(DOLL_EXTRA_PARTS.BODYSHAPES, DOLL_EXTRA_PARTS.UTILITYSHAPES, HEAD_CATEGORIES.ARCHETYPES, HEAD_CATEGORIES.FACEMODIFIERS)
MASKING_CATEGORIES = cdsuc.EnumList(BODY_CATEGORIES.FEET, BODY_CATEGORIES.OUTER, BODY_CATEGORIES.TOPINNER, BODY_CATEGORIES.TOPMIDDLE, BODY_CATEGORIES.TOPTIGHT, BODY_CATEGORIES.TOPOUTER, BODY_CATEGORIES.HANDS, BODY_CATEGORIES.BOTTOMINNER, BODY_CATEGORIES.BOTTOMOUTER, DOLL_EXTRA_PARTS.DEPENDANTS)
CATEGORIES_CONTAINING_GROUPS = cdsuc.EnumList(DOLL_PARTS.ACCESSORIES, BODY_CATEGORIES.TATTOO, HEAD_CATEGORIES.MAKEUP, DOLL_EXTRA_PARTS.DEPENDANTS)
DESIRED_ORDER = [BODY_CATEGORIES.SKIN,
 DOLL_PARTS.HEAD,
 DOLL_EXTRA_PARTS.DEPENDANTS,
 HEAD_CATEGORIES.ARCHETYPES,
 BLENDSHAPE_CATEGORIES.BODYSHAPES,
 BODY_CATEGORIES.SKINTYPE,
 BODY_CATEGORIES.SKINTONE,
 BODY_CATEGORIES.TATTOO,
 HEAD_CATEGORIES.MAKEUP,
 BODY_CATEGORIES.SCARS,
 HAIR_CATEGORIES.BEARD,
 BODY_CATEGORIES.BOTTOMINNER,
 BODY_CATEGORIES.TOPINNER,
 BODY_CATEGORIES.BOTTOMUNDERWEARTUCKED,
 BODY_CATEGORIES.BOTTOMUNDERWEAR,
 BODY_CATEGORIES.BOTTOMTIGHT,
 BODY_CATEGORIES.TOPUNDERWEARTUCKED,
 BODY_CATEGORIES.SOCKSTUCKED,
 BODY_CATEGORIES.BOTTOMMIDDLE,
 BODY_CATEGORIES.TOPUNDERWEAR,
 BODY_CATEGORIES.SOCKS,
 BODY_CATEGORIES.HANDSINNER,
 BODY_CATEGORIES.FEETTUCKED,
 BODY_CATEGORIES.BOTTOMOUTERTUCKED,
 BODY_CATEGORIES.TOPTIGHT,
 BODY_CATEGORIES.TOPMIDDLE,
 BODY_CATEGORIES.BOTTOMOUTER,
 BODY_CATEGORIES.FEET,
 ACCESSORIES_CATEGORIES.ACCESSORIES,
 BODY_CATEGORIES.HANDS,
 BODY_CATEGORIES.TOPOUTER,
 HAIR_CATEGORIES.HAIR,
 BODY_CATEGORIES.OUTER]
MAKEUP_GROUPS = cdsuc.EnumList('implants', 'eyes', 'eyeshadow', 'eyebrowbase', 'eyebrows', 'scarring', 'freckles', 'blush', 'eyelashes', 'augmentations')
GROUPS = {HEAD_CATEGORIES.MAKEUP: list(MAKEUP_GROUPS)}
MAKEUP_EYEBROWS = SEPERATOR_CHAR.join([HEAD_CATEGORIES.MAKEUP, 'eyebrows'])
MAKEUP_EYELASHES = SEPERATOR_CHAR.join([HEAD_CATEGORIES.MAKEUP, 'eyelashes'])
MAKEUP_EYES = SEPERATOR_CHAR.join([HEAD_CATEGORIES.MAKEUP, 'eyes'])
BODY_BLENDSHAPE_ZONES = paperdoll.BODY_BLENDSHAPE_ZONES
HEAD_BLENDSHAPE_ZONES = paperdoll.HEAD_BLENDSHAPE_ZONES
ALL_BLENDSHAPE_ZONES = paperdoll.ALL_BLENDSHAPE_ZONES
BLENDSHAPE_AXIS = cdsuc.EnumList('left', 'right', 'down', 'up', 'front', 'back')
BLENDSHAPE_AXIS_PAIRS = ((BLENDSHAPE_AXIS.LEFT, BLENDSHAPE_AXIS.RIGHT), (BLENDSHAPE_AXIS.DOWN, BLENDSHAPE_AXIS.UP), (BLENDSHAPE_AXIS.FRONT, BLENDSHAPE_AXIS.BACK))
DOLL_PART_TO_CATEGORIES = {DOLL_PARTS.BODY: BODY_CATEGORIES,
 DOLL_PARTS.HEAD: HEAD_CATEGORIES,
 DOLL_PARTS.HAIR: HAIR_CATEGORIES,
 DOLL_PARTS.ACCESSORIES: ACCESSORIES_CATEGORIES}
CATEGORIES_THATCLEAN_MATERIALMAP = cdsuc.EnumList(BODY_CATEGORIES.OUTER, BODY_CATEGORIES.TOPOUTER, BODY_CATEGORIES.FEET, BODY_CATEGORIES.BOTTOMOUTER, BODY_CATEGORIES.HANDS, DOLL_PARTS.ACCESSORIES)
DEFAULT_NUDE_HEAD = DOLL_PARTS.HEAD + SEPERATOR_CHAR + 'head_generic'
DEFAULT_NUDE_EYELASHES = HEAD_CATEGORIES.MAKEUP + SEPERATOR_CHAR + 'eyelashes' + SEPERATOR_CHAR + 'eyelashes_01'
DEFAULT_NUDE_LEGS = BODY_CATEGORIES.BOTTOMINNER + SEPERATOR_CHAR + 'legs_nude'
DEFAULT_NUDE_FEET = BODY_CATEGORIES.FEET + SEPERATOR_CHAR + 'feet_nude'
DEFAULT_NUDE_HANDS = BODY_CATEGORIES.HANDS + SEPERATOR_CHAR + 'hands_nude'
DEFAULT_NUDE_TORSO = BODY_CATEGORIES.TOPINNER + SEPERATOR_CHAR + 'torso_nude'
DEFAULT_NUDE_SLEEVESUPPER = DOLL_EXTRA_PARTS.DEPENDANTS + SEPERATOR_CHAR + 'sleevesupper' + SEPERATOR_CHAR + 'standard'
DEFAULT_NUDE_SLEEVESLOWER = DOLL_EXTRA_PARTS.DEPENDANTS + SEPERATOR_CHAR + 'sleeveslower' + SEPERATOR_CHAR + 'standard'
DEFAULT_NUDE_PARTS = [DEFAULT_NUDE_HEAD,
 DEFAULT_NUDE_LEGS,
 DEFAULT_NUDE_FEET,
 DEFAULT_NUDE_HANDS,
 DEFAULT_NUDE_SLEEVESLOWER,
 DEFAULT_NUDE_SLEEVESUPPER,
 DEFAULT_NUDE_TORSO]
OUTSOURCING_JESSICA_PATH = 'R:/Settings/OutsourcingJessica.txt'
BODY_UVS = (0.0, 0.0, 0.5, 1.0)
HEAD_UVS = (0.5, 0.0, 1.0, 0.5)
HAIR_UVS = (0.5, 0.5, 0.75, 1.0)
ACCE_UVS = (0.75, 0.5, 1.0, 1.0)
DEFAULT_UVS = (0.0, 0.0, 1.0, 1.0)
RED_FILE = 0
STUBBLE_PATH = 1
SHADER_PATH = 2
CLOTH_OVERRIDE = 3
CLOTH_PATH = 4
TEXTURE_STUB = 'res:/texture/global/stub.dds'
SKIN_GENERIC_PATH = '/skin/generic/'
MAP_FORMAT_DDS = 'dds'
MAP_FORMAT_TGA = 'tga'
MAP_FORMAT_PNG = 'png'
MAP_FORMATS = cdsuc.EnumList(MAP_FORMAT_DDS, MAP_FORMAT_TGA, MAP_FORMAT_PNG)
MAP_PREFIX_COLORIZE = 'colorize_'
MAP_SUFFIX_4K = '_4k'
MAP_SUFFIX_512 = '_512'
MAP_SUFFIX_256 = '_256'
MAP_SIZE_SUFFIXES = cdsuc.EnumList(MAP_SUFFIX_4K, MAP_SUFFIX_512, MAP_SUFFIX_256)
MAP_SUFFIX_D = '_d'
MAP_SUFFIX_L = '_l'
MAP_SUFFIX_M = '_m'
MAP_SUFFIX_N = '_n'
MAP_SUFFIX_O = '_o'
MAP_SUFFIX_S = '_s'
MAP_SUFFIX_Z = '_z'
MAP_SUFFIX_AO = '_ao'
MAP_SUFFIX_DA = '_da'
MAP_SUFFIX_LA = '_la'
MAP_SUFFIX_MN = '_mn'
MAP_SUFFIX_MM = '_mm'
MAP_SUFFIX_TN = '_tn'
MAP_SUFFIX_DRGB = '_drgb'
MAP_SUFFIX_LRGB = '_lrgb'
MAP_SUFFIX_MASK = '_mask'
MAP_TYPE_SUFFIXES = cdsuc.EnumList(MAP_SUFFIX_D, MAP_SUFFIX_L, MAP_SUFFIX_M, MAP_SUFFIX_N, MAP_SUFFIX_O, MAP_SUFFIX_S, MAP_SUFFIX_Z, MAP_SUFFIX_AO, MAP_SUFFIX_MN, MAP_SUFFIX_MM, MAP_SUFFIX_TN, MAP_SUFFIX_MASK)
GEO_FORMAT_RED = 'red'
GEO_FORMAT_GR2 = 'gr2'
GEO_FORMATS = cdsuc.EnumList(GEO_FORMAT_RED, GEO_FORMAT_GR2)
GEO_SUFFIX_LODA = '_loda'
GEO_SUFFIX_LOD0 = '_lod0'
GEO_SUFFIX_LOD1 = '_lod1'
GEO_SUFFIX_LOD2 = '_lod2'
GEO_SUFFIX_LOD3 = '_lod3'
GEO_LOD_SUFFIXES = cdsuc.EnumList(GEO_SUFFIX_LODA, GEO_SUFFIX_LOD0, GEO_SUFFIX_LOD1, GEO_SUFFIX_LOD2, GEO_SUFFIX_LOD3)
FEMALE_DECAL_BINDPOSE = 'res:/Graphics/Character/Global/Poses/FemaleTattooPose.gr2'
MALE_DECAL_BINDPOSE = 'res:/Graphics/Character/Global/Poses/MaleTattooPose.gr2'
AXIS_DIRECTIONS = {'up': util.KeyVal(id='up', field='weightUpDown', positive=True),
 'down': util.KeyVal(id='down', field='weightUpDown', positive=False),
 'left': util.KeyVal(id='left', field='weightLeftRight', positive=True),
 'right': util.KeyVal(id='right', field='weightLeftRight', positive=False),
 'forward': util.KeyVal(id='forward', field='weightForwardBack', positive=True),
 'back': util.KeyVal(id='back', field='weightForwardBack', positive=False)}
SPECIAL_HANDLE_SHAPES = paperdoll.SPECIAL_HANDLE_SHAPES
SculptingRow = collections.namedtuple('SculptingRow', 'sculptLocationID weightUpDown weightLeftRight weightForwardBack')
ModifierRow = collections.namedtuple('ModifierRow', 'modifierLocationID paperdollResourceID paperdollResourceVariation')
ColorSelectionRow = collections.namedtuple('ColorSelectionRow', 'colorID colorNameA colorNameBC weight gloss')
AppearanceRow = collections.namedtuple('AppearanceRow', 'hairDarkness')
__dnaConverter__ = None

def GetDNAConverter():
    global __dnaConverter__
    if __dnaConverter__ is None:
        __dnaConverter__ = DNAConverter()
    return __dnaConverter__


def GetPatternList():
    patternDir = blue.paths.ResolvePath('res:\\Graphics\\Character\\Patterns')
    suffix = 'dds'
    if legacy_r_drive.loadFromContent:
        if not os.path.exists(OUTSOURCING_JESSICA_PATH):
            suffix = 'tga'
    patternList = []
    if os.path.exists(patternDir):
        list = os.listdir(patternDir)
        for file in list:
            if file.lower().endswith('_z.' + suffix):
                patternList.append(file[:-6])

    return patternList


def CreateEntries(path):
    entries = {}
    for root, dirs, files in walk.walk(path):
        if len(root) > len(path):
            key = str(root[len(path) + 1:]).lower()
            key = key.replace('\\', '/')
            layer = key.split('/')[0]
            for every in iter(files):
                every = str(every)
                if MODIFIERNAMEFILE in every:
                    f = blue.ResFile()
                    f.Open(root + '/' + every)
                    data = f.read()
                    f.Close()
                    data = data.lower()
                    modifierNames = data.split('\r\n')
                    for modifierName in iter(modifierNames):
                        entryKey = key + '/' + modifierName
                        entries[entryKey] = [modifierName]

            if '/' not in key:
                continue
            if layer not in DOLL_PARTS + DOLL_EXTRA_PARTS + HEAD_CATEGORIES + BODY_CATEGORIES + HAIR_CATEGORIES + ACCESSORIES_CATEGORIES:
                continue
            entries[key] = []
            for every in iter(files):
                if every not in ('_', MODIFIERNAMEFILE):
                    try:
                        entries[key].append(str(root + '/' + every))
                    except:
                        entries[key].append(str(root.replace('resTest', 'res') + '/' + every))

            if not entries[key]:
                del entries[key]

    return entries


def GetMorphsFromGr2(path, ignoreFileNames = []):
    import fnmatch
    filename = ''
    gr2Path = ''
    osPath = os.path.abspath(blue.paths.ResolvePath(path))
    for path, dirs, files in os.walk(os.path.abspath(osPath)):
        for filename in fnmatch.filter(files, '*.gr2'):
            if 'lod1' not in filename.lower() and 'lod2' not in filename.lower() and filename not in ignoreFileNames:
                gr2Path = os.path.join(path, filename)
                break

    names = set()
    if os.path.exists(blue.paths.ResolvePath(gr2Path)):
        gr2Res = blue.resMan.GetResource(str(gr2Path), 'raw')
        while not gr2Res.isPrepared:
            blue.synchro.Yield()

        meshCount = gr2Res.GetMeshCount()
        for i in xrange(meshCount):
            morphCount = gr2Res.GetMeshMorphCount(i)
            for j in xrange(morphCount):
                name = gr2Res.GetMeshMorphName(i, j)
                name = ''.join([ letter for letter in name if not letter.isdigit() ])
                names.add(name)

    return (list(names), filename)


def GetCategorizedBlendShapeNames(blendShapeNames):
    headBlendShapes = []
    bodyBlendShapes = []

    def AddToListByZones(blendShapeName, zones, container):
        for zone in zones:
            if zone in blendShapeName:
                container.append(blendShapeName)
                return True

        return False

    for blendShapeName in blendShapeNames:
        if not AddToListByZones(blendShapeName, HEAD_BLENDSHAPE_ZONES, headBlendShapes):
            AddToListByZones(blendShapeName, BODY_BLENDSHAPE_ZONES, bodyBlendShapes)

    headBlendShapes.sort()
    bodyBlendShapes.sort()
    data = {BLENDSHAPE_CATEGORIES.FACEMODIFIERS: headBlendShapes,
     BLENDSHAPE_CATEGORIES.BODYSHAPES: bodyBlendShapes}
    return data


def AddBlendshapeEntries(path, entries, category):
    badMorphFiles = []
    bscDict = {}
    for i in xrange(100):
        blendShapeNames, filenameChosen = GetMorphsFromGr2(path, badMorphFiles)
        if blendShapeNames:
            bscDict = GetCategorizedBlendShapeNames(blendShapeNames)
            if bscDict.get(category):
                break
        badMorphFiles.append(filenameChosen)

    for bs in bscDict.get(category, []):
        entry = category + '/' + bs.lower()
        if entry not in entries:
            entries[entry] = [bs]
        else:
            entries[entry].append(bs)


def DumpBlendshapes(malePath, femalePath, mode = 'w'):

    def DumpGender(path):
        import CCP_P4
        entries = {}
        AddBlendshapeEntries(path + '/head', entries, BLENDSHAPE_CATEGORIES.FACEMODIFIERS)
        finalOrder = dict()
        for each in entries:
            key = each.split('/')[0]
            items = finalOrder.get(key, set())
            items.add(entries[each][0])
            finalOrder[key] = items

        for each in finalOrder:
            listData = list(finalOrder[each])
            listData.sort()
            filePath = blue.paths.ResolvePath(path + '/' + each + '/modifierNames.yaml')
            fileDir = os.path.dirname(filePath)
            if not os.path.exists(fileDir):
                os.mkdir(fileDir)
            CCP_P4.P4Add(filePath)
            CCP_P4.P4Edit(filePath)
            f = file(filePath, mode)
            for item in listData:
                f.write(item + '\n')

            f.flush()
            f.close()

    DumpGender(femalePath)
    DumpGender(malePath)


def DumpYaml():
    import CCP_P4

    def fun():
        femalePath = FEMALE_BASE_PATH
        femaleTestPath = femalePath.replace('Modular', MODULAR_TEST_CASES_FOLDER)
        femaleOptionsPath = FEMALE_OPTION_FILE_PATH
        malePath = MALE_BASE_PATH
        maleTestPath = malePath.replace('Modular', MODULAR_TEST_CASES_FOLDER)
        maleOptionsPath = MALE_OPTION_FILE_PATH
        DumpBlendshapes(malePath, femalePath)
        if DUMP_MODULAR_TEST_CASES_TO_OPTIONS:
            DumpBlendshapes(maleTestPath, femaleTestPath, mode='a')

        def DumpGenderOption(traversePath, traverseTestPath, optionFilePath):
            optionFilePath = blue.paths.ResolvePath(optionFilePath)
            CCP_P4.P4Add(optionFilePath)
            CCP_P4.P4Edit(optionFilePath)
            f = file(optionFilePath, 'w')
            entries = CreateEntries(traversePath)
            yaml.dump(entries, f, default_flow_style=False)
            f.close()
            if DUMP_MODULAR_TEST_CASES_TO_OPTIONS:
                f = file(optionFilePath, 'a')
                entries = CreateEntries(traverseTestPath)
                yaml.dump(entries, f, default_flow_style=False)
                f.close()

        DumpGenderOption(femalePath, femaleTestPath, femaleOptionsPath)
        DumpGenderOption(malePath, maleTestPath, maleOptionsPath)
        if GENDER_ROOT:
            root = blue.paths.ResolvePath('res:{0}\\Character'.format(BASE_GRAPHICS_FOLDER))
        else:
            root = blue.paths.ResolvePath('res:\\{0}\\Character\\Modular'.format(BASE_GRAPHICS_FOLDER))
        patternsPath = os.path.abspath(root + '\\PatternOptions.yaml')
        CCP_P4.P4Edit(patternsPath)
        CCP_P4.P4Add(patternsPath)
        pf = file(patternsPath, 'w')
        yaml.dump(GetPatternList(), pf, default_flow_style=False)
        pf.close()
        if DUMP_MODULAR_TEST_CASES_TO_OPTIONS:
            patternsPath = root + '\\PatternOptions.yaml'
            pf = file(patternsPath, 'a')
            yaml.dump(GetPatternList(), pf, default_flow_style=False)
            pf.close()

    import uthread
    uthread.new(fun)


def Property(func):
    return property(**func())


def HashDecalList(decalList):
    if not decalList:
        return 0
    s = '.'.join([ str(x) for x in decalList ])
    key = hash(s)
    return key


def ConvertDNAForDB(dollDNA, characterMetadata):
    charInfo = util.KeyVal()
    charInfo.types = characterMetadata.types
    charInfo.typeColors = characterMetadata.typeColors
    charInfo.typeWeights = characterMetadata.typeWeights
    charInfo.typeSpecularity = characterMetadata.typeSpecularity
    charInfo.hairDarkness = characterMetadata.hairDarkness
    charInfo.faceModifiers = {}
    charInfo.bodyShapes = {}
    charInfo.utilityShapes = {}
    charInfo.typeTuck = {}
    for each in dollDNA:
        if type(each) is dict:
            category = each[DNA_STRINGS.CATEGORY]
            if category == HEAD_CATEGORIES.FACEMODIFIERS:
                key = each[DNA_STRINGS.PATH].split(SEPERATOR_CHAR)[1]
                charInfo.faceModifiers[key] = each[DNA_STRINGS.WEIGHT]
            elif category == DOLL_EXTRA_PARTS.BODYSHAPES:
                key = each[DNA_STRINGS.PATH].split(SEPERATOR_CHAR)[1]
                charInfo.bodyShapes[key] = each[DNA_STRINGS.WEIGHT]
            elif category == DOLL_EXTRA_PARTS.UTILITYSHAPES:
                key = each[DNA_STRINGS.PATH].split(SEPERATOR_CHAR)[1]
                charInfo.utilityShapes[key] = each[DNA_STRINGS.WEIGHT]
            elif category == DOLL_EXTRA_PARTS.DEPENDANTS:
                if DNA_STRINGS.VARIATION in each:
                    pathParts = each[DNA_STRINGS.PATH].split(SEPERATOR_CHAR)
                    key = '%s%s%s' % (pathParts[0], SEPERATOR_CHAR, pathParts[1])
                    charInfo.typeTuck[key] = each[DNA_STRINGS.VARIATION]

    return GetDNAConverter().ConvertDNAForDB(charInfo)


class DNAConverter(LogMixin):

    def __init__(self):
        log.LogMixin.__init__(self, 'svc.paperdoll')
        self.sculptingShapesCache = None
        self.modifierLocationCache = None
        self.colorNamesCache = None
        self.colorKeysCache = None

    def ConvertDNAForDB(self, dollInfo):
        dollData = util.KeyVal(appearance=None, sculpts=[], colors=[], modifiers=[])
        dollData.appearance = self.ExtractAppearanceRowFromDollInfo(dollInfo)
        dollData.sculpts = self.ExtractSculptRowsFromDollInfo(dollInfo)
        dollData.modifiers = self.ExtractModifierRowsFromDollInfo(dollInfo)
        dollData.colors = self.ExtractColorRowsFromDollInfo(dollInfo)
        self.LogInfo('Converted DNA to DB. sculpts:', len(dollData.sculpts), ' modifiers:', len(dollData.modifiers), ' colors:', len(dollData.colors))
        return dollData

    def ExtractAppearanceRowFromDollInfo(self, dollInfo):
        return AppearanceRow(dollInfo.get('hairDarkness', 0.0))

    def ExtractSculptRowsFromDollInfo(self, dollInfo):
        sculptingShapes = self.GetSculptingShapes()
        sculptModifiers = {}
        for categoryName in ['faceModifiers', 'bodyShapes', 'archetypes']:
            for sculptKey, weight in dollInfo.get(categoryName, {}).iteritems():
                sculptInfo = sculptingShapes[categoryName].get(sculptKey, None)
                if sculptInfo is None:
                    if categoryName != 'utilityShapes':
                        self.LogError('Sculpting information for ', categoryName, ',', sculptKey, 'is missing, skipping!')
                    continue
                if sculptInfo.row.sculptLocationID not in sculptModifiers:
                    sculptModifiers[sculptInfo.row.sculptLocationID] = util.KeyVal(sculptLocationID=sculptInfo.row.sculptLocationID, weightUpDown=None, weightLeftRight=None, weightForwardBack=None)
                rowData = sculptModifiers[sculptInfo.row.sculptLocationID]
                value = weight
                if not sculptInfo.axis.positive:
                    value = -weight
                setattr(rowData, sculptInfo.axis.field, value)

        res = []
        for v in sculptModifiers.itervalues():
            res.append(SculptingRow(v.sculptLocationID, v.weightUpDown, v.weightLeftRight, v.weightForwardBack))

        return res

    def ExtractModifierRowsFromDollInfo(self, dollInfo):
        modifierByKey = self.GetModifierLocations()
        res = []
        modTypes = dollInfo.get('types', {})
        modVars = dollInfo.get('typeTuck', {})
        for typeKey, resourceID in modTypes.iteritems():
            if resourceID is None:
                continue
            modifierInfo = modifierByKey.get(typeKey)
            if modifierInfo is None:
                self.LogError('Missing modifier data for ', typeKey)
                continue
            varation = None
            if modifierInfo.variationKey is not None and len(modifierInfo.variationKey) and modifierInfo.variationKey in modVars:
                varation = int(modVars[modifierInfo.variationKey][1:])
            res.append(ModifierRow(modifierInfo.modifierLocationID, resourceID, varation))

        return res

    def ExtractColorRowsFromDollInfo(self, dollInfo):
        colorNames = self.GetColorNames()
        colorKeys = self.GetColorKeys()
        typeColors = dollInfo.get('typeColors', {})
        typeWeights = dollInfo.get('typeWeights', {})
        typeGloss = dollInfo.get('typeSpecularity', {})
        fakeColor = util.KeyVal(colorNameID=0)
        res = []
        for colorKey, (colorNameAStr, colorNameBCStr) in typeColors.iteritems():
            colorNameA = 0
            colorNameBC = 0
            weight = 0.0
            gloss = 0.0
            colorInfo = colorKeys.get(colorKey)
            if colorInfo is None:
                self.LogError('Missing color information for ', colorKey, 'skipping extraction')
                continue
            colorNameA = colorNames.get(colorNameAStr.lower(), fakeColor).colorNameID
            if colorNameBCStr is not None and colorInfo.hasSecondary:
                colorNameBC = colorNames.get(colorNameBCStr.lower(), fakeColor).colorNameID
            if colorKey in typeWeights and colorInfo.hasWeight:
                weight = typeWeights[colorKey]
            if colorKey in typeGloss and colorInfo.hasWeight:
                gloss = typeGloss[colorKey]
            res.append(ColorSelectionRow(colorInfo.colorID, colorNameA, colorNameBC, weight, gloss))

        return res

    def GetSculptingShapes(self):
        if self.sculptingShapesCache is None:
            self.sculptingShapesCache = {}
            for row in cfg.paperdollSculptingLocations:
                if row.weightKeyCategory not in self.sculptingShapesCache:
                    self.sculptingShapesCache[row.weightKeyCategory] = {}
                for d in AXIS_DIRECTIONS.iterkeys():
                    if row.weightKeyPrefix in SPECIAL_HANDLE_SHAPES:
                        key = '%sshape' % row.weightKeyPrefix
                        self.sculptingShapesCache[row.weightKeyCategory][key] = util.KeyVal(row=row, axis=SPECIAL_HANDLE_SHAPES[row.weightKeyPrefix])
                    else:
                        key = '%s_%sshape' % (row.weightKeyPrefix, d)
                        self.sculptingShapesCache[row.weightKeyCategory][key] = util.KeyVal(row=row, axis=AXIS_DIRECTIONS[d])

        return self.sculptingShapesCache

    def GetModifierLocations(self):
        if self.modifierLocationCache is None:
            self.modifierLocationCache = {}
            for row in cfg.paperdollModifierLocations:
                self.modifierLocationCache[row.modifierKey] = row

        return self.modifierLocationCache

    def GetColorNames(self):
        if self.colorNamesCache is None:
            self.colorNamesCache = {}
            for row in cfg.paperdollColorNames:
                self.colorNamesCache[row.colorName] = row

        return self.colorNamesCache

    def GetColorKeys(self):
        if self.colorKeysCache is None:
            self.colorKeysCache = {}
            for row in cfg.paperdollColors:
                self.colorKeysCache[row.colorKey] = row

        return self.colorKeysCache
