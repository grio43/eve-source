#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\statistics.py
from carbonui import Align, TextHeader, TextBody, TextColor, uiconst, PickState
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from eve.client.script.ui import eveThemeColor
from gametime import HOUR, SEC
from localization import GetByLabel

class StatisticContainer(ContainerAutoSize):
    PADDING_LINE_TO_STATISTIC = 8
    PADDING_NAME_TO_STATISTIC = 0
    LINE_WIDTH = 1
    COLOR_LINE = eveThemeColor.THEME_FOCUS
    COLOR_STATISTIC_NAME = TextColor.SECONDARY
    default_clipChildren = True
    default_alignMode = Align.TOTOP

    def __init__(self, statistic_name, *args, **kwargs):
        self.statistic_name = statistic_name
        super(StatisticContainer, self).__init__(*args, **kwargs)
        self._construct_line()
        self._construct_texts_container()

    def _construct_line(self):
        self._line = Line(name='line', parent=self, align=Align.TOLEFT, color=self.COLOR_LINE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, width=self.LINE_WIDTH)

    def _construct_texts_container(self):
        self._texts_container = ContainerAutoSize(name='texts_container', parent=self, align=Align.TOTOP, alignMode=Align.TOTOP, padLeft=self.PADDING_LINE_TO_STATISTIC)
        self._statistic = TextHeader(name='statistic', parent=self._texts_container, align=Align.TOTOP, maxLines=1)
        self._statistic_name = TextBody(name='statistic_name', parent=self._texts_container, align=Align.TOTOP, text=self.statistic_name, color=self.COLOR_STATISTIC_NAME, padTop=self.PADDING_NAME_TO_STATISTIC)

    def set_value(self, value):
        self._statistic.text = u'%s' % value
        self.height = self._statistic.textheight + self.PADDING_NAME_TO_STATISTIC + self._statistic_name.textheight


class StatisticsContainer(GridContainer):
    PADDING_BETWEEN_STATISTICS = 12
    LABEL_PATH_INFOMORPH_RATE_NAME = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/InfomorphGenerationRateName'
    LABEL_PATH_INFOMORPH_RATE_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/InfomorphGenerationRateTooltip'
    LABEL_PATH_INFOMORPH_RATE_DATA = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/InfomorphGenerationRateData'
    LABEL_PATH_WORKFORCE_COST_NAME = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/WorkforceCostName'
    LABEL_PATH_WORKFORCE_COST_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/WorkforceCostTooltip'
    LABEL_PATH_PERCENTAGE = 'UI/Common/Formatting/Percentage'

    def __init__(self, controller, should_show_workforce_cost = True, *args, **kwargs):
        self._controller = controller
        self.should_show_workforce_cost = should_show_workforce_cost
        super(StatisticsContainer, self).__init__(*args, **kwargs)
        self.lines = 1
        self.columns = 2 if self.should_show_workforce_cost else 1
        self._construct_informorph_generation_rate_container()
        self._construct_workforce_cost_container()

    def _construct_informorph_generation_rate_container(self):
        cont = Container(name='infomorph_generation_rate_cont', parent=self, align=Align.TOALL, clipChildren=True, padRight=self.PADDING_BETWEEN_STATISTICS)
        self.infomorph_generation_rate = StatisticContainer(name='infomorph_generation_rate', parent=cont, align=Align.TOTOP, statistic_name=GetByLabel(self.LABEL_PATH_INFOMORPH_RATE_NAME), pickState=PickState.ON, hint=GetByLabel(self.LABEL_PATH_INFOMORPH_RATE_TOOLTIP))

    def _construct_workforce_cost_container(self):
        cont = Container(name='workforce_cost_cont', parent=self, align=Align.TOALL, clipChildren=True, padRight=self.PADDING_BETWEEN_STATISTICS)
        self.workforce_cost = StatisticContainer(name='workforce_cost', parent=cont, align=Align.TOTOP, statistic_name=GetByLabel(self.LABEL_PATH_WORKFORCE_COST_NAME), display=self.should_show_workforce_cost, pickState=PickState.ON)

    def _update_infomorph_generation_rate(self):
        lower, upper = self._controller.get_current_infomorph_generation_rates_per_second()
        infomorph_generation_rate = GetByLabel(self.LABEL_PATH_INFOMORPH_RATE_DATA, lower=int(lower * HOUR / SEC), upper=int(upper * HOUR / SEC))
        self.infomorph_generation_rate.set_value(infomorph_generation_rate)

    def _update_workforce_cost(self):
        workforce_cost = self._controller.get_current_workforce_cost()
        workforce_cost_percentage = self._controller.get_current_workforce_cost_as_percentage()
        percentage_label = GetByLabel(self.LABEL_PATH_PERCENTAGE, percentage=workforce_cost_percentage)
        self.workforce_cost.set_value(percentage_label)
        self.workforce_cost.hint = GetByLabel(self.LABEL_PATH_WORKFORCE_COST_TOOLTIP, workforce_units=workforce_cost, workforce_cost_percentage=percentage_label)

    def _update_height(self):
        self.height = max(self.infomorph_generation_rate.height, self.workforce_cost.height)

    def update_height(self):
        self._update_height()

    def load_controller(self, controller):
        self._controller = controller
        self._update_infomorph_generation_rate()
        self._update_workforce_cost()
        self._update_height()
