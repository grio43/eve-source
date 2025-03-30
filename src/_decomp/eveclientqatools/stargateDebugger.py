#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\stargateDebugger.py
import copy
import logging
import os
import blue
import carbonui.const as uiconst
import evegraphics.gateLogoConst as lconst
import geo2
import uthread2
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from carbonui.control.window import Window
log = logging.getLogger(__name__)
UNSELECTED_ELEMENT = (None, 'UNSELECTED')

def DictToListTuple(dictionary):
    return [ (key, value) for key, value in dictionary.items() ]


def FindIndexFromKey(wantedKey, listOfTuples, default = 0):
    return next((index for index, value in enumerate(listOfTuples) if value[0] == wantedKey), default)


class StargateDebuggerModel(object):

    def __init__(self, gateEffectEventNames):
        self.gateEffectEventNames = gateEffectEventNames
        self.systemStatusIcons = [UNSELECTED_ELEMENT] + lconst.SYSTEM_STATUS_ICONS.items()
        self.factionBanners = [UNSELECTED_ELEMENT] + lconst.FACTION_BANNERS.items()
        self.warningIcons = [UNSELECTED_ELEMENT, (lconst.BANNER_TRAFFIC_WARNING, 'Travel Warning'), (lconst.TRIGLAVIAN_TRAVEL_WARNING, 'Triglavian warning')]

    def GetSystemStatusIcon(self, iconName):
        firstMatch = next((x for x in self.systemStatusIcons if x[0] == iconName), UNSELECTED_ELEMENT)
        return firstMatch

    def GetSystemStatusIconPath(self, iconName):
        return os.path.join(lconst.SYSTEM_STATUS_DIR, self.GetSystemStatusIcon(iconName))

    def GetFactionBanner(self, factionName):
        firstMatch = next((x for x in self.factionBanners if x[0] == factionName), UNSELECTED_ELEMENT)
        return firstMatch

    def GetFactionBannerPath(self, factionName):
        return os.path.join(lconst.FACTION_BANNER_DIR, self.GetSystemStatusIcon(factionName))


