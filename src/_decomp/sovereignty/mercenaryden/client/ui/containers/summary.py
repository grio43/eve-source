#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\summary.py
import eveformat
from carbon.common.script.util.format import FmtAmt
from carbonui import Align, TextHeader, TextBody, TextDetail, TextColor, PickState, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor, eveThemeColor
from localization import GetByLabel
from sovereignty.mercenaryden.client.ui.containers.statistics import StatisticsContainer

class SummaryContainer(ContainerAutoSize):
    default_alignMode = Align.TOTOP
    LABEL_PATH_FAILED_TO_LOAD_DATA = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/FailedToLoadData'
    LABEL_PATH_OWNER = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/Owner'
    LABEL_PATH_SKYHOOK_OWNER = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/SkyhookOwner'
    LABEL_PATH_INFOMORPHS_COLLECTED = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/InfomorphsCollected'
    LABEL_PATH_STATE_ACTIVE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/StateNameActive'
    LABEL_PATH_STATE_INACTIVE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/StateNameInactive'
    LABEL_PATH_TOOLTIP_STATE_ACTIVE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/StateTooltipActive'
    LABEL_PATH_TOOLTIP_STATE_INACTIVE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/StateTooltipInactive'
    PADDING_CONTENT = 16
    PADDING_SUMMARY_TO_STATE = 4
    PADDING_STATE_ICON_TO_LABEL = 2
    PADDING_TOP_OF_DETAIL = 1
    PADDING_TOP_TO_STATISTICS = 24
    ICON_TEXTURE_STATE = 'res:/UI/Texture/classes/Contacts/onlineIcon.png'
    ICON_SIZE_STATE = 14
    COLOR_STATE_ACTIVE = eveColor.SUCCESS_GREEN
    COLOR_STATE_INACTIVE = eveColor.DANGER_RED
    COLOR_DETAIL_LABEL = TextColor.SECONDARY
    COLOR_DETAIL_TEXT = TextColor.NORMAL
    COLOR_DETAIL_FAILED_TO_LOAD = TextColor.SECONDARY
    COLOR_BACKGROUND = eveThemeColor.THEME_FOCUSDARK
    OPACITY_ICON_GLOW = 0.8
    OPACITY_BACKGROUND = 0.4

    def __init__(self, controller, should_show_owner, should_show_skyhook_owner, should_show_infomorphs_collected, should_show_workforce_cost, should_show_bg = True, *args, **kwargs):
        self._controller = controller
        self.should_show_owner = should_show_owner
        self.should_show_skyhook_owner = should_show_skyhook_owner
        self.should_show_infomorphs_collected = should_show_infomorphs_collected
        self.should_show_workforce_cost = should_show_workforce_cost
        self.should_show_bg = should_show_bg
        super(SummaryContainer, self).__init__(*args, **kwargs)
        self._construct_content()

    def _construct_content(self):
        self._content = ContainerAutoSize(name='content', parent=self, align=Align.TOTOP, padding=self.PADDING_CONTENT)
        self._construct_background()
        self._construct_top_container()
        self._construct_statistics_container()

    def _construct_background(self):
        if not self.should_show_bg:
            return
        Fill(name='background_color', bgParent=self, color=self.COLOR_BACKGROUND, opacity=self.OPACITY_BACKGROUND)

    def _construct_top_container(self):
        self._top_container = ContainerAutoSize(name='top_container', parent=self._content, align=Align.TOTOP, alignMode=Align.TOTOP)
        self._construct_name_container()
        self._construct_owner_container()
        self._construct_skyhook_owner_container()
        self._construct_infomorphs_collected_container()

    def _construct_top_right_container(self):
        top_right_container = ContainerAutoSize(name='top_right_container', parent=self.name_cont, align=Align.TORIGHT)
        self._state_container = ContainerAutoSize(name='state_container', parent=top_right_container, align=Align.TOPLEFT, alignMode=Align.TOPLEFT, pickState=PickState.ON, top=3)
        state_icon_container = Container(name='state_icon_container', parent=self._state_container, align=Align.TOPLEFT, width=self.ICON_SIZE_STATE, height=self.ICON_SIZE_STATE)
        self._state_icon = Sprite(name='state_icon', parent=state_icon_container, align=Align.CENTER, width=self.ICON_SIZE_STATE, height=self.ICON_SIZE_STATE, texturePath=self.ICON_TEXTURE_STATE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self.OPACITY_ICON_GLOW, pickState=PickState.OFF, top=2)
        self._state_text = TextDetail(name='state_text', parent=self._state_container, align=Align.TOPLEFT, padLeft=self.ICON_SIZE_STATE + self.PADDING_STATE_ICON_TO_LABEL)

    def _construct_name_container(self):
        self.name_cont = ContainerAutoSize(name='name_cont', parent=self._top_container, align=Align.TOTOP, clipChildren=True, alignMode=Align.TOTOP)
        self._construct_top_right_container()
        self._name_text = TextHeader(name='name_text', parent=self.name_cont, align=Align.TOTOP, pickState=PickState.ON)

    def _construct_owner_container(self):
        self._owner_text = TextBody(name='owner_label', parent=self._top_container, align=Align.TOTOP, padTop=self.PADDING_TOP_OF_DETAIL, pickState=PickState.ON, display=self.should_show_owner)

    def _construct_skyhook_owner_container(self):
        self._skyhook_owner_text = TextBody(name='skyhook_owner_label', parent=self._top_container, align=Align.TOTOP, padTop=self.PADDING_TOP_OF_DETAIL, pickState=PickState.ON, display=self.should_show_skyhook_owner)

    def _construct_infomorphs_collected_container(self):
        self._infomorphs_collected_text = TextBody(name='infomorphs_collected_label', parent=self._top_container, align=Align.TOTOP, padTop=self.PADDING_TOP_OF_DETAIL, pickState=PickState.ON, display=self.should_show_infomorphs_collected)

    def _construct_statistics_container(self):
        self._statistics = StatisticsContainer(name='statistics', parent=self._content, align=Align.TOTOP, padTop=self.PADDING_TOP_TO_STATISTICS, controller=self._controller, should_show_workforce_cost=self.should_show_workforce_cost)

    def _update_state(self):
        if self._controller.is_enabled():
            self._state_icon.color = self.COLOR_STATE_ACTIVE
            self._state_text.text = GetByLabel(self.LABEL_PATH_STATE_ACTIVE)
            self._state_container.hint = GetByLabel(self.LABEL_PATH_TOOLTIP_STATE_ACTIVE)
        else:
            self._state_icon.color = self.COLOR_STATE_INACTIVE
            self._state_text.text = GetByLabel(self.LABEL_PATH_STATE_INACTIVE)
            self._state_container.hint = GetByLabel(self.LABEL_PATH_TOOLTIP_STATE_INACTIVE)

    def _update_texts(self):
        self._name_text.text = self._controller.get_mercenary_den_name(should_show_link=True)
        self._owner_text.text = self._format_details(label=GetByLabel(self.LABEL_PATH_OWNER), text=self._controller.get_owner_name())
        skyhook_owner = self._controller.get_skyhook_owner_name()
        if skyhook_owner:
            self._skyhook_owner_text.text = self._format_details(label=GetByLabel(self.LABEL_PATH_SKYHOOK_OWNER), text=skyhook_owner)
        else:
            self._skyhook_owner_text.text = self._format_details_failed_to_load(label=GetByLabel(self.LABEL_PATH_SKYHOOK_OWNER))
        self._infomorphs_collected_text.text = self._format_details(label=GetByLabel(self.LABEL_PATH_INFOMORPHS_COLLECTED), text=FmtAmt(self._controller.get_infomorphs_collected()))

    def _format_details(self, label, text):
        return self._format_label_and_text(label, text, self.COLOR_DETAIL_LABEL, self.COLOR_DETAIL_TEXT)

    def _format_details_failed_to_load(self, label):
        text = GetByLabel(self.LABEL_PATH_FAILED_TO_LOAD_DATA)
        text_color = self.COLOR_DETAIL_FAILED_TO_LOAD
        return self._format_label_and_text(label, text, self.COLOR_DETAIL_LABEL, text_color)

    def _format_label_and_text(self, label, text, label_color, text_color):
        formatted_label = eveformat.color(label, label_color)
        formatted_text = eveformat.color(text, text_color)
        return '%s %s' % (formatted_label, formatted_text)

    def load_controller(self, controller):
        self._controller = controller
        self._update_state()
        self._update_texts()
        self._statistics.load_controller(self._controller)

    def update_height(self):
        self._statistics.update_height()
