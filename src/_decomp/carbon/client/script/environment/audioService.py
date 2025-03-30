#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\environment\audioService.py
import logging
import sys
import audio2
import trinity
import uthread2
import dogma.const as dogmaconst
import eveaudio
import eveaudio.const as audConst
import eveaudio.immersiveoverlay
import evecamera
from carbon.common.script.sys.service import Service
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.script.sys.eveCfg import InShipInSpace
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from eveaudio.eveaudiomanager import CreateAudioManager
from eveaudio.fsdUtils import GetEventFromSoundID
from eveaudio.helpers import CreateAudioObserver
from eveaudio.shiphealthnotification import ShipHealthNotifier
from eveaudio.ui import UIAudioManager
CUSTOM_SOUND_LEVELS_SETTINGS = {'custom_atmosphere': 'advanced_settings_atmosphere',
 'custom_jumpactivation': 'advanced_settings_jump_activations',
 'custom_secondaryinterfaces': 'advanced_settings_secondary_interfaces',
 'custom_shipeffects': 'advanced_settings_ship_effects',
 'custom_shipsounds': 'advanced_settings_ship_sounds',
 'custom_turrets': 'advanced_settings_turrets',
 'custom_warningsfx': 'advanced_settings_warning_sfx',
 'custom_uiclick': 'advanced_settings_uiclick'}
DAMPENING_SETTINGS = {'inactiveSounds_master': 'custom_damp_master',
 'inactiveSounds_music': 'custom_damp_music',
 'inactiveSounds_turrets': 'custom_damp_turrets',
 'inactiveSounds_shield': 'custom_damp_shield',
 'inactiveSounds_armor': 'custom_damp_armor',
 'inactiveSounds_hull': 'custom_damp_hull',
 'inactiveSounds_shipsound': 'custom_damp_shipsound',
 'inactiveSounds_jumpgates': 'custom_damp_jumpgates',
 'inactiveSounds_wormholes': 'custom_damp_wormholes',
 'inactiveSounds_jumping': 'custom_damp_jumping',
 'inactiveSounds_aura': 'custom_damp_aura',
 'inactiveSounds_modules': 'custom_damp_modules',
 'inactiveSounds_explosions': 'custom_damp_explosions',
 'inactiveSounds_warping': 'custom_damp_warping',
 'inactiveSounds_locking': 'custom_damp_locking',
 'inactiveSounds_planets': 'custom_damp_planets',
 'inactiveSounds_impacts': 'custom_damp_impacts',
 'inactiveSounds_deployables': 'custom_damp_deployables',
 'inactiveSounds_boosters': 'custom_damp_boosters',
 'inactiveSounds_stationint': 'custom_damp_stationint',
 'inactiveSounds_stationext': 'custom_damp_stationext',
 'inactiveSounds_structures': 'custom_damp_structures'}
INDUSTRY_LEVELS = {i:u'set_industry_level_%s_state' % (i,) for i in xrange(6)}
RESEARCH_LEVELS = {i:u'set_research_level_%s_state' % (i,) for i in xrange(6)}
logger = logging.getLogger('audioSvc')

def GetAudioService():
    return sm.GetService('audio')


