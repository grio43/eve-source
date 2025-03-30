#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\const.py
import math
from itertoolsext.Enum import Enum
import eve.common.lib.appConst as appconst
import inventorycommon.const as invconst

@Enum

class InputType(object):
    GRAPHIC_ID = 'Graphic ID'
    ICON_ID = 'Icon ID'
    TYPE_ID = 'Type ID'
    RED_FILE = 'Red File'


@Enum

class IconRenderFormat(object):
    PNG = 'png'
    JPG = 'jpg'


@Enum

class Language(object):
    ENGLISH = None
    CHINESE = 'zh'
    AUTO_DETECT = 'auto'


RENDER_64 = [(64, IconRenderFormat.PNG)]
RENDER_128 = [(128, IconRenderFormat.PNG)]
RENDER_512 = [(512, IconRenderFormat.JPG)]
RENDER_64_128 = [(64, IconRenderFormat.PNG), (128, IconRenderFormat.PNG)]
RENDER_64_512 = [(64, IconRenderFormat.PNG), (512, IconRenderFormat.JPG)]
RENDER_64_128_512 = [(64, IconRenderFormat.PNG), (128, IconRenderFormat.PNG), (512, IconRenderFormat.JPG)]

class IconStyle(object):
    STANDARD = 1
    BP_ORIGINAL = 2
    BP_COPY = 4
    BP_REACTION = 8
    BP_RELIC = 16
    BP_DUST = 32
    HOLOGRAM = 64
    TRANSPARENT = 128
    ALL_BP = BP_ORIGINAL | BP_COPY | BP_REACTION | BP_DUST | BP_RELIC
    ALL = STANDARD | ALL_BP | HOLOGRAM | TRANSPARENT


STYLE_STRINGS = {}
STYLE_STRINGS[IconStyle.STANDARD] = None
STYLE_STRINGS[IconStyle.BP_ORIGINAL] = 'bp'
STYLE_STRINGS[IconStyle.BP_COPY] = 'bpc'
STYLE_STRINGS[IconStyle.BP_RELIC] = 'relic'
STYLE_STRINGS[IconStyle.BP_DUST] = 'dust'
STYLE_STRINGS[IconStyle.BP_REACTION] = 'reaction'
STYLE_STRINGS[IconStyle.TRANSPARENT] = 'tr'
STYLE_STRINGS[IconStyle.HOLOGRAM] = 'isis'

@Enum

class IconMetaGroup(object):
    T1 = appconst.metaGroupTech1
    T2 = appconst.metaGroupTech2
    T3 = appconst.metaGroupTech3
    FACTION = appconst.metaGroupFaction
    STORYLINE = appconst.metaGroupStoryline
    DEADSPACE = appconst.metaGroupDeadspace
    OFFICER = appconst.metaGroupOfficer
    ABYSSAL = appconst.metaGroupAbyssal
    PREMIUM = appconst.metaGroupPremium
    LIMITED_TIME = appconst.metaGroupLimitedTime
    STRUCTURE_T1 = appconst.metaGroupStructureTech1
    STRUCTURE_T2 = appconst.metaGroupStructureTech2
    STRUCTURE_FACTION = appconst.metaGroupStructureFaction


ALL_METAGROUPS = [ l for l in IconMetaGroup ]
ALL_METAGROUPS_NO_T1 = [ l for l in IconMetaGroup if l != IconMetaGroup.T1 ]

@Enum

class IconFaction(object):
    GENERIC = 'generic'
    AMARR = 'amarr'
    CALDARI = 'caldari'
    GALLENTE = 'gallente'
    MINMATAR = 'minmatar'
    ANGEL = 'angel'
    BLOODRAIDER = 'bloodraider'
    GURISTA = 'guristas'
    MORDU = 'mordu'
    SANSHA = 'sansha'
    CONCORD = 'concord'
    UPWELL = 'upwell'
    ORE = 'ore'
    SOE = 'soe'
    JOVE = 'jove'
    ROGUE = 'rogue'
    SOCT = 'soct'
    SLEEPER = 'sleeper'
    TALOCAN = 'talocan'
    TRIGLAVIAN = 'triglavian'
    WHO = 'who'


