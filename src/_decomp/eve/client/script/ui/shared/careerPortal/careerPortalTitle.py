#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\careerPortalTitle.py
from carbonui import TextAlign, uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import CaptionLabel
from eve.client.script.ui.shared.careerPortal import careerConst
from localization import GetByLabel

class CareerPortalTitle(Container):

    def ApplyAttributes(self, attributes):
        super(CareerPortalTitle, self).ApplyAttributes(attributes)
        self.PrepareUI()
        careerConst.CAREER_WINDOW_STATE_SETTING.on_change.connect(self.OnCareerWindowStateChanged)
        self.OnCareerWindowStateChanged(careerConst.CAREER_WINDOW_STATE_SETTING.get())

    def PrepareUI(self):
        self.title = CaptionLabel(parent=self, name='titleLabel', align=uiconst.TOBOTTOM, textAlign=TextAlign.CENTER, glowBrightness=0.6, bold=True, text=GetByLabel('UI/CareerPortal/CareersViewTitle'), color=eveColor.AIR_TURQUOISE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, uppercase=True, fontsize=28)

    def Close(self):
        careerConst.CAREER_WINDOW_STATE_SETTING.on_change.disconnect(self.OnCareerWindowStateChanged)
        super(CareerPortalTitle, self).Close()

    def OnCareerWindowStateChanged(self, state):
        if state != careerConst.CareerWindowState.CAREERS_VIEW:
            animations.FadeOut(self.title, duration=0.5)
            return
        animations.FadeIn(self.title, duration=0.5)
