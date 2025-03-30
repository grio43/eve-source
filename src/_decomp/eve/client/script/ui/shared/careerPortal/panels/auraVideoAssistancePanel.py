#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\panels\auraVideoAssistancePanel.py
import localization
from carbonui import ButtonVariant, uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from careergoals.client.career_goal_svc import get_career_goals_svc
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveCaptionSmall, EveLabelMedium
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.panels.basePanel import BasePanel
from eveui import Sprite
from fsdBuiltData.client.agency.helpVideoFSDLoader import AgencyHelpVideosFSDLoader
from localization import GetByMessageID

class AuraVideoAssistancePanel(BasePanel):
    default_name = 'AuraAssistancePanel'
    default_alignMode = uiconst.TOTOP

    def __init__(self, *args, **kwargs):
        super(AuraVideoAssistancePanel, self).__init__(*args, **kwargs)
        self.ConstructLayout()
        self.auraBadge = Sprite(name='auraBadge', texturePath='res:/UI/Texture/classes/careerPortal/aura/AURABADGE.png', align=uiconst.TOPRIGHT, parent=self, width=careerConst.AURA_BADGE_WIDTH, height=careerConst.AURA_BADGE_HEIGHT)
        careerConst.SELECTED_ACTIVITY_SETTING.on_change.connect(self.LoadActivity)
        self.LoadActivity(careerConst.SELECTED_ACTIVITY_SETTING.get())

    def Close(self):
        careerConst.SELECTED_ACTIVITY_SETTING.on_change.disconnect(self.LoadActivity)
        super(AuraVideoAssistancePanel, self).Close()

    def ConstructLayout(self):
        self._ConstructTitle()
        EveCaptionSmall(name='helpVideosTitle', parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CareerPortal/HelpVideos'), bold=True, top=16)
        self.helpVideosContainer = ContainerAutoSize(name='helpVideoContainer', parent=self, align=uiconst.TOTOP)

    def _ConstructTitle(self):
        EveCaptionLarge(name='title', parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CareerPortal/AuraAssistancePanelTitle'), color=self.color, bold=True)

    def LoadActivity(self, activityID):
        self.helpVideosContainer.Flush()
        selectedCareer = careerConst.SELECTED_CAREER_PATH_SETTING.get()
        goalsInGroup = get_career_goals_svc().get_goal_data_controller().get_goals_in_group(selectedCareer, activityID)
        distinctVideos = set((int(goal.definition.video_id) for goal in goalsInGroup if goal.definition.has_video_id()))
        if not distinctVideos:
            EveLabelMedium(parent=self.helpVideosContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CareerPortal/NoVideosAvailable'), top=8)
        else:
            for videoID in distinctVideos:
                if not videoID:
                    continue
                video = AgencyHelpVideosFSDLoader.GetByID(videoID)
                if not video:
                    continue
                Button(parent=Container(parent=self.helpVideosContainer, align=uiconst.TOTOP, height=32, top=8), name='videoButton', align=uiconst.CENTERLEFT, label=GetByMessageID(video.nameID), texturePath='res:/UI/Texture/classes/careerPortal/playVideo.png', func=get_career_portal_controller_svc().play_video, variant=ButtonVariant.GHOST, args=video.path)
