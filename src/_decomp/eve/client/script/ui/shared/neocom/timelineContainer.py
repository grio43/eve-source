#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\timelineContainer.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from carbonui.uianimations import animations
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SKILLQUEUETIMELINE
from eve.client.script.ui.shared.cloneGrade.omegaCloneIcon import OmegaCloneIcon
from localization import GetByLabel

class TimelineContainer(Container):
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.offset = None
        self.omegaIcon = None
        self.segments = []
        self.unallocated = None
        self.duration = None

    def ConstructOmegaIcon(self):
        iconsize = 24
        self.omegaIcon = OmegaCloneIcon(parent=self, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconsize,
         iconsize), opacity=0.75, idx=0, tooltipText=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/QueueAlphaLimitation'), origin=ORIGIN_SKILLQUEUETIMELINE)

    def AddSegment(self, fraction, color):
        if self.destroyed:
            return
        segment = Fill(parent=self, align=uiconst.TOLEFT_PROP, color=color, width=fraction, state=uiconst.UI_DISABLED)
        self.segments.append(segment)

    def SetOffset(self, offset):
        if self.offset is None:
            self.offset = Container(align=uiconst.TOLEFT_PROP, parent=self, idx=0)
        self.offset.width = offset

    def SetUnallocated(self, fraction):
        if not self.unallocated:
            self.unallocated = Sprite(parent=self, align=uiconst.TOLEFT_NOPUSH, texturePath='res:/UI/Texture/classes/CharacterSheet/injectorArrow.png', tileX=True, idx=0)
            animations.FadeTo(self.unallocated, startVal=0.1, endVal=0.8, duration=3.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
        width, _ = self.GetAbsoluteSize()
        self.unallocated.width = width * fraction

    def FlushLine(self):
        if self.omegaIcon:
            self.omegaIcon.Hide()
        for segment in self.segments:
            segment.Close()

        self.segments = []

    def SetDuration(self, duration):
        if sm.GetService('cloneGradeSvc').IsOmega():
            return
        self.duration = duration
        width, _ = self.GetAbsoluteSize()
