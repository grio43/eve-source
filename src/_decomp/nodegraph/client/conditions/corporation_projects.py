#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\corporation_projects.py
from eve.common.script.sys.idCheckers import IsPlayerCorporation
from nodegraph.client.conditions.base import Condition

class HasActiveCorporationProjects(Condition):
    atom_id = 618

    @staticmethod
    def _has_any_active_corporation_project():
        from corporation.client.goals.goalsController import CorpGoalsController
        goals = CorpGoalsController.get_instance()
        active_goals = goals.get_active_goals()
        return len(active_goals) > 0

    def validate(self, **kwargs):
        if not IsPlayerCorporation(session.corpid):
            return False
        return self._has_any_active_corporation_project()


class IsAllowedToCreateCorporationProjects(Condition):
    atom_id = 620

    def validate(self, **kwargs):
        from corporation.client.goals import goalsUtil
        return goalsUtil.CanAuthorGoals()
