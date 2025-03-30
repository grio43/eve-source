#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\dbrow.py
import dogma.data
import telemetry
from carbon.common.script.util.timerstuff import ClockThis
from eve.common.script.sys import eveCfg
from eve.common.lib import appConst as const

def LookupConstValue(name, default = '.exception'):
    return ClockThis('SKITMIX::LookupConstValue', _LookupConstValue, name, default, False)


def ConstValueExists(name):
    return ClockThis('SKITMIX::LookupConstValue', _LookupConstValue, name, '', True)


constMap = {}

@telemetry.ZONE_FUNCTION
def _LookupConstValue(name, default, justChecking):
    if not constMap:

        @telemetry.ZONE_FUNCTION
        def MakeReverseConstValues(constMap):
            sets = [[[],
              'category',
              '_categoryName',
              'categoryID'],
             [[],
              'group',
              '_groupName',
              'groupID'],
             [[],
              'metaGroup',
              '_metaGroupName',
              'metaGroupID'],
             [[],
              'type',
              '_typeName',
              'typeID'],
             [dogma.data.get_all_attributes(),
              'attribute',
              'attributeName',
              'attributeID'],
             [dogma.data.get_all_effects(),
              'effect',
              'effectName',
              'effectID']]
            for rs, prefix, colName, constID in sets:
                for row in rs:
                    constMap[eveCfg.MakeConstantName(getattr(row, colName, ''), prefix)] = getattr(row, constID, 0)

        ClockThis('^boot::MakeReverseConstValues', MakeReverseConstValues, constMap)
    if justChecking:
        return name in constMap or name in const.__dict__
    if name in constMap:
        return constMap[name]
    if name in const.__dict__:
        return const.__dict__[name]
    if default != '.exception':
        return default
    raise AttributeError("There's no legacy const value called '%s'" % name)
