#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\sofGenericValidation.py
from evegraphics.validation.commonUtilities import Validate
import re

@Validate('EveSOFDataGeneric')
def ValidateVisibilityGroups(context, genericData):
    groupnames = [ group.name.lower() for group in genericData.visibilityGroups ]
    duplicateNames = []
    for group in genericData.visibilityGroups:
        if groupnames.count(group.name.lower()) > 1:
            duplicateNames.append(group.name)
        if not re.search('^[0-9_a-z\\-]*$', group.name):
            context.Error(group, 'Visibility Group "%s" is not correctly named (numbers, lower case numbers, - and _ acceptable)' % group.name)

    if len(duplicateNames) > 0:
        context.Error(genericData, 'Duplicate visibility groups: (%s)' % ', '.join(duplicateNames))
