#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\icon\associated.py
import localization
import signals
import threadutils
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from expertSystems.client import texture
from expertSystems.client.service import ExpertSystemService
from expertSystems.client.util import expert_system_benefits_player
from expertSystems.data import get_associated_expert_systems

class State(object):
    hidden = 0
    available = 1
    active = 2


class Controller(object):
    __notifyevents__ = ('OnExpertSystemsUpdated_Local', 'OnSkillsChanged')

    def __init__(self, type_id, state = State.hidden):
        self.type_id = type_id
        self.on_state_changed = signals.Signal()
        self._state = state
        self.update_state()
        ServiceManager.Instance().RegisterNotify(self)

    @property
    def state(self):
        return self._state

    def close(self):
        ServiceManager.Instance().UnregisterNotify(self)
        self.on_state_changed.clear()

    @threadutils.highlander_threaded
    def update_state(self):
        new_state = self._get_new_state()
        if new_state != self._state:
            self._state = new_state
            self.on_state_changed()

    def _get_new_state(self):
        expert_systems = get_associated_expert_systems(self.type_id)
        if not any((expert_system_benefits_player(expert_system.type_id) for expert_system in expert_systems)):
            return State.hidden
        my_expert_systems = ExpertSystemService.instance().GetMyExpertSystems()
        if any((expert_system.type_id in my_expert_systems for expert_system in expert_systems)):
            return State.active
        elif expert_systems:
            return State.available
        else:
            return State.hidden

    def OnExpertSystemsUpdated_Local(self):
        self.update_state()

    def OnSkillsChanged(self, skill_info):
        self.update_state()


class AssociatedExpertSystemIcon(Container):
    default_state = uiconst.UI_NORMAL

    def __init__(self, type_id, icon_size = 24, on_click = None, **kwargs):
        self.controller = Controller(type_id)
        self.icon_size = icon_size
        self._on_click = on_click
        self.icon = None
        kwargs.setdefault('width', self.icon_size)
        kwargs.setdefault('height', self.icon_size)
        super(AssociatedExpertSystemIcon, self).__init__(**kwargs)
        self.layout()
        self.update()
        self.controller.on_state_changed.connect(self.update)

    def layout(self):
        self.icon = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self.icon_size, height=self.icon_size)

    def update(self):
        if self.controller.state == State.hidden:
            self.display = False
        elif self.controller.state == State.available:
            self.display = True
            self.icon.SetRGB(1.0, 1.0, 1.0)
            self.icon.SetTexturePath(texture.logo_inactive_24)
        elif self.controller.state == State.active:
            self.display = True
            self.icon.SetTexturePath(texture.badge_24)
            self.icon.SetRGB(1.0, 1.0, 1.0)

    def Close(self):
        self.controller.close()
        super(AssociatedExpertSystemIcon, self).Close()

    def GetHint(self):
        if self.controller.state == State.available:
            return localization.GetByLabel('UI/ExpertSystem/AssociatedSystemAvailable')
        if self.controller.state == State.active:
            return localization.GetByLabel('UI/ExpertSystem/AssociatedSystemActive')

    def OnClick(self, *args):
        if self._on_click:
            self._on_click()
