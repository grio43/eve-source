#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skilltrading\skillInjectorBar.py
import localization
import trinity
import uthread
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import CaptionLabel
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.neocom.skillConst import COLOR_UNALLOCATED_1
from eve.client.script.ui.skilltrading.skillInjectorBarAmountLabel import InjectorBarAmountLabel

class SkillInjectorBar(Container):
    default_width = 350
    default_height = 52

    def ApplyAttributes(self, attributes):
        super(SkillInjectorBar, self).ApplyAttributes(attributes)
        self.totalPoints = attributes.get('totalPoints', 0)
        self.injectorItem = attributes.injectorItem
        self.onComplete = attributes.onComplete
        self.skillSvc = sm.GetService('skills')
        self.ConstructLayout()

    def ConstructLayout(self):
        gaugeCont = Container(name='GaugeContainer', parent=self, align=uiconst.TOTOP, height=32)
        Frame(parent=gaugeCont, texturePath='res:/UI/Texture/classes/skilltrading/frame.png', cornerSize=3, opacity=0.5)
        self.gaugeBG = GradientSprite(bgParent=gaugeCont, align=uiconst.TOALL, rgbData=[(0.0, (1.0, 1.0, 1.0))], alphaData=[(0.0, 0.0),
         (0.4, 0.9),
         (0.6, 0.9),
         (1.0, 0.0)], opacity=0.1)
        arrowCont = Container(parent=gaugeCont, align=uiconst.TOALL)
        self.frame = Frame(bgParent=arrowCont, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/buttonBg.png', cornerSize=5, color=Color.GRAY2)
        self.arrows = Sprite(bgParent=arrowCont, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', translationSecondary=(-0.16, 0), spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, opacity=0.2)
        animations.MorphVector2(self.arrows, 'translationSecondary', startVal=(0.16, 0.0), endVal=(-0.16, 0.0), duration=2.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        self.label = CaptionLabel(parent=arrowCont, align=uiconst.CENTER)
        self.gauge = Gauge(parent=gaugeCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=30, gaugeHeight=30, top=1, color=COLOR_UNALLOCATED_1, backgroundColor=(1.0, 1.0, 0.0, 0.0))
        self.unallocatedPointsLabel = InjectorBarAmountLabel(parent=self, align=uiconst.TOTOP, top=2, amount=self.skillSvc.GetFreeSkillPoints())

    def SetTotalPoints(self, totalPoints):
        self.totalPoints = totalPoints

    def OnInjectionStarted(self):
        self.FillGauge()
        self.SetUnallocatedPointsLabel()

    def FillGauge(self):
        completeText = localization.GetByLabel('UI/SkillTrading/InjectionComplete')
        self.gauge.SetValueTimed(1.0, duration=0.6, callback=lambda : self.AnimSetLabel(completeText))

    def SetUnallocatedPointsLabel(self):
        self.unallocatedPointsLabel.AnimSetAmount(self.totalPoints)

    def AnimSetLabel(self, text):
        uthread.new(self._AnimSetLabel, text)

    def _AnimSetLabel(self, text):
        animations.FadeOut(self.label, duration=0.25, sleep=True)
        self.label.SetText(text)
        animations.FadeIn(self.label, duration=0.3)
