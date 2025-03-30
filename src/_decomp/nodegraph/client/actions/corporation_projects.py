#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\corporation_projects.py
from eve.common.script.sys.idCheckers import IsPlayerCorporation
from .base import Action

class BaseCreateCorporationProject(Action):

    def __init__(self, name = None, description = None, desired_progress = None, **kwargs):
        super(BaseCreateCorporationProject, self).__init__(**kwargs)
        self.name = self.get_atom_parameter_value('name', name)
        self.description = self.get_atom_parameter_value('description', description)
        self.desired_progress = self.get_atom_parameter_value('desired_progress', desired_progress)

    def start(self, **kwargs):
        super(BaseCreateCorporationProject, self).start(**kwargs)
        if IsPlayerCorporation(session.corpid):
            self._create_project()

    def _create_project(self):
        from corporation.client.goals.goalsController import CorpGoalsController
        goals = CorpGoalsController.get_instance()
        goals.create_goal(name=self.name, description=self.description, desired_progress=self.desired_progress, method_type=self._get_contribution_method(), contribution_fields=self._get_contribution_parameters(), career_path=self._get_career_path(), payment_per_contribution=None)

    def _get_contribution_method(self):
        raise NotImplementedError('Must implement Contribution Method definition in derived class')

    def _get_contribution_parameters(self):
        raise NotImplementedError('Must implement Contribution Method parameters in derived class')

    def _get_career_path(self):
        raise NotImplementedError('Must implement Career Path choice in derived class')

    @classmethod
    def get_subtitle(cls, name = None, description = None, desired_progress = None, method_type = None, **kwargs):
        return name


class CreateManufactureProject(BaseCreateCorporationProject):
    atom_id = 617

    def __init__(self, name = None, description = None, desired_progress = None, item_type = None, **kwargs):
        super(CreateManufactureProject, self).__init__(name, description, desired_progress, **kwargs)
        self.item_type = self.get_atom_parameter_value('item_type', item_type)

    def _get_contribution_method(self):
        from goals.common.goalConst import ContributionMethodTypes
        return ContributionMethodTypes.MANUFACTURE_ITEM

    def _get_contribution_parameters(self):
        return {'item_type': self.item_type}

    def _get_career_path(self):
        from characterdata.careerpathconst import career_path_industrialist
        return career_path_industrialist
