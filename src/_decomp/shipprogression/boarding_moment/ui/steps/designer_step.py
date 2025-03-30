#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\steps\designer_step.py
import evetypes
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import TextBody, TextColor, uiconst, TextCustom, Align
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.text.const import FontSizePreset
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveIcon
from localization import GetByLabel
from npcs.npccorporations import get_designer_description, get_npc_corporation_name
from shipprogression.boarding_moment.ui.sounds import get_typing_sound_service, CINEMATIC_SHIP_INTRO_TEXT_1
from shipprogression.boarding_moment.ui.steps.base import _BoardingUIStepBase
from shipprogression.boarding_moment.ui.utils import roll_in

class DesignerStep(_BoardingUIStepBase):
    MARGIN_BOTTOM = 250
    FADE_IN_DURATION = 0.1
    designer_icons = []

    def ApplyAttributes(self, attributes):
        self.designer_icons = []
        super(DesignerStep, self).ApplyAttributes(attributes)

    def _update(self):
        for idx, designerIcon in enumerate(self.designer_icons):
            offset = 0.45 * idx
            designerIcon.FadeIn(0.35, offset)
            uthread2.start_tasklet(self._play_audio, offset)

    def _play_audio(self, offset):
        uthread2.sleep(offset)
        if not self.destroyed:
            PlaySound('cinematic_ship_intro_icon_designer')

    def _construct_layout(self):
        self.designer_cont = Container(parent=self, align=Align.BOTTOMLEFT, height=120, width=1400, top=self.MARGIN_BOTTOM, left=self.MARGIN_LEFT)
        self.designer_label = TextBody(parent=self.designer_cont, align=Align.TOPLEFT, color=TextColor.SECONDARY, top=-32, text='')
        designer_ids = evetypes.GetDesigners(self.typeID)
        if not designer_ids or len(designer_ids) == 0:
            return
        if len(designer_ids) == 1:
            self.designer_label.SetText(GetByLabel('UI/ShipProgression/BoardingMomentDesignedBy'))
            self._construct_designer_icon_single(self.designer_cont, designer_ids[0])
        else:
            self.designer_label.SetText(GetByLabel('UI/ShipProgression/BoardingMomentDesignCollaborationBy'))
            self._construct_designer_icons(self.designer_cont, designer_ids)

    ICON_SIZE = 112

    def _construct_designer_icon_single(self, parent, designerID):
        designer_icon = DesignerIconSingle(parent=parent, align=Align.CENTERLEFT, designerID=designerID, icon_size=self.ICON_SIZE)
        self.designer_icons.append(designer_icon)

    def _construct_designer_icons(self, parent, designerIDs):
        designerCont = FlowContainer(name='designerFlowCont', parent=parent, align=Align.TOBOTTOM, contentSpacing=(48, 16))
        for designerID in designerIDs:
            self._construct_designer_icon(designerCont, designerID)

    def _construct_designer_icon(self, flowCont, designerID):
        designerIcon = DesignerIcon(parent=flowCont, designerID=designerID, icon_size=self.ICON_SIZE)
        self.designer_icons.append(designerIcon)


class DesignerIcon(Container):
    default_padding = 10
    default_align = Align.NOALIGN

    def ApplyAttributes(self, attributes):
        super(DesignerIcon, self).ApplyAttributes(attributes)
        self.designerID = attributes.designerID
        self.icon_size = attributes.icon_size
        self.pos = (0,
         0,
         self.icon_size,
         self.icon_size)
        self.designerLogo = eveIcon.GetLogoIcon(itemID=self.designerID, parent=self, state=uiconst.UI_NORMAL, hint=get_designer_description(self.designerID), align=uiconst.CENTER, pos=(0,
         0,
         self.icon_size - 20,
         self.icon_size - 20), ignoreSize=True, opacity=0)
        self.bg = Sprite(parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTER, width=self.icon_size, height=self.icon_size, texturePath='res:/UI/Texture/classes/ShipInfo/logo_frame.png', color=(0.1, 0.1, 0.1, 0.65), opacity=0)

    def FadeIn(self, duration, delay):
        animations.FadeIn(self.designerLogo, duration=duration, timeOffset=delay + 0.2)
        animations.FadeIn(self.bg, endVal=0.65, duration=duration, timeOffset=delay)


class DesignerIconSingle(DesignerIcon):

    def ApplyAttributes(self, attributes):
        super(DesignerIconSingle, self).ApplyAttributes(attributes)
        self.designer_name = get_npc_corporation_name(self.designerID)
        self.designer_name_label = TextCustom(parent=self, align=Align.CENTERLEFT, left=self.icon_size + 20, text='', fontsize=FontSizePreset.DISPLAY, letterspace=5)

    def FadeIn(self, duration, delay):
        super(DesignerIconSingle, self).FadeIn(duration, delay)
        uthread2.StartTasklet(roll_in, self.designer_name_label, self.designer_name, delay=0.5, duration=0.5, onStart=self.on_start_typing_1, onEnd=self.on_stop_typing_1)

    def on_start_typing_1(self):
        get_typing_sound_service().play_sound(CINEMATIC_SHIP_INTRO_TEXT_1)

    def on_stop_typing_1(self):
        get_typing_sound_service().stop_sound(CINEMATIC_SHIP_INTRO_TEXT_1)
