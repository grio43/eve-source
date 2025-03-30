#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\steps\traits_step.py
import eveicon
import trinity
import uthread2
from carbonui import Align, TextColor, TextBody, TextAlign
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.uianimations import animations
from carbonui.uiconst import BlendMode
from localization import GetByMessageID
from carbon.client.script.environment.AudioUtil import PlaySound
from shipprogression.boarding_moment.ui.sounds import get_typing_sound_service, CINEMATIC_SHIP_INTRO_TEXT_1
from shipprogression.boarding_moment.ui.steps.base import _BoardingUIStepBase
from shipprogression.boarding_moment.ui.utils import unscramble

class TraitsStep(_BoardingUIStepBase):
    MARGIN_LEFT = 230
    traits = []

    def ApplyAttributes(self, attributes):
        self.traits = []
        super(TraitsStep, self).ApplyAttributes(attributes)

    def _update(self):
        for idx, trait in enumerate(self.traits):
            trait.FadeIn(idx, self.FADE_IN_DELAY + self.delay)

    def _construct_layout(self):
        self.traitsCont = Container(parent=self, align=Align.BOTTOMLEFT, height=120, width=1500, top=self.MARGIN_TOP, left=self.MARGIN_LEFT)
        self._construct_traits()

    def _construct_traits(self):
        try:
            traitIDs = [ x[1] for x in sorted(cfg.infoBubbleTypeElements[self.typeID].items(), key=lambda data: int(data[0])) ][:5]
        except:
            traitIDs = []

        for traitID in traitIDs:
            trait = TraitStepTrait(parent=self.traitsCont, traitID=traitID)
            self.traits.append(trait)


class TraitStepTrait(Container):
    default_align = Align.TOLEFT
    default_width = 90
    default_padRight = 8

    def ApplyAttributes(self, attributes):
        super(TraitStepTrait, self).ApplyAttributes(attributes)
        self.traitID = attributes.traitID
        self.sound_controller = get_typing_sound_service()
        definition = cfg.infoBubbleElements[self.traitID]
        iconID = definition['icon']
        nameID = definition['nameID']
        iconCont = Container(parent=self, align=Align.TOTOP, height=32, padTop=16, padBottom=8)
        self.icon = Sprite(parent=iconCont, align=Align.CENTER, height=32, width=32, texturePath=eveicon.get(iconID, default=iconID), color=TextColor.NORMAL, opacity=0)
        self.video = StreamingVideoSprite(parent=iconCont, videoPath='res:/video/shared/trait_bg.webm', videoLoop=False, videoAutoPlay=False, disableAudio=True, align=Align.CENTER, spriteEffect=trinity.TR2_SFX_COPY, blendMode=BlendMode.ADD, width=64, height=64)
        self.name_string = GetByMessageID(nameID)
        self.name_label = TextBody(parent=self, align=Align.TOTOP, text='', textAlign=TextAlign.CENTER, opacity=0, padTop=12)

    def FadeIn(self, idx, fadeInDelay):
        iconDelay = fadeInDelay + idx * 0.35
        animations.FadeIn(self.icon, endVal=0.75, duration=0.5, timeOffset=iconDelay)
        textDelay = iconDelay + 0.35
        animations.FadeIn(self.name_label, endVal=0.75, duration=0.5, timeOffset=textDelay)
        uthread2.StartTasklet(unscramble, self.name_label, self.name_string, delay=textDelay, duration=0.4)
        uthread2.StartTasklet(self.PlayDelayed, iconDelay - 0.6)

    def PlayDelayed(self, delay):
        uthread2.Sleep(delay)
        PlaySound('cinematic_ship_intro_icon_trait')
        self.video.Play()

    def start_sound(self):
        self.sound_controller.play_sound(CINEMATIC_SHIP_INTRO_TEXT_1)

    def stop_sound(self):
        self.sound_controller.stop_sound(CINEMATIC_SHIP_INTRO_TEXT_1)
