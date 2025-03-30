#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\platformtools\common\dnahelper\__init__.py
from ._dnaparts import DNAParts, DNAPartNames, DNAElementKinds, HFR_PARTS, MATERIAL_PARTS, PATTERN_PARTS, PATTERN_MATERIAL_PARTS, ALL_PATTERN_PARTS, OTHER_PARTS, LAYOUT_PARTS, DNA_DATA_PARTS, DNA_ALL_PARTS, LAYOUT_DESCRIPTOR_PARTS

def IsDNAValid(dna):
    try:
        if not dna:
            return False
        dnaParts = DNAParts()
        dnaParts.SetFromDNA(dna)
        return bool(dnaParts.hull) and bool(dnaParts.faction) and bool(dnaParts.race)
    except Exception:
        return False


def DnaToDescriptor(dna):
    return DnaToDescriptor(DNAParts(dna))


def DnaPartsToDescriptor(dnaParts):
    try:
        import trinity
    except:
        raise ImportError('This functionality requires trinity')

    descriptor = trinity.EveSOFDNADescriptor()
    descriptor.hull = dnaParts.hull
    descriptor.faction = dnaParts.faction
    descriptor.race = dnaParts.race
    return descriptor
