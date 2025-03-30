#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\carousel.py
import logging
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from collections import OrderedDict
CIRCLE_FULL_PNG = 'res:/UI/Texture/Shared/Carousel/circleFull.png'
CIRCLE_EMPTY_PNG = 'res:/UI/Texture/Shared/Carousel/circleEmpty.png'
logger = logging.getLogger(__name__)

class Carousel(ScrollContainer):
    default_name = 'Carousel'
    default_alignMode = uiconst.TOLEFT
    default_scrollBarDisabled = True
    default_interval = 5
    default_scrollSpeed = 1.2

    def ApplyAttributes(self, attributes):
        super(Carousel, self).ApplyAttributes(attributes)
        self.buttons = OrderedDict()
        self.interval = attributes.get('interval', self.default_interval)
        self.scrollSpeed = attributes.get('scrollSpeed', self.default_scrollSpeed)
        self.autoScrollTimer = None
        self.previousButton = None
        self.ConstructButtonContainer()
        self.ConstructControlButtons()
        self.StartAutoScroll()

    def InitializeButtons(self):
        self.ClearButtons()
        try:
            firstButton = self.buttons.values()[0]
        except IndexError:
            logger.error('cannot initialize carousel without children')
        else:
            self.SetButtonFull(firstButton)

    def ConstructButtonContainer(self):
        self.buttonContainer = ContainerAutoSize(name='carouselButtons', parent=self.clipCont, align=uiconst.CENTERBOTTOM, state=uiconst.UI_NORMAL, height=24, top=8, idx=0)

    def ConstructControlButtons(self):
        self.leftButton = ButtonIcon(name='leftButton', parent=self.buttonContainer, align=uiconst.TOLEFT, width=8, height=8, iconSize=8, texturePath='res:/UI/Texture/Shared/Carousel/leftArrow.png', func=self.SelectPreviousChild)
        self.centerButtonContainer = ContainerAutoSize(parent=self.buttonContainer, align=uiconst.TOLEFT)
        self.rightButton = ButtonIcon(name='rightButton', parent=self.buttonContainer, align=uiconst.TOLEFT, width=8, height=8, iconSize=8, left=4, texturePath='res:/UI/Texture/Shared/Carousel/rightArrow.png', func=self.SelectNextChild)

    def show_control_buttons(self):
        self.leftButton.display = True
        self.rightButton.display = True

    def hide_control_buttons(self):
        self.leftButton.display = False
        self.rightButton.display = False

    def AddControlButtonForChild(self, child):
        if child in self.buttons:
            return
        self.buttons[child] = ButtonIcon(name='%s_carouselCircle' % child.name, parent=self.centerButtonContainer, align=uiconst.TOLEFT, width=8, height=8, iconSize=6, left=4, texturePath=CIRCLE_EMPTY_PNG)

    def Close(self, *args):
        self.StopAutoScroll()
        super(Carousel, self).Close(*args)

    def _InsertChild(self, idx, obj):
        super(Carousel, self)._InsertChild(idx, obj)
        self.AddControlButtonForChild(obj)

    def _AppendChild(self, obj):
        super(Carousel, self)._AppendChild(obj)
        self.AddControlButtonForChild(obj)

    def StartAutoScroll(self):
        self.autoScrollTimer = AutoTimer(self.interval * 1000, self.ScrollToNext)

    def StopAutoScroll(self):
        if not self.autoScrollTimer:
            return
        self.autoScrollTimer.KillTimer()
        self.autoScrollTimer = None

    def ScrollToNext(self):
        if self.mainCont.HasAnimation('left'):
            return
        childToMove = self.mainCont.children[0]
        self.ClearButtons()
        self.SetButtonFull(self.buttons[self.mainCont.children[1]])
        animations.MorphScalar(self.mainCont, 'left', startVal=self.mainCont.left, endVal=self.mainCont.left - childToMove.width, duration=self.scrollSpeed, callback=lambda : self.MoveChildToBack(childToMove), curveType=uiconst.ANIM_SMOOTH)

    def ScrollToPrevious(self):
        if self.mainCont.HasAnimation('left'):
            return
        self.MoveChildToFront(self.mainCont.children[-1])
        animations.MorphScalar(self.mainCont, 'left', startVal=self.mainCont.left, endVal=0, duration=self.scrollSpeed, curveType=uiconst.ANIM_SMOOTH)

    def MoveChildToFront(self, child):
        self._RemoveChild(child)
        self._InsertChild(0, child)
        self.ClearButtons()
        self.SetButtonFull(self.buttons[child])
        self.mainCont.left = -child.width

    def ClearButtons(self):
        for button in self.buttons.values():
            button.SetTexturePath(CIRCLE_EMPTY_PNG)

    @staticmethod
    def SetButtonFull(button):
        button.SetTexturePath(CIRCLE_FULL_PNG)

    def MoveChildToBack(self, child):
        self._RemoveChild(child)
        self._AppendChild(child)
        self.mainCont.left = 0

    def SelectPreviousChild(self, *args):
        self.StopAutoScroll()
        self.ScrollToPrevious()
        self.StartAutoScroll()

    def SelectNextChild(self, *args):
        self.StopAutoScroll()
        self.ScrollToNext()
        self.StartAutoScroll()
