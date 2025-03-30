#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\abyss\keyActivationWindow.py
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.control.combo import Combo
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

class DeployActivationController(BaseActivationController):

    def __init__(self, key, game_mode_id):
        self._gameMode = abyss.get_game_mode(game_mode_id)
        self._typeID = key.typeID
        super(DeployActivationController, self).__init__(key.itemID, ClientValidator(self._gameMode, key=key))

    @property
    def tier(self):
        return GetAttribute(self.typeID, dogma.const.attributeDifficultyTier)

    @property
    def typeID(self):
        return self._typeID

    @property
    def weather(self):
        return GetAttribute(self.typeID, dogma.const.attributeWeatherID)

    def _Validate(self):
        self._validator.validate_deploy()

    def _Activate(self):
        if self._gameMode.should_jump_on_deploy:
            sm.GetService('sessionMgr').PerformSessionChange('JumpToAbyss', sm.GetService('abyss').deploy_entrance_gate, self.itemID, self._gameMode.id)
        else:
            sm.GetService('abyss').deploy_entrance_gate(self.itemID, self._gameMode.id)
        self._isFinished = True

    def GetText(self):
        raise NotImplementedError


class CoOpActivationController(DeployActivationController):

    def __init__(self, key):
        super(CoOpActivationController, self).__init__(key, abyss.GameModeID.COOP)

    def GetText(self):
        if self.isActivating:
            return localization.GetByLabel('UI/Abyss/Deploying')
        else:
            return localization.GetByLabel('UI/Abyss/Fleet')


class TwoPlayerActivationController(DeployActivationController):

    def __init__(self, key):
        super(TwoPlayerActivationController, self).__init__(key, abyss.GameModeID.TWO_PLAYER)

    def GetText(self):
        if self.isActivating:
            return localization.GetByLabel('UI/Abyss/Deploying')
        else:
            return localization.GetByLabel('UI/Abyss/Fleet')


class SoloActivationController(DeployActivationController):

    def __init__(self, key):
        super(SoloActivationController, self).__init__(key, abyss.GameModeID.SOLO)

    def GetText(self):
        if self.isActivating:
            return localization.GetByLabel('UI/Abyss/Jumping')
        else:
            return localization.GetByLabel('UI/Abyss/Activate')


class KeyActivationController(object):

    def __init__(self, key):
        self._itemID = key.itemID
        self._typeID = key.typeID
        self.onChange = signals.Signal(signalName='onChange')
        self.coOpActivationController = CoOpActivationController(key)
        self.twoPlayerActivationController = TwoPlayerActivationController(key)
        self.activationController = SoloActivationController(key)
        self.activationController.onChange.connect(self.onChange)
        self.coOpActivationController.onChange.connect(self.onChange)
        self.twoPlayerActivationController.onChange.connect(self.onChange)

    @property
    def itemID(self):
        return self._itemID

    @property
    def isFinished(self):
        return self.activationController.isFinished or self.coOpActivationController.isFinished or self.twoPlayerActivationController.isFinished

    @property
    def isSuspicious(self):
        return self.activationController.isSuspicious

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
        self.coOpActivationController.Close()
        self.activationController.Close()
        self.twoPlayerActivationController.Close()
        self.onChange.clear()


