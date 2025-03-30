#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\heroNotifications.py
import eveui
import gametime
import trinity
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import StreamingVideoSprite, Sprite
from carbonui.uianimations import animations
from characterdata.factions import get_faction_name
from characterdata.races import get_race_name
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLargeUpper
from eve.client.script.ui.heronotification.animation import garble_reveal_label
from eve.client.script.ui.heronotification.golden import GoldenPositionContainerAutoSize
import carbonui.const as uiconst
import datetime
import eve.common.lib.appConst as appConst
import factionwarfare.const as fwConst
from eve.common.script.util.facwarCommon import IsPirateFWFaction, IsOccupierFWFaction
from fwwarzone.client.facwarUtil import IsMyOccupierEnemyFaction, IsMyFwFaction
from localization import GetByLabel
DEFAULT_LOW_PRIORITY_VIDEO = 'res:/UI/Texture/classes/frontlines/videos/objectiveAchievedNeutral.webm'
iconMapping = {appConst.factionAmarrEmpire: 'res:/UI/Texture/classes/frontlines/factions/amarr.png',
 appConst.factionCaldariState: 'res:/UI/Texture/classes/frontlines/factions/caldari.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/classes/frontlines/factions/gallente.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/classes/frontlines/factions/minmatar.png'}
adjacencyTextMapping = {fwConst.ADJACENCY_STATE_FRONTLINE: 'UI/FactionWarfare/frontlines/SystemNowFrontline',
 fwConst.ADJACENCY_STATE_SECONDLINE: 'UI/FactionWarfare/frontlines/SystemNowSecondLine',
 fwConst.ADJACENCY_STATE_BACKLINE: 'UI/FactionWarfare/frontlines/SystemNowBackline'}

def _GetLowPriorityVideoPath(positivityState):
    if positivityState > 0:
        return 'res:/UI/Texture/classes/frontlines/videos/objectiveAchievedPositive.webm'
    if positivityState < 0:
        return 'res:/UI/Texture/classes/frontlines/videos/objectiveAchievedNegative.webm'
    return 'res:/UI/Texture/classes/frontlines/videos/objectiveAchievedNeutral.webm'


def _GetHighPriorityVideoPath(positivityState):
    if positivityState > 0:
        return 'res:/UI/Texture/classes/frontlines/videos/systemFlipPositive.webm'
    if positivityState < 0:
        return 'res:/UI/Texture/classes/frontlines/videos/systemFlipNegative.webm'
    return 'res:/UI/Texture/classes/frontlines/videos/systemFlipNeutral.webm'


def _GetPositivityState(goodChangeForTarget, targetFactionID):
    positivityState = 0
    if session.warfactionid:
        if IsMyOccupierEnemyFaction(targetFactionID):
            positivityState = -1 if goodChangeForTarget else 1
        elif IsMyFwFaction(targetFactionID):
            positivityState = 1 if goodChangeForTarget else -1
    return positivityState


def _GetRaceOrFactionName(factionID):
    try:
        raceID = appConst.raceByFaction[factionID]
    except KeyError:
        return get_faction_name(factionID)

    occupierRaceName = get_race_name(raceID)
    return occupierRaceName


