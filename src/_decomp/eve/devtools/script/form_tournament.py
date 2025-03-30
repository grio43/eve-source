#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\form_tournament.py
import math
import operator
from collections import defaultdict, OrderedDict
import blue
import dogma.const
import dogma.data
import evetypes
import tournamentmanagement.const as tourneyConst
import tournamentmanagement.tournamentTimerFormatter as tournamentTimer
import uthread
from carbon.common.script.net import moniker
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from destructionEffect import destructionType as destructionEffectType
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.control.button import Button
from carbonui.control.window import Window
from eve.common.lib import appConst
from eveexceptions import ExceptionEater, UserError
from eveprefs import prefs
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler
from tournamentmanagement.client.tournamentDropShadowElement import DropShadowElement
DEFAULT_FANCY_UI_BACKGROUND = 'Fancy_NoLogo_UI_Background.png'
FANCY_BACKGROUND_PATH = 'res:/UI/Texture/Tournament/'
fancyBackgroundOptions = [('Default', DEFAULT_FANCY_UI_BACKGROUND)]
ICON_ID_BY_EFFECT_ID = {dogma.const.effectShipModuleFocusedWarpDisruptionScript: appConst.iconModuleWarpScrambler,
 dogma.const.effectShipModuleFocusedWarpScramblingScript: appConst.iconModuleWarpScramblerMWD,
 dogma.const.effectEwTargetPaint: appConst.iconModuleTargetPainter,
 dogma.const.effectTargetMaxTargetRangeAndScanResolutionBonusHostile: appConst.iconModuleSensorDamper,
 dogma.const.effectTargetGunneryMaxRangeAndTrackingSpeedBonusHostile: appConst.iconModuleTrackingDisruptor,
 dogma.const.effectTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile: appConst.iconModuleTrackingDisruptor,
 dogma.const.effectTurretWeaponRangeFalloffTrackingSpeedMultiplyTargetHostile: appConst.iconModuleTrackingDisruptor,
 dogma.const.effectEntitySensorDampen: appConst.iconModuleSensorDamper,
 dogma.const.effectSensorBoostTargetedHostile: appConst.iconModuleSensorDamper,
 dogma.const.effectNpcEntityTrackingDisruptor: appConst.iconModuleTrackingDisruptor,
 dogma.const.effectGuidanceDisrupt: appConst.iconModuleGuidanceDisruptor,
 dogma.const.effectEntityTargetPaint: appConst.iconModuleTargetPainter,
 dogma.const.effectDecreaseTargetSpeed: appConst.iconModuleStasisWeb,
 dogma.const.effectWarpScrambleForEntity: appConst.iconModuleWarpScrambler,
 dogma.const.effectModifyTargetSpeed2: appConst.iconModuleStasisWeb,
 dogma.const.effectConcordWarpScramble: appConst.iconModuleWarpScrambler,
 dogma.const.effectConcordModifyTargetSpeed: appConst.iconModuleStasisWeb,
 dogma.const.effectWarpScrambleBlockMWDWithNPCEffect: appConst.iconModuleWarpScramblerMWD,
 dogma.const.effectWarpDisruptSphere: appConst.iconModuleFocusedWarpScrambler,
 dogma.const.effectLeech: appConst.iconModuleNosferatu,
 dogma.const.effectEnergyDestabilizationNew: appConst.iconModuleEnergyNeutralizer,
 dogma.const.effectEntityCapacitorDrain: appConst.iconModuleEnergyNeutralizer,
 dogma.const.effectEnergyDestabilizationForStructure: appConst.iconModuleEnergyNeutralizer,
 dogma.const.effectEnergyNeutralizerFalloff: appConst.iconModuleEnergyNeutralizer,
 dogma.const.effectEnergyNosferatuFalloff: appConst.iconModuleNosferatu,
 dogma.const.effectWarpScrambleForStructure: appConst.iconModuleWarpScrambler,
 dogma.const.effectDecreaseTargetSpeedForStructures: appConst.iconModuleStasisWeb,
 dogma.const.effectEssWarpScramble: appConst.iconModuleWarpScrambler,
 dogma.const.effectWarpScrambleTargetMWDBlockActivationForEntity: appConst.iconModuleWarpScramblerMWD,
 dogma.const.effectEwTestEffectJam: appConst.iconModuleECM,
 dogma.const.effectEntityTargetJam: appConst.iconModuleECM,
 dogma.const.effectFighterAbilityECM: appConst.iconModuleECM,
 dogma.const.effectFighterAbilityEnergyNeutralizer: appConst.iconModuleEnergyNeutralizer,
 dogma.const.effectFighterAbilityStasisWebifier: appConst.iconModuleStasisWeb,
 dogma.const.effectFighterAbilityWarpDisruption: appConst.iconModuleWarpScrambler,
 dogma.const.effectFighterAbilityTackle: appConst.iconModuleFighterTackle,
 dogma.const.effectRemoteSensorDampFalloff: appConst.iconModuleSensorDamper,
 dogma.const.effectRemoteTargetPaintFalloff: appConst.iconModuleTargetPainter,
 dogma.const.effectShipModuleTrackingDisruptor: appConst.iconModuleTrackingDisruptor,
 dogma.const.effectRemoteWebifierFalloff: appConst.iconModuleStasisWeb,
 dogma.const.effectShipModuleGuidanceDisruptor: appConst.iconModuleGuidanceDisruptor,
 dogma.const.effectRemoteECMFalloff: appConst.iconModuleECM,
 dogma.const.effectEntityECMFalloff: appConst.iconModuleECM,
 dogma.const.effectEntityEnergyNeutralizerFalloff: appConst.iconModuleEnergyNeutralizer,
 dogma.const.effectStarbaseEnergyNeutralizerFalloff: appConst.iconModuleEnergyNeutralizer,
 dogma.const.effectRemoteSensorDampEntity: appConst.iconModuleSensorDamper,
 dogma.const.effectRemoteTargetPaintEntity: appConst.iconModuleTargetPainter,
 dogma.const.effectNpcEntityWeaponDisruptor: appConst.iconModuleTrackingDisruptor,
 dogma.const.effectRemoteWebifierEntity: appConst.iconModuleStasisWeb,
 dogma.const.effectRemoteTracking: appConst.iconModuleRemoteTracking,
 dogma.const.effectEnergyTransfer: appConst.iconModuleEnergyTransfer,
 dogma.const.effectTargetMaxTargetRangeAndScanResolutionBonusAssistance: appConst.iconModuleSensorBooster,
 dogma.const.effectScanStrengthTargetPercentBonus: appConst.iconModuleECCMProjector,
 dogma.const.effectTargetArmorRepair: appConst.iconModuleArmorRepairer,
 dogma.const.effectShieldTransfer: appConst.iconModuleShieldBooster,
 dogma.const.effectShipModuleRemoteArmorRepairer: appConst.iconModuleArmorRepairer,
 dogma.const.effectShipModuleAncillaryRemoteArmorRepairer: appConst.iconModuleArmorRepairer,
 dogma.const.effectShipModuleRemoteCapacitorTransmitter: appConst.iconModuleEnergyTransfer,
 dogma.const.effectShipModuleRemoteHullRepairer: appConst.iconModuleHullRepairer,
 dogma.const.effectShipModuleRemoteShieldBooster: appConst.iconModuleShieldBooster,
 dogma.const.effectShipModuleAncillaryRemoteShieldBooster: appConst.iconModuleShieldBooster,
 dogma.const.effectRemoteSensorBoostFalloff: appConst.iconModuleSensorBooster,
 dogma.const.effectShipModuleRemoteTrackingComputer: appConst.iconModuleRemoteTracking,
 dogma.const.effectRemoteECCMFalloff: appConst.iconModuleECCMProjector,
 dogma.const.effectNpcEntityRemoteHullRepairer: appConst.iconModuleHullRepairer,
 dogma.const.effectNpcEntityRemoteArmorRepairer: appConst.iconModuleArmorRepairer,
 dogma.const.effectNpcEntityRemoteShieldBooster: appConst.iconModuleShieldBooster,
 dogma.const.effectShipModuleRemoteArmorMutadaptiveRepairer: appConst.iconModuleMutadaptiveArmorRepairer}
