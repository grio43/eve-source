#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\objectives\base\objective.py
from carbonui.primitives.sprite import Sprite
from localization import GetByMessageID
from missions.client.ui.missionObjectiveData import AgentMissionObjective
from storylines.client.objectives.base.bookmark import create_bookmark

class StorylineObjective(AgentMissionObjective):
    OBJECTIVE_ICON_PADDING = 4

    def __init__(self, objective_id, title, text, title_icon = None, icon = None, icon_type_id = None, icon_item_id = None, dungeon_id = None, objective_values = None):
        self.objective_id = objective_id
        self.title = GetByMessageID(title)
        self.title_icon = title_icon
        self.text = GetByMessageID(text, **(objective_values or {}))
        self.icon = icon
        self.icon_type_id = icon_type_id
        self.icon_item_id = icon_item_id
        self.dungeon_id = dungeon_id
        self.warp_action = None
        super(StorylineObjective, self).__init__(iconItemID=self.icon_item_id, iconTypeID=self.icon_type_id, missionHint=self.text, header=self.title, activeIcon=self.title_icon)

    def Update(self, is_active = None, warp_action = None):
        self._SetWarpAction(warp_action)
        self._SetActiveState(is_active)

    def _SetActiveState(self, is_active):
        if is_active is None:
            return
        if is_active:
            self.SetActive()
        else:
            self.SetInactive()

    def _SetWarpAction(self, warp_action):
        self.warp_action = warp_action
        location_id = session.solarsystemid2 if self.warp_action else None
        self.bookmark = create_bookmark(location_id)

    def _Warp(self):
        if self.warp_action and callable(self.warp_action):
            self.warp_action()
            return
        super(StorylineObjective, self)._Warp()

    def HasIcon(self):
        return self.icon or self.icon_type_id

    def BuildIcon(self, name, parent, align, state, opacity, width, height):
        if self.icon:
            Sprite(name=name, parent=parent, align=align, state=state, opacity=opacity, width=width - 2 * self.OBJECTIVE_ICON_PADDING, height=height - 2 * self.OBJECTIVE_ICON_PADDING, texturePath=self.icon)
        else:
            super(StorylineObjective, self).BuildIcon(name, parent, align, state, opacity, width, height)

    def IsInActiveMissionDungeon(self):
        return self.dungeon_id and self.dungeon_id == sm.GetService('dungeonTracking').GetCurrentDungeonID()

    def GetLocationButtonName(self):
        return 'ObjectiveLocationButton'
