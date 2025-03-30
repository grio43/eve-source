#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\qa.py
import logging
from carbon.common.script.sys.serviceConst import ROLE_QA
from eveexceptions import UserError
from nodegraph.client.util import wait_for_session
from nodegraph.client.actions.base import Action

class QAAction(Action):
    atom_id = None

    def start(self, **kwargs):
        super(QAAction, self).start(**kwargs)
        if not bool(session.role & ROLE_QA):
            raise UserError("You can't execute this action!")
        try:
            self._execute(**kwargs)
        except Exception as e:
            logging.error('QA Action failed: %s', e)

    def _execute(self, **kwargs):
        pass


class SlashCommand(QAAction):
    atom_id = 134

    def __init__(self, slash_command = '', wait_for_session = None, **kwargs):
        super(SlashCommand, self).__init__(**kwargs)
        self.slash_command = slash_command
        self.wait_for_session = self.get_atom_parameter_value('wait_for_session', wait_for_session)

    def _execute(self, **kwargs):
        if self.wait_for_session:
            wait_for_session()
        if sm.GetService('publicQaToolsClient').CommandAllowed(self.slash_command):
            sm.GetService('publicQaToolsClient').SlashCmd(self.slash_command)
        else:
            sm.GetService('slash').SlashCmd(self.slash_command)

    @classmethod
    def get_subtitle(cls, slash_command = '', wait_for_session = None, **kwargs):
        return u'{} {}'.format(slash_command, '(Wait for session)' if cls.get_atom_parameter_value('wait_for_session', wait_for_session) else '')
