#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\simpleCurtain.py
from math import pi
import log
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
import uthread
from carbonui import uiconst
from carbonui.uianimations import animations

class SimpleCurtain(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self._statusIconColor = 0
        self.topParent = Container(parent=self, align=uiconst.TOTOP_PROP, height=1.0)
        self.barHeight = 24
        self._CreateBar(attributes.curtainText)
        self._SetTopContainer(attributes)
        self._SetBottomContainer(attributes)
        self.isUp = False
        self.callback = attributes.callback
        self.SetStatusIconOff()

    def _SetBottomContainer(self, attributes):
        self.bottomContainer = attributes.bottomContainer
        self.bottomContainer.SetParent(self)
        self.bottomContainer.align = uiconst.TOALL
        self.bottomContainer.name += '_bottomContainer'

    def _SetTopContainer(self, attributes):
        self.topContainer = attributes.topContainer
        self.topContainer.SetParent(self.topParent)
        self.topContainer.name += '_topContainer'
        self.topContainer.align = uiconst.TOALL

    def _CreateBar(self, text):
        self.bar = Container(parent=self.topParent, align=uiconst.TOBOTTOM, height=self.barHeight, state=uiconst.UI_NORMAL)
        GradientSprite(bgParent=self.bar, rotation=-pi / 2, rgbData=[(0, (0.3, 0.3, 0.3))], alphaData=[(0, 0.5), (0.9, 0.15)])
        barLabelParent = Container(parent=self.bar, align=uiconst.CENTER, height=self.barHeight, width=300, state=uiconst.UI_DISABLED)
        self.isUpIcons = [Sprite(parent=barLabelParent, align=uiconst.CENTERLEFT, pos=(-15, 0, 32, 32), name='statusIcon', state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Icons/105_32_4.png', idx=0), Sprite(parent=barLabelParent, align=uiconst.CENTERRIGHT, pos=(-15, 0, 32, 32), name='statusIcon', state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Icons/105_32_4.png', idx=0)]
        self.barLabel = EveCaptionSmall(parent=barLabelParent, text=text, align=uiconst.CENTER)
        w = self.barLabel.width
        barLabelParent.left -= 25
        barLabelParent.width = w + 50
        self.bar.OnClick = self.ToggleBar

    def ToggleBar(self, *args):
        self.bar.state = uiconst.UI_DISABLED
        try:
            oldIsUp = self._IsUp()
            self.isUp = not self.isUp
            if oldIsUp:
                self._MoveBarDown()
            else:
                self._MoveBarUp()
            self.CallCallback()
        finally:
            self.bar.state = uiconst.UI_NORMAL

    def _IsUp(self):
        return self.isUp

    def _MoveBarUp(self):
        self.isUp = True
        self._HideContainers()
        self.topParent.align = uiconst.TOTOP
        self.topParent.height = self._GetHeight()
        animations.MorphScalar(self.topParent, 'height', endVal=24, duration=0.15, sleep=True)
        self.SetStatusIconOn()
        self._ShowContainers()

    def _MoveBarDown(self):
        self.isUp = False
        self._HideContainers()
        self.topParent.align = uiconst.TOTOP_PROP
        currentHeight = self._GetHeight()
        self.topParent.height = float(self.barHeight) / currentHeight
        animations.MorphScalar(self.topParent, 'height', endVal=1, duration=0.15, sleep=True)
        self.SetStatusIconOff()
        self._ShowContainers()

    def _ShowContainers(self):
        self.topContainer.state = uiconst.UI_PICKCHILDREN
        self.bottomContainer.state = uiconst.UI_PICKCHILDREN
        uthread.parallel([(self._AnimateContainerOpacity, (self.topContainer, 1.0)), (self._AnimateContainerOpacity, (self.bottomContainer, 1.0))])

    def _HideContainers(self):
        uthread.parallel([(self._AnimateContainerOpacity, (self.topContainer, 0.0)), (self._AnimateContainerOpacity, (self.bottomContainer, 0.0))])
        self.topContainer.state = uiconst.UI_DISABLED
        self.bottomContainer.state = uiconst.UI_DISABLED

    def _AnimateContainerOpacity(self, container, endOpacity):
        animations.FadeIn(container, endVal=endOpacity, duration=0.1, sleep=True)

    def _GetHeight(self):
        _, currentHeight = self.GetAbsoluteSize()
        return currentHeight

    def _SetUpIconsTexturePath(self, texturePath):
        for ic in self.isUpIcons:
            ic.LoadTexture(texturePath)

    def SetStatusIconOn(self):
        self._SetUpIconsTexturePath('res:/UI/Texture/Icons/105_32_5.png')

    def SetStatusIconOff(self):
        self._SetUpIconsTexturePath('res:/UI/Texture/Icons/105_32_4.png')

    def CallCallback(self):
        try:
            if self.callback is not None:
                self.callback(self.isUp)
        except Exception:
            log.LogException('Failed to call callback when curtain was clicked')
