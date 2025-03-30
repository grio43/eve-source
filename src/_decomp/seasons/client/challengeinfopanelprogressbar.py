#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\challengeinfopanelprogressbar.py
import carbonui.const as uiconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbon.common.script.sys.service import ROLE_QA
from carbonui.control.contextMenu.menuData import MenuData
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.infoPanels.info_panel_progress_bar import InfoPanelProgressBar
from gametime import GetSimTime, SEC
from localization import GetByLabel, GetByMessageID
from localization.formatters import FormatTimeIntervalShortWritten
from seasons.client.const import get_challenge_progress_counter_label_short_text, SEASONS_CLAIM_REWARD_LABEL
from seasons.client.util import OpenSeasonsWindow
from seasons.common.const import REWARD_FANFARE_SOUND
PROGRESS_FRAME_CORNER_SIZE = 16
PROGRESS_FRAME_OFFSET = -14
PROGRESS_FRAME_PAD_RIGHT = 7
PROGRESS_BAR_CORNER_SIZE = 15
PROGRESS_BAR_OFFSET = -13
PROGRESS_BAR_UPDATE_ANIMATION_SPEED = 2
PROGRESS_FRAME_DEFAULT_OPACITY = 0.35
PROGRESS_FRAME_HOVER_OPACITY = 0.7
PROGRESS_BAR_DEFAULT_OPACITY = 0.5
PROGRESS_BAR_HOVER_OPACITY = 1.0
DEFAULT_PROGRESS_LABEL_PAD_LEFT = -2
TOOLTIP_WRAP_WIDTH = 200

