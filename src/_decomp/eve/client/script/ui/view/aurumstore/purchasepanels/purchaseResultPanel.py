#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\purchasepanels\purchaseResultPanel.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from eve.client.script.ui.view.aurumstore.purchasepanels.basePurchasePanel import BasePurchasePanel
from eve.client.script.ui.view.aurumstore.shared.const import TEXT_PADDING, PROGRESS_TRANSITION_TIME
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import VgsLabelLarge

class PurchaseResultPanel(BasePurchasePanel):
    default_name = 'purchaseResultPanel'

    def ApplyAttributes(self, attributes):
        super(PurchaseResultPanel, self).ApplyAttributes(attributes)
        self.audioEventName = attributes.audioEventName
        cont = Container(parent=self, align=uiconst.TOPLEFT, height=72, padTop=4)
        self.iconForegroundTransform = Transform(parent=cont, align=uiconst.CENTERTOP, width=72, height=78, scalingCenter=(0.5, 0.5))
        self.iconForeground = Sprite(parent=self.iconForegroundTransform, align=uiconst.CENTER, texturePath=attributes.iconForegroundTexturePath, width=72, height=64, opacity=0)
        self.iconBackgroundTransform = Transform(parent=cont, align=uiconst.CENTERTOP, width=72, height=78, scalingCenter=(0.5, 0.5))
        self.iconBackground = Sprite(parent=self.iconBackgroundTransform, align=uiconst.CENTER, texturePath=attributes.iconBackgroundTexturePath, width=72, height=64, opacity=0)
        captionCont = Container(parent=self, align=uiconst.TOTOP, height=40, padding=(TEXT_PADDING,
         4,
         TEXT_PADDING,
         0))
        VgsLabelLarge(parent=captionCont, align=uiconst.CENTER, text=attributes.textTitle)

    def OnPanelActivated(self):
        if self.audioEventName:
            sm.GetService('audio').SendUIEvent(self.audioEventName)
        uicore.animations.FadeIn(self.iconBackground, duration=0.5, timeOffset=PROGRESS_TRANSITION_TIME)
        uicore.animations.FadeIn(self.iconForeground, duration=0.5, timeOffset=PROGRESS_TRANSITION_TIME + 0.5)
        uicore.animations.Tr2DScaleTo(self.iconBackgroundTransform, (2.0, 2.0), (1.0, 1.0), duration=0.25, timeOffset=PROGRESS_TRANSITION_TIME)
        uicore.animations.Tr2DScaleTo(self.iconForegroundTransform, (2.0, 2.0), (1.0, 1.0), duration=0.25, timeOffset=PROGRESS_TRANSITION_TIME + 0.5)
