#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\skill.py
from .base import Event

class AvailableSkillPointsChanged(Event):
    atom_id = 142
    __notifyevents__ = ['OnFreeSkillPointsChanged_Local']

    def OnFreeSkillPointsChanged_Local(self):
        skill_points = sm.GetService('skills').GetFreeSkillPoints()
        self.invoke(skill_points=skill_points)


class SkillsChanged(Event):
    atom_id = 135
    __notifyevents__ = ['OnSkillsChanged']

    def OnSkillsChanged(self, *args, **kwargs):
        self.invoke()


class SkillPointsInjected(Event):
    atom_id = 143
    __notifyevents__ = ['OnSkillPointsInjected_Local']

    def OnSkillPointsInjected_Local(self, quantity):
        self.invoke(quantity=quantity)


class SkillPointsUsed(Event):
    atom_id = 153
    __notifyevents__ = ['OnFreeSkillPointsChanged_Local']

    def __init__(self, **kwargs):
        super(SkillPointsUsed, self).__init__(**kwargs)
        self._compared_skill_points = 0

    def start(self):
        super(SkillPointsUsed, self).start()
        self._compared_skill_points = sm.GetService('skills').GetFreeSkillPoints()

    def OnFreeSkillPointsChanged_Local(self):
        skill_points = sm.GetService('skills').GetFreeSkillPoints()
        if skill_points < self._compared_skill_points:
            self.invoke(skill_points=skill_points, skill_points_used=self._compared_skill_points - skill_points)
        self._compared_skill_points = skill_points


class SkillQueueChanged(Event):
    atom_id = 136
    __notifyevents__ = ['OnSkillQueueModified']

    def OnSkillQueueModified(self, *args, **kwargs):
        self.invoke()


class SkillPlanTrainingStarted(Event):
    atom_id = 412
    __notifyevents__ = ['OnSkillPlanTrainingStarted']

    def OnSkillPlanTrainingStarted(self, skill_plan_id, skill_plan_name):
        self.invoke(skill_plan_id=skill_plan_id, skill_plan_name=skill_plan_name)


class SkillPlanPageChanged(Event):
    atom_id = 277
    __notifyevents__ = ['OnSelectedSkillPlanChanged']

    def OnSelectedSkillPlanChanged(self, *args, **kwargs):
        self.invoke()


class SkillPlanCareerPathSelected(Event):
    atom_id = 396
    __notifyevents__ = ['OnSkillPlansCareerPathTabChanged']

    def OnSkillPlansCareerPathTabChanged(self, career_path_id):
        self.invoke(career_path_id=career_path_id)


class SkillPlanFactionSelected(Event):
    atom_id = 400
    __notifyevents__ = ['OnSkillPlanFactionTabChanged']

    def OnSkillPlanFactionTabChanged(self, faction_id):
        self.invoke(faction_id=faction_id)


class SkillMissingTooltipShown(Event):
    atom_id = 366
    __notifyevents__ = ['OnSkillMissingTooltipShown']

    def OnSkillMissingTooltipShown(self, *args, **kwargs):
        self.invoke()


class SkillMissingTooltipClosed(Event):
    atom_id = 367
    __notifyevents__ = ['OnSkillMissingTooltipClosed']

    def OnSkillMissingTooltipClosed(self, *args, **kwargs):
        self.invoke()


class SkillPlanContentsToggled(Event):
    atom_id = 442

    def _register(self):
        from eve.client.script.ui.skillPlan import skillPlanUISignals
        skillPlanUISignals.on_skill_collapse_changing.connect(self._on_skill_collapse_changing)

    def _unregister(self):
        from eve.client.script.ui.skillPlan import skillPlanUISignals
        skillPlanUISignals.on_skill_collapse_changing.disconnect(self._on_skill_collapse_changing)

    def _on_skill_collapse_changing(self, *args, **kwargs):
        self.invoke()
