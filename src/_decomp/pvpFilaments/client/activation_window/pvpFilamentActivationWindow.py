#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\activation_window\pvpFilamentActivationWindow.py
import uthread2
from carbonui.uicore import uicore
import evetypes
import eveui
from carbonui.control.window import Window
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.crimewatch.crimewatchTimers import Timer, TimerType
from .clientPVPfilamentValidator import ClientPVPFilamentValidator
from .pvpFilamentController import PVPFilamentActivationController
from .pvpFilamentJumpButton import PVPFilamentJumpButton
SHIP_RESTRICTION_ICON_TYPE_ID = 44213

class PVPFilamentActivationWindow(Window):
    __guid__ = 'PVPFilamentActivationWindow'
    default_fixedWidth = 450
    default_fixedHeight = 450
    default_width = 450
    default_height = 450
    default_left = '__center__'
    default_top = '__center__'
    default_windowID = 'PVPFilamentActivationWindow'
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
            return super(PVPFilamentActivationWindow, cls).Open(**attributes)
        item = attributes.get('item', None)
        if item.itemID == window._controller.itemID:
            window.Maximize()
            return window
        window.CloseByUser()
        return super(PVPFilamentActivationWindow, cls).Open(**attributes)

    def ApplyAttributes(self, attributes):
        super(PVPFilamentActivationWindow, self).ApplyAttributes(attributes)
        self._controller = PVPFilamentActivationController(attributes.item, ClientPVPFilamentValidator())
        self._updateThread = None
        if self._controller.is_event_active:
            self._Layout()
            self.SetCaption(evetypes.GetName(self._controller.typeID))
            self._controller.onChange.connect(self.UpdateState)
            self.UpdateState()
        else:
            self._inactive_window()

    def _inactive_window(self):
        eveui.EveCaptionLarge(parent=self.GetMainArea(), align=eveui.Align.center_top, text=self._controller.inActiveText, maxWidth=400, top=180)
        eveui.Sprite(parent=self.GetMainArea(), align=eveui.Align.center, top=-60, height=64, width=64, texturePath='res:/ui/Texture/WindowIcons/provingGrounds.png')

    def _Layout(self):
        self.HideHeader()
        self.bottomCont = eveui.Container(parent=self.GetMainArea(), align=eveui.Align.to_bottom, height=60)
        self.mainCont = eveui.Container(parent=self.GetMainArea(), align=eveui.Align.to_all, padding=(16, 16, 16, 0))
        self._ConstructInfo()
        self._ConstructRestrictions()
        self._ConstructTraceRestriction()
        self._ConstructKillTimerInfo()
        self._ConstructInQueue()
        self._ConstructButton()

    def _ConstructInfo(self):
        filamentCont = eveui.ContainerAutoSize(parent=self.mainCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, minHeight=72, callback=self._FixHeight)
        ItemIcon(parent=filamentCont, align=eveui.Align.top_left, state=eveui.State.disabled, pos=(4, 4, 64, 64), showOmegaOverlay=False, typeID=self._controller.typeID)
        filamentInnerCont = eveui.ContainerAutoSize(parent=filamentCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=(76, 8, 8, 8), callback=self._FixHeight)
        eveui.EveCaptionMedium(parent=filamentInnerCont, align=eveui.Align.to_top, text=self._controller.name)
        eveui.EveLabelMedium(parent=filamentInnerCont, align=eveui.Align.to_top, text=self._controller.typeDescription)

    def _ConstructRestrictions(self):
        shipRestrictionCont = eveui.ContainerAutoSize(parent=self.mainCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, minHeight=64, callback=self._FixHeight)
        ItemIcon(parent=shipRestrictionCont, align=eveui.Align.top_left, state=eveui.State.disabled, pos=(8, 4, 56, 56), showOmegaOverlay=False, typeID=SHIP_RESTRICTION_ICON_TYPE_ID)
        shipRestrictionInnerCont = eveui.ContainerAutoSize(parent=shipRestrictionCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=(76, 8, 8, 8), callback=self._FixHeight)
        eveui.EveLabelLargeBold(parent=shipRestrictionInnerCont, align=eveui.Align.to_top, text=self._controller.shipRestrictionTitle)
        eveui.EveLabelMedium(parent=shipRestrictionInnerCont, align=eveui.Align.to_top, text=self._controller.shipRestrictionDescription)

    def _ConstructTraceRestriction(self):
        traceRestrictionCont = eveui.ContainerAutoSize(parent=self.mainCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, minHeight=64, callback=self._FixHeight)
        eveui.Sprite(parent=traceRestrictionCont, align=eveui.Align.top_left, state=eveui.State.disabled, pos=(8, 4, 56, 56), showOmegaOverlay=False, texturePath='res:/ui/Texture/WindowIcons/abyssalFilament.png')
        traceRestrictionInnerCont = eveui.ContainerAutoSize(parent=traceRestrictionCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=(76, 8, 8, 8), callback=self._FixHeight)
        eveui.EveLabelLargeBold(parent=traceRestrictionInnerCont, align=eveui.Align.to_top, text=self._controller.traceRestrictionTitle)
        eveui.EveLabelMedium(parent=traceRestrictionInnerCont, align=eveui.Align.to_top, text=self._controller.traceRestrictionDescription)

    def _ConstructKillTimerInfo(self):
        killTimerCont = eveui.ContainerAutoSize(parent=self.mainCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, minHeight=64, top=8, bgColor=(0.3, 0.1, 0.1, 0.5), callback=self._FixHeight)
        timer = Timer(parent=killTimerCont, align=eveui.Align.top_left, pos=(20, 16, 48, 48), timerType=TimerType.AbyssalPvpExpiration)
        timer.state = eveui.State.disabled
        timerInnerCont = eveui.ContainerAutoSize(parent=killTimerCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=(76, 8, 8, 8), callback=self._FixHeight)
        eveui.EveLabelMedium(parent=timerInnerCont, align=eveui.Align.to_top, text=self._controller.killTimerDescription)

    def _ConstructInQueue(self):
        self.inQueueContainer = container = eveui.Container(state=eveui.State.normal, parent=self.mainCont, top=8, align=eveui.Align.to_top, opacity=0)
        leftContainer = eveui.Container(parent=container, align=eveui.Align.to_left, width=76)
        timer = Timer(parent=leftContainer, align=eveui.Align.center, timerType=TimerType.JumpCloak, height=32, width=32)
        timer.state = eveui.State.disabled
        rightContainer = eveui.Container(parent=container, align=eveui.Align.to_top, height=50)
        eveui.EveLabelLargeBold(parent=rightContainer, align=eveui.Align.to_top, text=self._controller.estimatedQueueTimeTitle)
        inQueueCont = eveui.Container(parent=rightContainer, align=eveui.Align.to_top, height=16)
        eveui.EveLabelMedium(parent=inQueueCont, align=eveui.Align.to_left, padRight=4, text=self._controller.timeInqueueLabel)
        self.timeInQueue = eveui.EveLabelMedium(parent=inQueueCont, align=eveui.Align.to_all, text='')
        estimatedCont = eveui.Container(parent=rightContainer, align=eveui.Align.to_top, height=16)
        eveui.EveLabelMedium(parent=estimatedCont, align=eveui.Align.to_left, padRight=4, text=self._controller.estimatedTimeLabel)
        self.estimatedTime = eveui.EveLabelMedium(parent=estimatedCont, align=eveui.Align.to_all, text='')

    def _ConstructButton(self):
        PVPFilamentJumpButton(parent=self.bottomCont, align=eveui.Align.center, fixedheight=28, fixedwidth=120, controller=self._controller)
        button = eveui.Button(parent=self.bottomCont, align=eveui.Align.center_right, left=20, texturePath='res:/ui/Texture/WindowIcons/provingGrounds.png', func=self._OpenInfoWindow, hint=self._controller.provingGroundsHint)
        button.width = 32

    def _OpenInfoWindow(self, *args, **kwargs):
        sm.GetService('pvpFilamentSvc').OpenPVPFilamentEventWindow(self._controller.typeID)

    def _FixHeight(self):
        height = self.bottomCont.height
        height += self.mainCont.padTop + self.mainCont.padBottom
        for child in self.mainCont.children:
            height += uicore.ReverseScaleDpi(child.displayHeight) + child.top

        self.SetFixedHeight(height)
        self.SetHeight(height)

    def Close(self, *args, **kwargs):
        super(PVPFilamentActivationWindow, self).Close(*args, **kwargs)
        self._controller.Close()

    def UpdateState(self):
        if self._controller.isFinished:
            eveui.fade_out(self.GetMainArea(), duration=0.3, on_complete=self.CloseByUser)
        if self._controller.isInQueue and not self._controller.isFinished:
            self.estimatedTime.text = self._controller.estimatedQueueTime
            if not self._updateThread:
                self._updateThread = uthread2.start_tasklet(self._UpdateRoutine)
                eveui.animate(self.inQueueContainer, 'height', end_value=50, duration=0.3)
                eveui.fade_in(self.inQueueContainer, duration=0.3, time_offset=0.2)
        else:
            eveui.fade_out(self.inQueueContainer, duration=0.2)
            eveui.animate(self.inQueueContainer, 'height', end_value=0, duration=0.3)

    def _UpdateRoutine(self):
        while not self.destroyed:
            if not self._controller.isInQueue or self._controller.isFinished:
                break
            self.timeInQueue.text = self._controller.timeInQueue
            uthread2.sleep(1)

        self._updateThread = None