def GetIconFaction(sofHull, sofFaction, sofRace):
    if sofHull.startswith('dal') or sofHull.startswith('tardis'):
        return IconFaction.WHO
    elif sofFaction == 'bloodraider':
        return IconFaction.BLOODRAIDER
    elif sofFaction == 'guristas':
        return IconFaction.GURISTA
    elif sofFaction.startswith('upwell'):
        return IconFaction.UPWELL
    elif sofRace == 'amarr':
        return IconFaction.AMARR
    elif sofRace == 'caldari':
        return IconFaction.CALDARI
    elif sofRace == 'gallente':
        return IconFaction.GALLENTE
    elif sofRace == 'minmatar':
        return IconFaction.MINMATAR
    elif sofRace == 'angel':
        return IconFaction.ANGEL
    elif sofRace == 'mordu':
        return IconFaction.MORDU
    elif sofRace == 'sansha':
        return IconFaction.SANSHA
    elif sofRace == 'concord':
        return IconFaction.CONCORD
    elif sofRace == 'soe':
        return IconFaction.SOE
    elif sofRace == 'ore':
        return IconFaction.ORE
    elif sofRace == 'rogue':
        return IconFaction.ROGUE
    elif sofRace == 'soct':
        return IconFaction.SOCT
    elif sofRace == 'sleeper':
        return IconFaction.SLEEPER
    elif sofRace == 'talocan':
        return IconFaction.TALOCAN
    elif sofRace == 'triglavian':
        return IconFaction.TRIGLAVIAN
    elif sofRace == 'jove':
        return IconFaction.JOVE
    else:
        return IconFaction.GENERIC


_FACTION_SCENES = {}
_FACTION_SCENES[IconFaction.GENERIC] = 'res:/dx9/scene/iconbackground/generic.red'
_FACTION_SCENES[IconFaction.AMARR] = 'res:/dx9/scene/iconbackground/amarr.red'
_FACTION_SCENES[IconFaction.CALDARI] = 'res:/dx9/scene/iconbackground/caldari.red'
_FACTION_SCENES[IconFaction.GALLENTE] = 'res:/dx9/scene/iconbackground/gallente.red'
_FACTION_SCENES[IconFaction.MINMATAR] = 'res:/dx9/scene/iconbackground/minmatar.red'
_FACTION_SCENES[IconFaction.ANGEL] = 'res:/dx9/scene/iconbackground/angel.red'
_FACTION_SCENES[IconFaction.BLOODRAIDER] = 'res:/dx9/scene/iconbackground/bloodraider.red'
_FACTION_SCENES[IconFaction.GURISTA] = 'res:/dx9/scene/iconbackground/guristas.red'
_FACTION_SCENES[IconFaction.MORDU] = 'res:/dx9/scene/iconbackground/mordu.red'
_FACTION_SCENES[IconFaction.SANSHA] = 'res:/dx9/scene/iconbackground/sansha.red'
_FACTION_SCENES[IconFaction.CONCORD] = 'res:/dx9/scene/iconbackground/concord.red'
_FACTION_SCENES[IconFaction.ORE] = 'res:/dx9/scene/iconbackground/ore.red'
_FACTION_SCENES[IconFaction.SOE] = 'res:/dx9/scene/iconbackground/soe.red'
_FACTION_SCENES[IconFaction.JOVE] = 'res:/dx9/scene/iconbackground/jove.red'
_FACTION_SCENES[IconFaction.ROGUE] = 'res:/dx9/scene/iconbackground/rogue.red'
_FACTION_SCENES[IconFaction.SOCT] = 'res:/dx9/scene/iconbackground/soct.red'
_FACTION_SCENES[IconFaction.SLEEPER] = 'res:/dx9/scene/iconbackground/sleeper.red'
_FACTION_SCENES[IconFaction.TALOCAN] = 'res:/dx9/scene/iconbackground/talocan.red'
_FACTION_SCENES[IconFaction.TRIGLAVIAN] = 'res:/dx9/scene/iconbackground/triglavian.red'
_FACTION_SCENES[IconFaction.WHO] = 'res:/dx9/scene/iconbackground/who.red'

def GetSceneForSofRaceFaction(sofHull, sofFaction, sofRace):
    return GetSceneForFaction(GetIconFaction(sofHull, sofFaction, sofRace))


