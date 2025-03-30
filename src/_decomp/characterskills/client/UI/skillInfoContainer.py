#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\client\UI\skillInfoContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from characterskills.client.UI.util import get_skill_title, get_skill_subtitle, get_skill_description, get_skill_progress_info
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelSmallBold, EveLabelSmall
SKILL_ICON_SIZE = 64
PADDING_TOOLTIP_L = 8
PADDING_TOOLTIP_R = 0
PADDING_TOOLTIP_V = 4
PADDING_CAPTION_H = 6
PADDING_CAPTION_V = 4
PADDING_TITLE_TO_SUBTITLE = 0
PADDING_SUBTITLE_TO_DESCRIPTION = 6
PADDING_DESCRIPTION_TO_PROGRESS = 6
OPACITY_TITLE = 1.0
OPACITY_SUBTITLE = 0.8
OPACITY_DESCRIPTION = 0.8
OPACITY_SKILL_PROGRESS = 1.0

class SkillInfoContainer(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(SkillInfoContainer, self).ApplyAttributes(attributes)
        skill_type_id = attributes.skillTypeID
        skill_level = attributes.skillLevel
        is_reward = attributes.isReward
        self.left_container = Container(name='left_container', parent=self, width=SKILL_ICON_SIZE, align=uiconst.TOLEFT)
        self.right_container = ContainerAutoSize(name='right_container', parent=self, align=uiconst.TOTOP, padding=(4, 0, 10, 0))
        self.add_skill_icon()
        self.add_skill_info(skill_type_id, skill_level)

    def add_skill_icon(self):
        Sprite(name='skill_icon', parent=self.left_container, width=SKILL_ICON_SIZE, height=SKILL_ICON_SIZE, align=uiconst.TOPLEFT, texturePath='res:/ui/texture/icons/50_64_11.png')

    def add_skill_info(self, skill_type_id, skill_level):
        skill_title = get_skill_title(skill_type_id, skill_level)
        skill_subtitle = get_skill_subtitle(skill_type_id)
        skill_description = get_skill_description(skill_type_id)
        skill_progress = get_skill_progress_info(skill_type_id)
        EveLabelMediumBold(name='skill_title_label', parent=self.right_container, align=uiconst.TOTOP, text=skill_title, opacity=OPACITY_TITLE)
        EveLabelSmall(name='skill_subtitle_label', parent=self.right_container, align=uiconst.TOTOP, text=skill_subtitle, opacity=OPACITY_SUBTITLE, padTop=PADDING_TITLE_TO_SUBTITLE)
        EveLabelSmall(name='skill_description_label', parent=self.right_container, align=uiconst.TOTOP, text=skill_description, opacity=OPACITY_DESCRIPTION, padTop=PADDING_SUBTITLE_TO_DESCRIPTION)
        EveLabelSmallBold(name='skill_progress_label', parent=self.right_container, align=uiconst.TOTOP, text=skill_progress, opacity=OPACITY_SKILL_PROGRESS, padTop=PADDING_DESCRIPTION_TO_PROGRESS)
