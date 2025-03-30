#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\panels\auraCareerAssistancePanel.py
import localization
from carbonui import TextAlign, uiconst, ButtonFrameType, ButtonVariant
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from characterdata.careerpath import get_career_path_name_id
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium, EveCaptionSmall
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.shared.careerPortal.panels.basePanel import BasePanel
from eve.client.script.ui.shared.careerPortal.util import OpenSkillPlanWindow
from eveui import Sprite
INFO_ICON_SIZE = 16
TYPE_ICON_SIZE = 32
DEFAULT_PADDING = 4

class AuraCareerAssistancePanel(BasePanel):
    default_name = 'AuraAssistancePanel'
    default_alignMode = uiconst.TOTOP

    def __init__(self, *args, **kwargs):
        super(AuraCareerAssistancePanel, self).__init__(*args, **kwargs)
        self.ConstructLayout()
        self.auraBadge = Sprite(name='auraBadge', texturePath='res:/UI/Texture/classes/careerPortal/aura/AURABADGE.png', align=uiconst.TOPRIGHT, parent=self, width=careerConst.AURA_BADGE_WIDTH, height=careerConst.AURA_BADGE_HEIGHT)
        careerConst.SELECTED_CAREER_PATH_SETTING.on_change.connect(self.LoadCareer)
        self.LoadCareer(careerConst.SELECTED_CAREER_PATH_SETTING.get())

    def Close(self):
        careerConst.SELECTED_CAREER_PATH_SETTING.on_change.disconnect(self.LoadCareer)
        super(AuraCareerAssistancePanel, self).Close()

    def ConstructLayout(self):
        self._ConstructTitle()
        self._ConstructCareerAgentMissionDescription()
        Line(parent=self, align=uiconst.TOTOP, top=INFO_ICON_SIZE)
        self._ConstructSkillPlanSection()

    def _ConstructSkillPlanSection(self):
        EveCaptionSmall(name='skillPlansTitle', parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CareerPortal/AuraAssistanceSkillPlansTitle'), bold=True, top=INFO_ICON_SIZE)
        EveLabelMedium(name='skillPlansDescription', parent=self, align=uiconst.TOTOP, textAlign=TextAlign.LEFT, top=8, text=localization.GetByLabel('UI/CareerPortal/AuraAssistanceSkillPlansText'))
        self.openSkillPlanBtn = Button(parent=self, align=uiconst.TOTOP, top=INFO_ICON_SIZE, texturePath='res:/UI/Texture/classes/careerPortal/aura_icon_skillplans.png', variant=ButtonVariant.GHOST, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT)

    def _ConstructCareerAgentMissionDescription(self):
        self.careerAgentMissionContainer = ContainerAutoSize(name='careerAgentMissionContainer', parent=self, align=uiconst.TOTOP, top=INFO_ICON_SIZE)
        EveCaptionSmall(name='careerAgentMissionTitle', parent=self.careerAgentMissionContainer, align=uiconst.TOTOP, textAlign=TextAlign.LEFT, text=localization.GetByLabel('UI/CareerPortal/AuraAssistanceCareerAgentMissionsTitle'), bold=True)
        self.careerAgentMissionDescription = EveLabelMedium(name='careerAgentMissionDescription', parent=self.careerAgentMissionContainer, align=uiconst.TOTOP, textAlign=TextAlign.LEFT, top=8)

    def _ConstructTitle(self):
        EveCaptionLarge(name='title', parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CareerPortal/AuraAssistancePanelTitle'), color=self.color, bold=True)

    def LoadCareer(self, careerID):
        if not careerID:
            return
        careerPathName = localization.GetByMessageID(get_career_path_name_id(careerID))
        self.careerAgentMissionDescription.text = localization.GetByLabel('UI/CareerPortal/AuraAssistanceCareerAgentsText', careerPathName=careerPathName)
        self.openSkillPlanBtn.SetLabel(localization.GetByLabel('UI/CareerPortal/AuraAssistanceOpenSkillPlanButton', careerPathName=careerPathName))
        self.openSkillPlanBtn.func = lambda x: OpenSkillPlanWindow(careerID)
