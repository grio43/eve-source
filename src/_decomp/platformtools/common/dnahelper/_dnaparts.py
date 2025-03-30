#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\platformtools\common\dnahelper\_dnaparts.py
import re
from platformtools.compatibility.dependencies.itertoolsext import Enum

@Enum

class DNAPrefixes(object):
    MATERIAL = 'material?'
    VARIANT = 'variant?'
    PATTERN = 'pattern?'
    LAYOUT = 'layout?'
    RES_PATH_INSERT = 'respathinsert?'
    EXPERIMENTAL = 'experimental?'


@Enum

class _DNAPartCounts(object):
    MATERIAL = 4
    PATTERN_MATERIAL = 2


@Enum

class DNAElementKinds(object):
    HULL = 'hull'
    FACTION = 'faction'
    RACE = 'race'
    MATERIAL = 'material'
    PATTERN = 'pattern'
    VARIANT = 'variant'
    RES_PATH_INSERT = 'resPathInsert'
    EXPERIMENTAL = 'experimental'
    LAYOUT = 'layout'


@Enum

class DNAPartNames(object):
    HULL = 'hull'
    FACTION = 'faction'
    RACE = 'race'
    MATERIAL_1 = 'material1'
    MATERIAL_2 = 'material2'
    MATERIAL_3 = 'material3'
    MATERIAL_4 = 'material4'
    PATTERN = 'pattern'
    PATTERN_MATERIAL_1 = 'patternMaterial1'
    PATTERN_MATERIAL_2 = 'patternMaterial2'
    VARIANT = 'variant'
    RES_PATH_INSERT = 'resPathInsert'
    EXPERIMENTAL = 'experimental'
    LAYOUTS = 'layouts'
    MATERIALS = 'materials'
    PATTERN_MATERIALS = 'patternMaterials'
    MATERIAL_PROPERTIES = [MATERIAL_1,
     MATERIAL_2,
     MATERIAL_3,
     MATERIAL_4]
    PATTERN_MATERIAL_PROPERTIES = [PATTERN_MATERIAL_1, PATTERN_MATERIAL_2]


HFR_PARTS = [(DNAElementKinds.HULL, DNAPartNames.HULL), (DNAElementKinds.FACTION, DNAPartNames.FACTION), (DNAElementKinds.RACE, DNAPartNames.RACE)]
MATERIAL_PARTS = [(DNAElementKinds.MATERIAL, DNAPartNames.MATERIAL_1),
 (DNAElementKinds.MATERIAL, DNAPartNames.MATERIAL_2),
 (DNAElementKinds.MATERIAL, DNAPartNames.MATERIAL_3),
 (DNAElementKinds.MATERIAL, DNAPartNames.MATERIAL_4)]
PATTERN_PARTS = [(DNAElementKinds.PATTERN, DNAPartNames.PATTERN)]
PATTERN_MATERIAL_PARTS = [(DNAElementKinds.MATERIAL, DNAPartNames.PATTERN_MATERIAL_1), (DNAElementKinds.MATERIAL, DNAPartNames.PATTERN_MATERIAL_2)]
ALL_PATTERN_PARTS = PATTERN_PARTS + PATTERN_MATERIAL_PARTS
OTHER_PARTS = [(DNAElementKinds.LAYOUT, DNAPartNames.LAYOUTS)]
LAYOUT_PARTS = HFR_PARTS + MATERIAL_PARTS + PATTERN_PARTS + OTHER_PARTS
DNA_DATA_PARTS = HFR_PARTS + MATERIAL_PARTS + ALL_PATTERN_PARTS + OTHER_PARTS
DNA_ALL_PARTS = DNA_DATA_PARTS + [(DNAElementKinds.VARIANT, DNAPartNames.VARIANT), (DNAElementKinds.RES_PATH_INSERT, DNAPartNames.RES_PATH_INSERT), (DNAElementKinds.EXPERIMENTAL, DNAPartNames.EXPERIMENTAL)]
LAYOUT_DESCRIPTOR_PARTS = HFR_PARTS + MATERIAL_PARTS + PATTERN_PARTS + [(DNAElementKinds.LAYOUT, DNAElementKinds.LAYOUT)]
_LAYOUT_REGEX = re.compile('([a-z]+)([0-9]+)', re.I)

