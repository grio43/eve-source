#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\deltaContainer.py
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.glowSprite import GlowSprite
from localization import GetByLabel

class DeltaContainer(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_height = 20
    upArrow = 'res:/UI/Texture/classes/MultiSell/up.png'
    downArrow = 'res:/UI/Texture/classes/MultiSell/down.png'
    equalSprite = 'res:/UI/Texture/classes/MultiSell/equal.png'
    belowColor = '<color=0xffff5050>'
    aboveColor = '<color=0xff00ff00>'

    def ApplyAttributes(self, attributes):
        super(DeltaContainer, self).ApplyAttributes(attributes)
        delta = attributes.delta
        self.func = attributes.func
        self.icon = GlowSprite(name='icon', parent=self, align=uiconst.CENTERRIGHT, width=16, height=16, state=uiconst.UI_DISABLED, color=Color.WHITE)
        self.deltaText = EveLabelSmall(parent=self, align=uiconst.CENTERRIGHT, left=20)
        self.UpdateDelta(delta)

    def OnClick(self):
        self.func()

    def OnMouseEnter(self, *args):
        self.icon.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.icon.OnMouseExit()

    def UpdateDelta(self, delta):
        deltaText = self.GetDeltaText(delta)
        if delta > 0:
            self.deltaText.text = deltaText
            self.deltaText.align = uiconst.BOTTOMRIGHT
            texturePath = self.upArrow
        elif delta < 0:
            self.deltaText.text = deltaText
            self.deltaText.align = uiconst.TOPRIGHT
            texturePath = self.downArrow
        else:
            self.deltaText.text = ''
            texturePath = self.equalSprite
        self.icon.SetTexturePath(texturePath)

    def GetDeltaText(self, delta):
        if delta < 0:
            color = self.belowColor
        else:
            color = self.aboveColor
        if abs(delta) < 1.0:
            showFraction = 1
        else:
            showFraction = 0
        deltaText = '%s%s</color>' % (color, GetByLabel('UI/Common/Percentage', percentage=FmtAmt(delta * 100, showFraction=showFraction)))
        return deltaText


class BuyDeltaContainer(DeltaContainer):
    upArrow = 'res:/UI/Texture/classes/MultiSell/upBuy.png'
    downArrow = 'res:/UI/Texture/classes/MultiSell/downBuy.png'
    belowColor = '<color=0xff00ff00>'
    aboveColor = '<color=0xffff5050>'


class SellDeltaContainer(DeltaContainer):
    upArrow = 'res:/UI/Texture/classes/MultiSell/up.png'
    downArrow = 'res:/UI/Texture/classes/MultiSell/down.png'
    belowColor = '<color=0xffff5050>'
    aboveColor = '<color=0xff00ff00>'
