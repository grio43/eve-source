#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\importantmission.py
from agentinteraction.constUI import PADDING_XSMALL
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite

class ImportantMissionContainer(Container):
    default_align = uiconst.TOLEFT
    default_padRight = PADDING_XSMALL
    default_name = 'important_mission_container'

    def ApplyAttributes(self, attributes):
        self.header = None
        self.text = None
        self.standing_list = None
        super(ImportantMissionContainer, self).ApplyAttributes(attributes)
        size = attributes.size
        self.important_mission_sprite = Sprite(name='important_mission_sprite', parent=self, align=uiconst.CENTER, pos=(0,
         0,
         size,
         size), texturePath='res:/UI/Texture/Classes/AgentInteraction/ImportantMission.png')
        self.important_mission_sprite.LoadTooltipPanel = self.LoadTooltipPanel

    def update_header_text(self, header, text, standing_list):
        self.header = header
        self.text = text
        self.standing_list = standing_list

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddCaptionSmall(text=self.header, colSpan=tooltipPanel.columns)
        if self.text:
            tooltipPanel.AddLabelMedium(text=self.text, wrapWidth=300, colSpan=tooltipPanel.columns)
        if self.standing_list:
            for name, value in self.standing_list:
                tooltipPanel.AddLabelMedium(text=name)
                tooltipPanel.AddLabelMedium(text=value)
                tooltipPanel.FillRow()