def ObjectiveCompletedInSystem(parent, solarSystemID, targetFactionID, objectiveMode):
    if solarSystemID != session.solarsystemid2:
        return
    targetRaceName = _GetRaceOrFactionName(targetFactionID)
    goodChangeForTarget = True
    if objectiveMode == fwConst.OBJECTIVE_MODE_SUPPLY_DEPOT:
        header = GetByLabel('UI/FactionWarfare/frontlines/SupplyDepotDestroyed', factionName=targetRaceName)
        subText = GetByLabel('UI/FactionWarfare/frontlines/WarEffortWeakend')
        goodChangeForTarget = False
    elif objectiveMode == fwConst.OBJECTIVE_MODE_SUPPLY_CACHE:
        header = GetByLabel('UI/FactionWarfare/frontlines/SupplyDepotDestroyed', factionName=targetRaceName)
        subText = GetByLabel('UI/FactionWarfare/frontlines/WarEffortWeakend')
        goodChangeForTarget = False
    elif objectiveMode == fwConst.OBJECTIVE_MODE_RENDEZVOUS_POINT:
        header = GetByLabel('UI/FactionWarfare/frontlines/RendezvousCompleted', factionName=targetRaceName)
        subText = GetByLabel('UI/FactionWarfare/frontlines/WarEffortStrengthened')
    elif objectiveMode == fwConst.OBJECTIVE_MODE_PROPAGANDA:
        header = GetByLabel('UI/FactionWarfare/frontlines/PropagandaBeaconCompleted', factionName=targetRaceName)
        subText = GetByLabel('UI/FactionWarfare/frontlines/WarEffortStrengthened')
    elif objectiveMode == fwConst.OBJECTIVE_MODE_LISTENING_POST:
        header = GetByLabel('UI/FactionWarfare/frontlines/ListeningPostCompleted', factionName=targetRaceName)
        subText = GetByLabel('UI/FactionWarfare/frontlines/WarEffortWeakend')
        goodChangeForTarget = False
    else:
        return
    iconTexturePath = iconMapping.get(targetFactionID, None)
    positivityState = _GetPositivityState(goodChangeForTarget, targetFactionID)
    videoPath = _GetLowPriorityVideoPath(positivityState)
    return ShowLowPriorityFanfare(parent, header.upper(), subText, videoPath, iconTexturePath)


def SystemChangedAdjacency(parent, solarSystemID, currentOccupationState):
    if solarSystemID != session.solarsystemid2:
        return
    videoPath = DEFAULT_LOW_PRIORITY_VIDEO
    labelPath = adjacencyTextMapping.get(currentOccupationState.adjacencyState, None)
    if not labelPath:
        return
    solarSystemName = cfg.evelocations.Get(solarSystemID).name
    header = GetByLabel(labelPath, systemName=solarSystemName)
    subText = GetByLabel('UI/FactionWarfare/frontlines/BattlelinesHaveShifted')
    return ShowLowPriorityFanfare(parent, header.upper(), subText, videoPath)


def SystemFlipped(parent, solarSystemID, currentOccupationState):
    if solarSystemID != session.solarsystemid2:
        return
    occupierID = currentOccupationState.occupierID
    occupierRaceName = _GetRaceOrFactionName(occupierID)
    systemName = cfg.evelocations.Get(solarSystemID).name
    header = GetByLabel('UI/FactionWarfare/frontlines/SystemCaptured', factionName=occupierRaceName, solarSystemName=systemName)
    positivityState = _GetPositivityState(True, occupierID)
    videoPath = _GetHighPriorityVideoPath(positivityState)
    iconTexturePath = iconMapping.get(occupierID, None)
    return ShowHighPriorityFanfare(parent, header.upper(), videoPath, iconTexturePath)


def BattlefieldWon(parent, solarSystemID, winnerFactionID):
    winnerName = _GetRaceOrFactionName(winnerFactionID)
    solarSystemName = cfg.evelocations.Get(solarSystemID).name
    header = GetByLabel('UI/FactionWarfare/frontlines/BattlefieldWon', factionName=winnerName, solarSystemName=solarSystemName)
    subText = GetByLabel('UI/FactionWarfare/frontlines/WarEffortStrengthened')
    positivityState = _GetPositivityState(True, winnerFactionID)
    videoPath = _GetLowPriorityVideoPath(positivityState)
    iconTexturePath = iconMapping.get(winnerFactionID, None)
    return ShowLowPriorityFanfare(parent, header.upper(), subText, videoPath, iconTexturePath)


def DungeonConquered(parent, factionID):
    headerPath = 'UI/FactionWarfare/frontlines/SiteConquered'
    subTextPath = 'UI/FactionWarfare/frontlines/SiteConqueredSubText'
    return _DungeonCompleted(parent, headerPath, subTextPath, factionID)


