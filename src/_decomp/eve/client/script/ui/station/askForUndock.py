#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\askForUndock.py
import carbonui.const as uiconst

def IsOkToBoardWithModulesLackingSkills(dogmaLocation, Message):
    if settings.user.suppress.Get('suppress.AskUndockWithModulesLackingSkill', None) is None:
        try:
            if dogmaLocation.GetModulesLackingSkills():
                if Message('AskUndockWithModulesLackingSkill', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return False
        except KeyError:
            return False

    return True
