#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\pirateIncursions\panels\corruptionsuppression.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.text.styles import TextFixedStyleBase
from eve.client.script.ui import eveColor
from carbonui.primitives.container import Container
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from localization import GetByLabel
from pirateinsurgency.client.dashboard.const import GetCorruptionIconForStage, GetSuppressionIconForStage

class CorruptionSuppressionPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(CorruptionSuppressionPanel, self).__init__(*args, **kwargs)
        self._construct_layout()

    def _construct_layout(self):
        self._corruptionsuppression_section = SectionAutoSize(name='_corruptionsuppression_section', parent=self, clipChildren=True, align=uiconst.TOALL, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/Corruption/CorruptionSectionTitle'))
        scroll = ScrollContainer(parent=self._corruptionsuppression_section, align=uiconst.TOTOP, height=90)
        self._corruptionsuppression_label = TextBody(name='_corruptionsuppression_label', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Corruption/CorruptionSectionText'), padding=5)
        table_header_cont = Container(name='table_header_cont', parent=self._corruptionsuppression_section, align=uiconst.TOTOP, height=40)
        stage_header_cont = Container(name='stage_header_cont', parent=table_header_cont, align=uiconst.TOLEFT_PROP, padTop=15, width=0.1)
        corruption_header_cont = Container(name='corruption_header_cont', parent=table_header_cont, align=uiconst.TOLEFT_PROP, padTop=15, width=0.45)
        suppression_header_cont = Container(name='suppression_header_cont', parent=table_header_cont, align=uiconst.TOLEFT_PROP, padTop=15, width=0.45)
        TextBody(parent=stage_header_cont, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Corruption/StageHeader'), bold=1)
        TextBody(parent=corruption_header_cont, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Corruption/CorruptionHeader'), bold=1)
        TextBody(parent=suppression_header_cont, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Corruption/SuppressionHeader'), bold=1)
        numberOfVisibleStages = 5
        rowHeight = 50
        tableContheight = (numberOfVisibleStages + 1) * 50
        tableContScroll = ScrollContainer(name='tableContScroll', parent=Container(parent=self._corruptionsuppression_section, height=tableContheight, align=uiconst.TOTOP), align=uiconst.TOALL, clipChildren=True)
        for i in range(numberOfVisibleStages):
            TableRow(name='table_cont', parent=tableContScroll, align=uiconst.TOTOP, height=rowHeight, stageNumber=i + 1, top=20)

    def get_searchable_strings(self):
        return [self._corruptionsuppression_section.headerText, self._corruptionsuppression_label.GetText()]


class TableRow(Container):

    def ApplyAttributes(self, attributes):
        super(TableRow, self).ApplyAttributes(attributes)
        self.stageNumber = attributes.stageNumber
        self._construct_layout()

    def _construct_layout(self):
        number_column = Container(name='number_column', parent=self, align=uiconst.TOLEFT_PROP, width=0.05)
        NumberLabel(parent=number_column, text=GetByLabel('UI/Agency/PirateIncursions/Guides/Corruption/stageNumber0{}'.format(self.stageNumber)), color=eveColor.CRYO_BLUE, align=uiconst.CENTERLEFT)
        corruption_icon_column = Container(name='corruption_icon_column', parent=self, align=uiconst.TOLEFT_PROP, width=0.05)
        Sprite(name='stage_icon', parent=corruption_icon_column, align=uiconst.BOTTOMLEFT, texturePath=GetCorruptionIconForStage(self.stageNumber), state=uiconst.UI_DISABLED, height=40, width=40)
        corruption_bonus_column = Container(name='corruption_bonus_column', parent=self, align=uiconst.TOLEFT_PROP, width=0.425)
        corruptionBonus = GetByLabel('UI/Agency/PirateIncursions/Guides/Corruption/CorruptionBonusStage0{}'.format(self.stageNumber))
        if len(corruptionBonus.splitlines()) > 1:
            corruptionBonusSplit = corruptionBonus.splitlines()
            corruptionBonus = '-' + corruptionBonusSplit[0] + '\n' + '-' + corruptionBonusSplit[2]
        TextBody(parent=corruption_bonus_column, align=uiconst.CENTERLEFT, width=300, text=corruptionBonus, left=10)
        suppression_icon_column = Container(name='suppression_icon_column', parent=self, align=uiconst.TOLEFT_PROP, width=0.05)
        Sprite(name='stage_icon', parent=suppression_icon_column, align=uiconst.CENTER, texturePath=GetSuppressionIconForStage(self.stageNumber), state=uiconst.UI_DISABLED, height=32, width=32)
        suppression_bonus_column = Container(name='suppression_bonus_column', parent=self, align=uiconst.TOLEFT_PROP, width=0.425)
        suppressionBonus = GetByLabel('UI/Agency/PirateIncursions/Guides/Corruption/SuppressionBonusStage0{}'.format(self.stageNumber))
        if len(suppressionBonus.splitlines()) > 1:
            suppressionBonusSplit = suppressionBonus.splitlines()
            suppressionBonus = '-' + suppressionBonusSplit[0] + '\n' + '-' + suppressionBonusSplit[2]
        TextBody(parent=suppression_bonus_column, align=uiconst.CENTERLEFT, width=300, text=suppressionBonus, left=10)


class NumberLabel(TextFixedStyleBase):
    default_fontsize = 30
