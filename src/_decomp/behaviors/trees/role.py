#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\role.py
from behaviors.actions.blackboards import BlackboardSetMessageToStringValueAction
from behaviors.actions.blackboards import BlackboardSetMessageToBooleanValueAction
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.composites import Sequence
from behaviors.conditions.blackboards import IsBlackboardValueNone
from brennivin.itertoolsext import Bundle
ROLE_ADDRESS = (ScopeTypes.Item, 'ROLE')
GROUP_MEMBER_ROLE_ASSIGNED_ADDRESS = (ScopeTypes.EntityGroup, 'GROUP_MEMBER_ROLE_ASSIGNED')

def CreateRegisterEntityRole(role):
    return Sequence(Bundle(name='Registering Entity Role')).AddSubTask(IsBlackboardValueNone(Bundle(valueAddress=ROLE_ADDRESS))).AddSubTask(BlackboardSetMessageToStringValueAction(Bundle(name='Remember my role', messageAddress=ROLE_ADDRESS, value=role))).AddSubTask(BlackboardSetMessageToBooleanValueAction(Bundle(name='Notify group on role', messageAddress=GROUP_MEMBER_ROLE_ASSIGNED_ADDRESS, value=True)))