def DungeonDefended(parent, factionID):
    headerPath = 'UI/FactionWarfare/frontlines/SiteDefended'
    subTextPath = 'UI/FactionWarfare/frontlines/SiteDefendedSubText'
    return _DungeonCompleted(parent, headerPath, subTextPath, factionID)


def _DungeonCompleted(parent, headerPath, subTextPath, factionID):
    header = GetByLabel(headerPath)
    raceName = _GetRaceOrFactionName(factionID)
    subText = GetByLabel(subTextPath, factionName=raceName)
    videoPath = _GetLowPriorityVideoPath(1)
    iconTexturePath = iconMapping.get(factionID, None)
    return ShowLowPriorityFanfare(parent, header, subText, videoPath, iconTexturePath)


def FullCorruption(parent, solarSystemID):
    if solarSystemID != session.solarsystemid2:
        return
    solarSystemName = cfg.evelocations.Get(solarSystemID).name
    header = GetByLabel('UI/PirateInsurgencies/Notifications/CorruptionStage5', solarSystemName=solarSystemName)
    positivityState = 0
    if IsPirateFWFaction(session.warfactionid):
        positivityState = 1
    elif IsOccupierFWFaction(session.warfactionid):
        positivityState = -1
    videoPath = _GetHighPriorityVideoPath(positivityState)
    return ShowHighPriorityFanfare(parent, header.upper(), videoPath)


def FullSuppression(parent, solarSystemID):
    if solarSystemID != session.solarsystemid2:
        return
    solarSystemName = cfg.evelocations.Get(solarSystemID).name
    header = GetByLabel('UI/PirateInsurgencies/Notifications/SuppressionStage5', solarSystemName)
    positivityState = 0
    if IsOccupierFWFaction(session.warfactionid):
        positivityState = 1
    elif IsPirateFWFaction(session.warfactionid):
        positivityState = -1
    videoPath = _GetHighPriorityVideoPath(positivityState)
    return ShowHighPriorityFanfare(parent, header.upper(), videoPath)


def ShowLowPriorityFanfare(parent, header, subText, videoPath, iconTexturePath = None):
    PlaySound('fanfare_low_priority_play')
    container = GoldenPositionContainerAutoSize(parent=parent, alignMode=uiconst.CENTER, state=uiconst.UI_DISABLED)
    secBeforeFadeOut = 3.9
    video = StreamingVideoSprite(parent=container, align=uiconst.CENTER, pos=(0, 0, 400, 200), videoPath=videoPath, spriteEffect=trinity.TR2_SFX_COPY, blendMode=trinity.TR2_SBM_ADD)

    def _PlayVideo():
        video.Play()
        while not video.isFinished and not video.destroyed:
            eveui.wait_for_next_frame()

    def _ShowMainLabel():
        mainLabel = EveCaptionLarge(parent=container, align=uiconst.CENTER, maxLines=1, opacity=0.0, top=-30)
        then = gametime.GetWallclockTime()
        garble_reveal_label(label=mainLabel, text=header, step_duration=datetime.timedelta(milliseconds=30), time_offset=datetime.timedelta(milliseconds=500))
        duration = gametime.GetSecondsSinceWallclockTime(then)
        timeOffset = max(0, secBeforeFadeOut - duration)
        uthread2.sleep(timeOffset)
        animations.FadeOut(mainLabel, duration=0.5)

    def _ShowSubLabel():
        subLabelCont = ContainerAutoSize(name='subLabelCont', parent=container, align=uiconst.CENTER, top=0, opacity=0.0, alignMode=uiconst.CENTER, idx=0)
        subLabel = EveLabelLargeUpper(parent=subLabelCont, align=uiconst.CENTER, color=eveColor.BLACK, idx=0, text=subText, padding=(4, 2, 4, 2), shadowOffset=(0, 0), shadowSpriteEffect=None)
        fill = Fill(parent=subLabelCont, color=(1, 1, 1, 1), opacity=0.0)
        uthread2.sleep(0.1)
        offset = 1.0
        duration = 0.2
        halfSize = subLabelCont.height / 2
        animations.FadeIn(subLabelCont, duration=0.1, timeOffset=offset)
        animations.FadeIn(fill, duration=0.1, timeOffset=offset)
        animations.MorphScalar(fill, 'height', startVal=halfSize, endVal=0, timeOffset=offset, duration=duration)
        animations.MorphScalar(fill, 'top', startVal=halfSize, endVal=0, timeOffset=offset, duration=duration)
        uthread2.sleep(secBeforeFadeOut)
        animations.MorphScalar(fill, 'height', startVal=0, endVal=halfSize, duration=duration)
        animations.MorphScalar(fill, 'top', startVal=0, endVal=halfSize, duration=duration, callback=fill.Hide)
        animations.FadeOut(subLabel, duration=duration)

    def ShowLogo():
        factionSprite = Sprite(name='factionSprite', parent=container, texturePath=iconTexturePath, pos=(0, 46, 48, 48), align=uiconst.CENTER, idx=0, opacity=0.0)
        animations.FadeIn(factionSprite, duration=0.5, timeOffset=1.0)
        uthread2.sleep(secBeforeFadeOut)
        animations.FadeOut(factionSprite, duration=0.5)

    videoTasklet = uthread2.start_tasklet(_PlayVideo)
    mainLabelTasklet = uthread2.start_tasklet(_ShowMainLabel)
    subLabelTasklet = uthread2.start_tasklet(_ShowSubLabel)
    if iconTexturePath:
        logoTasklet = uthread2.start_tasklet(ShowLogo)
    mainLabelTasklet.get()
    subLabelTasklet.get()
    videoTasklet.get()
    if iconTexturePath:
        logoTasklet.get()


