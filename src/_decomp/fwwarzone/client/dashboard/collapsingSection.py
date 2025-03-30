#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\collapsingSection.py
import math
from carbonui import uiconst, TextColor
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelLarge

class CollapsingSection(ContainerAutoSize):
    default_headerText = 'CollapsingSection'
    default_collapsed = True
    default_showDividerLine = True
    default_alignMode = uiconst.TOTOP
    default_isContainerAutoSize = False
    default_headerTextIndentation = 20

    def ApplyAttributes(self, attributes):
        super(CollapsingSection, self).ApplyAttributes(attributes)
        self.headerText = attributes.get('headerText', self.default_headerText)
        self.collapsed = attributes.get('collapsed', self.default_collapsed)
        self.section = attributes.get('section')
        self.showDividerLine = attributes.get('showDividerLine', self.default_showDividerLine)
        self.preToggleCallback = attributes.get('preToggleCallback', self.defaultPreToggleCallback)
        self.expandedSectionHeight = self.section.height
        self.expandedSectionHeightWithHeader = self.expandedSectionHeight + 40
        self.isContainerAutoSize = attributes.get('isContainerAutoSize', self.default_isContainerAutoSize)
        self.headerTextIndentation = attributes.get('headerTextIndentation', self.default_headerTextIndentation)
        self.headerCont = None
        self.ConstructLayout()

    def ConstructLayout(self):
        self.headerCont = Container(parent=self, align=uiconst.TOTOP, height=40, state=uiconst.UI_NORMAL)
        self.headerCont.OnClick = self.Toggle
        DividerLine(parent=self, align=uiconst.TOBOTTOM_NOPUSH)
        self.arrowCont = Transform(width=16, height=16, padRight=17, parent=self.headerCont, align=uiconst.TORIGHT, state=uiconst.UI_DISABLED, rotation=math.pi / 2.0 if self.collapsed else 0.0, rotationCenter=(0.5, 0.5))
        self.arrow = Sprite(name='arrow', parent=self.arrowCont, texturePath='res:/UI/Texture/Icons/38_16_229.png', align=uiconst.CENTER, width=16, height=16)
        self.headerLabel = EveLabelLarge(parent=self.headerCont, align=uiconst.CENTERLEFT, text=self.headerText, padding=(self.headerTextIndentation,
         5,
         5,
         5), color=TextColor.SECONDARY if self.collapsed else TextColor.HIGHLIGHT)
        self.section.align = uiconst.TOTOP
        self.children.append(self.section)
        if self.collapsed:
            self.section.height = 0

    def Toggle(self, callCallback = True):
        if callCallback:
            self.preToggleCallback(self)
        animations.StopAnimation(self.section, 'height')
        if self.collapsed:
            self.headerLabel.color = TextColor.HIGHLIGHT
            self.collapsed = False
            if self.isContainerAutoSize:
                self.section.ExpandHeight(duration=0.25)
            else:
                animations.MorphScalar(self.section, 'height', startVal=self.section.height, endVal=self.expandedSectionHeight, duration=0.25)
        else:
            self.headerLabel.color = TextColor.SECONDARY
            self.collapsed = True
            if self.isContainerAutoSize:
                self.section.CollapseHeight(duration=0.25)
            else:
                animations.MorphScalar(self.section, 'height', startVal=self.section.height, endVal=0, duration=0.25)
        newRotation = math.pi / 2.0 if self.collapsed else 0.0
        self.arrowCont.rotation = newRotation

    def defaultPreToggleCallback(self, *args):
        pass