class ChallengeInfoPanelProgressBar(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.seasonService = sm.GetService('seasonService')
        self.challenge = attributes.challenge
        self.expiration_date = None
        self.left_sprite = None
        self.right_sprite = None
        self._layout()
        self.update_progress_bar(self.challenge.progress, suppress_animation=True)
        self._update_counter()

    def _layout(self):
        self.progress_bar = InfoPanelProgressBar(parent=self)
        self.progress_bar.OnClick = self.OnClick
        self.progress_bar.GetHint = self.GetHint
        self.progress_bar.GetMenu = self.GetMenu
        self.challenge_label_container = self.progress_bar.content_container
        self.progress_label = EveLabelMedium(name='progress_label', parent=self.challenge_label_container, align=uiconst.TORIGHT)
        self.challenge_label = EveLabelMedium(name='challenge_label', parent=self.challenge_label_container, align=uiconst.TOALL, width=self.challenge_label_container.width)
        if self.challenge.expiration_minutes > 0:
            seasonSvc = sm.GetService('seasonService')
            self.expiration_date = seasonSvc.get_challenge_expiration_date(self.challenge.challenge_id)
            self.challengeExpiryLabel = EveLabelMedium(name='timer_label', parent=self, align=uiconst.CENTERRIGHT, text='', maxLines=1, height=16, right=40, pos=(-77, 0, 70, 16))
            self.expiryTimer = AutoTimer(500, self._update_timer_label)
            self.blinkTimer = AutoTimer(1000, self._update_timer_blink)

    def show_claim_button(self):
        if self.left_sprite is not None and self.right_sprite is not None:
            animations.MorphScalar(self.left_sprite, 'opacity', 0.5, 1.0, duration=1.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
            animations.MorphScalar(self.right_sprite, 'opacity', 0.5, 1.0, duration=1.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def show_dormant(self):
        self.update_progress_bar(self.challenge.max_progress, suppress_animation=True)
        self._update_counter()

    def update_progress_bar(self, new_progress, suppress_animation = False):
        callback = None
        if self.challenge.reward_date and not self.challenge.is_dormant:
            callback = self.show_claim_button
        self.progress_bar.set_progress(progress=float(new_progress) / self.challenge.max_progress, snap_to_value=suppress_animation, on_complete=callback)

    def update_challenge(self, new_progress):
        self.challenge.progress = new_progress
        self.update_progress_bar(new_progress)
        self._update_counter()

    def _update_expiration_timer(self):
        time_remaining = max(self.expiration_date - GetSimTime(), 0)
        nextChallengeTime = FormatTimeIntervalShortWritten(time_remaining)
        nextChallengeText = GetByLabel('UI/Seasons/NextChallengeLabel', nextChallengeTime=nextChallengeTime)
        self.progress_label.SetText(nextChallengeText)
        if time_remaining <= 0:
            self.expiration_timer_thread = None

    def _update_counter(self):
        if self.challenge.reward_date:
            self.challenge_label.Hide()
            self.progress_label.align = uiconst.CENTER
            challenge_progress_counter_text = GetByLabel(SEASONS_CLAIM_REWARD_LABEL)
            if self.challenge.is_dormant:
                if self.expiration_date is None:
                    self.expiration_date = self.seasonService.get_challenge_expiration_date(self.challenge.challenge_id)
                if self.expiration_date is not None:
                    self._update_expiration_timer()
                    self.expiration_timer_thread = AutoTimer(500, self._update_expiration_timer)
            else:
                self.progress_label.SetText(challenge_progress_counter_text)
                self.left_sprite = Sprite(parent=self.challenge_label_container, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/ShipUI/expandBtnRight.png', width=20, height=20, state=uiconst.UI_DISABLED)
                self.right_sprite = Sprite(parent=self.challenge_label_container, align=uiconst.TORIGHT, texturePath='res:/UI/Texture/classes/ShipUI/expandBtnLeft.png', width=20, height=20, state=uiconst.UI_DISABLED)
        else:
            challenge_progress_counter_text = get_challenge_progress_counter_label_short_text(self.challenge)
            self.progress_label.SetText(challenge_progress_counter_text)
        label_text = GetByMessageID(self.challenge.progress_text)
        self.challenge_label.SetText(label_text)

    def GetHint(self):
        return self.challenge_label.text

    def OnClick(self, *args):
        if self.challenge.reward_date and not self.challenge.is_dormant:
            self.seasonService.claim_challenge_rewards(self.challenge, 'Info Panel')
            PlaySound(REWARD_FANFARE_SOUND)
        else:
            OpenSeasonsWindow()

    def Close(self):
        self.expiration_timer_thread = None
        animations.StopAllAnimations(self)
        super(ChallengeInfoPanelProgressBar, self).Close()

    def _update_timer_label(self):
        if self.challenge.is_progress_complete():
            self.challengeExpiryLabel.Hide()
            self.expiryTimer = None
        if self.expiration_date is not None:
            nextChallengeTime = FormatTimeIntervalShortWritten(max(self.expiration_date - GetSimTime(), 0))
            self.challengeExpiryLabel.text = nextChallengeTime

    def _update_timer_blink(self):
        if self.expiration_date is not None:
            remaining_duration = max(self.expiration_date - GetSimTime(), 0)
            if remaining_duration < 20 * SEC:
                animations.BlinkOut(self.challengeExpiryLabel, duration=1.0, endVal=0.25)

    def GetMenu(self):
        if not bool(session.role & ROLE_QA):
            return None
        qa_menu = MenuData()
        qa_menu.AddEntry('Open Challenge in FSD Editor', func=lambda : _open_challenge_in_fsd(self.challenge.challenge_id))
        qa_menu.AddEntry('Challenge ID: {}'.format(self.challenge.challenge_id))
        qa_menu.AddEntry('Challenge Type ID: {}'.format(self.challenge.challenge_type_id))
        qa_menu.AddSeparator()
        qa_menu.AddEntry('Complete Challenge', lambda : sm.GetService('slash').SlashCmd('/seasons challenge update {} {}'.format(self.challenge.challenge_id, self.challenge.max_progress)))
        qa_menu.AddEntry('Expire Challenge', lambda : sm.GetService('slash').SlashCmd('/seasons challenge expire {}'.format(self.challenge.challenge_id)))
        result = MenuData()
        result.AddEntry('QA', subMenuData=qa_menu)
        return result


def _open_challenge_in_fsd(content_id):
    import webbrowser
    webbrowser.open_new('http://localhost:8000/challenges/{}/'.format(content_id))
