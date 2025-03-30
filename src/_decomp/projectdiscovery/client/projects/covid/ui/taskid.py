#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\taskid.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import Label
from projectdiscovery.client.projects.covid.ui.containerwithcorners import ContainerWithCorners
from projectdiscovery.client.projects.covid.ui.devpopup import FixTaskIdDevPopup
FONTSIZE = 10
WIDTH = 140
HEIGHT = 20
COLOR_BACKGROUND = (0.9, 0.9, 1.0, 0.2)
PADDING_CONTAINER_TO_LABEL = 24
ICON_SIZE = 18
ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/recycleButtonOver.png'
PADDING_TOP = 10

class TaskID(Container):
    default_width = WIDTH
    default_height = HEIGHT
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        super(TaskID, self).ApplyAttributes(attributes)
        self._build_task_id_label()

    def _build_task_id_label(self):
        self.task_id_label_container = ContainerWithCorners(name='task_id_label_container', parent=self, align=uiconst.TOTOP, height=HEIGHT, bgColor=COLOR_BACKGROUND)
        self.task_id_label = Label(name='task_id_label', parent=self.task_id_label_container, align=uiconst.CENTERLEFT, fontsize=FONTSIZE, padLeft=PADDING_CONTAINER_TO_LABEL, width=WIDTH - 2 * PADDING_CONTAINER_TO_LABEL)
        fix_task_id_icon = Sprite(name='fix_task_id_icon', parent=self.task_id_label_container, align=uiconst.TORIGHT_NOPUSH, padLeft=PADDING_CONTAINER_TO_LABEL, width=ICON_SIZE, height=ICON_SIZE, texturePath=ICON_TEXTURE_PATH, hint='Fix a taskID')
        fix_task_id_icon.OnClick = lambda *args: self._fix_task_id()

    def _fix_task_id(self):
        FixTaskIdDevPopup.Open()

    def load_task_id(self, task_id):
        self.task_id_label.SetText('TaskID: %s' % task_id)