class DNAParts(object):

    def __init__(self, dna = None):
        self.hull = ''
        self.faction = ''
        self.race = ''
        self.materials = ['',
         '',
         '',
         '']
        self.variant = ''
        self.pattern = ''
        self.layouts = []
        self.customMaterials = ['', '']
        self.resPathInsert = ''
        self.experimental = ''
        if dna:
            self.SetFromDNA(dna)

    @property
    def material1(self):
        return self.materials[0]

    @material1.setter
    def material1(self, value):
        self.materials[0] = value

    @property
    def material2(self):
        return self.materials[1]

    @material2.setter
    def material2(self, value):
        self.materials[1] = value

    @property
    def material3(self):
        return self.materials[2]

    @material3.setter
    def material3(self, value):
        self.materials[2] = value

    @property
    def material4(self):
        return self.materials[3]

    @material4.setter
    def material4(self, value):
        self.materials[3] = value

    @property
    def patternMaterial1(self):
        return self.customMaterials[0]

    @patternMaterial1.setter
    def patternMaterial1(self, value):
        self.customMaterials[0] = value

    @property
    def patternMaterial2(self):
        return self.customMaterials[1]

    @patternMaterial2.setter
    def patternMaterial2(self, value):
        self.customMaterials[1] = value

    @property
    def patternMaterials(self):
        return self.customMaterials

    @patternMaterials.setter
    def patternMaterials(self, value):
        self.customMaterials = value

    def Reset(self):
        self.hull = ''
        self.faction = ''
        self.race = ''
        self.materials = ['',
         '',
         '',
         '']
        self.variant = ''
        self.pattern = ''
        self.layouts = []
        self.customMaterials = ['', '']
        self.resPathInsert = ''
        self.experimental = ''

    @staticmethod
    def DetermineDNAParts(dna):
        parts = dna.split(':')
        parts = _SanitizeParts(parts)
        otherParts = [''] * len(DNAPrefixes)
        for part in parts:
            for i, prefix in enumerate(DNAPrefixes):
                if part.startswith(prefix):
                    otherParts[i] = part
                    break

        hfr = [ x for x in parts if x not in otherParts ]
        hfr += [''] * max(0, 3 - len(hfr))
        return tuple(hfr[0:3] + otherParts)

    def SetFromGraphicID(self, graphicID, graphicsCache):
        self.Reset()
        hfr = graphicsCache.GetSOFDataForGraphicID(graphicID)
        if all(hfr):
            self.hull = hfr[0] or ''
            self.faction = hfr[1] or ''
            self.race = hfr[2] or ''
            materialData = graphicsCache.GetMaterialSetForGraphicID(graphicID)
            if materialData:
                self.pattern = materialData.get('sofPatternName', 'none')
                self.resPathInsert = materialData.get('resPathInsert', '')
                self.materials = [ materialData.get('material%i' % x, 'none') for x in range(1, 5) ]
                self.customMaterials = [ materialData.get('custommaterial%i' % x, 'none') for x in range(1, 3) ]
            layouts = graphicsCache.GetLayoutsForGraphicID(graphicID)
            if layouts:
                self.layouts = layouts
            return True
        else:
            return False

    def SetMaterialFromPart(self, part):
        if part:
            materials = part[len(DNAPrefixes.MATERIAL):].split(';')
            if len(materials) > _DNAPartCounts.MATERIAL:
                raise ValueError('Material part contains too many materials: {}'.format(part))
            if len(materials) < _DNAPartCounts.MATERIAL:
                raise ValueError('Material part contains too few materials: {}'.format(part))
            else:
                self.materials = part[len(DNAPrefixes.MATERIAL):].split(';')
        else:
            self.materials = ['',
             '',
             '',
             '']

    def SetVariantFromPart(self, part):
        if part:
            if len(part) <= len(DNAPrefixes.VARIANT):
                raise ValueError('Variant set with no value: {}'.format(part))
            self.variant = part[len(DNAPrefixes.VARIANT):]
        else:
            self.variant = ''

    def SetPatternFromPart(self, part):
        self.customMaterials = ['', '']
        if part:
            materials = part[len(DNAPrefixes.PATTERN):].split(';')
            if len(materials) > _DNAPartCounts.PATTERN_MATERIAL + 1:
                raise ValueError('Too many materials supplied for pattern: {}'.format(part))
            if len(part) <= len(DNAPrefixes.PATTERN):
                raise ValueError('Pattern set with no value: {}'.format(part))
            self.pattern = materials[0]
            for i in range(1, 3):
                try:
                    self.customMaterials[i - 1] = materials[i]
                except IndexError:
                    continue

        else:
            self.pattern = ''

    def SetResPathInsertFromPart(self, part):
        if part:
            if len(part) <= len(DNAPrefixes.RES_PATH_INSERT):
                raise ValueError('Res Path Insert set with no value: {}'.format(part))
            self.resPathInsert = part[len(DNAPrefixes.RES_PATH_INSERT):]
        else:
            self.resPathInsert = ''

    def SetExperimentalFromPart(self, part):
        if part:
            if len(part) <= len(DNAPrefixes.EXPERIMENTAL):
                raise ValueError('Experimental set with no value: {}'.format(part))
            self.experimental = part[len(DNAPrefixes.EXPERIMENTAL):] if part else ''
        else:
            self.experimental = ''

    def SetLayoutFromPart(self, part):
        if part:
            if len(part) <= len(DNAPrefixes.LAYOUT):
                raise ValueError('Layout set, but no layouts provided: {}'.format(part))
            layouts = part[len(DNAPrefixes.LAYOUT):].split(';')
            self.layouts = layouts
            self.layouts = [ layout for layout in self.layouts if layout.strip() != '' ]
        else:
            self.layouts = []

    def SetFromDNA(self, dna, onlyHullFactionRace = False):
        parts = self.DetermineDNAParts(dna)
        self.hull = parts[0] or ''
        self.faction = parts[1] or ''
        self.race = parts[2] or ''
        if onlyHullFactionRace:
            self.SetMaterialFromPart('')
            self.SetPatternFromPart('')
            self.SetResPathInsertFromPart('')
            self.SetVariantFromPart('')
            self.SetLayoutFromPart('')
            self.SetExperimentalFromPart('')
        else:
            self.SetMaterialFromPart(parts[3 + DNAPrefixes.GetIndex(DNAPrefixes.MATERIAL)])
            self.SetPatternFromPart(parts[3 + DNAPrefixes.GetIndex(DNAPrefixes.PATTERN)])
            self.SetResPathInsertFromPart(parts[3 + DNAPrefixes.GetIndex(DNAPrefixes.RES_PATH_INSERT)])
            self.SetVariantFromPart(parts[3 + DNAPrefixes.GetIndex(DNAPrefixes.VARIANT)])
            self.SetLayoutFromPart(parts[3 + DNAPrefixes.GetIndex(DNAPrefixes.LAYOUT)])
            self.SetExperimentalFromPart(parts[3 + DNAPrefixes.GetIndex(DNAPrefixes.EXPERIMENTAL)])

    def GetHFRPart(self):
        return str(self.hull) + ':' + str(self.faction) + ':' + str(self.race)

    @staticmethod
    def ConstructMaterialPart(materials):
        valid = False
        materialPart = ''
        for i, each in enumerate(materials):
            materialPart += ';' if i > 0 else ''
            if each and each != 'None':
                materialPart += each
                valid = True
            else:
                materialPart += 'None'

        if valid:
            return materialPart
        return ''

    def GetMaterialPart(self):
        materialPart = self.ConstructMaterialPart(self.materials)
        if materialPart:
            materialPart = DNAPrefixes.MATERIAL + materialPart
        return materialPart

    def GetVariantPart(self):
        if self.variant:
            return DNAPrefixes.VARIANT + self.variant
        return ''

    def GetPatternPart(self):
        if not self.pattern or self.pattern.lower() == 'none':
            return ''
        else:
            materialPart = self.ConstructMaterialPart(self.customMaterials)
            if materialPart:
                return DNAPrefixes.PATTERN + self.pattern + ';' + materialPart
            return DNAPrefixes.PATTERN + self.pattern

    def GetResPathInsertPart(self):
        if not self.resPathInsert:
            return ''
        else:
            return DNAPrefixes.RES_PATH_INSERT + self.resPathInsert

    def GetLayoutPart(self):
        if not self.layouts or len(self.layouts) == 0:
            return ''
        else:
            return DNAPrefixes.LAYOUT + ';'.join(self.layouts)

    def GetExperimentalPart(self):
        if not self.experimental:
            return ''
        return DNAPrefixes.EXPERIMENTAL + self.experimental

    def ConstructDNA(self):
        dna = self.GetHFRPart()
        parts = [self.GetMaterialPart(),
         self.GetVariantPart(),
         self.GetPatternPart(),
         self.GetResPathInsertPart(),
         self.GetLayoutPart(),
         self.GetExperimentalPart()]
        for part in parts:
            if part:
                dna += ':' + part

        return dna

    def _SplitHullIntoSubsystems(self):
        a = self.hull.split(';')
        if len(a) != 4:
            return [a[0],
             '',
             '',
             '']
        else:
            return a

    def _SetHullFromSubsystemsList(self, subsystems):
        self.hull = ''
        for each in subsystems:
            self.hull += each + ';'

        if ';;;;' in self.hull:
            self.hull = subsystems[0]
        else:
            self.hull = self.hull[:-1]

    def GetSubsystems(self):
        return self._SplitHullIntoSubsystems()

    subsystems = property(GetSubsystems, None)

    def GetSubsystem(self, index):
        ss = self._SplitHullIntoSubsystems()
        if index < len(ss):
            return ss[index]
        else:
            return ''

    def SetSubsystem(self, value, index):
        ss = self._SplitHullIntoSubsystems()
        if index < len(ss):
            ss[index] = value
            self._SetHullFromSubsystemsList(ss)
        else:
            return ''

    def __str__(self):
        return self.ConstructDNA()

    def _GetSubsystem1(self):
        return self.GetSubsystem(0)

    def _SetSubsystem1(self, value):
        self.SetSubsystem(value, 0)

    def _GetSubsystem2(self):
        return self.GetSubsystem(1)

    def _SetSubsystem2(self, value):
        self.SetSubsystem(value, 1)

    def _GetSubsystem3(self):
        return self.GetSubsystem(2)

    def _SetSubsystem3(self, value):
        self.SetSubsystem(value, 2)

    def _GetSubsystem4(self):
        return self.GetSubsystem(3)

    def _SetSubsystem4(self, value):
        self.SetSubsystem(value, 3)

    rootHull = property(_GetSubsystem1, _SetSubsystem1)
    subsystem1 = property(_GetSubsystem1, _SetSubsystem1)
    subsystem2 = property(_GetSubsystem2, _SetSubsystem2)
    subsystem3 = property(_GetSubsystem3, _SetSubsystem3)
    subsystem4 = property(_GetSubsystem4, _SetSubsystem4)


def _SanitizeParts(parts):
    result = []
    for part in parts:
        part = part.strip()
        part = part.replace('//n', '')
        result.append(part)

    return result