def GetSceneForFaction(iconFaction):
    return _FACTION_SCENES.get(iconFaction, 'res:/dx9/scene/iconbackground/generic.red')


OUTLINE_THICKNESS = 0
OUTLINE_HARDLINES = False
OUTLINE_COLOR = {}
OUTLINE_COLOR[IconFaction.AMARR] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.CALDARI] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.GALLENTE] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.MINMATAR] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.ANGEL] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.BLOODRAIDER] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.GURISTA] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.MORDU] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.SANSHA] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.CONCORD] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.SOE] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.ORE] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.UPWELL] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.SOCT] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.ROGUE] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.SLEEPER] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.JOVE] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.TALOCAN] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.TRIGLAVIAN] = (255, 255, 255, 255)
OUTLINE_COLOR[IconFaction.GENERIC] = (255, 255, 255, 255)

@Enum

class IconBackground(object):
    NONE = None
    BP_ORIGINAL = 'BP_ORIGINAL'
    BP_COPY = 'BP_COPY'
    BP_RELIC = 'BP_RELIC'
    BP_DUST = 'BP_DUST'
    BP_REACTION = 'BP_REACTION'
    TRANSPARENT = 'TRANSPARENT'
    RACIAL = 'RACIAL'


def GetBackgroundPathAndTransparency(background, faction):
    transparent = background == IconBackground.TRANSPARENT
    if background == IconBackground.RACIAL:
        path = RACIAL_BACKGROUND_PATHS.get(faction, None)
    else:
        path = BACKGROUND_PATHS.get(background, None)
    return (path, transparent)


BACKGROUND_PATHS = {}
BACKGROUND_PATHS[IconBackground.NONE] = None
BACKGROUND_PATHS[IconBackground.BP_ORIGINAL] = 'res:/UI/Texture/Icons/BPO.png'
BACKGROUND_PATHS[IconBackground.BP_COPY] = 'res:/UI/Texture/Icons/BPC.png'
BACKGROUND_PATHS[IconBackground.BP_RELIC] = 'res:/UI/Texture/Icons/relic.png'
BACKGROUND_PATHS[IconBackground.BP_DUST] = 'res:/UI/Texture/Icons/BPD.png'
BACKGROUND_PATHS[IconBackground.BP_REACTION] = 'res:/UI/Texture/Icons/reaction.png'
BACKGROUND_PATHS[IconBackground.TRANSPARENT] = None
RACIAL_BACKGROUND_PATHS = {}
RACIAL_BACKGROUND_PATHS[IconFaction.AMARR] = 'res:/TestCases/IconBackgrounds/gradient/amarr.png'
RACIAL_BACKGROUND_PATHS[IconFaction.CALDARI] = 'res:/TestCases/IconBackgrounds/gradient/caldari.png'
RACIAL_BACKGROUND_PATHS[IconFaction.GALLENTE] = 'res:/TestCases/IconBackgrounds/gradient/gallente.png'
RACIAL_BACKGROUND_PATHS[IconFaction.MINMATAR] = 'res:/TestCases/IconBackgrounds/gradient/minmatar.png'
RACIAL_BACKGROUND_PATHS[IconFaction.ANGEL] = 'res:/TestCases/IconBackgrounds/gradient/angel.png'
RACIAL_BACKGROUND_PATHS[IconFaction.BLOODRAIDER] = 'res:/TestCases/IconBackgrounds/gradient/bloodraider.png'
RACIAL_BACKGROUND_PATHS[IconFaction.GURISTA] = 'res:/TestCases/IconBackgrounds/gradient/gurista.png'
RACIAL_BACKGROUND_PATHS[IconFaction.MORDU] = 'res:/TestCases/IconBackgrounds/gradient/mordu.png'
RACIAL_BACKGROUND_PATHS[IconFaction.SANSHA] = 'res:/TestCases/IconBackgrounds/gradient/sansha.png'
RACIAL_BACKGROUND_PATHS[IconFaction.CONCORD] = 'res:/TestCases/IconBackgrounds/gradient/concord.png'
RACIAL_BACKGROUND_PATHS[IconFaction.SOE] = 'res:/TestCases/IconBackgrounds/gradient/soe.png'
RACIAL_BACKGROUND_PATHS[IconFaction.ORE] = 'res:/TestCases/IconBackgrounds/gradient/ore.png'
RACIAL_BACKGROUND_PATHS[IconFaction.UPWELL] = 'res:/TestCases/IconBackgrounds/gradient/upwell.png'
RACIAL_BACKGROUND_PATHS[IconFaction.SOCT] = 'res:/TestCases/IconBackgrounds/gradient/soct.png'
RACIAL_BACKGROUND_PATHS[IconFaction.ROGUE] = 'res:/TestCases/IconBackgrounds/gradient/rogue.png'
RACIAL_BACKGROUND_PATHS[IconFaction.SLEEPER] = 'res:/TestCases/IconBackgrounds/gradient/sleeper.png'
RACIAL_BACKGROUND_PATHS[IconFaction.JOVE] = 'res:/TestCases/IconBackgrounds/gradient/jove.png'
RACIAL_BACKGROUND_PATHS[IconFaction.TALOCAN] = 'res:/TestCases/IconBackgrounds/gradient/talocan.png'
RACIAL_BACKGROUND_PATHS[IconFaction.TRIGLAVIAN] = 'res:/TestCases/IconBackgrounds/gradient/triglavian.png'
RACIAL_BACKGROUND_PATHS[IconFaction.GENERIC] = 'res:/TestCases/IconBackgrounds/gradient/generic.png'