def ShowHighPriorityFanfare(parent, header, videoPath, iconTexturePath = None):
    PlaySound('fanfare_high_priority_play')
    container = GoldenPositionContainerAutoSize(parent=parent, alignMode=uiconst.CENTER, state=uiconst.UI_DISABLED)
    secBeforeFadeOut = 3.9
    video = StreamingVideoSprite(parent=container, align=uiconst.CENTER, pos=(0, 0, 1740, 170), videoPath=videoPath, spriteEffect=trinity.TR2_SFX_COPY, blendMode=trinity.TR2_SBM_ADD)

    def _PlayVideo():
        video.Play()
        while not video.isFinished and not video.destroyed:
            eveui.wait_for_next_frame()

    def _ShowMainLabel():
        mainLabel = EveCaptionLarge(parent=container, align=uiconst.CENTER, maxLines=1, opacity=0.0)
        then = gametime.GetWallclockTime()
        garble_reveal_label(label=mainLabel, text=header, step_duration=datetime.timedelta(milliseconds=30), time_offset=datetime.timedelta(milliseconds=500))
        duration = gametime.GetSecondsSinceWallclockTime(then)
        timeOffset = max(0, secBeforeFadeOut - duration)
        animations.FadeOut(mainLabel, duration=0.5, timeOffset=timeOffset)

    def ShowLogo():
        factionSprite = Sprite(name='factionSprite', parent=container, texturePath=iconTexturePath, pos=(0, 46, 48, 48), align=uiconst.CENTER, idx=0, opacity=0.0)
        animations.FadeIn(factionSprite, duration=1.0, timeOffset=0.5)
        uthread2.sleep(secBeforeFadeOut)
        animations.FadeOut(factionSprite, duration=0.5)

    videoTasklet = uthread2.start_tasklet(_PlayVideo)
    mainLabelTasklet = uthread2.start_tasklet(_ShowMainLabel)
    if iconTexturePath:
        logoTasklet = uthread2.start_tasklet(ShowLogo)
    if iconTexturePath:
        logoTasklet.get()
    mainLabelTasklet.get()
    videoTasklet.get()
