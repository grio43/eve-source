#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\common\descriptionIcon.py
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.moreIcon import DescriptionIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium

class DescriptionIconLabel(ContainerAutoSize):
    default_name = 'DescriptionIconLabel'
    default_height = 30
    default_text = ''
    default_maxWidth = None

    def ApplyAttributes(self, attributes):
        super(DescriptionIconLabel, self).ApplyAttributes(attributes)
        self.text = attributes.Get('text', self.default_text)
        self.maxWidth = attributes.Get('maxWidth', self.default_maxWidth)
        self.alignText = attributes.Get('alignText', uiconst.TOLEFT)
        self.tooltipPanelClassInfo = attributes.Get('tooltipPanelClassInfo', None)
        self.ConstructLayout()

    def ConstructLayout(self):
        descriptionIconContainer = Container(name='descriptionIconContainer', parent=self, align=self.alignText, width=DescriptionIcon.default_width)
        self.descriptionIcon = DescriptionIcon(name='descriptionIcon', parent=descriptionIconContainer, align=uiconst.CENTER, tooltipPanelClassInfo=self.tooltipPanelClassInfo, hint=self.hint)
        maxWidth = self.maxWidth - DescriptionIcon.default_width if self.maxWidth else None
        labelCont = ContainerAutoSize(parent=self, align=self.alignText, left=10)
        EveLabelMedium(name='label', parent=labelCont, text=self.text, align=uiconst.CENTERLEFT, color=TextColor.SECONDARY, maxWidth=maxWidth, lineSpacing=-0.1)

    def SetHint(self, hint):
        self.descriptionIcon.hint = hint
