#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\pirateIncursions\panels\activity.py
from carbonui.control.scrollContainer import ScrollContainer
import eveicon
from carbonui.primitives.container import Container
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.text.styles import TextFixedStyleBase
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.activityConst import HOWTO, WHERE, REWARDS, NAME
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from localization import GetByLabel

class ActivityPanel(BasePanel):

    def ApplyAttributes(self, attributes):
        super(ActivityPanel, self).ApplyAttributes(attributes)
        self.activity = attributes.get('activity')
        self.constructRewards = attributes.get('constructRewards')
        self.headerTexturePath = attributes.get('headerTexturePath')
        self.activityScaleText = attributes.get('activityScaleText')
        self.activityRewardTypeText = attributes.get('activityRewardTypeText')
        self._construct_layout()

    def _construct_layout(self):
        self._details_section = SectionAutoSize(name='_details_section', parent=self, align=uiconst.TOALL, headerText='Details')
        self._image_cont = Container(parent=self._details_section, align=uiconst.TOTOP, width=790, height=112, state=uiconst.UI_DISABLED)
        Frame(texturePath=self.headerTexturePath, bgParent=self._image_cont)
        self._activityname_label = BigTitle(name='_activityname_label', parent=self._image_cont, align=uiconst.TOTOP, text=GetByLabel(NAME[self.activity]), padding=10, bold=1)
        self._first_line = Container(parent=self._image_cont, align=uiconst.TOTOP, height=20, padLeft=10)
        self._player_icon = Sprite(name='_player_icon', parent=Container(parent=self._first_line, align=uiconst.TOLEFT_PROP, width=0.03), align=uiconst.TOLEFT, width=16, height=16, texturePath=eveicon.person, state=uiconst.UI_DISABLED)
        self._player_label = TextBody(name='_player_label', parent=self._first_line, align=uiconst.TOLEFT_PROP, text=self.activityScaleText, height=20, width=0.15, bold=1)
        self._ship_icon = Sprite(name='_ship_icon', parent=Container(parent=self._first_line, align=uiconst.TOLEFT_PROP, width=0.03), align=uiconst.TOLEFT, width=16, height=16, texturePath=eveicon.spaceship_command, state=uiconst.UI_DISABLED)
        self._ship_label = TextBody(name='_ship_label', parent=self._first_line, align=uiconst.TOLEFT_PROP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/ActivityShipTypeT1'), height=20, width=0.15, bold=1)
        self._second_line = Container(parent=self._image_cont, align=uiconst.TOTOP, height=20, padLeft=10, padTop=5)
        self._reward_icon = Sprite(name='_reward_icon', parent=Container(parent=self._second_line, align=uiconst.TOLEFT_PROP, width=0.03), align=uiconst.TOLEFT, width=16, height=16, texturePath='res:/UI/Texture/classes/agency/pirateIncursions/cup.png', state=uiconst.UI_DISABLED)
        self._reward_label = TextBody(name='_reward_label', parent=self._second_line, align=uiconst.TOLEFT_PROP, text=self.activityRewardTypeText, height=20, width=0.15, bold=1)
        self._ship_icon = Sprite(name='_ship_icon', parent=Container(parent=self._second_line, align=uiconst.TOLEFT_PROP, width=0.03), align=uiconst.TOLEFT, width=16, height=16, texturePath='res:/UI/Texture/classes/frontlines/battlefield.png', state=uiconst.UI_DISABLED)
        self._ship_label = TextBody(name='_ship_label', parent=self._second_line, align=uiconst.TOLEFT_PROP, text='PvE & PvP', height=20, width=0.15, bold=1)
        scroll = ScrollContainer(parent=self._details_section, align=uiconst.TOTOP, height=250)
        textPadding = 6
        self._howto_label = TextBody(name='_howto_label', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/HeaderHowTo'), padTop=2 * textPadding, bold=1)
        self._howto_description = TextBody(name='_howto_description', parent=scroll, align=uiconst.TOTOP, text=GetByLabel(HOWTO[self.activity]), padTop=textPadding, state=uiconst.UI_NORMAL)
        self._where_label = TextBody(name='_where_label', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/HeaderWhere'), padTop=4 * textPadding, bold=1)
        self._where_description = TextBody(name='_where_description', parent=scroll, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=GetByLabel(WHERE[self.activity]), padTop=textPadding)
        if self.constructRewards:
            self._reward_label = TextBody(name='_reward_label', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/HeaderRewards'), padTop=4 * textPadding, bold=1)
            self._reward_description = TextBody(name='_reward_description', parent=scroll, align=uiconst.TOTOP, text=GetByLabel(REWARDS[self.activity]), padTop=textPadding, state=uiconst.UI_NORMAL)

    def get_searchable_strings(self):
        return [self._activityname_label.text]


class BigTitle(TextFixedStyleBase):
    default_fontsize = 25
