#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\ui\projectdiscoveryheader.py
import logging
import blue
import localization
from carbon.common.script.util.format import FmtAmt
from carbonui import fontconst, uiconst
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.polygon import Polygon
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorline import VectorLine
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from uthread2 import StartTasklet
import projectdiscovery.client.const
from projectdiscovery.client.util.util import calculate_score_bar_length, calculate_rank_band
from projectdiscovery.common.const import INITIAL_PLAYER_SCORE, PLAYER_NOT_IN_DATABASE_ERROR_CODE
from projectdiscovery.common.exceptions import NoConnectionToAPIError, MissingKeyError
logger = logging.getLogger(__name__)

class ProjectDiscoveryWindowHeader(Container):
    __notifyevents__ = ['OnPlayerStateUpdated']
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(ProjectDiscoveryWindowHeader, self).ApplyAttributes(attributes)
        self.player_statistics = attributes.get('playerStatistics')
        self.update_score_bar_thread = None
        sm.RegisterNotify(self)
        StartTasklet(self.initialize)

    def initialize(self):
        self.cursor = uiconst.UICURSOR_HASMENU
        self.pdService = sm.RemoteSvc('ProjectDiscovery')
        self._is_mouse_down = False
        self.playerState = self.pdService.get_player_state()
        self.old_player_state = None
        if not self.player_statistics:
            self.player_statistics = self.get_player_statistics(False)
        self.experience = self.playerState.experience
        self.rank = self.playerState.rank
        self.total_xp_needed_for_previous_rank = None
        self.total_xp_needed_for_next_rank = self.pdService.get_total_needed_xp(self.rank + 1)
        self.total_xp_needed_for_current_rank = self.pdService.get_total_needed_xp(self.rank)
        self.full_needle_rotation = -4.7
        self.setup_layout()
        self.score = 0
        self.old_score = 0
        self.needle_Rotation = self.score * self.full_needle_rotation
        self.update_header()
        self._update_tooltips()

    def setup_layout(self):
        self.headerContainer = Container(name='headerContainer', parent=self, align=uiconst.CENTERTOP, height=34, width=230)
        self.scoreBarContainer = Container(name='scoreBarContainer', parent=self, align=uiconst.CENTERBOTTOM, height=8, width=self.headerContainer.width - 10, bgColor=(0.62, 0.54, 0.53, 0.26), top=10)
        self._initialize_score_bar_length()
        self.scoreBar = VectorLine(name='scoreBar', parent=self.scoreBarContainer, align=uiconst.CENTERLEFT, translationFrom=(0, 0), translationTo=(self.calculate_score_bar_length(), 0), colorFrom=(1.0, 1.0, 1.0, 0.95), colorTo=(1.0, 1.0, 1.0, 0.95), widthFrom=3, widthTo=3, left=3)
        VectorLine(name='emptyScoreBar', parent=self.scoreBarContainer, align=uiconst.CENTERLEFT, translationFrom=(0, 0), translationTo=(self.scoreBarLength, 0), colorFrom=(0.0, 0.0, 0.0, 0.75), colorTo=(0.0, 0.0, 0.0, 0.75), widthFrom=3, widthTo=3, left=5)
        self.rankInfoContainer = Container(name='rankInfoContainer', parent=self.headerContainer, align=uiconst.TOLEFT, width=75, top=3)
        self.rankIcon = Sprite(name='rankIcon', parent=self.rankInfoContainer, texturePath=self.get_rank_icon_path(self.rank), height=36, width=36, align=uiconst.TOLEFT, left=5)
        self.rankLabel = eveLabel.Label(parent=self.rankInfoContainer, fontsize=16, text=self.rank, align=uiconst.CENTERLEFT, left=40)
        self.nextRankInfoContainer = Container(name='rankInfoContainer', parent=self.headerContainer, align=uiconst.TORIGHT, width=75, top=3)
        self.nextRankIcon = Sprite(name='rankIcon', parent=self.nextRankInfoContainer, texturePath=self.get_rank_icon_path(self.rank + 1), height=36, width=36, align=uiconst.TORIGHT, left=5)
        self.nextRankLabel = eveLabel.Label(parent=self.nextRankInfoContainer, fontsize=16, text=self.rank + 1, align=uiconst.CENTERRIGHT, left=40)
        self.accuracyRatingContainer = Container(name='accuracyRatingContainer', parent=self.headerContainer, align=uiconst.CENTER, width=75, height=35, left=5, top=3)
        self.accuracyRatingIconContainer = Container(name='accuracyRatingIconContainer', parent=self.accuracyRatingContainer, height=32, width=32, align=uiconst.CENTER, top=-7, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/accuracyMeterBack.png')
        self.emptySprite = Sprite(name='emptySprite', parent=self.accuracyRatingIconContainer, width=32, height=32, align=uiconst.CENTER)
        SetTooltipHeaderAndDescription(targetObject=self.emptySprite, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/AccuracyRatingTooltip'))
        self.accuracyNeedleIconContainer = Transform(parent=self.accuracyRatingIconContainer, height=32, width=32, align=uiconst.TORIGHT, rotation=0)
        self.accuracyNeedleIcon = Sprite(name='accuracyNeedleIcon', parent=self.accuracyNeedleIconContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/accuracyMeterNeedle.png', width=32, height=32, rotation=2.4, align=uiconst.CENTER)
        self.accuracyArcFill = Polygon(parent=self.accuracyRatingIconContainer, align=uiconst.CENTER)
        self.accuracyArcFill.MakeArc(radius=0, outerRadius=10, fromDeg=-225.0, toDeg=-225.0, outerColor=(1.0, 1.0, 0, 0.7), innerColor=(1.0, 1.0, 0, 0.7))
        self.accuracyRatingLabel = eveLabel.Label(name='AccuracyRating', parent=self.accuracyRatingContainer, fontsize=fontconst.EVE_SMALL_FONTSIZE, text='00,0%', align=uiconst.CENTERBOTTOM, autoFitToText=True, height=20, top=1)
        self.state = uiconst.UI_NORMAL

    def _initialize_score_bar_length(self):
        self.scoreBarLength = self.scoreBarContainer.width - 10
        self.oldScoreBarLength = self.calculate_score_bar_length()

    def OnMouseDownDrag(self, *args):
        if self._is_mouse_down:
            sm.ScatterEvent('OnProjectDiscoveryHeaderDragged')

    def OnMouseDown(self, *args):
        self._is_mouse_down = True
        sm.ScatterEvent('OnProjectDiscoveryMouseDownOnHeader')

    def OnMouseUp(self, *args):
        self._is_mouse_down = False

    def OnMouseEnter(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryMouseEnterHeader')

    def OnMouseExit(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryMouseExitHeader')

    def get_player_statistics(self, get_history):
        statistics = None
        try:
            statistics = self.pdService.get_player_statistics(get_history)
        except (NoConnectionToAPIError, MissingKeyError):
            sm.ScatterEvent('OnNoConnectionToAPIError')

        return statistics

    def update_accuracy_rating_text(self):
        if self.score > 0.9991:
            self.score = 1
        self.accuracyRatingLabel.SetText(str(FmtAmt(self.score * 100, showFraction=1) + '%'))

    def update_accuracy_meter(self):
        self.accuracyNeedleIconContainer.rotation = self.needle_Rotation
        self.accuracyArcFill.MakeArc(radius=0, outerRadius=10, fromDeg=-225.0, toDeg=self.score * 265 - 225.0, outerColor=(1.0, 1.0, 0, 0.7), innerColor=(1.0, 1.0, 0, 0.7))

    def OnPlayerStateUpdated(self, player_state):
        self.old_player_state = self.playerState
        self.playerState = player_state
        if self.has_progress_changed():
            self.OnUpdateScoreBar(self.playerState)
        self._update_tooltips()

    def has_progress_changed(self):
        if self.old_player_state.experience != self.playerState.experience:
            return True
        if self.old_player_state.rank != self.playerState.rank:
            return True
        return False

    def update_score(self, score):
        self.old_score = self.score
        self.score = score
        animations.MorphScalar(self, 'accuracy', self.old_score, self.score)
        self.needle_Rotation = self.score * self.full_needle_rotation
        self.update_accuracy_rating_text()
        self.update_accuracy_meter()

    def OnUpdateScoreBar(self, player_state):
        self.playerState = player_state
        self.rank = self.playerState.rank
        self.total_xp_needed_for_previous_rank = self.total_xp_needed_for_current_rank
        self.total_xp_needed_for_current_rank = self.pdService.get_total_needed_xp(self.rank)
        self.total_xp_needed_for_next_rank = self.pdService.get_total_needed_xp(self.rank + 1)
        self.experience = self.playerState.experience
        if self.update_score_bar_thread:
            self.update_score_bar_thread.Kill()
        self.update_score_bar_thread = StartTasklet(self.update_score_bar)

    def calculate_score_bar_length(self):
        return calculate_score_bar_length(self.experience, self.total_xp_needed_for_current_rank, self.total_xp_needed_for_next_rank, self.scoreBarLength)

    def update_score_bar(self):
        try:
            blue.synchro.Sleep(500)
            new_score_bar_length = self.calculate_score_bar_length()
            counter = self.oldScoreBarLength
            self.oldScoreBarLength = new_score_bar_length
            while counter >= new_score_bar_length:
                counter += 0.5
                if counter >= ScaleDpi(self.scoreBarLength - 5):
                    counter = -1
                    self.update_rank_values()
                    sm.ScatterEvent('OnProjectDiscoveryLevelUp', self.rank, self.total_xp_needed_for_current_rank, self.total_xp_needed_for_next_rank)
                else:
                    sm.ScatterEvent('OnProjectDiscoveryExperience', self._get_experience(self.total_xp_needed_for_previous_rank, self.total_xp_needed_for_current_rank, counter))
                    if self.scoreBar.renderObject:
                        self.scoreBar.renderObject.translationTo = (counter, 0)
                    blue.synchro.Sleep(1)

            while counter < new_score_bar_length:
                counter += 0.5
                sm.ScatterEvent('OnProjectDiscoveryExperience', self._get_experience(self.total_xp_needed_for_current_rank, self.total_xp_needed_for_next_rank, counter))
                if self.scoreBar.renderObject:
                    self.scoreBar.renderObject.translationTo = (counter, 0)
                blue.synchro.Sleep(1)

            self.update_rank_values()
            sm.ScatterEvent('OnProjectDiscoveryExperience', self.experience)
            self._update_tooltips()
        finally:
            self.update_score_bar_thread = None

    def _get_experience(self, xp_from, xp_to, score_bar_length):
        t = float(score_bar_length) / float(self.scoreBarLength)
        return int((1.0 - t) * xp_from + t * xp_to)

    def get_rank_icon_path(self, rank = None):
        used_rank = self.rank if rank is None else rank
        return projectdiscovery.client.const.rank_paths[calculate_rank_band(used_rank)]

    def update_rank_values(self):
        self.playerState = self.pdService.get_player_state()
        self.rank = self.playerState.rank
        self.experience = self.playerState.experience
        self.rankIcon.SetTexturePath(self.get_rank_icon_path())
        self.nextRankIcon.SetTexturePath(self.get_rank_icon_path(self.rank + 1))
        self.rankIcon.ReloadTexture()
        self.rankLabel.SetText(self.rank)
        self.nextRankLabel.SetText(self.rank + 1)
        self.rankLabel.ResolveAutoSizing()
        self.nextRankLabel.ResolveAutoSizing()

    def update_header(self):
        if self.player_statistics:
            if 'message' in self.player_statistics:
                logger.warning('ProjectDiscovery::update_header::Unhandled message received from the API: %s' % self.player_statistics['message'])
                if 'code' in self.player_statistics:
                    if self.player_statistics['code'] == PLAYER_NOT_IN_DATABASE_ERROR_CODE:
                        self.score = INITIAL_PLAYER_SCORE
                        self.needle_Rotation = self.score * self.full_needle_rotation
                        self.update_accuracy_rating_text()
                        self.update_accuracy_meter()
            else:
                self.score = self.player_statistics['project']['score']
                self.needle_Rotation = self.score * self.full_needle_rotation
                self.update_accuracy_rating_text()
                self.update_accuracy_meter()

    @property
    def accuracy(self):
        return self.score

    @accuracy.setter
    def accuracy(self, new_accuracy):
        self.score = new_accuracy
        self.needle_Rotation = self.score * self.full_needle_rotation
        self.update_accuracy_rating_text()
        self.update_accuracy_meter()

    def _update_tooltips(self):
        SetTooltipHeaderAndDescription(targetObject=self.rankIcon, headerText=localization.GetByLabel('UI/ProjectDiscovery/AnalystRankTooltip'), descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/CurrentExperienceTooltip', experience=FmtAmt(self.playerState.experience)))
        SetTooltipHeaderAndDescription(targetObject=self.nextRankIcon, headerText=localization.GetByLabel('UI/ProjectDiscovery/NextAnalystRankTooltip'), descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ExperienceNeededTooltip', experience=FmtAmt(self.total_xp_needed_for_next_rank)))
