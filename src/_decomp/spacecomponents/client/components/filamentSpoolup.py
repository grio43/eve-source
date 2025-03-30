#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\filamentSpoolup.py
from carbonui.control.contextMenu.menuData import MenuData
from localization import GetByLabel
from randomJump import RandomJumpError
from randomJump.client.clientRandomJumpValidator import ClientRandomJumpValidator
from randomJump.error import get_short_error_path_for_self
from spacecomponents import Component

class FilamentSpoolup(Component):

    def GetGMMenu(self):
        menu_data = MenuData()
        menu_data.AddEntry(text='Get Valid Ships', func=self.GMGetValidShips)
        return menu_data

    def GMGetValidShips(self):
        sm.GetService('slash').SlashCmd(u'/spacecomponent filamentSpoolup %s getvalidships' % self.itemID)


def GetErrorForRandomJumpTraceGate():
    validator = ClientRandomJumpValidator()
    try:
        validator.validate_jump()
    except RandomJumpError as e:
        errors = e.errors
        for errorLine in errors:
            errorCode, errorArgs = errorLine
            path = get_short_error_path_for_self(errorCode, *errorArgs)
            return path
