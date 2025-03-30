#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelSeasons.py
import uthread2
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_SEASONS, MODE_HIDDEN
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_SEASONS_INFO_PANEL
from eve.client.script.ui.util.uix import GetTextHeight
from localization import GetByLabel
from seasons.client.challengeinfopaneltaskentry import ChallengeInfoPanelTaskEntry
from carbonui.uicore import uicore
from uihider import UiHiderMixin
from seasons.client.util import OpenSeasonsWindow
COMPLETED_CHALLENGE_FADE_OUT_DURATION = 1.0
DEFAULT_PADDING = 6

class InfoPanelSeasons(UiHiderMixin, InfoPanelBase):
    default_name = 'InfoPanelSeasons'
    uniqueUiName = UNIQUE_NAME_SEASONS_INFO_PANEL
    default_iconTexturePath = 'res:/UI/Texture/classes/Seasons/eventIcon_18x18.png'
    default_state = uiconst.UI_PICKCHILDREN
    label = 'UI/Seasons/InfoPanelChallengesTitle'
    hasSettings = True
    panelTypeID = PANEL_SEASONS
    challengeContainer = None
    __notifyevents__ = ['OnSeasonSelectionUpdated']

    def ApplyAttributes(self, attributes):
        super(InfoPanelSeasons, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.seasonService = sm.GetService('seasonService')
        self.ConstructMainContent()

    def OnSeasonSelectionUpdated(self):
        if self.seasonService.is_season_visible_in_agency():
            self.ConstructMainContent()

    def ConstructMainContent(self):
        self.mainCont.Flush()
        self.SetTitle()
        if self.seasonService.is_selection_needed():
            SeasonalSelectionPanel(parent=self, align=uiconst.TOTOP, descriptionText=self.seasonService.get_navigation_description())
        else:
            SeasonalChallenges(parent=self, align=uiconst.TOTOP)

    def ConstructHeaderButton(self):
        return self.ConstructSimpleHeaderButton()

    def SetTitle(self):
        title = self.seasonService.get_navigation_season_title()
        if title is None:
            title = GetByLabel(self.label)
        self.headerCont.Flush()
        self.titleLabel = self.headerCls(name='title', text=title, parent=self.headerCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)

    @staticmethod
    def IsAvailable():
        seasonSvc = sm.GetService('seasonService')
        return seasonSvc.is_season_visible()


class SeasonalSelectionPanel(ContainerAutoSize):
    default_name = 'SeasonalSelectionPanel'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.descriptionText = attributes.descriptionText
        self.ConstructSelectionPanel()

    def ConstructSelectionPanel(self):
        selectionCont = ContainerAutoSize(parent=self.parent.mainCont, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        Fill(name='selectionPanelBackground', bgParent=selectionCont, state=uiconst.UI_DISABLED, opacity=0.1, color=(1.0, 1.0, 1.0))
        textHeight = GetTextHeight(strng=self.descriptionText, width=256, fontsize=EVE_MEDIUM_FONTSIZE) + 8
        descriptionContainer = Container(parent=selectionCont, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=textHeight, left=DEFAULT_PADDING, top=2, padRight=DEFAULT_PADDING)
        EveLabelMedium(parent=descriptionContainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=self.descriptionText, linkStyle=uiconst.LINKSTYLE_SUBTLE)
        buttonContainer = ContainerAutoSize(parent=selectionCont, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        Button(parent=buttonContainer, texturePath='res:/UI/Texture/classes/agency/icons/ContentTypes/agency.png', align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Seasons/MultipleSeasonsTexts/selectButton'), left=DEFAULT_PADDING, top=DEFAULT_PADDING, func=self.OpenSeasonSelection)

    def OpenSeasonSelection(self, *args):
        OpenSeasonsWindow()

    def _IsCollapsed(self):
        return self.parent.mode == MODE_HIDDEN


class SeasonalChallenges(ContainerAutoSize):
    default_name = 'SeasonalChallenges'
    default_state = uiconst.UI_PICKCHILDREN
    challengeContainer = None
    __notifyevents__ = ['OnChallengeProgressUpdateInClient',
     'OnChallengeCompletedInClient',
     'OnChallengeRewardsGrantedInClient',
     'OnChallengeExpiredInClient',
     'OnSeasonsFsdDataChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.seasonService = sm.GetService('seasonService')
        self._LoadActiveChallenges()
        self.challengeContainer = None
        self.challengeTaskEntries = {}
        self.openChallengesLinkGrid = None
        self._ConstructChallengeContainer()
        self._UpdateChallengeEntries()

    def _LoadActiveChallenges(self):
        self.activeChallenges = self.seasonService.get_active_challenges_by_character_id()

    def _IsCollapsed(self):
        return self.parent.mode == MODE_HIDDEN

    def _ShouldShowChallengeDetails(self):
        return not self._IsCollapsed() and settings.char.ui.Get('show_challenge_details_in_info_panel', True)

    def _ConstructChallengeContainer(self):
        if not self.challengeContainer or self.challengeContainer.destroyed:
            self.parent.mainCont.Flush()
            self.challengeContainer = ContainerAutoSize(parent=self.parent.mainCont, name='challengeContainer', align=uiconst.TOTOP)
        if self.challengeContainer:
            self.challengeContainer.Flush()

    def _UpdateChallengeEntries(self):
        updatedActiveChallenges = self.seasonService.get_active_challenges_by_character_id()
        for challenge_id, challenge in self.activeChallenges.iteritems():
            self.seasonService.get_challenge(challenge_id)
            if challenge_id not in updatedActiveChallenges:
                challengeEntry = self.challengeTaskEntries.pop(challenge_id, None)
                if challengeEntry:
                    challengeEntry.Close()

        for challenge_id, challenge in updatedActiveChallenges.iteritems():
            if challenge.is_dormant:
                challengeEntry = self.challengeTaskEntries.get(challenge_id, None)
                if challengeEntry is not None:
                    animations.FadeIn(challengeEntry)
                    challengeEntry.show_dormant()
                    continue
            idx = updatedActiveChallenges.keys().index(challenge_id)
            if challenge_id not in self.challengeTaskEntries:
                self.challengeTaskEntries[challenge_id] = ChallengeInfoPanelTaskEntry(name='challengeInfoPanelTaskEntry', parent=self.challengeContainer, align=uiconst.TOTOP, challenge=challenge, open_challenges_function=OpenSeasonsWindow, show_details=self._ShouldShowChallengeDetails(), idx=idx)
            self.challengeTaskEntries[challenge_id].idx = idx

        self.activeChallenges = updatedActiveChallenges
        self.challengeContainer.UpdateAlignment()

    def _GetChallenge(self, challengeID):
        return self.seasonService.get_challenge(challengeID)

    def OnChallengeProgressUpdateInClient(self, challengeID, newProgress):
        self._UpdateChallengeEntries()
        self.challengeTaskEntries[challengeID].update_challenge_progress(newProgress)

    def OnChallengeCompletedInClient(self, oldChallengeID):
        if oldChallengeID is None:
            return
        uthread2.start_tasklet(self._HideCompletedChallenge, oldChallengeID)

    def OnChallengeExpiredInClient(self, challengeID):
        uthread2.start_tasklet(self._HideCompletedChallenge, challengeID)

    def OnChallengeRewardsGrantedInClient(self, challengeID):
        challenge = self.activeChallenges.get(challengeID, None)
        challengeEntry = self.challengeTaskEntries.get(challengeID, None)
        if challengeEntry is not None:
            challengeEntry.update_challenge_progress(challenge.max_progress)

    def OnSeasonsFsdDataChanged(self):
        if sm.GetService('seasonService').is_season_visible():
            self._UpdateChallengeEntries()

    def _IsAnyChallengeShown(self):
        return bool(self.activeChallenges)

    def _IsChallengeAlreadyShown(self, challengeID):
        return self._IsAnyChallengeShown() and challengeID in self.activeChallenges

    def _HideCompletedChallenge(self, challengeID):
        challengeEntry = self.challengeTaskEntries.get(challengeID, None)
        if challengeEntry:
            uicore.animations.FadeOut(challengeEntry, duration=COMPLETED_CHALLENGE_FADE_OUT_DURATION)
        uthread2.call_after_wallclocktime_delay(self._UpdateChallengeEntries, COMPLETED_CHALLENGE_FADE_OUT_DURATION * 2)
