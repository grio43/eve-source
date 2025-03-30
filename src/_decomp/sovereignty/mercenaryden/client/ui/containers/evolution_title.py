#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\evolution_title.py
from carbonui import Align, TextColor, TextHeader
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from gametime import HOUR, SEC
from localization import GetByLabel

class BaseEvolutionTitleContainer(ContainerAutoSize):
    default_clipChildren = True
    PADDING_H_BETWEEN_TITLE_AND_TOOLTIP_ICON = 10
    ICON_SIZE_TOOLTIP = 16
    COLOR_TITLE_LABEL = TextColor.NORMAL
    LABEL_PATH_TITLE = None

    def __init__(self, *args, **kwargs):
        super(BaseEvolutionTitleContainer, self).__init__(*args, **kwargs)
        self._construct_content()

    def _construct_content(self):
        self._title_container = ContainerAutoSize(name='title_container', parent=self, align=Align.TOTOP, alignMode=Align.TOPLEFT)
        self._title = TextHeader(name='title_label', parent=self._title_container, align=Align.TOPLEFT, color=self.COLOR_TITLE_LABEL, text=GetByLabel(self.LABEL_PATH_TITLE))
        self.title_icon_container = ContainerAutoSize(name='title_icon_container', parent=self._title_container, align=Align.TOLEFT, width=self.ICON_SIZE_TOOLTIP, padLeft=self.PADDING_H_BETWEEN_TITLE_AND_TOOLTIP_ICON, left=self._title.width)
        self._title_icon = InfoGlyphIcon(name='title_info_icon', parent=self.title_icon_container, align=Align.CENTER, width=self.ICON_SIZE_TOOLTIP, height=self.ICON_SIZE_TOOLTIP)

    def load(self, controller):
        self._title_icon.hint = self._get_tooltip(controller)

    def _get_tooltip(self, controller):
        raise NotImplementedError('Must implement _get_tooltip in derived class')


class DevelopmentTitleContainer(BaseEvolutionTitleContainer):
    LABEL_PATH_TITLE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/DevelopmentTitle'
    LABEL_PATH_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/DevelopmentTooltip'
    LABEL_PATH_TOOLTIP_TEMP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/DevelopmentTooltipWithoutMTOs'
    LABEL_PATH_INFOMORPH_RATE_DATA = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/InfomorphGenerationRateData'
    LABEL_PATH_PERCENTAGE = 'UI/Common/Formatting/Percentage'

    def _get_tooltip(self, controller):
        should_show_mtos = controller.should_show_mtos()
        infomorphs_lower, infomorphs_upper = controller.get_current_infomorph_generation_rates_per_second()
        return GetByLabel(self.LABEL_PATH_TOOLTIP if should_show_mtos else self.LABEL_PATH_TOOLTIP_TEMP, current_rate=GetByLabel(self.LABEL_PATH_INFOMORPH_RATE_DATA, lower=int(infomorphs_lower * HOUR / SEC), upper=int(infomorphs_upper * HOUR / SEC)))


class AnarchyTitleContainer(BaseEvolutionTitleContainer):
    LABEL_PATH_TITLE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/AnarchyTitle'
    LABEL_PATH_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/AnarchyTooltip'
    LABEL_PATH_TOOLTIP_TEMP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/AnarchyTooltipWithoutMTOs'
    LABEL_PATH_PERCENTAGE = 'UI/Common/Formatting/Percentage'

    def _get_tooltip(self, controller):
        should_show_mtos = controller.should_show_mtos()
        workforce_cost = controller.get_current_workforce_cost_as_percentage()
        return GetByLabel(self.LABEL_PATH_TOOLTIP if should_show_mtos else self.LABEL_PATH_TOOLTIP_TEMP, workforce_cost=GetByLabel(self.LABEL_PATH_PERCENTAGE, percentage=workforce_cost))