@Enum

class IconOverlay(object):
    NONE = None
    BP_ORIGINAL = 'res:/UI/Texture/Icons/bpo_overlay.png'
    BP_COPY = 'res:/UI/Texture/Icons/bpc_overlay.png'
    BP_RELIC = 'res:/UI/Texture/Icons/relic_overlay.png'
    BP_REACTION = 'res:/UI/Texture/Icons/bpc_overlay.png'


@Enum

class IconViewMode(object):
    TOP = 'TOP'
    SIDE_RIGHT = 'SIDE_RIGHT'
    SIDE_LEFT = 'SIDE_LEFT'
    FRONT = 'FRONT'
    PERSPECTIVE = 'PERSPECTIVE'
    TURRET = 'TURRET'
    FREE = 'FREE'


VIEW_MODE_SUN_DIRECTIONS = {}
VIEW_MODE_SUN_DIRECTIONS[IconViewMode.TOP] = (0.0, -1.0, 0.0)
VIEW_MODE_SUN_DIRECTIONS[IconViewMode.SIDE_RIGHT] = (1.0, 0.0, 0.0)
VIEW_MODE_SUN_DIRECTIONS[IconViewMode.SIDE_LEFT] = (-1.0, 0.0, 0.0)
VIEW_MODE_SUN_DIRECTIONS[IconViewMode.FRONT] = (0.0, 0.0, -1.0)
VIEW_MODE_SUN_DIRECTIONS[IconViewMode.PERSPECTIVE] = (-0.3, -0.7, 0.0)
VIEW_MODE_SUN_DIRECTIONS[IconViewMode.TURRET] = (-0.5719, -0.7886, 0.2258)
VIEW_MODE_CAMERA_ANGLES = {}
VIEW_MODE_CAMERA_ANGLES[IconViewMode.TOP] = (math.radians(0.0), math.radians(-90.0), math.radians(0.0))
VIEW_MODE_CAMERA_ANGLES[IconViewMode.SIDE_RIGHT] = (math.radians(-90.0), math.radians(0.0), math.radians(0.0))
VIEW_MODE_CAMERA_ANGLES[IconViewMode.SIDE_LEFT] = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
VIEW_MODE_CAMERA_ANGLES[IconViewMode.FRONT] = (math.radians(-0.0), math.radians(0.0), math.radians(-90.0))
VIEW_MODE_CAMERA_ANGLES[IconViewMode.PERSPECTIVE] = (math.radians(20.0), math.radians(-25.0), math.radians(0.0))
VIEW_MODE_CAMERA_ANGLES[IconViewMode.TURRET] = (math.radians(-90.0), math.radians(0.0), math.radians(0.0))
USE_STATIC_BACKGROUNDS = False
BLUEPRINT_SCENE_GFXID = 21345
DEFAULT_ICON_DIFF_TOLERANCE = 0.01
