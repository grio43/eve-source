#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\nodditestrunner.py
import uuid
import blue
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from nodditests.client.arguments import Arguments
from nodditests.client.reporting.teamcityreporter import TeamCityReporter
from nodditests.client.runner import Runner

class NoddiTestRunner(Service):
    __guid__ = 'svc.noddiTestRunner'

    def Run(self, *args, **kwargs):
        super(NoddiTestRunner, self).Run(*args, **kwargs)
        self.runner = None
        arguments = Arguments(blue.pyos.GetArg()[1:])
        if arguments.has_argument('/noddi_test'):
            if arguments.has_argument('/test_report_folder'):
                report_folder = arguments.get_string_value('/test_report_folder')
            else:
                report_folder = '.'
            reporter = TeamCityReporter(str(uuid.uuid4()), report_folder)
            self.runner = Runner(arguments, self.SelectCharacter, self.RunNodeGraph, reporter)
            sm.RegisterNotify(self.runner)

    @property
    def node_graph(self):
        return sm.GetService('node_graph')

    def SelectCharacter(self, characterID):
        cs = uicore.layer.charsel
        cs.TryEnterGame(int(characterID), secondChoiceID=None, skipTutorial=True)

    def RunNodeGraph(self, testCase):
        return self.node_graph.StartClientNodeGraph(testCase, blackboard_parameters=[])
