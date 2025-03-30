#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\abyss\AbyssJumpWindow.py
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveLabel
from carbonui.control.window import Window
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.crimewatch import crimewatchConst
from eve.client.script.ui.crimewatch.crimewatchTimers import Timer, TimerType
from eve.common.lib import appConst
import abyss
from abyss.client import ClientValidator
import blue
import dogma.const
import evetypes
import localization
import signals
import uthread
from eve.client.script.ui.shared.abyss.baseActivationController import BaseActivationController
from eve.client.script.ui.shared.abyss.activateButton import ActivateButton
from eve.client.script.ui.shared.abyss.const import TIER_DESCRIPTION_BY_TIER, WEATHER_DESCRIPTION_BY_TYPE
from eve.client.script.ui.shared.abyss.utils import GetAttribute

class JumpActivationController(BaseActivationController):

    def __init__(self, gateID, gameModeID, typeID):
        super(JumpActivationController, self).__init__(gateID, ClientValidator(abyss.get_game_mode(gameModeID), gate_id=gateID, type_id=typeID))

    def _Validate(self):
        self._validator.validate_jump()

    def _Activate(self):
        sm.GetService('sessionMgr').PerformSessionChange('JumpToAbyss', sm.GetService('abyss').activate_entrance_gate, self.itemID)
        self._isFinished = True

    def GetText(self):
        if self.isActivating:
            return localization.GetByLabel('UI/Abyss/Jumping')
        else:
            return localization.GetByLabel('UI/Abyss/Activate')


class AbyssEntranceWindowController(object):

    def __init__(self, gateID):
        ballpark = sm.GetService('michelle').GetBallpark()
        slimItem = ballpark.GetInvItem(gateID)
        self._itemID = gateID
        self._typeID = slimItem.abyssFilamentTypeID
        self._gameModeID = slimItem.gameModeID or abyss.GameModeID.UNKNOWN
        self.jumpController = JumpActivationController(gateID, self._gameModeID, self._typeID)
        self.onChange = signals.Signal(signalName='onChange')
        self.jumpController.onChange.connect(self.onChange)

    @property
    def itemID(self):
        return self._itemID

    @property
    def isFinished(self):
        return self.jumpController.isFinished

    @property
    def isSuspicious(self):
        return False

    @property
    def name(self):
        return evetypes.GetName(self.typeID)

    @property
    def suspectDescription(self):
        color = crimewatchConst.Colors.Suspect.GetHex()
        time = FmtDate(appConst.criminalTimerTimeout)
        return localization.GetByLabel('UI/Abyss/SuspectDescription', color=color, time=time)

    @property
    def tier(self):
        return GetAttribute(self.typeID, dogma.const.attributeDifficultyTier)

    @property
    def tierDescription(self):
        label = TIER_DESCRIPTION_BY_TIER[self.tier]
        return localization.GetByLabel(label)

    @property
    def timerDescription(self):
        color = crimewatchConst.Colors.Red.GetHex()
        time = FmtDate(abyss.DEFAULT_ABYSS_CONTENT_DURATION)
        return localization.GetByLabel('UI/Abyss/TimerDescription', color=color, time=time)

    @property
    def typeDescription(self):
        return localization.GetByLabel(abyss.get_game_mode(self._gameModeID).jump_description_label)

    @property
    def typeID(self):
        return self._typeID

    @property
    def weather(self):
        return GetAttribute(self.typeID, dogma.const.attributeWeatherID)

    @property
    def weatherDescription(self):
        label = WEATHER_DESCRIPTION_BY_TYPE[self.weather]
        return localization.GetByLabel(label)

    @property
    def weatherName(self):
        return evetypes.GetName(self.weather)

    def Close(self):
        self.jumpController.Close()
        self.onChange.clear()

    def GetKeyTypeID(self, gateID):
        ballpark = sm.GetService('michelle').GetBallpark()
        slimItem = ballpark.GetInvItem(gateID)
        return slimItem.abyssFilamentTypeID