class StargateDebuggerView(object):

    def __init__(self, model):
        self.model = model
        self.name = 'Stargate Debugger'
        self.upperLeftContainer = None
        self.upperRightContainer = None
        self.lowerLeftContainer = None
        self.lowerRightContainer = None
        self.controllerDelegate = None
        self.destinationAllianceCombo = None
        self.originAllianceCombo = None
        self.warningCombo = None
        self.logoCombos = []
        self.wnd = None
        self.controllerVariables = None
        self.animationStateCombo = None
        self.resetButton = None

    def Setup(self, bannerModel):
        wnd = Window.Open()
        wnd.SetMinSize([600, 370])
        wnd.SetCaption(self.name)
        wnd._OnClose = self.controllerDelegate.OnClose
        main = wnd.GetMainArea()
        self.wnd = wnd
        self._SetupContainers(main)
        self._AddAnimationStateCombobox(self.lowerLeftContainer)
        self._AddBannerComboboxes(bannerModel)
        self._AddResetButton()
        for eventName in self.model.gateEffectEventNames:
            self._AddEventHandlerButtons(eventName)

    def _SetupContainers(self, main):
        upperContainer = Container(name='upperContainer', parent=main, align=uiconst.TOTOP, height=200, width=600)
        self.upperLeftContainer = Container(name='upperLeftContainer', parent=upperContainer, align=uiconst.TOLEFT, padTop=10, padBottom=10, padLeft=10, padRight=10, height=200, width=300)
        self.upperRightContainer = Container(name='upperRightContainer', parent=upperContainer, align=uiconst.TOLEFT, padTop=10, padBottom=10, padLeft=10, padRight=10, height=200, width=300)
        lowerContainer = Container(name='lowerContainer', parent=main, align=uiconst.TOTOP, height=140, width=600)
        self.lowerLeftContainer = Container(name='lowerLeftContainer', parent=lowerContainer, align=uiconst.TOLEFT, padLeft=10, padRight=10, height=140, width=300)
        self.lowerRightContainer = Container(name='lowerRightContainer', parent=lowerContainer, align=uiconst.TOLEFT, padLeft=10, padRight=10, height=140, width=300)

    def _AddAnimationStateCombobox(self, lowerContainer):
        self.animationStateCombo = self._CreateCombo(name='AnimationState', values=[ str(i) for i in range(0, len(self.controllerDelegate.animVar.enumValues.split(','))) ], callback=self.controllerDelegate.AnimationChanged, select=2, label='Animation state', parent=lowerContainer, padBottom=8)

    def _AddEventHandlerButtons(self, eventName):
        eventHandlerButtonContainer = self._CreateContainer('eventHandler', self.lowerLeftContainer, padTop=8)
        eventButton = Button(name=eventName, align=uiconst.TOLEFT, parent=eventHandlerButtonContainer, label=eventName, func=self.controllerDelegate.PlayEventOnGate(eventName, 1), height=30, width=100)
        eventButton50 = Button(name='x50', align=uiconst.TOLEFT, parent=eventHandlerButtonContainer, label='x50', func=self.controllerDelegate.PlayEventOnGate(eventName, 50), height=30, width=100)

    def _AddResetButton(self):
        resetButtonContainer = self._CreateContainer('Reset', self.lowerRightContainer)
        self.resetButton = Button(name='Reset', align=uiconst.TOLEFT, parent=resetButtonContainer, label='Reset All', func=self.controllerDelegate.ResetState, height=30, width=100)

    def _AddBannerComboboxes(self, bannerModel):
        self.destinationAllianceCombo = self._CreateCombo(name='DestinationAllianceCombo', values=[ value for key, value in self.model.factionBanners ], callback=self.controllerDelegate.DestinationAllianceChanged, select=FindIndexFromKey(bannerModel.destAllianceID, self.model.factionBanners), label='Destination Alliance Banner', parent=self.upperLeftContainer)
        self.originAllianceCombo = self._CreateCombo(name='DestinationAllianceCombo', values=[ value for key, value in self.model.factionBanners ], callback=self.controllerDelegate.OriginAllianceChanged, select=FindIndexFromKey(bannerModel.originAllianceID, self.model.factionBanners), label='Origin Alliance Banner', parent=self.upperLeftContainer)
        self.warningCombo = self._CreateCombo(name='WarningCombo', values=[ value for key, value in self.model.warningIcons ], callback=self.controllerDelegate.SystemWarningChanged, select=FindIndexFromKey(bannerModel.targetSystemWarningIcon, self.model.warningIcons), label='Warning Logos', parent=self.upperLeftContainer)
        for i in range(0, len(bannerModel.logoList)):
            logoCombo = self._CreateCombo(name='Logo ' + str(i), values=[ value for key, value in self.model.systemStatusIcons ], callback=self.controllerDelegate.LogoListChanged(i), select=FindIndexFromKey(bannerModel.logoList[i], self.model.systemStatusIcons), label='Side Logo ' + str(i), parent=self.upperRightContainer)
            self.logoCombos.append(logoCombo)

    def _CreateCombo(self, name, values, callback, select, label, parent, align = uiconst.TOLEFT, width = 220, padBottom = 0):
        container = self._CreateContainer(name, parent, padBottom=padBottom)
        return Combo(name=name + '_combo', align=align, width=width, height=18, parent=container, label=label, options=[ (name, i) for i, name in enumerate(values) ], callback=callback, select=select)

    def _CreateContainer(self, name, parent, padTop = 16, padBottom = 0, align = uiconst.TOTOP):
        return Container(name=name + '_container', parent=parent, align=align, height=18, padTop=padTop, padBottom=padBottom, padLeft=5, padRight=5)