class KeyActivationWindow(Window):
    __guid__ = 'form.KeyActivationWindow'
    default_fixedWidth = 420
    default_left = '__center__'
    default_top = '__center__'
    default_windowID = 'KeyActivationWindow'
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
            return super(KeyActivationWindow, cls).Open(**attributes)
        itemID = attributes.get('itemID', None)
        if itemID == window.controller.itemID:
            window.Maximize()
            return window
        window.CloseByUser()
        return super(KeyActivationWindow, cls).Open(**attributes)

    def ApplyAttributes(self, attributes):
        super(KeyActivationWindow, self).ApplyAttributes(attributes)
        self.gameModeControllers = {}
        self.activeGameMode = None
        self.controller = KeyActivationController(attributes.item)
        self.Layout()
        self.SetCaption(evetypes.GetName(self.controller.typeID))
        self.controller.onChange.connect(self.UpdateState)
        self.activeGameMode = self.gameModeControllers[self.GetDefaultGameModeSetting()]
        self.gameModeControllers[self.GetDefaultGameModeSetting()].state = uiconst.UI_NORMAL

    def Layout(self):
        self.mainCont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, callback=self._FixHeight)
        self.mainCont.DisableAutoSize()
        filamentCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=64)
        ItemIcon(parent=filamentCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 64, 64), showOmegaOverlay=False, typeID=self.controller.typeID)
        filamentInnerCont = ContainerAutoSize(parent=filamentCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 0, 0, 0))
        eveLabel.EveLabelMedium(parent=filamentInnerCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Abyss/FilamentSoloAndFleetShortDescription'))
        eveLabel.EveLabelMedium(parent=filamentInnerCont, align=uiconst.TOTOP, top=8, text=self.controller.tierDescription)
        weatherCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, top=16, minHeight=56)
        ItemIcon(parent=weatherCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(4, 0, 56, 56), showOmegaOverlay=False, typeID=self.controller.weather)
        weatherInnerCont = ContainerAutoSize(parent=weatherCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 0, 0, 0))
        eveLabel.EveLabelLargeBold(parent=weatherInnerCont, align=uiconst.TOTOP, text=self.controller.weatherName)
        eveLabel.EveLabelMedium(parent=weatherInnerCont, align=uiconst.TOTOP, text=self.controller.weatherDescription)
        timerCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, top=16, bgColor=(0.3, 0.1, 0.1, 0.5))
        Timer(parent=timerCont, align=uiconst.TOPLEFT, pos=(16, 16, 32, 32), timerType=TimerType.AbyssalContentExpiration)
        timerInnerCont = ContainerAutoSize(parent=timerCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 16, 16, 16))
        eveLabel.EveLabelMedium(parent=timerInnerCont, align=uiconst.TOTOP, text=self.controller.timerDescription)
        if self.controller.isSuspicious:
            suspectCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=64, top=8, bgColor=(0.3, 0.1, 0.1, 0.5))
            Timer(parent=suspectCont, align=uiconst.TOPLEFT, pos=(16, 16, 32, 32), timerType=TimerType.Suspect)
            suspectInnerCont = ContainerAutoSize(parent=suspectCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(70, 16, 16, 16))
            eveLabel.EveLabelMedium(parent=suspectInnerCont, align=uiconst.TOTOP, text=self.controller.suspectDescription)
        self.bottomCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, padTop=16)
        Combo(name='abyssGameModeCombo', parent=ContainerAutoSize(parent=self.bottomCont, align=uiconst.TOTOP, padBottom=16), align=uiconst.CENTER, height=30, width=140, options=self.GetAbyssGameModeOptions(), callback=self.OnGameModeChanged, select=self.GetDefaultGameModeSetting())
        self.gameModeControllers[1] = ActivateButton(parent=ContainerAutoSize(parent=self.bottomCont, align=uiconst.TOTOP), align=uiconst.CENTER, state=uiconst.UI_HIDDEN, fixedheight=30, fixedwidth=140, controller=self.controller.activationController)
        self.gameModeControllers[2] = ActivateButton(parent=ContainerAutoSize(parent=self.bottomCont, align=uiconst.TOTOP), align=uiconst.CENTER, state=uiconst.UI_HIDDEN, fixedheight=30, fixedwidth=140, controller=self.controller.twoPlayerActivationController)
        self.gameModeControllers[3] = ActivateButton(parent=ContainerAutoSize(parent=self.bottomCont, align=uiconst.TOTOP), align=uiconst.CENTER, state=uiconst.UI_HIDDEN, fixedheight=30, fixedwidth=140, controller=self.controller.coOpActivationController)
        self.mainCont.EnableAutoSize()

    def _FixHeight(self):
        content_height = self.mainCont.height + self.mainCont.padTop + self.mainCont.padBottom
        _, height = self.GetWindowSizeForContentSize(height=content_height)
        self.SetFixedHeight(height)

    def Close(self, *args, **kwargs):
        super(KeyActivationWindow, self).Close(*args, **kwargs)
        self.controller.Close()

    def UpdateState(self):
        if self.controller.isFinished:
            uthread.new(self._AnimCloseWindow)

    def _AnimCloseWindow(self):
        blue.pyos.synchro.SleepWallclock(1000)
        animations.FadeOut(self.GetMainArea(), duration=0.3, sleep=True)
        self.CloseByUser()

    def GetAbyssGameModeOptions(self):
        cruiser = localization.GetByLabel('UI/Abyss/cruiserSelection')
        destroyer = localization.GetByLabel('UI/Abyss/destroyerSelection')
        frigate = localization.GetByLabel('UI/Abyss/frigateSelection')
        return ((cruiser,
          1,
          None,
          'res:/UI/Texture/Shared/Brackets/cruiser_16.png'), (destroyer,
          2,
          None,
          'res:/UI/Texture/Shared/Brackets/destroyer_16.png'), (frigate,
          3,
          None,
          'res:/UI/Texture/Shared/Brackets/frigate_16.png'))

    def OnGameModeChanged(self, comboBox, key, value):
        self.activeGameMode.state = uiconst.UI_HIDDEN
        self.activeGameMode = self.gameModeControllers[value]
        self.gameModeControllers[value].state = uiconst.UI_NORMAL
        self.SetDefaultGameModeSetting(value)

    def GetDefaultGameModeSetting(self):
        return settings.char.ui.Get('abyssGameModeSetting', 1)

    def SetDefaultGameModeSetting(self, gameModeSetting):
        return settings.char.ui.Set('abyssGameModeSetting', gameModeSetting)


def __SakeReloadHook():
    try:
        instance = KeyActivationWindow.GetIfOpen()
        if instance:
            KeyActivationWindow.Reload(instance)
    except Exception:
        import log
        log.LogException()
