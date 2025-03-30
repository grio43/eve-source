#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\locatorValidation.py
import ctypes
import string
import re
from evegraphics.validation.commonUtilities import Validate, SceneType
from evegraphics.validation.errors import SingleObjectValidationError
from evegraphics.validation.validationFunctions import ListIsNotEmpty, ShouldBeGreaterThanOrEqual
from evegraphics.validation import resources
import geo2
import limits
import trinity

@Validate('EveSOFDataHull(owner)/.../List[EveSOFDataHullLocator](locators)')
def ValidateTurretLocatorsCount(context, owner, locators):
    minTurretLocators = limits.GetValue(owner.category, limits.MIN_TURRET_LOCATOR_COUNT)
    if minTurretLocators is None:
        return
    validTurretSetNames = ['locator_turret_', 'locator_atomic_']
    locatorsByName = {locator.name:locator for locator in locators}
    turretLocators = set()
    for validTurretSetName in validTurretSetNames:
        for locatorName, locator in locatorsByName.iteritems():
            if locatorName.startswith(validTurretSetName):
                setIdentifier = re.search('%s\\d+' % validTurretSetName, locatorName).group()
                turretLocators.add(setIdentifier)

    if len(turretLocators) < minTurretLocators:
        context.Error(locators, 'Too few turret locators, expected to get %d locators, but only found %d: [%s]' % (minTurretLocators, len(turretLocators), ','.join(turretLocators)))


@Validate('EveSOFDataHull(owner)/.../List[EveSOFDataHullLocator](locators)')
def ValidateTurretLocatorName(context, owner, locators):
    minTurretLocators = limits.GetValue(owner.category, limits.MIN_TURRET_LOCATOR_COUNT)
    if minTurretLocators is None:
        return
    validTurretSetNames = ['locator_turret_', 'locator_atomic_']
    locatorsByName = {locator.name:locator for locator in locators}
    locatorSetIdentifiers = {setName:[] for setName in validTurretSetNames}
    for validTurretSetName in validTurretSetNames:
        for locatorName, locator in locatorsByName.iteritems():
            if locatorName.startswith(validTurretSetName):
                if not re.match('[a-z]+_[a-z]+_\\d+[a-z]', locatorName):
                    context.Error(locator, 'Incorrectly named turret locator')
                    continue
                setIndex = int(re.search('\\d+', locatorName.replace(validTurretSetName, '')).group())
                setLetter = re.search('[a-z]+', locatorName.replace(validTurretSetName, '')).group()
                locatorSetIdentifiers[validTurretSetName].append((setIndex, setLetter))

    for turretSetName, identifiers in locatorSetIdentifiers.iteritems():
        if len(identifiers) == 1:
            context.Error(locators, 'Turret set has only 1 locator. There should be more than 1...')
            continue
        identifiers.sort()
        for index, (turretIndex, turretLetter) in enumerate(identifiers):
            currentLocatorName = '%s%d%s' % (turretSetName, turretIndex, turretLetter)
            locator = locatorsByName[currentLocatorName]
            if index == 0:
                if turretIndex != 1 or turretLetter != 'a':
                    context.Error(locator, 'Incorrect name should be %s%d%s' % (turretSetName, 1, 'a'))
                continue
            lastIndex, lastLetter = identifiers[index - 1]
            lastLocatorName = '%s%d%s' % (turretSetName, lastIndex, lastLetter)
            incorrectIndex = turretIndex not in (lastIndex, lastIndex + 1)
            incorrectLetter = turretIndex == lastIndex and ord(turretLetter) != ord(lastLetter) + 1
            incorrectStartingLetter = turretIndex == lastIndex + 1 and turretLetter != 'a'
            if incorrectIndex or incorrectLetter or incorrectStartingLetter:
                context.Error(locator, "Incorrect name when following this locator '%s'" % lastLocatorName)


@Validate('EveSOFDataHullLocatorSet')
def ValidateEveSOFDataHullLocatorSet(context, sofLocatorSet):
    context.Expect(sofLocatorSet, 'locators', ListIsNotEmpty)


def RemoveSofLocatorSets(owner):

    def inner():
        owner.locatorSets.removeAt(-1)

    return ('Remove all locator sets from hull', inner, True)


@Validate('EveSOFDataHull(owner)/.../List[EveSOFDataHullLocatorSet](sofLocatorSets)')
def StructureSetsShouldNotHaveLocators(context, owner, sofLocatorSets):
    if owner.category == 'structure_states' and sofLocatorSets:
        context.Error(sofLocatorSets, 'Structure state hulls should not have locators', actions=(RemoveSofLocatorSets(owner),))


