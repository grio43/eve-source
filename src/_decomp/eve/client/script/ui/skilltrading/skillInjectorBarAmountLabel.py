#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skilltrading\skillInjectorBarAmountLabel.py
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelSmall

class InjectorBarAmountLabel(Container):
    default_height = 17

    def ApplyAttributes(self, attributes):
        super(InjectorBarAmountLabel, self).ApplyAttributes(attributes)
        self._amount = attributes.get('amount', 0)
        self.Layout()

    def Layout(self):
        Frame(parent=self, texturePath='res:/UI/Texture/classes/skilltrading/frame.png', cornerSize=3, opacity=0.5)
        Sprite(bgParent=self, align=uiconst.TOALL, padding=(4, 4, 4, 4), texturePath='res:/UI/Texture/classes/skilltrading/checker_bg.png', opacity=0.4, tileX=True, tileY=True)
        self.label = EveLabelSmall(parent=self, align=uiconst.CENTER)
        self.UpdateLabel()

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = int(value)
        self.UpdateLabel()

    def AnimSetAmount(self, amount):
        animations.MorphScalar(self, 'amount', startVal=self.amount, endVal=amount, callback=lambda : setattr(self, 'amount', amount))

    def UpdateLabel(self):
        text = localization.GetByLabel('UI/SkillTrading/UnallocatedPointsLabel', amount=self.amount)
        self.label.SetText(text)
