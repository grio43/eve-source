#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\sessionTimeIndicator.py
import math
import carbonui.const as uiconst
import blue
import localization
from carbon.common.script.util.format import FmtTimeInterval
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform

class SessionTimeIndicator(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        size = 24
        self.ramps = Container(parent=self, name='ramps', pos=(0,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        leftRampCont = Container(parent=self.ramps, name='leftRampCont', pos=(0,
         0,
         size / 2,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, clipChildren=True)
        self.leftRamp = Transform(parent=leftRampCont, name='leftRamp', pos=(0,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        Sprite(parent=self.leftRamp, name='rampSprite', pos=(0,
         0,
         size / 2,
         size), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/TiDiIndicator/left.png', color=(0, 0, 0, 0.5))
        rightRampCont = Container(parent=self.ramps, name='rightRampCont', pos=(0,
         0,
         size / 2,
         size), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, clipChildren=True)
        self.rightRamp = Transform(parent=rightRampCont, name='rightRamp', pos=(-size / 2,
         0,
         size,
         size), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        Sprite(parent=self.rightRamp, name='rampSprite', pos=(size / 2,
         0,
         size / 2,
         size), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/TiDiIndicator/right.png', color=(0, 0, 0, 0.5))
        self.coloredPie = Sprite(parent=self, name='tidiColoredPie', pos=(0,
         0,
         size,
         size), texturePath='res:/UI/Texture/classes/TiDiIndicator/circle.png', state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.5))

    def AnimSessionChange(self):
        if session.nextSessionChange is not None:
            duration = session.nextSessionChange - blue.os.GetSimTime()
            while blue.os.GetSimTime() < session.nextSessionChange:
                timeDiff = session.nextSessionChange - blue.os.GetSimTime()
                progress = timeDiff / float(duration)
                self.SetProgress(1.0 - progress)
                timeLeft = FmtTimeInterval(timeDiff, breakAt='sec')
                self.hint = localization.GetByLabel('UI/Neocom/SessionChangeHint', timeLeft=timeLeft)
                self.state = uiconst.UI_NORMAL
                blue.pyos.synchro.Yield()

        self.SetProgress(1.0)
        self.state = uiconst.UI_HIDDEN

    def SetProgress(self, progress):
        progress = max(0.0, min(1.0, progress))
        leftRamp = min(1.0, max(0.0, progress * 2))
        rightRamp = min(1.0, max(0.0, progress * 2 - 1.0))
        self.leftRamp.SetRotation(math.pi + math.pi * leftRamp)
        self.rightRamp.SetRotation(math.pi + math.pi * rightRamp)
