#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\generalValidation.py
from evegraphics.validation.commonUtilities import Validate
from evegraphics.validation.resources import GetResource, ResourceType
from evegraphics.validation.validationFunctions import VisibilityGroupIsValid

@Validate('List[*]')
def BlueListsContainNoDuplicates(context, genericList):
    reported = set()
    if getattr(genericList, '__bluetype__') == 'blue.List':
        for each in genericList:
            if each not in reported and len([ x for x in genericList if x is each ]) != 1:
                reported.add(each)
                context.Error(each, 'duplicate item %s in the list' % (getattr(each, 'name', '') or each))


@Validate('*')
def NoDeprecatedTypes(context, node):
    typeInfo = getattr(node, 'TypeInfo', None)
    if not typeInfo:
        return
    docstring = typeInfo()[0]['description']
    if ':jessica-deprecated:' in docstring:
        context.Error(node, 'is of deprecated type %s' % type(node).__name__)


@Validate('*')
def ValidateVisibilityGroup(context, node):
    visibilityGroup = getattr(node, 'visibilityGroup', None)
    if not visibilityGroup:
        return
    if not VisibilityGroupIsValid(context, visibilityGroup):
        context.Error(node, 'Visibility "%s" does not exist' % visibilityGroup)
