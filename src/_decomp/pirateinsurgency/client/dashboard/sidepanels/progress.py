#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\sidepanels\progress.py
from eve.client.script.ui.services.insurgenceDashboardSvc import WrapCallbackWithErrorHandling
from functools import partial
import carbonui
import gametime
import localization
import uthread2
from carbonui import uiconst, TextColor, TextBody
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from characterdata.factions import get_faction_name
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.skillPlan.skillPlanInfoIcon import SkillPlanInfoIcon
from evelink.client import location_link
from localization import GetByLabel
from pirateinsurgency.client.dashboard.const import WARZONE_ID_TO_PIRATE_FACTION_ID, GetPirateFactionIDFromWarzoneID, GetFactionColorFromPerspectiveOfMilitia, GetSuppressionColor
from pirateinsurgency.client.dashboard.widgets.track import FactionScoreProgressTrack
from pirateinsurgency.const import CAMPAIGN_STATE_FORECASTING, CAMPAIGN_STATE_PIRATE_WIN, CAMPAIGN_STATE_ANTIPIRATE_WIN, PIRATE_BADGE, ANTIPIRATE_BADGE, CAMPAIGN_STATE_NO_WINNER

class Progress(ContainerAutoSize):
    default_clipChildren = True
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(Progress, self).ApplyAttributes(attributes)
        self.dashboardSvc = attributes.get('dashboardSvc')

    def SuppressionStageCallback(self, stage, snapshot):
        self.suppressionTrackCont.Flush()
        highlightColor = GetSuppressionColor(fill=False)
        antipirateAmbitionModifier = max(0, snapshot.antipiratePointsRequired - snapshot.piratePointsRequired)
        FactionScoreProgressTrack(parent=self.suppressionTrackCont, align=uiconst.TOTOP, name='suppressionTrack', trackColor=eveColor.GUNMETAL_GREY, trackBackgroundColor=eveColor.MATTE_BLACK, highlightColor=highlightColor, value=stage, stages=snapshot.antipiratePointsRequired, badgeTexturePath='res:/UI/Texture/classes/pirateinsurgencies/faction_badges/antipirate_32.png', ambitionModifier=antipirateAmbitionModifier)

    def CorruptionStageCallback(self, stage, snapshot):
        self.corruptionTrackCont.Flush()
        pirateFactionID = GetPirateFactionIDFromWarzoneID(snapshot.warzoneID)
        highlightColor = GetFactionColorFromPerspectiveOfMilitia(session.warfactionid, pirateFactionID, fill=False)
        pirateAmbitionModifier = max(0, snapshot.piratePointsRequired - snapshot.antipiratePointsRequired)
        FactionScoreProgressTrack(parent=self.corruptionTrackCont, align=uiconst.TOTOP, name='corruptionTrack', trackColor=eveColor.GUNMETAL_GREY, trackBackgroundColor=eveColor.MATTE_BLACK, highlightColor=highlightColor, value=stage, stages=snapshot.piratePointsRequired, badgeTexturePath='res:/UI/Texture/classes/pirateinsurgencies/faction_badges/pirate_32.png', ambitionModifier=pirateAmbitionModifier)

    def OnInsurgencySelected(self, campaignSnapshot):
        self.Flush()
        loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER)
        self.cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(16, 0, 16, 16))
        if campaignSnapshot.fsmState == CAMPAIGN_STATE_FORECASTING:
            self.ForecastingState(campaignSnapshot)
            self.AddFOBSpawnedText(campaignSnapshot)
        elif campaignSnapshot.fsmState == CAMPAIGN_STATE_PIRATE_WIN:
            self.PirateWinState()
        elif campaignSnapshot.fsmState == CAMPAIGN_STATE_ANTIPIRATE_WIN:
            self.AntipirateWinState()
        elif campaignSnapshot.fsmState == CAMPAIGN_STATE_NO_WINNER:
            self.NoWinnerState()
        else:
            self.NonForcastingState(campaignSnapshot)
        loadingWheel.Hide()

    def AddFOBSpawnedText(self, campaignSnapshot):
        DividerLine(parent=self.cont, padTop=16, align=uiconst.TOTOP)
        warzoneID = self.dashboardSvc.GetSystemWarzoneID(campaignSnapshot.originSolarsystemID)
        pirateFaction = WARZONE_ID_TO_PIRATE_FACTION_ID[warzoneID]
        factionName = get_faction_name(pirateFaction)
        TextBody(parent=self.cont, padTop=16, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=GetByLabel('UI/PirateInsurgencies/FOBLocationInfo', factionName=factionName, systemName=location_link(campaignSnapshot.originSolarsystemID)))

    def NoWinnerState(self):
        noWinnerCont = ContainerAutoSize(name='noWinnerCont', parent=self.cont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        carbonui.TextBody(parent=noWinnerCont, text=GetByLabel('UI/PirateInsurgencies/noVictory'), align=uiconst.TOTOP)

    def AntipirateWinState(self):
        antipirateWinCont = Container(name='antipirateWinCont', parent=self.cont, align=uiconst.TOTOP, height=48)
        spriteCont = Container(name='spriteCont', parent=antipirateWinCont, align=uiconst.TOLEFT, width=48, height=48)
        Sprite(name='pirateSprite', parent=spriteCont, texturePath='res:/UI/Texture/classes/pirateinsurgencies/faction_badges/antipirate_victory.png', align=uiconst.TOPLEFT, width=48, height=48, top=-10)
        textCont = Container(parent=antipirateWinCont, name='textCont', align=uiconst.TOLEFT, width=200, padLeft=8)
        carbonui.TextBody(text=GetByLabel('UI/PirateInsurgencies/antiPirateVictory'), align=uiconst.TOTOP, parent=textCont, color=TextColor.HIGHLIGHT)
        carbonui.TextBody(align=uiconst.TOTOP, parent=textCont, text=GetByLabel('UI/PirateInsurgencies/insurgencyEnded'))

    def PirateWinState(self):
        pirateWinCont = Container(name='pirateWinCont', parent=self.cont, align=uiconst.TOTOP, height=48)
        spriteCont = Container(name='spriteCont', parent=pirateWinCont, align=uiconst.TOLEFT, height=48, width=48)
        Sprite(name='pirateSprite', parent=spriteCont, texturePath='res:/UI/Texture/classes/pirateinsurgencies/faction_badges/pirate_victory.png', align=uiconst.TOPLEFT, width=48, height=48, top=-8)
        textCont = Container(parent=pirateWinCont, name='textCont', align=uiconst.TOLEFT, width=200, padLeft=8)
        carbonui.TextBody(text=GetByLabel('UI/PirateInsurgencies/pirateVictory'), align=uiconst.TOTOP, parent=textCont, color=TextColor.HIGHLIGHT)
        carbonui.TextBody(align=uiconst.TOTOP, parent=textCont, text=GetByLabel('UI/PirateInsurgencies/insurgencyEnded'))

    def ForecastingState(self, campaignSnapshot):
        carbonui.TextBody(parent=self.cont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/nextInsurgencyIn'), color=TextColor.SECONDARY)
        timerCont = ContainerAutoSize(parent=self.cont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        intervalLeft = max(0, campaignSnapshot.stateExpiryTimestamp - gametime.GetWallclockTime())
        timeString = localization.formatters.FormatTimeIntervalShort(intervalLeft, showFrom='hour', showTo='second')
        time = carbonui.TextHeadline(parent=timerCont, align=uiconst.TOTOP, text=timeString)
        SkillPlanInfoIcon(parent=timerCont, align=uiconst.CENTERRIGHT, width=20, height=20, hint=GetByLabel('UI/PirateInsurgencies/forecastingTooltip'))

        def update_loop():
            while not self.destroyed:
                timeLeft = max(0, campaignSnapshot.stateExpiryTimestamp - gametime.GetWallclockTime())
                timeString = localization.formatters.FormatTimeIntervalShort(timeLeft, showFrom='hour', showTo='second')
                time.SetText(timeString)
                uthread2.Sleep(1)

        uthread2.StartTasklet(update_loop)

    def NonForcastingState(self, campaignSnapshot):
        TextBody(parent=self.cont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/FOBIsIn', systemName=location_link(campaignSnapshot.originSolarsystemID)), padTop=16, color=TextColor.NORMAL, state=uiconst.UI_NORMAL)
        self.suppressionTrackCont = ContainerAutoSize(parent=self.cont, align=uiconst.TOTOP, height=24, padTop=16, name='suppressionTrackCont')
        self.corruptionTrackCont = ContainerAutoSize(parent=self.cont, align=uiconst.TOTOP, height=24, padTop=16, name='corruptionTrackCont')
        suppLW = LoadingWheel(parent=self.suppressionTrackCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        corrLW = LoadingWheel(parent=self.corruptionTrackCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        suppressionCallback = partial(self.SuppressionStageCallback, snapshot=campaignSnapshot)
        wrappedSuppressionCallback = WrapCallbackWithErrorHandling(suppressionCallback, parentContainer=self.suppressionTrackCont, fullErrorBox=False, onErrorCallback=suppLW.Hide)
        corruptionCallback = partial(self.CorruptionStageCallback, snapshot=campaignSnapshot)
        wrappedCorruptionCallback = WrapCallbackWithErrorHandling(corruptionCallback, parentContainer=self.corruptionTrackCont, fullErrorBox=False, onErrorCallback=corrLW.Hide)
        self.dashboardSvc.RequestCurrentSuppressionStage(campaignSnapshot.campaignID, wrappedSuppressionCallback)
        self.dashboardSvc.RequestCurrentCorruptionStage(campaignSnapshot.campaignID, wrappedCorruptionCallback)