class AbyssActivationWindow(Window):
    __guid__ = 'form.AbyssActivationWindow'
    default_fixedWidth = 420
    default_left = '__center__'
    default_top = '__center__'
    default_windowID = 'AbyssActivationWindow'
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
            return super(AbyssActivationWindow, cls).Open(**attributes)
        itemID = attributes.get('itemID', None)
        if itemID == window.controller.itemID:
            window.Maximize()
            return window
        window.CloseByUser()
        return super(AbyssActivationWindow, cls).Open(**attributes)

    def ApplyAttributes(self, attributes):
        super(AbyssActivationWindow, self).ApplyAttributes(attributes)
        self.controller = AbyssEntranceWindowController(attributes.item)
        self.Layout()
        self.SetCaption(evetypes.GetName(self.controller.typeID))
        self.controller.onChange.connect(self.UpdateState)

    def Layout(self):
        self.mainCont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, padding=0, callback=self._FixHeight, idx=0)
        filamentCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=64)
        ItemIcon(parent=filamentCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 64, 64), showOmegaOverlay=False, typeID=self.controller.typeID)
        filamentInnerCont = ContainerAutoSize(parent=filamentCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 0, 0, 0))
        eveLabel.EveLabelMedium(parent=filamentInnerCont, align=uiconst.TOTOP, text=self.controller.typeDescription)
        eveLabel.EveLabelMedium(parent=filamentInnerCont, align=uiconst.TOTOP, top=8, text=self.controller.tierDescription)
        weatherCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, top=16, alignMode=uiconst.TOTOP, minHeight=56)
        ItemIcon(parent=weatherCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(4, 0, 56, 56), showOmegaOverlay=False, typeID=self.controller.weather)
        weatherInnerCont = ContainerAutoSize(parent=weatherCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 0, 0, 0))
        eveLabel.EveLabelLargeBold(parent=weatherInnerCont, align=uiconst.TOTOP, text=self.controller.weatherName)
        eveLabel.EveLabelMedium(parent=weatherInnerCont, align=uiconst.TOTOP, text=self.controller.weatherDescription)
        timerCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=64, top=16, bgColor=(0.3, 0.1, 0.1, 0.5))
        Timer(parent=timerCont, align=uiconst.TOPLEFT, pos=(16, 16, 32, 32), timerType=TimerType.AbyssalContentExpiration)
        timerInnerCont = ContainerAutoSize(parent=timerCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 16, 16, 16))
        eveLabel.EveLabelMedium(parent=timerInnerCont, align=uiconst.TOTOP, text=self.controller.timerDescription)
        if self.controller.isSuspicious:
            suspectCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=64, top=16, bgColor=(0.3, 0.1, 0.1, 0.5))
            Timer(parent=suspectCont, align=uiconst.TOPLEFT, pos=(16, 16, 32, 32), timerType=TimerType.Suspect)
            suspectInnerCont = ContainerAutoSize(parent=suspectCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 16, 16, 16))
            eveLabel.EveLabelMedium(parent=suspectInnerCont, align=uiconst.TOTOP, text=self.controller.suspectDescription)
        ActivateButton(parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, top=16), align=uiconst.CENTER, fixedheight=30, fixedwidth=120, controller=self.controller.jumpController)

    def _FixHeight(self):
        content_height = self.mainCont.height + self.mainCont.padTop + self.mainCont.padBottom
        _, height = self.GetWindowSizeForContentSize(height=content_height)
        self.SetFixedHeight(height)

    def Close(self, *args, **kwargs):
        super(AbyssActivationWindow, self).Close(*args, **kwargs)
        self.controller.Close()

    def UpdateState(self):
        if self.controller.isFinished:
            uthread.new(self._AnimCloseWindow)

    def _AnimCloseWindow(self):
        blue.pyos.synchro.SleepWallclock(1000)
        animations.FadeOut(self.GetMainArea(), duration=0.3, sleep=True)
        self.CloseByUser()