class AudioService(Service):
    __guid__ = 'svc.audio'
    __exportedcalls__ = {'Activate': [],
     'Deactivate': [],
     'GetMasterVolume': [],
     'SetMasterVolume': [],
     'GetUIVolume': [],
     'SetUIVolume': [],
     'GetWorldVolume': [],
     'SetWorldVolume': [],
     'GetVoiceVolume': [],
     'SetVoiceVolume': [],
     'GetCombatMusicUsage': [],
     'MuteSounds': [],
     'UnmuteSounds': [],
     'IsActivated': [],
     'AudioMessage': [],
     'GetDialoguePlayPosition': [],
     'LoadBanksForView': [],
     'PostDialogueEvent': [],
     'SendUIEvent': [],
     'SendUIEventWithCallback': [],
     'SetUIRTPC': [],
     'StartSoundLoop': [],
     'StopSoundLoop': [],
     'SubscribeToEventCallback': [],
     'UnsubscribeFromEventCallback': [],
     'BallSupportsAudio': [],
     'ItemSupportsAudio': [],
     'GetAudioEmittersOnItem': [],
     'GetOrCreateAudioEmitterForItem': [],
     'PlayEventOnItem': [],
     'PlaySoundOnItem': [],
     'StopEventOnItem': [],
     'StopSoundOnItem': [],
     'GetTurretSuppression': [],
     'SetTurretSuppression': [],
     'SetShipState': [],
     'SetupPlanet3DAudio': [],
     'WarpPreparation': [],
     'EnableDebugShowAllEmitters': [],
     'DisableDebugShowAllEmitters': [],
     'GetDebugDisplayAllEmitters': [],
     'SeekOnEventPercent': [],
     'SeekOnEventMs': [],
     'SetGameParameterOnAudioEmitter': []}
    __startupdependencies__ = ['settings', 'sceneManager', 'dynamicMusic']
    __dependencies__ = ['map', 'michelle']
    __notifyevents__ = ['DoBallsAdded',
     'DoBallsRemove',
     'OnActiveCameraChanged',
     'OnBallparkCall',
     'OnBallparkSetState',
     'OnCapacitorChange',
     'OnChannelsJoined',
     'OnClientEvent_ActivateModule',
     'OnClientEvent_DeactivateModule',
     'OnClientEvent_StopShip',
     'OnDamageStateChange',
     'OnDogmaItemChange',
     'OnDungeonTriggerAmbientSound',
     'OnDungeonEntered',
     'OnExitingDungeon',
     'OnIntroCompleted',
     'OnIntroStarted',
     'OnPlanetViewChanged',
     'OnProvingGroundsMatchFound',
     'OnViewStateChanged',
     'OnSessionChanged',
     'OnSessionReset',
     'OnSpecialFX',
     'OnWarpArrived',
     'OnWarpDecelerate',
     'OnClientEvent_WarpFinished']
    __componentTypes__ = ['audioEmitter']

    def __init__(self):
        Service.__init__(self)
        languageID = 'en' if self.AppGetSetting('forceEnglishVoice', False) else session.languageID
        self.manager = CreateAudioManager('res:/Audio/', languageID, 'Eve Client')
        self.soundLoops = {}
        self.lastLookedAt = None
        self.shipHealthNotifier = ShipHealthNotifier(self.SendWiseEvent, self.SetGlobalRTPC)
        self.lastSystemID = None
        self.lastCameraID = None
        self.shipState = None
        self.uiAudioManager = None
        self.immersiveOverlayManager = None
        self.activeAmbientDungeonSounds = []
        self.numEntitiesInPark = 0
        self.engineLimit = 0

    def Run(self, ms = None):
        self.active = False
        self.uiAudioManager = UIAudioManager()
        self.jukeboxPlayer = None
        self.immersiveOverlayManager = eveaudio.immersiveoverlay.Manager(send_audio_event=self.SendUIEvent)
        uthread2.StartTasklet(self._WatchActiveWindow)
        if self.AppGetSetting('audioEnabled', 1):
            self.Activate()

    def Stop(self, stream):
        self.uiAudioManager = None
        self.jukeboxPlayer = None

    def SetGlobalRTPC(self, rtpcName, value):
        if not self.IsActivated():
            return
        self.manager.SetGlobalRTPC(rtpcName, value)

    def SetGlobalState(self, stateGroup, stateName):
        if not self.IsActivated():
            return
        self.manager.SetState(unicode(stateGroup), unicode(stateName))

    def Activate(self):
        self.manager.Enable()
        self.active = True
        self.ApplySettings()
        sm.ScatterEvent('OnAudioActivated')

    def Deactivate(self):
        self.manager.Disable()
        self.activeAmbientDungeonSounds = []
        self.active = False
        sm.ScatterEvent('OnAudioDeactivated')

    def ApplySettings(self):
        self.SetMasterVolume(self.GetMasterVolume())
        self.SetUIVolume(self.GetUIVolume())
        self.SetWorldVolume(self.GetWorldVolume())
        self.SetVoiceVolume(self.GetVoiceVolume())
        self._SetAmpVolume(self.GetMusicVolume())
        self.SetTurretSuppression(self.GetTurretSuppression())
        self.SetOldJukeboxOverride(self.GetOldJukeboxOverride())
        self.SetCombatMusicUsage(self.GetCombatMusicUsage())
        if settings.user.audio.Get('soundLevel_advancedSettings', False):
            self.LoadUpSavedAdvancedSettings()

    def SetMasterVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_master'), vol)
        if persist:
            self.AppSetSetting('masterVolume', vol)

    def GetMasterVolume(self):
        return self.AppGetSetting('masterVolume', 0.7)

    def SetUIVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_ui'), vol)
        if persist:
            self.AppSetSetting('uiGain', vol)

    def GetUIVolume(self):
        return self.AppGetSetting('uiGain', 0.5)

    def SetWorldVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_world'), vol)
        if persist:
            self.AppSetSetting('worldVolume', vol)

    def SetCustomValue(self, vol, settingName, persist = True):
        rtpcConfigName = CUSTOM_SOUND_LEVELS_SETTINGS.get(settingName)
        if not rtpcConfigName:
            return
        self.SetSoundVolumeBetween0and1(volume=vol, configNameRTPC=rtpcConfigName, configNameAppSetting=settingName, persist=persist)

    def SetSoundVolumeBetween0and1(self, volume, configNameRTPC, configNameAppSetting, persist):
        if volume is None:
            volume = settings.user.audio.Get(configNameAppSetting, 0.5)
        if volume < 0.0 or volume > 1.0:
            raise RuntimeError('Erroneous value received for volume, configName=', configNameAppSetting)
        self.SetGlobalRTPC(unicode(configNameRTPC), volume)
        if persist:
            settings.user.audio.Set(configNameAppSetting, volume)

    def EnableAdvancedSettings(self):
        for eachSettingName in CUSTOM_SOUND_LEVELS_SETTINGS.iterkeys():
            self.SetCustomValue(vol=None, settingName=eachSettingName, persist=False)

    def DisableAdvancedSettings(self):
        for eachSettingName in CUSTOM_SOUND_LEVELS_SETTINGS.iterkeys():
            self.SetCustomValue(vol=0.5, settingName=eachSettingName, persist=False)

    def LoadUpSavedAdvancedSettings(self):
        for eachSettingName in CUSTOM_SOUND_LEVELS_SETTINGS.iterkeys():
            volume = settings.user.audio.Get(eachSettingName, 0.5)
            self.SetCustomValue(vol=volume, settingName=eachSettingName, persist=False)

    def SetDampeningValue(self, settingName, setOn = True):
        audioEvent = DAMPENING_SETTINGS.get(settingName)
        if not audioEvent:
            return
        if setOn:
            audioEvent += '_on'
        else:
            audioEvent += '_off'
        self.uiAudioManager.SendUIEvent(audioEvent)

    def SetDampeningValueSetting(self, settingName, setOn = True):
        settings.user.audio.Set(settingName, setOn)

    def DisableDampeningValues(self):
        for eachSettingName in DAMPENING_SETTINGS.iterkeys():
            self.SetDampeningValue(settingName=eachSettingName, setOn=False)

    def LoadUpSavedDampeningValues(self):
        for eachSettingName in DAMPENING_SETTINGS.iterkeys():
            setOn = settings.user.audio.Get(eachSettingName, False)
            self.SetDampeningValue(settingName=eachSettingName, setOn=setOn)

    def GetWorldVolume(self):
        return self.AppGetSetting('worldVolume', 0.7)

    def SetVoiceVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        if not self.IsActivated():
            return
        self.SetGlobalRTPC('volume_voice', vol)
        if persist:
            self.AppSetSetting('evevoiceGain', vol)

    def GetVoiceVolume(self):
        return self.AppGetSetting('evevoiceGain', 0.9)

    def _SetAmpVolume(self, volume = 0.5, persist = True):
        if volume < 0.0 or volume > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        if not self.IsActivated():
            return
        self.SetGlobalRTPC('volume_music', volume)
        if persist:
            self.AppSetSetting('eveampGain', volume)

    def UserSetAmpVolume(self, volume = 0.5, persist = True):
        self._SetAmpVolume(volume, persist)
        sm.GetService('dynamicMusic').MusicVolumeChangedByUser(volume)

    def GetMusicVolume(self):
        return self.AppGetSetting('eveampGain', 0.5)

    def IsActivated(self):
        return self.active

    def HandleFsdSoundID(self, soundID, emitter = None):
        if emitter:
            event = GetEventFromSoundID(soundID)
            if event:
                return emitter.SendEvent(event)
        else:
            self.LogError('FSD sound ID {} was passed in without a corresponding emitter.'.format(soundID))
        return 0

    def SendUIEvent(self, event):
        if not self.IsActivated():
            return
        return self.uiAudioManager.SendUIEvent(event)

    def StopUIEvent(self, playingID):
        self.uiAudioManager.StopUIEvent(playingID)

    def SendUIEventByTypeID(self, typeID):
        self.uiAudioManager.SendUIEventByTypeID(typeID)

    def PostDialogueEvent(self, event):
        self.uiAudioManager.PostDialogueEvent(event)

    def AppGetSetting(self, setting, default):
        try:
            return settings.public.audio.Get(setting, default)
        except (AttributeError, NameError):
            return default

    def AppSetSetting(self, setting, value):
        try:
            settings.public.audio.Set(setting, value)
        except (AttributeError, NameError):
            pass

    def AudioMessage(self, msg, msgKey = None):
        if not self.IsActivated():
            return
        self.uiAudioManager.SendAudioMessage(msg, userErrorKey=msgKey)

    def StartSoundLoop(self, rootLoopMsg):
        if not self.IsActivated():
            return
        try:
            if rootLoopMsg not in self.soundLoops:
                self.LogInfo('StartSoundLoop starting loop with root %s' % rootLoopMsg)
                self.soundLoops[rootLoopMsg] = 1
                self.uiAudioManager.SendUIEvent('msg_%s_play' % rootLoopMsg)
            else:
                self.soundLoops[rootLoopMsg] += 1
                self.LogInfo('StartSoundLoop incrementing %s loop to %d' % (rootLoopMsg, self.soundLoops[rootLoopMsg]))
        except:
            self.LogWarn('StartSoundLoop failed - halting loop with root', rootLoopMsg)
            self.uiAudioManager.SendUIEvent('msg_%s_stop' % rootLoopMsg)
            sys.exc_clear()

    def StopSoundLoop(self, rootLoopMsg, eventMsg = None):
        if rootLoopMsg not in self.soundLoops:
            self.LogInfo('StopSoundLoop told to halt', rootLoopMsg, 'but that message is not playing!')
            return
        try:
            self.soundLoops[rootLoopMsg] -= 1
            if self.soundLoops[rootLoopMsg] <= 0:
                self.LogInfo('StopSoundLoop halting message with root', rootLoopMsg)
                del self.soundLoops[rootLoopMsg]
                self.uiAudioManager.SendUIEvent('msg_%s_stop' % rootLoopMsg)
            else:
                self.LogInfo('StopSoundLoop decremented count of loop with root %s to %d' % (rootLoopMsg, self.soundLoops[rootLoopMsg]))
        except:
            self.LogWarn('StopSoundLoop failed due to an exception - forcibly halting', rootLoopMsg)
            self.uiAudioManager.SendUIEvent('msg_%s_stop' % rootLoopMsg)
            sys.exc_clear()

        if eventMsg is not None:
            self.uiAudioManager.SendUIEvent(eventMsg)

    def SetupPlanet3DAudio(self, planet, typeID):
        if typeID in audConst.PLANET_3D_AUDIO_TRIGGERS.keys():
            events = [audConst.PLANET_3D_AUDIO_TRIGGERS[typeID]]
            if IsTriglavianSystem(session.solarsystemid2):
                events.append(audConst.TRIG_PLANET_3D_TRIGGER)
            observer = CreateAudioObserver('planet_atmosphere')
            observer.observer.SetAttenuationScalingFactor(planet.radius)
            [ observer.observer.SendEvent(event) for event in events ]
            planet.observers.append(observer)

    def GetTurretSuppression(self):
        return self.AppGetSetting('suppressTurret', 0)

    def SetTurretSuppression(self, suppress, persist = True):
        if not self.IsActivated():
            return
        if suppress:
            self.SetGlobalRTPC('turret_muffler', 0.0)
            suppress = 1
        else:
            self.SetGlobalRTPC('turret_muffler', 1.0)
            suppress = 0
        if persist:
            self.AppSetSetting('suppressTurret', suppress)

    def GetOldJukeboxOverride(self):
        return self.AppGetSetting('useOldJukeboxOverride', 0)

    def SetOldJukeboxOverride(self, useClassicMusic):
        self.AppSetSetting('useOldJukeboxOverride', useClassicMusic)

    def GetCombatMusicUsage(self):
        return self.AppGetSetting('useCombatMusic', 1)

    def SetCombatMusicUsage(self, useCombatMusic):
        self.AppSetSetting('useCombatMusic', useCombatMusic)

    def MuteSounds(self):
        self.SetMasterVolume(0.0, False)

    def UnmuteSounds(self):
        self.SetMasterVolume(self.GetMasterVolume(), False)

    def SendWiseEvent(self, event):
        if event:
            self.uiAudioManager.SendUIEvent(event)

    def OnChannelsJoined(self, channelIDs):
        if not session.stationid:
            return
        if (('solarsystemid2', session.solarsystemid2),) in channelIDs:
            pilotsInChannel = eveaudio.GetPilotsInSystem()
            self.SetHangarPopulationSwitch(pilotsInChannel)

    def OnClientEvent_ActivateModule(self, effectID):
        if effectID == dogmaconst.effectModuleBonusMicrowarpdrive:
            self._SetControllerVariableOnShip(audConst.ModuleType.__name__, audConst.ModuleType.microwarpdrive.value)
        elif effectID == dogmaconst.effectModuleBonusAfterburner:
            self._SetControllerVariableOnShip(audConst.ModuleType.__name__, audConst.ModuleType.afterburner.value)
        self._SetControllerVariableOnShip(audConst.ModuleState.__name__, audConst.ModuleState.activated.value)

    def OnClientEvent_DeactivateModule(self, effectID):
        if effectID == dogmaconst.effectModuleBonusMicrowarpdrive:
            self._SetControllerVariableOnShip(audConst.ModuleType.__name__, audConst.ModuleType.microwarpdrive.value)
        elif effectID == dogmaconst.effectModuleBonusAfterburner:
            self._SetControllerVariableOnShip(audConst.ModuleType.__name__, audConst.ModuleType.afterburner.value)
        self._SetControllerVariableOnShip(audConst.ModuleState.__name__, audConst.ModuleState.powerdown.value)

    def OnClientEvent_StopShip(self):
        self._SetControllerVariableOnShip(audConst.STOP_SHIP_CTRL_VARIABLE, 1)

    def SetHangarPopulationSwitch(self, pilotsInChannel):
        self.uiAudioManager.SendUIEvent(eveaudio.GetHangarPopulationSwitch(pilotsInChannel))

    def SwapBanks(self, banks):
        self.manager.SwapSoundBanks(banks)

    def ReloadBanks(self):
        soundBankStatus = self.manager.ReloadSoundBanks()
        self.ApplySettings()
        return soundBankStatus

    def OnDamageStateChange(self, *args, **kwargs):
        return self.shipHealthNotifier.OnDamageStateChange(*args, **kwargs)

    def OnCapacitorChange(self, *args, **kwargs):
        return self.shipHealthNotifier.OnCapacitorChange(*args, **kwargs)

    def OnSessionChanged(self, isRemote, session, change):
        if 'userid' in change and session.userid:
            self.ApplySettings()
        if not session.stationid:
            if 'solarsystemid' in change:
                oldSolarSystem, newSolarSystem = change['solarsystemid']
                if oldSolarSystem and newSolarSystem:
                    eveaudio.PlaySystemSpecificEntrySound(self.lastSystemID, session.solarsystemid2, self.uiAudioManager.GetUIEmitter())
            self.lastSystemID = session.solarsystemid2
        if 'shipid' in change:
            oldShipID, newShipID = change['shipid']
            self._SetControllerVariableOnShip(audConst.ActingParty.__name__, audConst.ActingParty.firstParty.value, shipID=newShipID)
            self._SetControllerVariableOnShip(audConst.ActingParty.__name__, audConst.ActingParty.thirdParty.value, shipID=oldShipID)

    def OnSessionReset(self):
        self.manager.manager.StopAll()
        self.numEntitiesInPark = 0
        self.activeAmbientDungeonSounds = []

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, *args, **kwargs):
        if guid == audConst.MICROWARPDRIVE_GUID or guid == audConst.AFTERBURNER_GUID:
            if guid == audConst.MICROWARPDRIVE_GUID:
                self._SetControllerVariableOnShip(audConst.ModuleType.__name__, audConst.ModuleType.microwarpdrive.value, shipID=shipID)
            else:
                self._SetControllerVariableOnShip(audConst.ModuleType.__name__, audConst.ModuleType.afterburner.value, shipID=shipID)
            if not start:
                self._SetControllerVariableOnShip(audConst.ModuleState.__name__, audConst.ModuleState.deactivated.value, shipID=shipID)
            else:
                self._SetControllerVariableOnShip(audConst.ModuleState.__name__, audConst.ModuleState.activated.value, shipID=shipID)
        elif guid == audConst.WARPING_GUID:
            if shipID != session.shipid:
                self._SetControllerVariableOnShip(audConst.WarpState.__name__, audConst.WarpState.prep.value, shipID=shipID)

    def LoadBanksForView(self, newView):
        if newView == ViewState.Hangar:
            self.SetGlobalState('in_hangar', 'yes')
            self.SwapBanks(eveaudio.EVE_HANGAR_BANKS)
            eveaudio.SetTheraSystemHangarSwitch(session.solarsystemid2, self.uiAudioManager.GetUIEmitter())
        elif newView == ViewState.Space:
            self.SwapBanks(eveaudio.EVE_SPACE_BANKS)
        if newView != ViewState.Hangar:
            self.SetGlobalState('in_hangar', 'no')

    def _WatchActiveWindow(self):
        isActive = None
        while True:
            if settings.user.audio.Get('inactiveSounds_advancedSettings', False):
                if trinity.app.IsActive() != isActive:
                    isActive = trinity.app.IsActive()
                    if isActive:
                        self.DisableDampeningValues()
                    else:
                        self.LoadUpSavedDampeningValues()
            uthread2.Sleep(0.3)

    def OnBallparkSetState(self):
        self.SetResearchAndIndustryLevel()

    def SetResearchAndIndustryLevel(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return
        industryLevel = ballpark.industryLevel
        researchLevel = ballpark.researchLevel
        if industryLevel in INDUSTRY_LEVELS.keys():
            self.uiAudioManager.SendUIEvent(INDUSTRY_LEVELS.get(industryLevel))
        if researchLevel in RESEARCH_LEVELS.keys():
            self.uiAudioManager.SendUIEvent(RESEARCH_LEVELS.get(researchLevel))

    def OnDogmaItemChange(self, *args, **kwargs):
        if not InShipInSpace():
            return
        shipid = session.shipid
        ship = sm.StartService('godma').GetItem(shipid)
        if shipid and ship:
            cargoHoldState = ship.GetCapacity()
            return self.shipHealthNotifier.OnCargoHoldChange(shipid, cargoHoldState, *args, **kwargs)

    def OnDungeonTriggerAmbientSound(self, dungeonID, soundID, entityItemID):
        logger.info('Ambient sound {} was requested to play in dungeon {} on item {}'.format(soundID, dungeonID, entityItemID))
        emitterID = self.PlaySoundOnItem(soundID, entityItemID)
        if emitterID > 0:
            self.activeAmbientDungeonSounds.append((emitterID, soundID))

    def OnDungeonEntered(self, dungeonID, instanceID):
        self.activeAmbientDungeonSounds = []

    def OnExitingDungeon(self, dungeonID):
        if self.activeAmbientDungeonSounds:
            for emitterID, soundID in self.activeAmbientDungeonSounds:
                stopped = self.StopSoundOnEmitter(soundID, emitterID)
                if stopped:
                    logger.info('Ambient sound {} was stopped for dungeon {}'.format(soundID, dungeonID))

            self.activeAmbientDungeonSounds = []

    def OnIntroCompleted(self):
        self.SetGlobalState(*audConst.VIDEO_OVERLAY_STATE_OFF)

    def OnIntroStarted(self):
        self.SetGlobalState(*audConst.VIDEO_OVERLAY_STATE_ON)

    def OnPlanetViewChanged(self, planetID, oldPlanetID):
        events = []
        if planetID and not oldPlanetID:
            planetData = self.map.GetPlanetInfo(planetID)
            events.append(audConst.PI_AUDIO_TRIGGERS.get(planetData.typeID))
            if IsTriglavianSystem(session.solarsystemid2):
                events.append(audConst.TRIG_PLANET_PI_TRIGGER)
        elif oldPlanetID and not planetID:
            planetData = self.map.GetPlanetInfo(oldPlanetID)
            events.append(audConst.PI_AUDIO_TRIGGERS.get(planetData.typeID).replace('play', 'stop'))
            if IsTriglavianSystem(session.solarsystemid2):
                events.append(audConst.TRIG_PLANET_PI_TRIGGER.replace('play', 'stop'))
        [ self.uiAudioManager.SendUIEvent(event) for event in events ]

    def OnProvingGroundsMatchFound(self):
        self.uiAudioManager.SendUIEvent(audConst.UI_AUDIO_TRIGGERS['arena_opponent_matched'] + '_play')

    def OnViewStateChanged(self, fromView, toView):
        self.numEntitiesInPark = 0

    def DoBallsAdded(self, ballsToAdd):
        numEntities = 0
        for ball, slimItem in ballsToAdd:
            if getattr(slimItem, 'categoryID', None) in audConst.ENGINE_LIMITING_CATEGORIES:
                numEntities += 1

        self.numEntitiesInPark += numEntities
        self._LimitEnginesIfNeeded()

    def DoBallsRemove(self, pythonBalls, isRelease):
        numEntities = 0
        for ball, slimItem, terminal in pythonBalls:
            if getattr(slimItem, 'categoryID', None) in audConst.ENGINE_LIMITING_CATEGORIES:
                numEntities += 1

        self.numEntitiesInPark -= numEntities
        self._LimitEnginesIfNeeded()

    def OnActiveCameraChanged(self, cameraID):
        if session is None or self.lastCameraID == cameraID:
            return
        self.uiAudioManager.SendUIEvent('ship_camera_sounds_stop')
        if cameraID == evecamera.CAM_TACTICAL:
            self.uiAudioManager.SendUIEvent('state_camera_set_overview')
        elif cameraID == evecamera.CAM_SHIPPOV:
            if hasattr(session, 'shipid') and session.shipid is not None:
                ship = sm.GetService('michelle').GetItem(session.shipid)
                if ship:
                    self.uiAudioManager.SendUIEvent('state_camera_set_cockpit')
        else:
            self.uiAudioManager.SendUIEvent('state_camera_set_normal')

    def SetUIRTPC(self, rtpcName, value):
        self.uiAudioManager.SetUIRTPC(rtpcName, value)

    def WarpPreparation(self, action, shipID):
        ball = sm.GetService('michelle').GetBall(shipID)
        if action == 'play':
            if not self.GetShipState() == audConst.ShipState.preparing_warp:
                self._SetControllerVariableOnShip(audConst.WarpState.__name__, audConst.WarpState.prep.value, ball=ball, shipID=shipID)
                self.uiAudioManager.SendUIEvent(audConst.UI_AUDIO_TRIGGERS['warp_prep'] + '_play')
                self.AudioMessage('', msgKey='WarpDriveActive')
                self.SetShipState(audConst.ShipState.preparing_warp)
        if action == 'stop':
            if self.GetShipState() == audConst.ShipState.preparing_warp:
                self._SetControllerVariableOnShip(audConst.WarpState.__name__, audConst.WarpState.start.value, ball=ball, shipID=shipID)
                self.uiAudioManager.SendUIEvent(audConst.UI_AUDIO_TRIGGERS['warp_prep'] + '_stop')
                self.SetShipState(audConst.ShipState.warping)
        if action == 'cancel':
            if self.GetShipState() == audConst.ShipState.preparing_warp:
                self._SetControllerVariableOnShip(audConst.WarpState.__name__, audConst.WarpState.stop.value, ball=ball, shipID=shipID)
                self.uiAudioManager.SendUIEvent(audConst.UI_AUDIO_TRIGGERS['warp_prep_abort'] + '_play')
                self.SetShipState(audConst.ShipState.idle)

    def SetShipState(self, value):
        self.shipState = value

    def GetShipState(self):
        return self.shipState

    def SendUIEventWithCallback(self, event):
        return self.uiAudioManager.SendUIEventWithCallback(unicode(event))

    def SubscribeToEventCallback(self, callbackFunc):
        self.uiAudioManager.SubscribeToEventCallback(callbackFunc)

    def UnsubscribeFromEventCallback(self, callbackFunc):
        self.uiAudioManager.UnsubscribeFromEventCallback(callbackFunc)

    def OnBallparkCall(self, funcname, args):
        if args[0] == session.shipid:
            if funcname == 'WarpTo':
                self.WarpPreparation('play', args[0])
            if funcname == 'Stop':
                self.WarpPreparation('cancel', args[0])

    def OnWarpArrived(self, *args):
        self._SetControllerVariableOnShip(audConst.WarpState.__name__, audConst.WarpState.decelerate.value)

    def OnWarpDecelerate(self, warpToItemID, warpToTypeID):
        self.uiAudioManager.SendUIEvent('ship_warp_wind_end')
        self._SetControllerVariableOnShip(audConst.WarpState.__name__, audConst.WarpState.stop.value)

    def OnClientEvent_WarpFinished(self, warpToItemID, warpToTypeID):
        self._SetControllerVariableOnShip(audConst.WarpState.__name__, audConst.WarpState.finished.value)

    def PlayEventOnItem(self, event, itemID, emitterName = '3d_sfx', maxTries = 10, sleepTime = 0.5):
        ball = self._GetAndWaitForBall(itemID, maxTries=maxTries, sleepTime=sleepTime)
        if ball:
            audioEmitter = self.GetOrCreateAudioEmitterForItem(itemID, emitterName=emitterName, ball=ball)
            if audioEmitter:
                playingID = audioEmitter.SendEvent(event)
                if playingID > 0:
                    return audioEmitter.ID
        return 0

    def StopEventOnItem(self, event, itemID):
        audioEmitters = self.GetAudioEmittersOnItem(itemID)
        stopped = False
        for emitter in audioEmitters:
            stopped = emitter.StopEvent(event)
            if stopped:
                break

        return stopped

    def PlaySoundOnItem(self, soundID, itemID, emitterName = '3d_sfx', maxTries = 10, sleepTime = 0.5):
        event = GetEventFromSoundID(soundID)
        if event:
            return self.PlayEventOnItem(event, itemID, emitterName=emitterName, maxTries=maxTries, sleepTime=sleepTime)
        return 0

    def StopSoundOnItem(self, soundID, itemID):
        event = GetEventFromSoundID(soundID)
        if event:
            return self.StopEventOnItem(event, itemID)
        return False

    def StopSoundOnEmitter(self, soundID, emitterID, fadeOutDuration = 1000):
        event = GetEventFromSoundID(soundID)
        if event:
            emitter = self.manager.GetAudioEmitter(emitterID)
            if emitter:
                return emitter.StopEvent(event, fadeOutDuration)
        return False

    def ItemSupportsAudio(self, itemID, ball = None):
        if not ball:
            ball = self.michelle.GetBallAndWaitForModel(itemID)
        if ball:
            if self.BallSupportsAudio(ball):
                return True
        return False

    def BallSupportsAudio(self, ball):
        model = ball.GetModel()
        if model:
            if hasattr(model, 'observers'):
                return True
        return False

    def GetAudioEmittersOnItem(self, itemID):
        audioEmitters = []
        ball = self.michelle.GetBallAndWaitForModel(itemID)
        if ball:
            model = ball.GetModel()
            if model:
                audioEmitters = model.Find('audio2.AudEmitter')
        return audioEmitters

    def SetGameParameterOnAudioEmitter(self, emitterID, parameterName, parameterValue):
        emitter = self.manager.GetAudioEmitter(emitterID)
        if emitter:
            emitter.SetRTPC(parameterName, parameterValue)
            return True
        return False

    def SetDebugLogCallback(self, callback):
        self.manager.SetDebugLogCallback(callback)

    def StopDebugLogging(self):
        self.manager.StopDebugLogging()

    def EnableDebugShowAllEmitters(self):
        self.manager.manager.EnableDebugDisplayAllEmitters()

    def DisableDebugShowAllEmitters(self):
        self.manager.manager.DisableDebugDisplayAllEmitters()

    def GetDebugDisplayAllEmitters(self):
        try:
            return self.manager.manager.GetDebugDisplayAllEmitters()
        except AttributeError:
            return False

    def _SetControllerVariableOnShip(self, variableName, variableValue, ball = None, shipID = 0):
        if not shipID:
            shipID = session.shipid
        if shipID:
            if not ball:
                ball = self.michelle.GetBallAndWaitForModel(shipID)
            if ball and hasattr(ball, 'SetControllerVariable'):
                ball.SetControllerVariable(variableName, variableValue)

    def _LimitEnginesIfNeeded(self):
        if self.numEntitiesInPark > audConst.ENGINE_LIMIT_MIN:
            if not self.engineLimit > 0:
                logger.debug('Engine audio voice limiting activated.'.format(audConst.ENGINE_LIMIT_MIN))
            oneFifth = audConst.ENGINE_LIMIT_MIN / 5 % 100
            newLimit = 0
            if self.numEntitiesInPark in range(audConst.ENGINE_LIMIT_MIN, int(audConst.ENGINE_LIMIT_MAX * 0.5)):
                newLimit = oneFifth * 4 % 100
            elif self.numEntitiesInPark in range(int(audConst.ENGINE_LIMIT_MAX * 0.5), int(audConst.ENGINE_LIMIT_MAX * 0.75)):
                newLimit = oneFifth * 3 % 100
            elif self.numEntitiesInPark in range(int(audConst.ENGINE_LIMIT_MAX * 0.75), audConst.ENGINE_LIMIT_MAX):
                newLimit = oneFifth * 2 % 100
            elif self.numEntitiesInPark > audConst.ENGINE_LIMIT_MAX:
                newLimit = oneFifth
            if self.engineLimit != newLimit:
                self.engineLimit = newLimit
                self.SetGlobalRTPC(audConst.ENGINE_LIMIT_RTPC, newLimit)
                logger.debug('Engine audio voice limit is {} ships at one time because there are {} entities in the park'.format(newLimit, self.numEntitiesInPark))
        elif self.numEntitiesInPark < audConst.ENGINE_LIMIT_MIN and self.engineLimit > 0:
            logger.debug('Engine audio voice limiting deactivated. There are less than {} entities in the park'.format(audConst.ENGINE_LIMIT_MIN))
            self.engineLimit = 0
            self.SetGlobalRTPC(audConst.ENGINE_LIMIT_RTPC, audConst.ENGINE_LIMIT_MIN)

    def _GetAndWaitForBall(self, itemID, maxTries = 10, sleepTime = 0.5):
        ball = None
        sleepCount = 0
        while not ball:
            if sleepCount > maxTries:
                break
            ball = self.michelle.GetBall(itemID)
            if not ball:
                sleepCount += 1
                uthread2.Sleep(sleepTime)

        return ball

    def _GetOrCreateAudioEmitterForBall(self, ball, emitterName = 'entity_sfx'):
        audioEmitter = None
        if ball:
            if self.BallSupportsAudio(ball):
                model = ball.GetModel()
                emitter = model.Find('audio2.AudEmitter')
                if emitter:
                    audioEmitter = emitter[0]
                    logger.info('Found existing audio emitter {} for ball {}.'.format(audioEmitter.name, ball.id))
                else:
                    newObserver = CreateAudioObserver(emitterName)
                    model.observers.append(newObserver)
                    audioEmitter = newObserver.observer
                    logger.info('Created new audio emitter {} for ball {}'.format(audioEmitter.name, ball.id))
        return audioEmitter

    def GetOrCreateAudioEmitterForItem(self, itemID, emitterName = 'entity_sfx', ball = None):
        if not ball:
            ball = self.michelle.GetBallAndWaitForModel(itemID)
        audioEmitter = None
        if self.ItemSupportsAudio(itemID, ball=ball):
            audioEmitter = self._GetOrCreateAudioEmitterForBall(ball, emitterName=emitterName)
        return audioEmitter

    def SeekOnEventPercent(self, playingID, percentToSeek):
        self.uiAudioManager.SeekOnEventPercent(playingID, percentToSeek)

    def SeekOnEventMs(self, playingID, msToSeek):
        self.uiAudioManager.SeekOnEventMs(playingID, msToSeek)

    def GetDialoguePlayPosition(self, playingID):
        return self.uiAudioManager.GetEventPlayPosition(playingID)

    def CreateImmersiveOverlay(self, name):
        return self.immersiveOverlayManager.create(name)
