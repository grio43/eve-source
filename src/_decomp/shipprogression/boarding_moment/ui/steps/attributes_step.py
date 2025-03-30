#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\steps\attributes_step.py
import eveformat
import evetypes
import uthread2
from carbonui import TextBody, Align, TextColor
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.common.script.util.eveFormat import FmtDist2
from localization import GetByLabel
from shipprogression.boarding_moment.ui.steps.base import _BoardingUIStepBase
from shipprogression.boarding_moment.ui.utils import scramble_string, unscramble

class AttributesStep(_BoardingUIStepBase):
    FADE_IN_DURATION = 1.2
    LIFE_TIME = 3.5
    MARGIN_BOTTOM = 450

    def _construct_layout(self):
        self.textCont = ContainerAutoSize(parent=self, align=Align.BOTTOMLEFT, top=self.MARGIN_BOTTOM, left=self.MARGIN_LEFT)
        self.mass_string = GetByLabel('UI/ShipProgression/Mass', mass=evetypes.GetMass(self.typeID))
        self.mass = TextBody(parent=self.textCont, align=Align.TOPLEFT, text='-', color=TextColor.SECONDARY, opacity=0)
        self.volume_string = GetByLabel('UI/ShipProgression/Volume', volume=eveformat.volume_from_type(self.typeID))
        self.volume = TextBody(parent=self.textCont, align=Align.TOPLEFT, padTop=self.mass.height, text='-', color=TextColor.SECONDARY, opacity=0)
        self.shape_string = self._get_shape_string()
        self.shape_string_scrambled = scramble_string(self.shape_string)
        self.shape = TextBody(parent=self.textCont, align=Align.TOPLEFT, padTop=self.volume.height, text='-', color=TextColor.SECONDARY, opacity=0)

    def _get_shape_string(self):
        model = self.data['model']
        width, height, length = model.generatedShapeEllipsoidRadius
        long_axis = model.GetBoundingSphereRadius() * 2
        max_length = max(width, height, length)
        if height == max_length:
            axis_label = 'UI/ShipProgression/Height'
        elif width == max_length:
            axis_label = 'UI/ShipProgression/Width'
        else:
            axis_label = 'UI/ShipProgression/Length'
        return GetByLabel(axis_label, length=FmtDist2(long_axis, maxDecimals=0))

    def _update(self):
        animations.FadeIn(self.mass, endVal=0.5, duration=0.5)
        animations.FadeIn(self.volume, endVal=0.5, duration=0.5, timeOffset=0.25)
        animations.FadeIn(self.shape, endVal=0.5, duration=0.5, timeOffset=0.5)
        uthread2.StartTasklet(unscramble, self.mass, self.mass_string, delay=0.25, duration=0.5, onStart=self.on_start_typing_1, onEnd=self.on_stop_typing_1)
        uthread2.StartTasklet(unscramble, self.volume, self.volume_string, delay=0.5, duration=0.5, onStart=self.on_start_typing_1, onEnd=self.on_stop_typing_1)
        uthread2.StartTasklet(unscramble, self.shape, self.shape_string, delay=0.75, duration=0.5, onStart=self.on_start_typing_1, onEnd=self.on_stop_typing_1)