barWidth = 40
barPadding = 4
statusIconWidth = 20
maxStatusIcons = 6
effectsList = [appConst.iconModuleShieldBooster,
 appConst.iconModuleMutadaptiveArmorRepairer,
 appConst.iconModuleArmorRepairer,
 appConst.iconModuleHullRepairer,
 appConst.iconModuleFocusedWarpScrambler,
 appConst.iconModuleECM,
 appConst.iconModuleStasisGrappler,
 appConst.iconModuleStasisWeb,
 appConst.iconModuleWarpScrambler,
 appConst.iconModuleWarpScramblerMWD,
 appConst.iconModuleSensorDamper,
 appConst.iconModuleTrackingDisruptor,
 appConst.iconModuleGuidanceDisruptor,
 appConst.iconModuleEnergyNeutralizer,
 appConst.iconModuleNosferatu,
 appConst.iconModuleTargetPainter,
 appConst.iconModuleFighterTackle]

class TournamentWindow(Window):
    __guid__ = 'form.tournament'
    default_windowID = 'tournamentcamera'
    __notifyevents__ = ['OnPreMatchStart']

    def ApplyAttributes(self, attributes):
        if session.solarsystemid is None or session.structureid:
            raise UserError('You must be in space to run the camera tool')
        try:
            self.tourneyMoniker = moniker.Moniker('tourneyMgr', session.solarsystemid)
            activeMatchDetails = self.tourneyMoniker.GetActiveMatchForCamera()
        except KeyError:
            raise UserError('You must be in the arena system to get active matches')

        self.fancyUI = None
        self.warningLine = None
        self.maxPoints = 100
        self.teamDetails = []
        self.currentMatchNumber = None
        self.teamOneName = ''
        self.teamTwoName = ''
        self.nebulaID = None
        self.cameraMode = None
        self.updateElements = {}
        if activeMatchDetails:
            self.currentMatchNumber = activeMatchDetails['matchID']
            self.teamOneName = activeMatchDetails['teamOneName']
            self.teamTwoName = activeMatchDetails['teamTwoName']
            self.nebulaID = activeMatchDetails['nebulaID']
        Window.ApplyAttributes(self, attributes)
        self.height = 200
        self.width = 300
        self.SetScope(uiconst.SCOPE_ALL)
        self.SetCaption('Tournament Camera Tool')
        self.SetMinSize([self.width, self.height])
        self.MakeUnResizeable()
        self.ConstructLayout()
        uicore.layer.shipUI.display = False
        sm.GetService('sensorSuite').DisableSensorOverlay()
        NotificationSettingHandler().SetNotificationWidgetEnabled(False)

    def ConstructLayout(self):
        self.ConstructStartScreen()
        self.ConstructSpectatorScreen()
        self.ConstructFancyUIScreen()

    def ConstructFancyUIScreen(self):
        self.fancyUIWindow = Container(name='fancyUIWindow', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.fancyUISelect = Combo(label='Select FancyUI Background', parent=self.fancyUIWindow, options=fancyBackgroundOptions, padding=(5, 15, 5, 5), align=uiconst.TOTOP, callback=self.ChangeFancyUIBackground)
        fancyUIMaxEHPContainer = Container(name='fancyUIMaxEHPContainer', parent=self.fancyUIWindow, align=uiconst.TOTOP, height=25)
        fancyUIMaxDPSContainer = Container(name='fancyUIMaxDPSContainer', parent=self.fancyUIWindow, align=uiconst.TOTOP, height=25)
        fancyUIMaxControlContainer = Container(name='fancyUIMaxControlContainer', parent=self.fancyUIWindow, align=uiconst.TOTOP, height=25)
        eveLabel.Label(text='Max EHP', parent=fancyUIMaxEHPContainer, padding=(5, 5, 5, 5), align=uiconst.TOLEFT)
        eveLabel.Label(text='Max DPS', parent=fancyUIMaxDPSContainer, padding=(5, 5, 5, 5), align=uiconst.TOLEFT)
        eveLabel.Label(text='Max Control', parent=fancyUIMaxControlContainer, padding=(5, 5, 5, 5), align=uiconst.TOLEFT)
        self.fancyUIMaxEHPEdit = SingleLineEditText(name='fancyUIMaxEHPEdit', parent=fancyUIMaxEHPContainer, setvalue=str(prefs.GetValue('maxFancyEHP', 500000)), OnReturn=self.UpdateFancyUIBarMax, OnFocusLost=self.UpdateFancyUIBarMax, align=uiconst.TORIGHT)
        self.fancyUIMaxDPSEdit = SingleLineEditText(name='fancyUIMaxDPSEdit', parent=fancyUIMaxDPSContainer, setvalue=str(prefs.GetValue('maxFancyDPS', 4500)), OnReturn=self.UpdateFancyUIBarMax, OnFocusLost=self.UpdateFancyUIBarMax, align=uiconst.TORIGHT)
        self.fancyUIMaxControlEdit = SingleLineEditText(name='fancyUIMaxcontrolEdit', parent=fancyUIMaxControlContainer, setvalue=str(prefs.GetValue('maxFancyCont', 50)), OnReturn=self.UpdateFancyUIBarMax, OnFocusLost=self.UpdateFancyUIBarMax, align=uiconst.TORIGHT)
        self.fancyUI = Container(name='AT-Fancy', parent=uicore.layer.inflight, pos=(0,
         746,
         1920,
         334), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)

    def ConstructSpectatorScreen(self):
        self.cameraClientScreen = Container(name='cameraClientScreen', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        Button(label='Lock Dudes', parent=self.cameraClientScreen, padding=(5, 5, 5, 5), func=self.LockEveryone, align=uiconst.TOTOP)
        Button(label='Sort Locks', parent=self.cameraClientScreen, padding=(5, 5, 5, 5), func=self.SortLocks, align=uiconst.TOTOP)
        Button(label='Toggle Ship Bracket Text Always On', parent=self.cameraClientScreen, func=self.ToggleShipText, align=uiconst.TOTOP, padding=(5, 5, 5, 5))
        Button(label='Toggle Tactical Overlay', parent=self.cameraClientScreen, func=self.ToggleTacticalOverlay, align=uiconst.TOTOP, padding=(5, 5, 5, 5))
        Button(label='Set Tactical Camera', parent=self.cameraClientScreen, func=self.SetSpectatorCameraModeTactical, align=uiconst.TOTOP, padding=(5, 5, 5, 5))
        Button(label='Set Orbit Camera', parent=self.cameraClientScreen, func=self.SetSpectatorCameraModeOrbit, align=uiconst.TOTOP, padding=(5, 5, 5, 5))
        self.warningLine = Fill(name='AT-Camera Warning', parent=uicore.layer.main, pos=(0,
         752,
         1920,
         2), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, color=(1, 0, 0, 0.85))

    def ConstructStartScreen(self):
        self.startScreen = Container(name='startScreen', parent=self.sr.main, align=uiconst.TOALL)
        Button(label='Start Spectator Client', parent=self.startScreen, padding=(5, 5, 5, 5), func=self.SetCameraModeSpectator, align=uiconst.TOTOP)
        Button(label='Start FancyUI Client', parent=self.startScreen, padding=(5, 5, 5, 5), func=self.SetCameraModeFancyUI, align=uiconst.TOTOP)
        self.selectedCameraModeLabel = eveLabel.Label(name='selectedCameraModeLabel', parent=self.startScreen, padding=(5, 5, 5, 5), align=uiconst.TOTOP, text='Camera Mode:')
        self.currentMatchNumberLabel = eveLabel.Label(name='currentMatchNumber', parent=self.startScreen, padding=(5, 5, 5, 5), align=uiconst.TOTOP, text='Match Number: {}'.format(self.currentMatchNumber if self.currentMatchNumber else 'Waiting for match'))

    def FetchTeams(self):
        if session.solarsystemid != self.tourneyMoniker.GetMatchSystem():
            raise UserError('You must be in the arena system to fetch teams')
        teamComps = self.tourneyMoniker.GetTeamMembers(self.currentMatchNumber)
        cfg.eveowners.Prime([ x[0] for x in teamComps[0] ] + [ x[0] for x in teamComps[1] ])
        self.teamDetails = []
        for teamIdx in (0, 1):
            self.teamDetails.append(OrderedDict())
            teamComps[teamIdx].sort(key=operator.itemgetter(3, 1), reverse=True)
            for pilot in teamComps[teamIdx]:
                characterID = pilot[0]
                shipTypeID = pilot[1]
                shipID = pilot[2]
                points = pilot[3]
                characterName = cfg.eveowners[characterID].ownerName
                if shipTypeID in tourneyConst.tournamentShipTypeNicknames:
                    shipTypeName = tourneyConst.tournamentShipTypeNicknames[shipTypeID]
                else:
                    shipTypeName = evetypes.GetName(shipTypeID)
                self.teamDetails[teamIdx][shipID] = {'characterID': pilot[0],
                 'shipTypeID': shipTypeID,
                 'points': points,
                 'shipName': shipTypeName,
                 'characterName': characterName}

    def SetCameraModeSpectator(self, *args):
        self.selectedCameraModeLabel.text = 'Camera Mode: Spectator Camera'
        self.cameraMode = tourneyConst.tournamentCameraModeSpectator
        if self.currentMatchNumber is not None:
            self.StartCameraClient()

    def SetCameraModeFancyUI(self, *args):
        self.selectedCameraModeLabel.text = 'Camera Mode: Fancy UI'
        self.cameraMode = tourneyConst.tournamentCameraModeFancyUI
        if self.currentMatchNumber is not None:
            self.StartFancyUIClient()

    def OnPreMatchStart(self, matchID, teamOneName, teamTwoName, nebula):
        self.ClearSpectatorStandings()
        self.currentMatchNumber = matchID
        self.teamOneName = teamOneName
        self.teamTwoName = teamTwoName
        self.nebulaID = nebula
        self.currentMatchNumberLabel.text = 'Match Number: {}'.format(matchID)
        if self.cameraMode == tourneyConst.tournamentCameraModeSpectator:
            self.StartCameraClient()
        if self.cameraMode == tourneyConst.tournamentCameraModeFancyUI:
            self.StartFancyUIClient()

    def StartCameraClient(self, *args):
        self.FetchTeams()
        charMgr = sm.RemoteSvc('charMgr')
        for pilot in self.teamDetails[0].itervalues():
            charMgr.AddContact(pilot['characterID'], -10)

        for pilot in self.teamDetails[1].itervalues():
            charMgr.AddContact(pilot['characterID'], 10)

        neocomLayer = uicore.layer.Get('sidePanels')
        if neocomLayer is not None and neocomLayer.state != uiconst.UI_HIDDEN:
            neocomLayer.state = uiconst.UI_HIDDEN
        sm.GetService('infoPanel').ShowHideSidePanel(hide=True)
        sm.GetService('target').disableSpinnyReticule = True
        sm.GetService('target').overrideBarHeight = 120
        self.startScreen.state = uiconst.UI_HIDDEN
        self.cameraClientScreen.state = uiconst.UI_NORMAL
        self.warningLine.state = uiconst.UI_NORMAL
        scene = sm.GetService('sceneManager').GetActiveScene()
        for res in scene.backgroundEffect.resources:
            if res.name == 'NebulaMap':
                res.resourcePath = 'res:/dx9/scene/universe/%s_cube.dds' % (self.nebulaID,)
            if res.name == 'AlphaMap':
                res.resourcePath = 'res:/dx9/scene/universe/%s_cube_refl.dds' % (self.nebulaID,)
            if res.name == 'NebulaMapUV':
                res.resourcePath = 'res:/dx9/scene/universe/%s_cube_uv.dds' % (self.nebulaID,)

        scene.envMap1ResPath = 'res:/dx9/scene/universe/%s_cube.dds' % (self.nebulaID,)
        scene.envMap2ResPath = 'res:/dx9/scene/universe/%s_cube_blur.dds' % (self.nebulaID,)

    def StartFancyUIClient(self, *args):
        self.FetchTeams()
        sm.GetService('neocom').GetNeocomContainer().SetAlignRight()
        sm.GetService('neocom').GetNeocomContainer().SetAutoHideOn()
        barDetails = self.tourneyMoniker.GetFancyDetails(self.currentMatchNumber)
        neocomLayer = uicore.layer.Get('sidePanels')
        if neocomLayer is not None and neocomLayer.state != uiconst.UI_HIDDEN:
            neocomLayer.state = uiconst.UI_HIDDEN
        if self.updateElements:
            self.ResetFancyUI()
        self.startScreen.state = uiconst.UI_HIDDEN
        self.fancyUIWindow.state = uiconst.UI_NORMAL
        self.fancyUI.state = uiconst.UI_NORMAL
        self.matchTimer = tournamentTimer.TournamentTimerFormatter(defaultText='-00:00-')
        self.teamOneName = DropShadowElement(eveLabel.Label, text=self.teamOneName, parent=self.fancyUI, left=0, top=4, uppercase=True, fontsize=22, bold=True, color=(1, 1, 1, 1), shadowOffset=(3, 3), shadowColor=(0, 0, 0, 1))
        self.teamOneName.left = 760 - self.teamOneName.width
        self.leftTeamScore = DropShadowElement(eveLabel.Label, text='46', parent=self.fancyUI, left=0, top=2, fontsize=24, bold=True, color=(1, 1, 1, 1), shadowOffset=(3, 3))
        self.leftTeamScore.left = 812 - self.leftTeamScore.width
        self.teamTwoName = DropShadowElement(eveLabel.Label, text=self.teamTwoName, parent=self.fancyUI, left=1160, top=4, uppercase=True, fontsize=22, bold=True, color=(1, 1, 1, 1), shadowOffset=(5, 5))
        self.rightTeamScore = DropShadowElement(eveLabel.Label, text='26', parent=self.fancyUI, left=1100, top=2, fontsize=24, bold=True, color=(1, 1, 1, 1))
        self.leftTeamBar = Fill(name='redbar', parent=self.fancyUI, pos=(0, 0, 831, 5), align=uiconst.TOPLEFT, color=(199 / 255.0,
         72 / 255.0,
         72 / 255.0,
         1))
        self.rightTeamBar = Fill(name='bluebar', parent=self.fancyUI, pos=(1089, 0, 831, 5), align=uiconst.TOPLEFT, color=(29 / 255.0,
         97 / 255.0,
         168 / 255.0,
         1))
        defBarY = 38
        offBarY = 52
        contBarY = 66
        barHeight = 12
        self.leftTeamRep = Sprite(parent=self.fancyUI, pos=(500,
         defBarY,
         49,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarPurple.png')
        self.leftTeamEHP = Sprite(parent=self.fancyUI, pos=(550,
         defBarY,
         281,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarBlue.png')
        self.leftTeamOffFill = Sprite(parent=self.fancyUI, pos=(650,
         offBarY,
         181,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarRed.png')
        self.leftTeamOffBackground = Sprite(parent=self.fancyUI, pos=(350,
         offBarY,
         299,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Bar_Full.png')
        self.leftTeamContFill = Sprite(parent=self.fancyUI, pos=(710,
         contBarY,
         121,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarGreen.png')
        self.leftTeamContBackground = Sprite(parent=self.fancyUI, pos=(630,
         contBarY,
         79,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Bar_Full.png')
        self.rightTeamRep = Sprite(parent=self.fancyUI, pos=(1089 + 157 + 1,
         defBarY,
         60,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarPurple.png')
        self.rightTeamEHP = Sprite(parent=self.fancyUI, pos=(1089,
         defBarY,
         157,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarBlue.png')
        self.rightTeamOffFill = Sprite(parent=self.fancyUI, pos=(1089,
         offBarY,
         348,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarRed.png')
        self.rightTeamOffBackground = Sprite(parent=self.fancyUI, pos=(1089 + 348 + 1,
         offBarY,
         62,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Bar_Full.png')
        self.rightTeamContFill = Sprite(parent=self.fancyUI, pos=(1089,
         contBarY,
         284,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/AwesomeBarGreen.png')
        self.rightTeamContBackground = Sprite(parent=self.fancyUI, pos=(1089 + 284 + 1,
         contBarY,
         121,
         11), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Bar_Full.png')
        self.clockLabel = DropShadowElement(eveLabel.EveCaptionLarge, text='-00:00-', parent=self.fancyUI, left=0, top=0, color=(1, 1, 1, 1))
        self.clockLabel.left = 1920 / 2 - self.clockLabel.width / 2
        self.redBanContainer = Container(parent=self.fancyUI, pos=(16, 4, 316, 214), align=uiconst.TOPLEFT, clipChildren=True)
        self.blueBanContainer = Container(parent=self.fancyUI, pos=(16, 4, 316, 214), align=uiconst.TOPRIGHT, clipChildren=True)
        if len(barDetails[3][0]) + len(barDetails[3][1]) > 0:
            DropShadowElement(eveLabel.EveCaptionMedium, text='Ship Bans', parent=self.redBanContainer, align=uiconst.TOPLEFT, left=0, top=2)
            redHeight = 32
            for x in barDetails[3][0]:
                DropShadowElement(eveLabel.EveCaptionSmall, text=evetypes.GetName(x), parent=self.redBanContainer, align=uiconst.TOPLEFT, left=0, top=redHeight)
                redHeight += 20

            DropShadowElement(eveLabel.EveCaptionMedium, text='Ship Bans', parent=self.blueBanContainer, align=uiconst.TOPRIGHT, left=0, top=2)
            blueHeight = 32
            for x in barDetails[3][1]:
                DropShadowElement(eveLabel.EveCaptionSmall, text=evetypes.GetName(x), parent=self.blueBanContainer, align=uiconst.TOPRIGHT, left=0, top=blueHeight)
                blueHeight += 20

        statusIconsWidth = 258 / 2
        shipOffset = statusIconsWidth
        shipWidth = 98
        barsOffset = shipOffset + shipWidth
        barsWidth = 142
        speedOffset = barsOffset + barsWidth
        speedWidth = 49
        nameOffset = speedOffset + speedWidth
        nameWidth = 149
        pointsOffset = nameOffset + nameWidth
        pointsWidth = 40
        headerY = 90
        rowStartY = 114
        rowHeight = 18
        self.statusIconContainers = {}
        self.updateElements = {}
        for teamIdx, color in ((0, (1, 0, 0, 0.1)), (1, (0, 0, 1, 0.1))):
            for idx, pilot in enumerate(self.teamDetails[teamIdx].items()):
                yOffset = rowStartY + idx * rowHeight
                pilotName = pilot[1]['characterName']
                shipName = pilot[1]['shipName']
                shipID = pilot[0]
                points = pilot[1]['points']
                healthBarBackgroundColor = (143.0 / 255,
                 19.0 / 255,
                 19.0 / 255,
                 1)
                healthBarFillColor = (141.0 / 255,
                 141.0 / 255,
                 141.0 / 255,
                 1)
                if teamIdx == 0:
                    statusContainer = Container(parent=self.fancyUI, left=1920 / 2 - statusIconsWidth, top=yOffset, width=statusIconWidth * maxStatusIcons, height=statusIconWidth, align=uiconst.TOPLEFT)
                    self.statusIconContainers[shipID] = (statusContainer, 0, operator.add)
                    barContainer = Container(parent=self.fancyUI, left=1920 / 2 - barsOffset - barsWidth + 4, top=yOffset, width=barsWidth, height=rowHeight - 2, align=uiconst.TOPLEFT)
                    self.updateElements[shipID] = [0,
                     points,
                     DropShadowElement(eveLabel.EveLabelLarge, text='<b>0', parent=self.fancyUI, left=1920 / 2 - speedOffset - speedWidth + 4, top=yOffset, width=speedWidth, maxLines=1, color=(1, 1, 1, 0.95)),
                     barContainer,
                     Container(parent=barContainer, pos=(0,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     Container(parent=barContainer, pos=(barWidth + barPadding,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     Container(parent=barContainer, pos=((barWidth + barPadding) * 2,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     DropShadowElement(eveLabel.EveLabelLarge, text='<b>%d' % (points,), parent=self.fancyUI, left=1920 / 2 - pointsOffset - pointsWidth + 4, top=yOffset, width=pointsWidth, maxLines=1, color=(1, 1, 1, 0.95)),
                     DropShadowElement(eveLabel.EveLabelLarge, text='<b>%s' % (pilotName,), parent=self.fancyUI, left=1920 / 2 - nameOffset - nameWidth + 4, top=yOffset, width=nameWidth, maxLines=1, showEllipsis=True, color=(1, 1, 1, 0.95)),
                     DropShadowElement(eveLabel.EveLabelLarge, text='<b>%s' % (shipName,), parent=self.fancyUI, left=1920 / 2 - shipOffset - shipWidth + 4, top=yOffset, width=shipWidth, maxLines=1, color=(1, 1, 1, 0.95))]
                    self.updateElements[shipID].append(Sprite(parent=self.updateElements[shipID][4], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full.png'))
                    self.updateElements[shipID].append(Sprite(parent=self.updateElements[shipID][5], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full.png'))
                    self.updateElements[shipID].append(Sprite(parent=self.updateElements[shipID][6], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full.png'))
                    Sprite(parent=barContainer, pos=(0,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back.png', align=uiconst.TOPLEFT)
                    Sprite(parent=barContainer, pos=(barWidth + barPadding,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back.png', align=uiconst.TOPLEFT)
                    Sprite(parent=barContainer, pos=((barWidth + barPadding) * 2,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back.png', align=uiconst.TOPLEFT)
                else:
                    statusContainer = Container(parent=self.fancyUI, left=1920 / 2, top=yOffset, width=statusIconWidth * maxStatusIcons, height=statusIconWidth, align=uiconst.TOPLEFT)
                    self.statusIconContainers[shipID] = (statusContainer, statusIconsWidth - statusIconWidth, operator.sub)
                    barContainer = Container(parent=self.fancyUI, left=1920 / 2 + barsOffset + 4 + 6, top=yOffset, width=barsWidth, height=rowHeight - 2, align=uiconst.TOPLEFT)
                    self.updateElements[shipID] = [1,
                     points,
                     DropShadowElement(eveLabel.EveLabelLarge, text='<b>0', parent=self.fancyUI, left=1920 / 2 + speedOffset + 4, top=yOffset, width=speedWidth, maxLines=1, color=(1, 1, 1, 0.95)),
                     barContainer,
                     Container(parent=barContainer, pos=(0,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     Container(parent=barContainer, pos=(barWidth + barPadding,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     Container(parent=barContainer, pos=((barWidth + barPadding) * 2,
                      1,
                      barWidth,
                      rowHeight - 2), align=uiconst.TOPLEFT, clipChildren=True),
                     DropShadowElement(eveLabel.EveLabelLarge, text='<b>%d' % (points,), parent=self.fancyUI, left=1920 / 2 + pointsOffset + 4, top=yOffset, width=pointsWidth, maxLines=1, color=(1, 1, 1, 0.95)),
                     DropShadowElement(eveLabel.EveLabelLarge, text='<b>%s' % (pilotName,), parent=self.fancyUI, left=1920 / 2 + nameOffset + 4, top=yOffset, width=nameWidth, maxLines=1, showEllipsis=True, color=(1, 1, 1, 0.95)),
                     DropShadowElement(eveLabel.EveLabelLarge, text='<b>%s' % (shipName,), parent=self.fancyUI, left=1920 / 2 + shipOffset + 4, top=yOffset, width=shipWidth, maxLines=1, color=(1, 1, 1, 0.95))]
                    self.updateElements[shipID].append(Sprite(parent=self.updateElements[shipID][4], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full_Mirror.png'))
                    self.updateElements[shipID].append(Sprite(parent=self.updateElements[shipID][5], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full_Mirror.png'))
                    self.updateElements[shipID].append(Sprite(parent=self.updateElements[shipID][6], pos=(0,
                     0,
                     barWidth,
                     rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Block_Full_Mirror.png'))
                    (Sprite(parent=barContainer, pos=(0,
                      1,
                      barWidth,
                      rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back_Mirror.png', align=uiconst.TOPLEFT),)
                    Sprite(parent=barContainer, pos=(barWidth + barPadding,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back_Mirror.png', align=uiconst.TOPLEFT)
                    Sprite(parent=barContainer, pos=((barWidth + barPadding) * 2,
                     1,
                     barWidth,
                     rowHeight - 2), texturePath='res:/UI/Texture/Tournament/Block_Back_Mirror.png', align=uiconst.TOPLEFT)
                left = 350 if teamIdx == 0 else 1089
                Sprite(parent=self.fancyUI, pos=(left,
                 yOffset + 1,
                 481,
                 rowHeight - 2), align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Tournament/Player_Back.png')

        self.FancyBackground = Sprite(name='background', parent=self.fancyUI, texturePath=FANCY_BACKGROUND_PATH + DEFAULT_FANCY_UI_BACKGROUND, pos=(0, 0, 1920, 334))
        self.matchStartTime = None
        self.shipDeathTimes = {}
        self.maxEHP = float(prefs.GetValue('maxFancyEHP', 500000))
        self.maxDPS = float(prefs.GetValue('maxFancyDPS', 4500))
        self.maxCont = float(prefs.GetValue('maxFancyCont', 50))
        self.maxPoints = barDetails[2][5]
        uthread.new(self.FancyUIUpdate)

    def SortEffects(self, effectSet):
        desiredOrdering = effectsList
        return [ x for x in desiredOrdering if x in effectSet ]

    def HarvestStatusEffects(self):
        fx = sm.GetService('FxSequencer')
        clientDogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        effects = defaultdict(set)
        for shipID in self.updateElements.iterkeys():
            activations = fx.GetAllBallActivations(shipID)
            for activation in activations:
                for trigger in activation.triggers:
                    try:
                        moduleTypeID = trigger.moduleTypeID
                        groupID = evetypes.GetGroupID(moduleTypeID)
                        if groupID == appConst.groupArmorRepairProjector:
                            iconID = appConst.iconModuleArmorRepairer
                        elif groupID == appConst.groupPrecursorRepairer:
                            iconID = appConst.iconModuleMutadaptiveArmorRepairer
                        elif groupID == appConst.groupShieldTransporter:
                            iconID = appConst.iconModuleShieldBooster
                        elif groupID == appConst.groupRemoteHullRepairer:
                            iconID = appConst.iconModuleHullRepairer
                        elif groupID == appConst.groupStasisGrappler:
                            iconID = appConst.iconModuleStasisGrappler
                        else:
                            effectID = clientDogmaStaticSvc.GetDefaultEffect(moduleTypeID)
                            iconID = self.GetIconIDForEffectID(effectID)
                        effects[trigger.targetID].add(iconID)
                    except:
                        pass

        return effects

    def GetIconIDForEffectID(self, effectID):
        effect = dogma.data.get_effect(effectID)
        if effect.electronicChance:
            return appConst.iconModuleECM
        if effect.propulsionChance:
            return appConst.iconModuleStasisWeb
        return ICON_ID_BY_EFFECT_ID[effectID]

    def RandomStatusEffects(self):
        import random
        effects = {}
        possibleIcons = effectsList
        for shipID in self.updateElements.iterkeys():
            effects[shipID] = [ x for x in possibleIcons if random.random() > 0.5 ]

        return effects

    def UpdateFancyStatusEffects(self):
        for icon in self.iconsToCleanup:
            icon.Close()

        self.iconsToCleanup = []
        statusEffects = self.HarvestStatusEffects()
        for shipID in self.updateElements.iterkeys():
            effectSet = statusEffects[shipID]
            newList = self.SortEffects(effectSet)
            oldList = self.currentStatusIcons[shipID]
            iconContainerData = self.statusIconContainers[shipID]
            newIcons = {}
            for idx, (iconID, iconElement) in enumerate(oldList):
                try:
                    newIndex = newList.index(iconID)
                except ValueError:
                    uicore.animations.FadeOut(iconElement, duration=0.5)
                    self.iconsToCleanup.append(iconElement)
                    continue

                if newIndex != idx:
                    movement = iconContainerData[2](0, (newIndex - idx) * statusIconWidth)
                    uicore.animations.MoveOutRight(iconElement, amount=movement, duration=0.75)
                    if newIndex >= maxStatusIcons:
                        uicore.animations.FadeOut(iconElement, duration=0.5)
                        self.iconsToCleanup.append(iconElement)
                    else:
                        newIcons[newIndex] = (iconID, iconElement)
                else:
                    newIcons[idx] = (iconID, iconElement)

            oldIcons = set([ x[0] for x in oldList ])
            for idx, iconID in enumerate(newList):
                if idx >= maxStatusIcons:
                    break
                if iconID not in oldIcons:
                    iconLocation = iconContainerData[2](iconContainerData[1], idx * statusIconWidth) - 2
                    newIcon = eveIcon.Icon(parent=iconContainerData[0], align=uiconst.TOPLEFT, pos=(iconLocation,
                     -4,
                     24,
                     24), graphicID=iconID, ignoreSize=True, opacity=0)
                    uicore.animations.FadeIn(newIcon, duration=0.5)
                    newIcons[idx] = (iconID, newIcon)

            self.currentStatusIcons[shipID] = [ newIcons[idx] for idx in xrange(len(newIcons)) ]

    def UpdateFancyBars(self):
        barDetails = self.tourneyMoniker.GetFancyDetails(self.currentMatchNumber)
        barWidth = 481
        ehpPerPixel = barWidth / self.maxEHP
        repPerPixel = 60 * ehpPerPixel
        dpsPerPixel = barWidth / self.maxDPS
        contPerPixel = barWidth / self.maxCont
        leftTeamX = 350
        rightTeamX = 1089
        totalEHP, totalReps, fleetMaxDPS, fleetAppliedDPS, fleetMaxControl, fleetAppliedControl = barDetails[0] or (0, 0, 0, 0, 0, 0)
        ehpWidth = min(barWidth, math.ceil(totalEHP * ehpPerPixel))
        self.leftTeamEHP.width = ehpWidth
        self.leftTeamEHP.left = leftTeamX + barWidth - ehpWidth
        repWidth = math.ceil(totalReps * repPerPixel)
        repWidth = min(repWidth, barWidth - ehpWidth - 1)
        self.leftTeamRep.width = repWidth
        self.leftTeamRep.left = leftTeamX + barWidth - ehpWidth - 1 - repWidth
        curDPSWidth = min(barWidth, math.ceil(fleetAppliedDPS * dpsPerPixel))
        maxDPSWidth = max(0, min(barWidth, math.ceil(fleetMaxDPS * dpsPerPixel)) - curDPSWidth - 1)
        self.leftTeamOffFill.width = curDPSWidth
        self.leftTeamOffFill.left = leftTeamX + barWidth - curDPSWidth
        self.leftTeamOffBackground.width = maxDPSWidth
        self.leftTeamOffBackground.left = leftTeamX + barWidth - curDPSWidth - 1 - maxDPSWidth
        curControlWidth = min(barWidth, math.ceil(fleetAppliedControl * contPerPixel))
        maxControlWidth = max(0, min(barWidth, math.ceil(fleetMaxControl * contPerPixel)) - curControlWidth - 1)
        self.leftTeamContFill.width = curControlWidth
        self.leftTeamContFill.left = leftTeamX + barWidth - curControlWidth
        self.leftTeamContBackground.width = maxControlWidth
        self.leftTeamContBackground.left = leftTeamX + barWidth - curControlWidth - 1 - maxControlWidth
        totalEHP, totalReps, fleetMaxDPS, fleetAppliedDPS, fleetMaxControl, fleetAppliedControl = barDetails[1] or (0, 0, 0, 0, 0, 0)
        ehpWidth = min(barWidth, math.ceil(totalEHP * ehpPerPixel))
        self.rightTeamEHP.width = ehpWidth
        self.rightTeamEHP.left = rightTeamX
        repWidth = math.ceil(totalReps * repPerPixel)
        repWidth = min(repWidth, barWidth - ehpWidth - 1)
        self.rightTeamRep.width = repWidth
        self.rightTeamRep.left = rightTeamX + ehpWidth + 1
        curDPSWidth = min(barWidth, math.ceil(fleetAppliedDPS * dpsPerPixel))
        maxDPSWidth = max(0, min(barWidth, math.ceil(fleetMaxDPS * dpsPerPixel)) - curDPSWidth - 1)
        self.rightTeamOffFill.width = curDPSWidth
        self.rightTeamOffFill.left = rightTeamX
        self.rightTeamOffBackground.width = maxDPSWidth
        self.rightTeamOffBackground.left = rightTeamX + curDPSWidth + 1
        curControlWidth = min(barWidth, math.ceil(fleetAppliedControl * contPerPixel))
        maxControlWidth = max(0, min(barWidth, math.ceil(fleetMaxControl * contPerPixel)) - curControlWidth - 1)
        self.rightTeamContFill.width = curControlWidth
        self.rightTeamContFill.left = rightTeamX
        self.rightTeamContBackground.width = maxControlWidth
        self.rightTeamContBackground.left = rightTeamX + curControlWidth + 1
        matchState, startTime, tidiState, matchLength, overtimeLength, _ = barDetails[2]
        if matchState < tourneyConst.tournamentStateComplete:
            text, color = self.matchTimer.GetTimerTextAndColor(matchState, long(startTime), tidiState, matchLength, overtimeLength)
            self.clockLabel.text = text
            self.clockLabel.color = color
            self.clockLabel.left = uicore.desktop.width / 2 - self.clockLabel.width / 2

    def FancyUIUpdate(self):
        michelle = sm.GetService('michelle')
        ballsIHaveAnimatedDeathFor = {}
        self.currentStatusIcons = defaultdict(list)
        self.iconsToCleanup = []
        while not self.destroyed:
            with ExceptionEater('FancyStatus update'):
                self.UpdateFancyStatusEffects()
            with ExceptionEater('FancyBar update'):
                self.UpdateFancyBars()
            teamScores = [self.maxPoints, self.maxPoints]
            bp = michelle.GetBallpark()
            for shipID, (teamIdx, points, speedLabel, barContainer, bar1Cont, bar2Cont, bar3Cont, ptsLabel, nameLabel, shipLabel, bar1, bar2, bar3) in self.updateElements.iteritems():
                ball = michelle.GetBall(shipID)
                if ball and not (hasattr(ball, 'destructionEffectId') and destructionEffectType.isExplosionOrOverride(ball.destructionEffectId)):
                    teamScores[0 if teamIdx == 1 else 1] -= points
                    speedLabel.text = '<b>%d' % (math.sqrt(ball.vx ** 2 + ball.vy ** 2 + ball.vz ** 2),)
                    damageState = bp.GetDamageState(shipID)
                    ptsLabel.color = (1, 1, 1, 0.95)
                    nameLabel.color = (1, 1, 1, 0.95)
                    shipLabel.color = (1, 1, 1, 0.95)
                    if shipID in ballsIHaveAnimatedDeathFor:
                        ballsIHaveAnimatedDeathFor[shipID].Stop()
                        del ballsIHaveAnimatedDeathFor[shipID]
                        barContainer.opacity = 1
                        if shipID in self.shipDeathTimes:
                            del self.shipDeathTimes[shipID]
                else:
                    speedLabel.text = ''
                    damageState = (0, 0, 0)
                    if shipID not in ballsIHaveAnimatedDeathFor:
                        ballsIHaveAnimatedDeathFor[shipID] = uicore.animations.FadeOut(barContainer, duration=2)
                    ptsLabel.color = (1, 1, 1, 0.4)
                    nameLabel.color = (1, 1, 1, 0.4)
                    shipLabel.color = (1, 1, 1, 0.4)
                    if shipID not in self.shipDeathTimes:
                        self.shipDeathTimes[shipID] = blue.os.GetSimTime()
                ptsLabel.text = '<b>{}'.format(self.teamDetails[teamIdx][shipID]['points'])
                nameLabel.text = '<b>{}'.format(self.teamDetails[teamIdx][shipID]['characterName'])
                shipLabel.text = '<b>{}'.format(self.teamDetails[teamIdx][shipID]['shipName'])
                if damageState is None:
                    continue
                if teamIdx == 0:
                    bar1Cont.width = int(math.ceil(damageState[2] * (barWidth - 4))) + 2
                    if damageState[2] < 0.3:
                        bar1.texturePath = 'res:/UI/Texture/Tournament/Block_Damage.png'
                    else:
                        bar1.texturePath = 'res:/UI/Texture/Tournament/Block_Full.png'
                    bar2Cont.width = int(math.ceil(damageState[1] * (barWidth - 4))) + 2
                    if damageState[1] < 0.3:
                        bar2.texturePath = 'res:/UI/Texture/Tournament/Block_Damage.png'
                    else:
                        bar2.texturePath = 'res:/UI/Texture/Tournament/Block_Full.png'
                    bar3Cont.width = int(math.ceil(damageState[0] * (barWidth - 4))) + 2
                    if damageState[0] < 0.3:
                        bar3.texturePath = 'res:/UI/Texture/Tournament/Block_Damage.png'
                    else:
                        bar3.texturePath = 'res:/UI/Texture/Tournament/Block_Full.png'
                else:
                    bar1Cont.width = int(math.ceil(damageState[0] * (barWidth - 4))) + 2
                    bar1Cont.left = barWidth - bar1Cont.width
                    bar1.left = bar1Cont.width - barWidth
                    if damageState[0] < 0.3:
                        bar1.texturePath = 'res:/UI/Texture/Tournament/Block_Damage_Mirror.png'
                    else:
                        bar1.texturePath = 'res:/UI/Texture/Tournament/Block_Full_Mirror.png'
                    bar2Cont.width = int(math.ceil(damageState[1] * (barWidth - 4))) + 2
                    bar2Cont.left = barWidth + barPadding + (barWidth - bar2Cont.width)
                    bar2.left = bar2Cont.width - barWidth
                    if damageState[1] < 0.3:
                        bar2.texturePath = 'res:/UI/Texture/Tournament/Block_Damage_Mirror.png'
                    else:
                        bar2.texturePath = 'res:/UI/Texture/Tournament/Block_Full_Mirror.png'
                    bar3Cont.width = int(math.ceil(damageState[2] * (barWidth - 4))) + 2
                    bar3Cont.left = (barWidth + barPadding) * 2 + (barWidth - bar3Cont.width)
                    bar3.left = bar3Cont.width - barWidth
                    if damageState[2] < 0.3:
                        bar3.texturePath = 'res:/UI/Texture/Tournament/Block_Damage_Mirror.png'
                    else:
                        bar3.texturePath = 'res:/UI/Texture/Tournament/Block_Full_Mirror.png'

            self.leftTeamScore.text = str(teamScores[0])
            self.rightTeamScore.text = str(teamScores[1])
            leftTeamRemainingPointsWidth = int(831 * ((self.maxPoints - teamScores[1]) * 1.0 / self.maxPoints))
            rightTeamRemainingPointsWidth = int(831 * ((self.maxPoints - teamScores[0]) * 1.0 / self.maxPoints))
            self.leftTeamBar.left = 831 - leftTeamRemainingPointsWidth
            self.leftTeamBar.width = leftTeamRemainingPointsWidth
            self.rightTeamBar.width = rightTeamRemainingPointsWidth
            blue.synchro.SleepSim(100)

    def ChangeFancyUIBackground(self, combo, name, textureName):
        self.FancyBackground.texturePath = FANCY_BACKGROUND_PATH + textureName

    def UpdateFancyUIBarMax(self, *args):
        try:
            self.maxEHP = float(self.fancyUIMaxEHPEdit.GetValue())
            self.maxDPS = float(self.fancyUIMaxDPSEdit.GetValue())
            self.maxCont = float(self.fancyUIMaxControlEdit.GetValue())
        except ValueError:
            self.fancyUIMaxEHPEdit.SetValue(str(self.maxEHP))
            self.fancyUIMaxDPSEdit.SetValue(str(self.maxDPS))
            self.fancyUIMaxControlEdit.SetValue(str(self.maxCont))

    def Close(self, *args, **kwds):
        if self.fancyUI:
            self.fancyUI.Close()
        if self.warningLine:
            self.warningLine.Close()
        sm.GetService('target').disableSpinnyReticule = False
        sm.GetService('target').overrideBarHeight = None
        prefs.SetValue('bracketsAlwaysShowShipText', False)
        sm.GetService('bracket').Reload()
        self.ClearSpectatorStandings()
        neocomLayer = uicore.layer.Get('sidePanels')
        if neocomLayer is not None:
            neocomLayer.state = uiconst.UI_PICKCHILDREN
        sm.GetService('infoPanel').ShowHideSidePanel(hide=False)
        Window.Close(self, *args, **kwds)
        uicore.layer.shipUI.display = True

    def ClearSpectatorStandings(self):
        if self.teamDetails is not None:
            charMgr = sm.RemoteSvc('charMgr')
            for team in self.teamDetails:
                charMgr.DeleteContacts([ details['characterID'] for details in team.itervalues() ])

    def LockEveryone(self, *args):
        target = sm.GetService('target')
        for teamIdx in (0, 1):
            for shipID in self.teamDetails[teamIdx].iterkeys():
                uthread.new(target.TryLockTarget, shipID)

    def SortLocks(self, *args):
        target = sm.GetService('target')
        target.rowDict = defaultdict(list)
        for teamIdx in (0, 1):
            for shipID in self.teamDetails[teamIdx].iterkeys():
                if shipID in target.targetsByID:
                    target.rowDict[teamIdx].append(shipID)

        target.ArrangeTargets()

    def ToggleShipText(*args):
        prefs.SetValue('bracketsAlwaysShowShipText', not prefs.GetValue('bracketsAlwaysShowShipText', True))
        sm.GetService('bracket').Reload()

    def ResetFancyUI(self):
        self.fancyUI.Close()
        self.fancyUI = Container(name='AT-Fancy', parent=uicore.layer.inflight, pos=(0,
         746,
         1920,
         334), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)

    def ToggleTacticalOverlay(self, *args):
        sm.GetService('tactical').ToggleOnOff()

    def SetSpectatorCameraModeTactical(self, *args):
        uicore.cmd.GetCommandAndExecute('CmdSetCameraTactical')

    def SetSpectatorCameraModeOrbit(self, *args):
        uicore.cmd.GetCommandAndExecute('CmdSetCameraOrbit')
