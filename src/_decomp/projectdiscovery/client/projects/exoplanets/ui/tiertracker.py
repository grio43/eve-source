#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\ui\tiertracker.py
import evetypes
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorline import VectorLine
from carbonui.uianimations import animations
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from projectdiscovery.client import const
from carbonui.uicore import uicore
import carbonui.const as uiconst
import trinity
import logging
from projectdiscovery.client.util.util import calculate_rank_band
import localization
import inventorycommon.const as invConst
from utillib import KeyVal
logger = logging.getLogger(__name__)

class TierTracker(Container):
    TIER_SIZE = 80.0
    SPACE_BETWEEN_TIERS = 80.0
    CURRENT_BAR_OFFSET = 5.0
    default_align = uiconst.TOPLEFT
    default_height = 150
    default_clipChildren = False
    default_state = uiconst.UI_NORMAL
    __notifyevents__ = ['OnContinueToRewards', 'OnProjectDiscoveryExperience', 'OnProjectDiscoveryLevelUp']

    def ApplyAttributes(self, attributes):
        super(TierTracker, self).ApplyAttributes(attributes)
        self.cursor = uiconst.UICURSOR_LEFT_RIGHT_DRAG
        self._project_discovery_service = sm.RemoteSvc('ProjectDiscovery')
        self._player_state = self._project_discovery_service.get_player_state()
        self._rank = self._player_state.rank
        self._experience = self._player_state.experience
        self._experience_for_current_tier = None
        self._experience_for_next_tier = None
        self._tiers = attributes.get('tierInfo')
        self._tiers.sort(key=lambda tier: tier['level'])
        self._current_tier = None
        self._next_tier = None
        self._tier_circles = []
        self._is_animating_position = False
        self._update_by_player_state()
        self._setup_layout()
        self._current_position = self._parent_container.left
        self._next_position = self._parent_container.left
        self.fix_bar_offset_to_current_progression_length()
        self._mouse_down_position = None
        self._is_dragging = False
        self._update_arrow_states()
        sm.RegisterNotify(self)

    def _setup_layout(self):
        self._left_arrow = ButtonIcon(name='LeftArrow', parent=self, align=uiconst.TOLEFT, width=50, texturePath='res:/UI/Texture/Icons/38_16_100.png', func=self._backward, top=-self.TIER_SIZE / 2)
        self._right_arrow = ButtonIcon(name='RightArrow', parent=self, align=uiconst.TORIGHT, width=50, texturePath='res:/UI/Texture/Icons/38_16_99.png', func=self._forward, top=-self.TIER_SIZE / 2)
        self._main_container = Container(name='MainContainer', parent=self, align=uiconst.TOALL, clipChildren=True, top=-self.TIER_SIZE)
        self._parent_container = Container(name='ParentContainer', parent=self._main_container, algin=uiconst.TOPLEFT, clipChildren=False)
        self._setup_tier_icons()
        self._setup_progression_bar()
        self._update_tooltips()

    def _setup_progression_bar(self):
        self._line_end_icon = Container(name='LineEndIcon', parent=self._parent_container, align=uiconst.CENTERLEFT, height=12, width=2, bgColor=(1, 1, 1, 1), sate=uiconst.UI_NORMAL, left=self._get_length_of_progression())
        self._line_end_icon.pickState = uiconst.TR2_SPS_ON
        self._filled_line = VectorLine(name='FilledLine', parent=self._parent_container, align=uiconst.CENTERLEFT, padBottom=10, height=1, width=1, widthFrom=10, widthTo=10, translationFrom=(0, 0), translationTo=(self._get_length_of_progression(), 0), color=(0, 0.5, 0, 0.5))
        self._empty_line = VectorLine(name='EmptyLine', parent=self._parent_container, align=uiconst.CENTERLEFT, padBottom=10, height=1, width=1, widthFrom=10, widthTo=10, translationFrom=(0, 0), translationTo=(self._get_total_length_of_bar(), 0), color=(0.0, 0.04, 0.0, 1))

    def _setup_tier_icons(self):
        left = self.SPACE_BETWEEN_TIERS
        for tier in self._tiers:
            tier_circle = TierCircle(name='TierCircle', parent=self._parent_container, align=uiconst.CENTERLEFT, left=left, width=self.TIER_SIZE, tier=tier)
            self._tier_circles.append(tier_circle)
            left += self.TIER_SIZE + self.SPACE_BETWEEN_TIERS

        self._update_tier_collect_state()

    def _update_tier_collect_state(self):
        progression_length = self._get_length_of_progression()
        for tier_circle in self._tier_circles:
            if tier_circle.left + self.CURRENT_BAR_OFFSET < progression_length:
                tier_circle.show_achieved_overlay()

    def _get_total_length_of_bar(self):
        if not self._tiers:
            return 0
        return sum([ self.SPACE_BETWEEN_TIERS + self.TIER_SIZE for tier in self._tiers ]) - self.CURRENT_BAR_OFFSET

    def _get_length_of_progression(self):
        try:
            current_tier_index = [ i for i in xrange(len(self._tiers)) if self._tiers[i]['level'] == self._current_tier ][0] + 1 if self._current_tier else 0
            current_length = current_tier_index * (self.SPACE_BETWEEN_TIERS + self.TIER_SIZE)
            start = current_length - self.CURRENT_BAR_OFFSET if self._current_tier else 0
            end = current_length + self.SPACE_BETWEEN_TIERS + self.CURRENT_BAR_OFFSET
            t = self._get_t_to_next_progression()
            progression_to_next_tier = start * (1.0 - t) + end * t
            return min(progression_to_next_tier, self._get_total_length_of_bar())
        except AttributeError:
            logger.warning('_get_length_of_progression AttributeError', exc_info=1)

    def update_progress_bar(self):
        self._filled_translation_to = (self._get_length_of_progression(), 0)

    def _forward(self):
        if not self._is_animating_position:
            self._update_arrow_states()
            closest_paging_positions = self._get_closest_paging_positions()
            self._next_position = closest_paging_positions[1]
            self._move()

    def _backward(self):
        if not self._is_animating_position:
            self._update_arrow_states()
            closest_paging_positions = self._get_closest_paging_positions()
            self._next_position = closest_paging_positions[0]
            self._move()

    def _move(self):
        self._is_animating_position = True
        self._parent_container.StopAnimations()
        animations.MorphScalar(self._parent_container, 'left', self._get_current_position(), self._next_position, callback=self._after_position_animation)

    def _after_position_animation(self):
        self._update_arrow_states()
        self._current_position = self._next_position
        self._is_animating_position = False

    def _update_arrow_states(self):
        last_circle = self._tier_circles[-1]
        if int(self._parent_container.left) >= 0:
            self._left_arrow.Disable()
        else:
            self._left_arrow.Enable()
        if last_circle.GetAbsoluteRight() <= self._main_container.GetAbsoluteRight():
            self._right_arrow.Disable()
        else:
            self._right_arrow.Enable()

    @property
    def _filled_translation_to(self):
        return self._filled_line.translationTo

    @_filled_translation_to.setter
    def _filled_translation_to(self, translation_to):
        try:
            self._filled_line.translationTo = translation_to
            self._line_end_icon.left = translation_to[0]
            self._update_tier_collect_state()
            self._update_tooltips()
        except AttributeError:
            logger.warn('_filled_translation_to attribute error', exc_info=1)

    def fix_bar_offset_to_current_progression_length(self):
        position = self._filled_line.GetAbsoluteLeft() + self._get_length_of_progression()
        original_position = position
        offset = 0
        while not self._main_container.GetAbsoluteLeft() <= position <= self._main_container.GetAbsoluteRight():
            if position < self._main_container.GetAbsoluteLeft():
                offset += self.SPACE_BETWEEN_TIERS + self.TIER_SIZE
            else:
                offset -= self.SPACE_BETWEEN_TIERS + self.TIER_SIZE
            position = original_position + offset

        if offset:
            self._next_position = self._current_position + offset
            maximum, minimum = self._get_max_and_min_positions()
            self._next_position = max(min(maximum, self._next_position), minimum)
            self._move()
            return True
        return False

    def OnMouseWheel(self, amount, *args):
        amount /= 5
        amount *= -1
        self._parent_container.left += amount
        maximum, minimum = self._get_max_and_min_positions()
        self._parent_container.left = max(min(maximum, self._parent_container.left), minimum)
        self._update_arrow_states()

    def OnMouseDown(self, *args):
        self._is_dragging = True
        self._mouse_down_position = uicore.uilib.x - self.GetAbsoluteLeft()

    def OnMouseMove(self, *args):
        if self._is_dragging:
            maximum, minimum = self._get_max_and_min_positions()
            current = uicore.uilib.x - self.GetAbsoluteLeft()
            delta = current - self._mouse_down_position
            self._mouse_down_position = current
            self._parent_container.left += delta
            self._parent_container.left = max(min(maximum, self._parent_container.left), minimum)
            self._update_arrow_states()

    def OnMouseUp(self, *args):
        self._is_dragging = False

    def _get_current_position(self):
        return -(self._main_container.GetAbsoluteLeft() - self._parent_container.GetAbsoluteLeft())

    def _get_closest_paging_positions(self):
        diff = self.TIER_SIZE + self.SPACE_BETWEEN_TIERS
        current_position = self._get_current_position()
        left_over = current_position % diff
        if left_over != 0:
            current_position -= left_over
        return (min(current_position + diff, 0), current_position - diff)

    def _get_player_current_tier_level(self):
        current_rank = self._rank
        tiers_reached = [ tier['level'] for tier in self._tiers if tier['level'] <= current_rank ]
        if tiers_reached:
            return max(tiers_reached)
        return 0

    def _get_next_tier_level(self):
        current_tier_level = self._get_player_current_tier_level()
        tiers_left = [ tier['level'] for tier in self._tiers if tier['level'] > current_tier_level ]
        if tiers_left:
            return min(tiers_left)
        return current_tier_level

    def _update_by_player_state(self):
        self._current_tier = self._get_player_current_tier_level()
        self._next_tier = self._get_next_tier_level()
        if not self._experience_for_current_tier or not self._experience_for_next_tier or self._player_state.experience >= self._experience_for_next_tier:
            self._experience_for_current_tier = self._project_discovery_service.get_total_needed_xp(self._current_tier)
            self._experience_for_next_tier = self._project_discovery_service.get_total_needed_xp(self._next_tier)

    def _get_t_to_next_progression(self):
        current_experience = self._experience
        distance = float(self._experience_for_next_tier - self._experience_for_current_tier)
        t = float(current_experience - self._experience_for_current_tier) / distance if distance else 1
        return t

    def OnContinueToRewards(self, result, *args, **kwargs):
        if result:
            self._player_state = result['playerState']

    def update(self):
        self._update_by_player_state()
        self.update_progress_bar()

    def _update_tooltips(self):
        SetTooltipHeaderAndDescription(targetObject=self._line_end_icon, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/TierTrackerTooltip', experience=self._experience))

    def _get_max_and_min_positions(self):
        temp = -(self._get_total_length_of_bar() + self.CURRENT_BAR_OFFSET) + self._main_container.displayWidth / uicore.dpiScaling
        left_over = temp % (self.TIER_SIZE + self.SPACE_BETWEEN_TIERS)
        return (0.0, temp - left_over)

    def OnProjectDiscoveryExperience(self, experience):
        if hasattr(self, '_experience'):
            self._experience = experience
            self.update_progress_bar()

    def OnProjectDiscoveryLevelUp(self, new_rank, xp_for_new_rank, xp_for_next_rank):
        self._rank = new_rank
        self._update_by_player_state()

    def increment(self):
        self._current_tier = [ self._tiers[i]['level'] for i in xrange(len(self._tiers)) if self._tiers[i]['level'] > self._current_tier ][0] if self._current_tier < self._tiers[-1]['level'] else self._tiers[-1]['level']


class TierCircle(Container):
    HEIGHT_TO_WIDTH_RATIO = 1
    default_clipChildren = False
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(TierCircle, self).ApplyAttributes(attributes)
        self.height = self.width * self.HEIGHT_TO_WIDTH_RATIO
        self._tier = attributes.get('tier')
        self._is_achieved = False
        self._setup_layout()

    def _setup_layout(self):
        self._check_mark = Sprite(name='checkMark', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/checkmark.png', opacity=0, idx=0, state=uiconst.UI_DISABLED, align=uiconst.TOALL, color=(0, 1, 0, 1))
        self._check_base = Sprite(name='checkBase', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/checkBase.png', opacity=0, state=uiconst.UI_DISABLED, align=uiconst.TOALL, color=(0, 1, 0, 0.05))
        self._selected = Sprite(name='selected', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/select.png', state=uiconst.UI_DISABLED, align=uiconst.TOALL, color=(0, 0.05, 0, 1))
        self._done_glow = Sprite(name='doneGlow', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/doneGlow.png', opacity=0, state=uiconst.UI_DISABLED, align=uiconst.TOALL, color=(0, 0.5, 0, 1))
        self._reward_overlay_base = Sprite(name='rewardOverlayBase', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/rewardBase.png', opacity=0, state=uiconst.UI_DISABLED, align=uiconst.TOALL, color=(0, 0, 0, 0.7))
        self._reward_sprite = Icon(name='rewardSprite', parent=self, align=uiconst.TOALL, typeID=self.get_type_id(), itemID=None, ignoreSize=True, textureSecondaryPath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/rewardBase.png', spriteEffect=trinity.TR2_SFX_MASK, state=uiconst.UI_DISABLED, isCopy=True)
        self._base = Sprite(name='base', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/rewardprogress/rewardBase.png', state=uiconst.UI_DISABLED, align=uiconst.TOALL, color=(0, 0, 0, 1))
        self._rank_icon = Sprite(name='rankIcon', parent=self, texturePath=self._get_rank_icon_path(self._tier['level']), height=36, width=36, align=uiconst.CENTERTOP, top=self.height, opacity=0.3)
        self._level_label = EveLabelMedium(name='LevelLabel', parent=self, align=uiconst.CENTERTOP, top=self.height + self._rank_icon.height, text='%s' % self._tier['level'], opacity=0.3)

    def show_achieved_overlay(self):
        if not self._is_achieved:
            self._is_achieved = True
            animations.FadeIn(self._check_mark, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeTo(self._check_base, 0, 0.11, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeIn(self._done_glow, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeTo(self._reward_overlay_base, 0, 0.7, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeIn(self._level_label, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeIn(self._rank_icon, curveType=uiconst.ANIM_OVERSHOT2)
            self._selected.color = (0, 1, 0, 1)
            animations.FadeTo(self._selected, 0, 1, curveType=uiconst.ANIM_OVERSHOT2)

    def OnMouseEnter(self, *args):
        animations.SpGlowFadeIn(self._selected, duration=0.25)

    def OnMouseExit(self, *args):
        animations.SpGlowFadeOut(self._selected, duration=0.25)

    def _get_rank_icon_path(self, rank):
        return const.rank_paths[calculate_rank_band(rank)]

    def OnClick(self, *args):
        type_id = self.get_type_id()
        sm.GetService('info').ShowInfo(typeID=type_id, abstractinfo=self._GetAbstractInfo(type_id))

    def _GetAbstractInfo(self, typeID):
        if evetypes.GetCategoryID(typeID) != invConst.categoryBlueprint:
            return None
        bpSvc = sm.GetService('blueprintSvc')
        bpData = bpSvc.GetBlueprintTypeCopy(typeID, original=False, runsRemaining=1)
        return KeyVal(bpData=bpData)

    def get_type_id(self):
        if len(self._tier['types']) == 1:
            return self._tier['types'][0]
        return self._tier['types'][session.genderID]