class StargateDebuggerViewController(object):
    maxDistanceFromGate = 800000

    def __init__(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        self.stargateBall = bp.GetBall(itemID)
        try:
            starGateModel = self.stargateBall.model
            self.animVar = starGateModel.controllers[0].variables[0]
            self.initialAnimationState = self.animVar.value
        except IndexError as error:
            log.error('Error when indexing when finding stargate animation variable. Most likely stargate setup assumptions changed' + str(error))
            raise
        except Exception as error:
            log.error('Error when finding stargate animation variable. Most likely stargate setup assumptions changed' + str(error))
            raise

        self.model = StargateDebuggerModel(self._FindGateEffectEventNames(starGateModel))
        self.view = StargateDebuggerView(self.model)
        self.view.controllerDelegate = self
        self.initialBannerModel = self._ExtendLogos(self.stargateBall.bannerModel)
        self.bannerModel = self._ExtendLogos(self.stargateBall.bannerModel)
        self.closeTasklet = None
        self.originalSetBannerMethod = self.stargateBall.SetupStargateBanners

    def ShowUI(self):
        self.view.Setup(self.bannerModel)
        self.closeTasklet = uthread2.StartTasklet(self._CheckIfShouldClose)
        self._DisableSlimItemUpdateMethod()

    def _DisableSlimItemUpdateMethod(self):

        def SetStargateBannerReplacement(stargateBanner):
            pass

        self.stargateBall.SetupStargateBanners = SetStargateBannerReplacement

    def PlayEventOnGate(self, eventName, times):

        def _PlayEventOnGate(*args):
            for _ in range(0, times):
                self.stargateBall.model.HandleControllerEvent(eventName)

        return _PlayEventOnGate

    def AnimationChanged(self, comboBox, value, index):
        self.animVar.value = int(index)

    def SystemWarningChanged(self, comboBox, value, index):
        self.bannerModel.targetSystemWarningIcon = self.model.warningIcons[index][0]
        self.SetChange()

    def DestinationAllianceChanged(self, comboBox, value, index):
        self.bannerModel.destAllianceID = self.model.factionBanners[index][0]
        self.SetChange()

    def OriginAllianceChanged(self, comboBox, value, index):
        self.bannerModel.originAllianceID = self.model.factionBanners[index][0]
        self.SetChange()

    def LogoListChanged(self, logoIndex):

        def LogoListChangedSub(comboBox, value, index):
            self.bannerModel.logoList[logoIndex] = self.model.systemStatusIcons[index][0]
            self.SetChange()

        return LogoListChangedSub

    def SetChange(self):
        self.originalSetBannerMethod(self.bannerModel)

    def ResetState(self, *args):
        self.bannerModel = copy.deepcopy(self.initialBannerModel)
        self.SetChange()
        self.animVar.value = self.initialAnimationState
        self.view.animationStateCombo.SelectItemByIndex(int(self.animVar.value))
        self.SetBannerSelectionToState(self.initialBannerModel)

    def SetBannerSelectionToState(self, bannerModel):
        destAllianceSelection = FindIndexFromKey(bannerModel.destAllianceID, self.model.factionBanners)
        self.view.destinationAllianceCombo.SelectItemByIndex(destAllianceSelection)
        originAllianceSelection = FindIndexFromKey(bannerModel.originAllianceID, self.model.factionBanners)
        self.view.originAllianceCombo.SelectItemByIndex(originAllianceSelection)
        systemWarningSelection = FindIndexFromKey(bannerModel.targetSystemWarningIcon, self.model.warningIcons)
        self.view.warningCombo.SelectItemByIndex(systemWarningSelection)
        for i, combo in enumerate(self.view.logoCombos):
            logoSelection = FindIndexFromKey(bannerModel.logoList[i], self.model.systemStatusIcons)
            combo.SelectItemByIndex(logoSelection)

    def OnClose(self, *args):
        self.ResetState()
        if self.stargateBall is not None:
            self.stargateBall.SetupStargateBanners = self.originalSetBannerMethod
            self.stargateBall = None

    def _CheckIfShouldClose(self):
        while self.stargateBall is not None and hasattr(self.stargateBall.model, 'worldPosition') and geo2.Vec2Length(self.stargateBall.model.worldPosition) < self.maxDistanceFromGate:
            blue.synchro.SleepWallclock(5000)

        self.view.wnd.Close()

    def _FindGateEffectEventNames(self, starGateModel):
        effectNames = []
        for child in starGateModel.effectChildren:
            for controller in child.controllers:
                for eventHandler in controller.eventHandlers:
                    lowerName = eventHandler.name.lower()
                    if lowerName == 'arrival' or lowerName == 'departure':
                        effectNames.append(eventHandler.name)

        return effectNames

    def _ExtendLogos(self, bannerModel):
        needed = 5 - len(bannerModel.logoList)
        newBannerModel = copy.deepcopy(bannerModel)
        newBannerModel.logoList = newBannerModel.logoList + [-1] * needed
        return newBannerModel
