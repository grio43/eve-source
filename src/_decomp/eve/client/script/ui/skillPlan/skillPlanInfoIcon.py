#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanInfoIcon.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.infoIcon import InfoIcon
from carbonui import uiconst

class SkillPlanInfoIcon(Container):
    default_width = 20
    default_height = 20
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(SkillPlanInfoIcon, self).ApplyAttributes(attributes)
        InfoIcon(parent=self, name='showInfo', align=uiconst.CENTER, pos=(0, 0, 34, 34), texturePath='res:/UI/Texture/Classes/SkillPlan/infoIcon.png', state=uiconst.UI_DISABLED)