@Validate('EveSOFDataHull(owner)/.../List[EveSOFDataHullLocatorSet](sofLocatorSets)')
def ValidateListOfEveSOFDataHullLocatorSet(context, owner, sofLocatorSets):
    damageLocatorsMin = limits.GetValue(owner.category, limits.DAMAGE_LOCATORS_MIN)
    damageLocatorSet = None
    for locatorSet in sofLocatorSets:
        if locatorSet.name == 'damage':
            damageLocatorSet = locatorSet
            break

    if damageLocatorSet is None:
        if owner.category not in ('structure_states', 'placeholder') and damageLocatorsMin > 0:
            context.AddError(SingleObjectValidationError(sofLocatorSets, "has no locatorset called 'damage'"))
    elif damageLocatorsMin is not None:
        context.ExpectValue(damageLocatorSet, len(damageLocatorSet.locators), ShouldBeGreaterThanOrEqual(damageLocatorsMin), message='number of damage locators should be no less than %s (but is %s)' % (damageLocatorsMin, len(damageLocatorSet.locators)))


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullLocatorSet(sofLocatorSet)')
def ValidateLocatorSetBoneIndices(context, owner, sofLocatorSet):
    granny = resources.GetResource(context, owner.geometryResFilePath, resources.ResourceType.GRANNY)
    if not granny:
        return
    count = len(granny.meshes[0].bonebindings)
    for locator in sofLocatorSet.locators:
        if locator.boneIndex >= count:
            context.Error(locator, 'bone index is not valid')


@Validate('EveSOFDataHull(owner)/.../EveSOFDataHullLocatorSet(locators)')
def HullLocatorsAreCloseToGeometry(context, owner, locators):
    if locators.name not in ('damage', 'explosions'):
        return
    granny = resources.GetResource(context, owner.geometryResFilePath, resources.ResourceType.GRANNY)
    if not granny:
        return
    fi = ctypes.cast(granny.GetGrannyFileInfo(), ctypes.c_void_p).value
    for i, each in enumerate(locators.locators):
        direction = geo2.QuaternionTransformVector(each.rotation, (0, 1, 0))
        pos = geo2.Vec3Add(each.position, geo2.Vec3Scale(direction, 1))
        if not trinity.GrannyRayIntersection(fi, pos, geo2.Vec3Scale(direction, -1), -1, -1):
            context.Error(locators, '%s locators not touching geometry' % locators.name)
            return


_NAME_PATTERNS = (re.compile('locator_turret_(?P<index>\\d+)\\w?'),
 re.compile('locator_launcher_(?P<index>\\d+)\\w?'),
 re.compile('locator_booster_(?P<index>\\d+)'),
 re.compile('locator_audio_booster'),
 re.compile('locator_turretm_(?P<index>\\d+)\\w?'),
 re.compile('locator_moonharvester_(?P<index>\\d+)\\w?'),
 re.compile('locator_xl_(?P<index>\\d+)\\w?'),
 re.compile('locator_atomic_(?P<index>\\d+)\\w?'))
_HANGAR_NAME_PATTERNS = (re.compile('Traffic_Start_(?P<index>[123])\\w?'), re.compile('Traffic_End_(?P<index>[123])\\w?'))
_SEQUENCE_PATTERNS = (re.compile('locator_turret_(?P<index>\\d+)\\w?'), re.compile('locator_launcher_(?P<index>\\d+)\\w?'))

def _GetLocatorName(pattern):
    found = pattern.find('(')
    if found == -1:
        return pattern
    return pattern[:found]


@Validate('List[EveLocator2]', SceneType)
def ValidateLocatorNamesPrefixes(context, locators):
    isHangar = context.GetArgument(SceneType) == SceneType.HANGAR
    namePatterns = _NAME_PATTERNS
    if isHangar:
        namePatterns = _NAME_PATTERNS + _HANGAR_NAME_PATTERNS
    for locator in locators:
        found = False
        for i, pattern in enumerate(namePatterns):
            match = pattern.match(locator.name)
            if match:
                found = True
                break

        if not found:
            context.Error(locator, 'invalid locator name %s' % locator.name)


@Validate('List[EveLocator2]')
def ValidateLocatorNamesFormSequence(context, locators):
    indices = {}
    for locator in locators:
        found = False
        for i, pattern in enumerate(_SEQUENCE_PATTERNS):
            match = pattern.match(locator.name)
            if match:
                found = True
                try:
                    idx = int(match.group('index'))
                except IndexError:
                    break

                indices.setdefault(i, set()).add(idx)
                break

        if not found:
            continue

    for k, v in indices.items():
        if min(v) != 1 or max(v) != len(v):
            context.Error(locators, 'locator indices %s in names do not form a sequence 1, 2, ...' % _GetLocatorName(_NAME_PATTERNS[k].pattern))


@Validate('List[EveLocator2]')
def LocatorsHaveDistinctNames(context, locators):
    for each in locators:
        occurences = [ x for x in locators if x.name == each.name ]
        if len(occurences) != 1:
            context.Error(each, 'duplicate locator name %s' % each.name)


@Validate('/EveShip2/.../List[EveLocator2]')
def ShipMustHaveAudioBoosterLocator(context, locators):
    audio = [ x for x in locators if x.name == 'locator_audio_booster' ]
    if not audio:
        context.Error(locators, 'ship must have a locator_audio_booster locator')
