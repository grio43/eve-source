#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\voidspace\client\activation_window.py
from carbonui.uicore import uicore
import evetypes
import eveui
from carbonui.control.window import Window
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.crimewatch.crimewatchTimers import Timer, TimerType
from voidspace.client.client_validator import ClientVoidSpaceJumpValidator
from voidspace.client.void_space_activation_controller import VoidSpaceActivationController
from voidspace.client.void_space_jump_button import VoidSpaceJumpButton
SHIP_RESTRICTION_ICON_TYPE_ID = 44213

class VoidSpaceActivationWindow(Window):
    __guid__ = 'VoidSpaceActivationWindow'
    default_fixedWidth = 450
    default_fixedHeight = 450
    default_width = 450
    default_height = 450
    default_left = '__center__'
    default_top = '__center__'
    default_windowID = 'VoidSpaceActivationWindow'
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
            return cls(**attributes)
        item = attributes.get('item', None)
        if item.itemID == window._controller.itemID:
            window.Maximize()
            return window
        window.CloseByUser()
        return cls(**attributes)

    def ApplyAttributes(self, attributes):
        super(VoidSpaceActivationWindow, self).ApplyAttributes(attributes)
        self._controller = VoidSpaceActivationController(attributes.item, ClientVoidSpaceJumpValidator())
        self._updateThread = None
        self._Layout()
        self.SetCaption(evetypes.GetName(self._controller.typeID))
        self._controller.onChange.connect(self.UpdateState)
        self.UpdateState()

    def _Layout(self):
        self.HideHeader()
        self.bottomCont = eveui.Container(parent=self.GetMainArea(), align=eveui.Align.to_bottom, height=60)
        self.mainCont = eveui.Container(parent=self.GetMainArea(), align=eveui.Align.to_all, padding=(16, 16, 16, 0))
        self._ConstructInfo()
        self._ConstructRestrictions()
        self._ConstructTraceRestriction()
        self._ConstructKillTimerInfo()
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
        eveui.EveLabelLargeBold(parent=traceRestrictionInnerCont, align=eveui.Align.to_top, text=self._controller.traceDescriptionTitle)
        eveui.EveLabelMedium(parent=traceRestrictionInnerCont, align=eveui.Align.to_top, text=self._controller.traceDescription)

    def _ConstructKillTimerInfo(self):
        killTimerCont = eveui.ContainerAutoSize(parent=self.mainCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, minHeight=64, top=8, bgColor=(0.3, 0.1, 0.1, 0.5), callback=self._FixHeight)
        timer = Timer(parent=killTimerCont, align=eveui.Align.top_left, pos=(20, 16, 48, 48), timerType=TimerType.VoidSpaceContentExpiration)
        timer.state = eveui.State.disabled
        timerInnerCont = eveui.ContainerAutoSize(parent=killTimerCont, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=(76, 8, 8, 8), callback=self._FixHeight)
        eveui.EveLabelMedium(parent=timerInnerCont, align=eveui.Align.to_top, text=self._controller.killTimerDescription)

    def _ConstructButton(self):
        VoidSpaceJumpButton(parent=self.bottomCont, align=eveui.Align.center, fixedheight=28, fixedwidth=120, controller=self._controller)

    def _FixHeight(self):
        height = self.bottomCont.height
        height += self.mainCont.padTop + self.mainCont.padBottom
        for child in self.mainCont.children:
            height += uicore.ReverseScaleDpi(child.displayHeight) + child.top

        self.SetFixedHeight(height)
        self.SetHeight(height)

    def Close(self, *args, **kwargs):
        super(VoidSpaceActivationWindow, self).Close(*args, **kwargs)
        self._controller.Close()

    def UpdateState(self):
        if self._controller.isFinished:
            eveui.fade_out(self.GetMainArea(), duration=0.3, on_complete=self.CloseByUser)
