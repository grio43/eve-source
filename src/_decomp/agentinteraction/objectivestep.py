#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\objectivestep.py
import carbonui
import eveicon
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveIcon import OwnerIcon
from evemissions.client.objectives import ObjectiveState, CargoObjective
import trinity
ICON_SIZE = 32
STATE_ICON_SIZE = 16
IMAGE_SIZE = 64

class ObjectiveStep(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        self.step_info_container = None
        super(ObjectiveStep, self).ApplyAttributes(attributes)
        self.title_left = attributes.title_left
        self.title_right = attributes.title_right
        self.text = attributes.text
        self.step_state = attributes.step_state
        self.owner_id = attributes.get('owner_id', None)
        self.step = attributes.step
        content_padding_bottom = attributes.content_padding_bottom
        content_padding_top = attributes.content_padding_top
        self._build_objective_image()
        self.content = ContainerAutoSize(name='content', parent=self, align=uiconst.TOTOP, padBottom=content_padding_bottom, padTop=content_padding_top)
        self._build_title_container()
        self._build_step_container()

    def _build_objective_image(self):
        self.objective_image_container = Container(name='objective_image_container', parent=self, align=uiconst.TOLEFT, width=IMAGE_SIZE, padRight=15)
        if self.owner_id:
            OwnerIcon(name='objective_icon', parent=self.objective_image_container, align=uiconst.CENTER, width=IMAGE_SIZE, height=IMAGE_SIZE, ownerID=self.owner_id, spriteEffect=trinity.TR2_SFX_MASK, textureSecondaryPath='res:/UI/Texture/Classes/AgentInteraction/AgentCircle.png')
            Sprite(name='objective_icon_frame', parent=self.objective_image_container, texturePath='res:/UI/Texture/Classes/AgentInteraction/AgentCircleFrame.png', state=uiconst.UI_DISABLED, align=uiconst.CENTER, height=IMAGE_SIZE, width=IMAGE_SIZE, color=Color.WHITE)
        else:
            self.objective_image_container.Hide()

    def _build_title_container(self):
        self.title_container = Container(name='title_container', parent=self.content, align=uiconst.TOTOP, padBottom=3, height=20)
        self._build_title_left()
        self._build_title_right()

    def _build_title_left(self):
        carbonui.TextBody(name='title_left', parent=self.title_container, align=uiconst.TOLEFT, text=self.title_left, color=carbonui.TextColor.SECONDARY)

    def _build_title_right(self):
        carbonui.TextBody(name='title_right', parent=self.title_container, align=uiconst.TOLEFT, text=self.title_right, color=carbonui.TextColor.HIGHLIGHT, padLeft=8)

    def _build_step_container(self):
        self.step_container = ContainerAutoSize(name='step_container', parent=self.content, align=uiconst.TOTOP, height=ICON_SIZE, alignMode=uiconst.TOTOP)
        self._build_sprite()
        self._build_step_info()

    def _build_sprite(self):
        sprite_container = Container(name='sprite_container', parent=self.step_container, align=uiconst.TOLEFT, width=ICON_SIZE, padRight=4)
        state_icon_container = Container(name='state_icon_container', parent=sprite_container)
        Sprite(name='state_icon', parent=state_icon_container, align=uiconst.CENTER, width=STATE_ICON_SIZE, height=STATE_ICON_SIZE, texturePath=self._get_icon(), color=carbonui.TextColor.NORMAL)
        Frame(name='sprite_background', parent=sprite_container, color=self._get_state_color(), cornerSize=6, texturePath='res:/UI/Texture/Classes/AgentInteraction/ObjectiveStep_IconBackground.png')

    def _build_step_info(self):
        self.step_info_container = ContainerAutoSize(name='step_info_container', parent=self.step_container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.text_label = self._get_step_label(self.step_info_container, uiconst.TOTOP_NOPUSH)
        label_bg_cont = ContainerAutoSize(name='label_bg_cont', parent=self.step_info_container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.bg_fill = Fill(parent=label_bg_cont, align=uiconst.TOLEFT_NOPUSH, opacity=0.1)
        c = ContainerAutoSize(name='c', parent=label_bg_cont, align=uiconst.TOTOP, opacity=0.0)
        self._get_step_label(c, uiconst.TOTOP)
        text_width, _ = self.text_label.MeasureTextSize(self.text_label.text, maxLines=1)
        self.bg_fill.width = text_width + 2 * self.text_label.padLeft

    def _get_step_label(self, parent, alignment):
        return carbonui.TextBody(name='text', parent=parent, align=alignment, text=self.text, state=uiconst.UI_NORMAL, padding=(7, 8, 7, 8), color=carbonui.TextColor.HIGHLIGHT)

    def _get_state_color(self):
        if self.step_state == ObjectiveState.COMPLETED:
            return carbonui.TextColor.SUCCESS
        if self.step_state == ObjectiveState.FAILED:
            return carbonui.TextColor.DANGER
        return (1.0, 1.0, 1.0, 0.05)

    def _get_icon(self):
        if self.step_state == ObjectiveState.COMPLETED:
            return eveicon.checkmark
        return self.step.get_icon()
