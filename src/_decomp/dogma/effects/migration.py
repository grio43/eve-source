#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\effects\migration.py
import yaml
import dogma.data as dogma_data
from fsd import AbsJoin, GetBranchRoot
changeID = 133610
_userid = 1000012

def check_all_effects():
    effectCompiler = sm.GetService('effectCompiler')
    res = []
    for effect in dogma_data.get_all_effects():
        effectID = effect.effectID
        if not effect.modifierInfo and not effectCompiler.IsEffectPythonOverridden(effectID):
            res.append(effectID)

    print res


def firstChange():
    db = sm.GetService('DB2')
    bsdService = sm.GetService('BSD')
    x = {641: 54,
     649: 55,
     658: 53,
     664: 74}
    for expressionID, expressionGroupID in x.items():
        sqlRes = db.SQL('select revisionID from dogma.expressions where expressionID={}'.format(expressionID))
        revisionID = next(iter(sqlRes)).revisionID
        bsdService.RevisionEdit(_userid, changeID, revisionID, expressionGroupID=54)

    sqlRes = db.SQL('select revisionID from dogma.expressions where expressionID=6742')
    revisionID = next(iter(sqlRes)).revisionID
    bsdService.RevisionEdit(_userid, changeID, revisionID, arg2=3488)


def get_required_skill_string(modifierInfo):
    res = '-  domain: {}\n'.format(modifierInfo['domain'])
    res += '   func: {}\n'.format(modifierInfo['func'])
    res += '   modifiedAttributeID: {}\n'.format(modifierInfo['modifiedAttributeID'])
    res += '   modifyingAttributeID: {}\n'.format(modifierInfo['modifyingAttributeID'])
    res += '   operator: {}\n'.format(modifierInfo['operator'])
    res += '   skillTypeID: {}'.format(modifierInfo['skillTypeID'])
    return res


def get_item_modifier_string(modifierInfo):
    res = '-  domain: {}\n'.format(modifierInfo['domain'])
    res += '   func: {}\n'.format(modifierInfo['func'])
    res += '   modifiedAttributeID: {}\n'.format(modifierInfo['modifiedAttributeID'])
    res += '   modifyingAttributeID: {}\n'.format(modifierInfo['modifyingAttributeID'])
    res += '   operator: {}'.format(modifierInfo['operator'])
    return res


def get_location_group_string(modifierInfo):
    res = '-  domain: {}\n'.format(modifierInfo['domain'])
    res += '   func: {}\n'.format(modifierInfo['func'])
    res += '   groupID: {}\n'.format(modifierInfo['groupID'])
    res += '   modifiedAttributeID: {}\n'.format(modifierInfo['modifiedAttributeID'])
    res += '   modifyingAttributeID: {}\n'.format(modifierInfo['modifyingAttributeID'])
    res += '   operator: {}'.format(modifierInfo['operator'])
    return res


def get_location_modifier(modifierInfo):
    res = '-  domain: {}\n'.format(modifierInfo['domain'])
    res += '   func: {}\n'.format(modifierInfo['func'])
    res += '   modifiedAttributeID: {}\n'.format(modifierInfo['modifiedAttributeID'])
    res += '   modifyingAttributeID: {}\n'.format(modifierInfo['modifyingAttributeID'])
    res += '   operator: {}'.format(modifierInfo['operator'])
    return res


def secondChange():
    path = AbsJoin(GetBranchRoot(), 'packages', 'dogma', 'effects', 'modifier_data.yaml')
    db = sm.GetService('DB2')
    bsdService = sm.GetService('BSD')
    with open(path, 'r') as f:
        modifier_info_by_effect = yaml.load(f)
        print 'begin'
        for effectID, modifierInfos in modifier_info_by_effect.items():
            res = ''
            sqlRes = db.SQL('select * from dogma.effects where effectID={}'.format(effectID))
            revisionID = next(iter(sqlRes)).revisionID
            for modifierInfo in modifierInfos:
                if not res == '':
                    res += '\n'
                func = modifierInfo['func']
                if func == 'LocationRequiredSkillModifier' or func == 'OwnerRequiredSkillModifier':
                    x = get_required_skill_string(modifierInfo)
                elif func == 'ItemModifier' or func == 'LocationModifier':
                    x = get_item_modifier_string(modifierInfo)
                elif func == 'LocationGroupModifier':
                    x = get_location_group_string(modifierInfo)
                else:
                    raise RuntimeError('func name ({}) does not match any of the modifier functions, effectID: {}'.format(modifierInfo['func'], effectID))
                res += x

            bsdService.RevisionEdit(_userid, changeID, revisionID, modifierInfo=res)

        print 'done'
