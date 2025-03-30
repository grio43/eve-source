#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\sofFactionValidation.py
from evegraphics.validation.commonUtilities import Validate

@Validate('EveSOFDataFaction')
def ValidatePlanesetGroupIDs(context, faction):
    indices = []
    for item in faction.planeSets:
        try:
            indices.append(item.groupIndex)
        except AttributeError:
            context.Error(item, 'AttributeError: Planeset is missing the groupIndex attribute.')

    duplicates = set([ x for x in indices if indices.count(x) > 1 ])
    if duplicates:
        context.Error(faction, 'Multiple PlaneSets with the same groupIndex: ' + str(list(duplicates)))
