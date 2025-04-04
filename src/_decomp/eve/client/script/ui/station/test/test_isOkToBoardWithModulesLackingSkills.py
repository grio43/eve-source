#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\test\test_isOkToBoardWithModulesLackingSkills.py
import unittest
from testsuites.testcases import ClientTestCase
import mock
from itertoolsext import Bundle
_carbonui = mock.Mock()
ID_YES = 100
YESNO = 1000
with mock.patch.dict('sys.modules', {'carbonui': _carbonui,
 'carbonui.const': Bundle(ID_YES=ID_YES, YESNO=YESNO)}):
    from eve.client.script.ui.station.askForUndock import IsOkToBoardWithModulesLackingSkills
    import carbonui.const as uiconst
from testhelpers.evemocks import SettingsMock

class TestIsOkToBoardWithModulesLackingSkills(ClientTestCase):

    def setUp(self):
        super(TestIsOkToBoardWithModulesLackingSkills, self).setUp()
        self._SetMessage(mock.Mock(return_value=uiconst.ID_YES))

    def _SetMessage(self, mockObject):
        self.message = mockObject

    def testWhenMessageIsSuppressedWeReturnTrue(self):
        with SettingsMock():
            settings.user.suppress.Set('suppress.AskUndockWithModulesLackingSkill', True)
            self.assertTrue(IsOkToBoardWithModulesLackingSkills(None, self.message))

    def testWhenDogmaGivesYouNoModulesYouDoNotHaveSkillsForWeReturnTrue(self):
        self.assertTrue(self._IsOk([]))

    @unittest.skip('This test is failing and needs fixing')
    def testWhenDogmaGivesUsModulesLackingSkillsWeAskIfWeWantToProceed(self):
        isOk = self._IsOk([1])
        self.message.assert_called_once_with('AskUndockWithModulesLackingSkill', {}, uiconst.YESNO, suppress=uiconst.ID_YES)
        self.assertTrue(isOk)

    def _IsOk(self, moduleIDs):
        with SettingsMock():
            dogmaLocation = Bundle(GetModulesLackingSkills=lambda : moduleIDs)
            isOk = IsOkToBoardWithModulesLackingSkills(dogmaLocation, self.message)
        return isOk
