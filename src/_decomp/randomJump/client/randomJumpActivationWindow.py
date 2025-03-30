#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\randomJump\client\randomJumpActivationWindow.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveLabel
from carbonui.control.window import Window
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.crimewatch.crimewatchTimers import Timer, TimerType
import evetypes
import uthread
from randomJump.client.RandomJumpButton import RandomJumpButton
from randomJump.client.clientRandomJumpValidator import ClientRandomJumpValidator
from randomJump.client.randomJumpController import RandomJumpActivationController
SHIP_RESTRICTION_ICON_TYPE_ID = 44213

class RandomJumpActivationWindow(Window):
    __guid__ = 'form.RandomJumpActivationWindow'
    default_fixedWidth = 420
    default_left = '__center__'
    default_top = '__center__'
    default_windowID = 'RandomJumpActivationWindow'
    default_isCollapseable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_iconNum = 'res:/ui/Texture/WindowIcons/abyssalFilament.png'

    @classmethod
    def Open(cls, **attributes):
        window = cls.GetIfOpen()
        if not window:
            return super(RandomJumpActivationWindow, cls).Open(**attributes)
        item = attributes.get('item', None)
        if item.itemID == window.controller.itemID:
            window.Maximize()
            return window
        window.CloseByUser()
        return super(RandomJumpActivationWindow, cls).Open(**attributes)

    def ApplyAttributes(self, attributes):
        super(RandomJumpActivationWindow, self).ApplyAttributes(attributes)
        self.controller = RandomJumpActivationController(attributes.item, ClientRandomJumpValidator())
        self.Layout()
        self.SetCaption(evetypes.GetName(self.controller.typeID))
        self.controller.onChange.connect(self.UpdateState)

    def Layout(self):
        self.mainCont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, callback=self._FixHeight, idx=0)
        filamentCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=64)
        ItemIcon(parent=filamentCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 64, 64), showOmegaOverlay=False, typeID=self.controller.typeID)
        filamentInnerCont = ContainerAutoSize(parent=filamentCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 0, 0, 0))
        eveLabel.EveLabelMedium(parent=filamentInnerCont, align=uiconst.TOTOP, text=self.controller.typeDescription)
        if self.controller.activeSystem:
            eveLabel.EveLabelMedium(parent=filamentInnerCont, align=uiconst.TOTOP, padTop=8, text=self.controller.activeSystemDescription)
        shipRestrictionCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, top=16, minHeight=56)
        ItemIcon(parent=shipRestrictionCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(4, 0, 56, 56), showOmegaOverlay=False, typeID=SHIP_RESTRICTION_ICON_TYPE_ID)
        shipRestrictionInnerCont = ContainerAutoSize(parent=shipRestrictionCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 0, 0, 0))
        eveLabel.EveLabelLargeBold(parent=shipRestrictionInnerCont, align=uiconst.TOTOP, text=self.controller.shipRestrictionTitle)
        eveLabel.EveLabelMedium(parent=shipRestrictionInnerCont, align=uiconst.TOTOP, text=self.controller.shipRestrictionDescription)
        timerCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=64, top=16, bgColor=(0.3, 0.1, 0.1, 0.5))
        Timer(parent=timerCont, align=uiconst.TOPLEFT, pos=(20, 16, 48, 48), timerType=TimerType.Pvp)
        timerInnerCont = ContainerAutoSize(parent=timerCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 16, 16, 16))
        eveLabel.EveLabelMedium(parent=timerInnerCont, align=uiconst.TOTOP, text=self.controller.timerDescription)
        RandomJumpButton(parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, top=16), align=uiconst.CENTER, fixedheight=30, fixedwidth=120, controller=self.controller)

    def _FixHeight(self):
        content_height = self.mainCont.height + self.mainCont.padTop + self.mainCont.padBottom
        _, height = self.GetWindowSizeForContentSize(height=content_height)
        self.SetFixedHeight(height)

    def Close(self, *args, **kwargs):
        super(RandomJumpActivationWindow, self).Close(*args, **kwargs)
        self.controller.Close()

    def UpdateState(self):
        if self.controller.isFinished:
            uthread.new(self._AnimCloseWindow)

    def _AnimCloseWindow(self):
        animations.FadeOut(self.GetMainArea(), duration=0.3, sleep=True)
        self.CloseByUser()

    def Prepare_Header_(self):
        super(RandomJumpActivationWindow, self).Prepare_Header_()
