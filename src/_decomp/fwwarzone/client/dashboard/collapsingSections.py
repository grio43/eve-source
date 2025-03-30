#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\collapsingSections.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.themeColored import FillThemeColored

class CollapsableSectionsContainer(Container):
    default_layoutRoom = 1.0
    default_sections = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sections = attributes.get('sections', self.default_sections)
        self.layoutRoom = attributes.get('layoutRoom', self.default_layoutRoom)
        self.collapsableSections = []
        self.InitSections()

    def InitSections(self):
        for i in range(len(self.sections)):
            section, sectionName, collapsed = self.sections[i]
            sectionHeader = _SectionHeader(parent=self, align=uiconst.TOTOP, headerText=sectionName, collapsed=collapsed, padBottom=4)
            collapsableSection = _CollapsableSection(parent=self, align=uiconst.TOTOP_PROP, height=self.layoutRoom / len(self.sections), collapsed=False)
            sectionHeader.clickCallback = self._GetToggleFun(i)
            self.collapsableSections.append(collapsableSection)
            collapsableSection.children.append(section)

        for i in range(len(self.collapsableSections)):
            if self.collapsableSections[i].collapsed:
                self.ToggleSectionCollapse(i)

    def _GetToggleFun(self, sectionIdx):

        def _f():
            self.ToggleSectionCollapse(sectionIdx)

        return _f

    def ToggleSectionCollapse(self, sectionIdx):
        for i in range(len(self.collapsableSections)):
            if i == sectionIdx:
                self.collapsableSections[i].collapsed = not self.collapsableSections[i].collapsed

        for section in self.collapsableSections:
            if not section.collapsed:
                section.Expand(self.GetSectionHeight())
            else:
                section.Collapse()

    def GetSectionHeight(self):
        openSections = 0
        for section in self.collapsableSections:
            if not section.collapsed:
                openSections += 1

        return self.layoutRoom / openSections


class _SectionHeader(ContainerAutoSize):
    default_collapsed = False
    default_alignMode = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_animationDuration = 0.25

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.collapsed = attributes.get('collapsed', self.default_collapsed)
        self.headerText = attributes.get('headerText', '')
        self.animationDuration = attributes.get('animationDuration', self.default_animationDuration)
        self.Construct()
        self.clickCallback = None

    def Construct(self):
        self.headerCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT)
        Fill(bgParent=self.headerCont, opacity=0.05)
        self.arrowCont = Transform(width=16, height=16, left=2, parent=self.headerCont, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, rotation=math.pi / 2.0 if self.collapsed else 0.0, rotationCenter=(0.5, 0.5))
        self.arrow = Sprite(name='arrow', parent=self.arrowCont, texturePath='res:/UI/Texture/Icons/38_16_229.png', align=uiconst.CENTER, width=16, height=16)
        EveLabelLarge(parent=self.headerCont, align=uiconst.TOPLEFT, text=self.headerText, padding=5, bold=True, left=20)

    def OnClick(self, *args):
        if self.clickCallback:
            self.collapsed = not self.collapsed
            self.clickCallback()
            newRotation = math.pi / 2.0 if self.collapsed else 0.0
            self.arrowCont.rotation = newRotation


class _CollapsableSection(Container):
    default_collapsed = False
    default_animationDuration = 0.25

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.collapsed = attributes.get('collapsed', self.default_collapsed)
        self.initialSetHeight = attributes.get('height')
        self.animationDuration = attributes.get('animationDuration', self.default_animationDuration)

    def Expand(self, expandTo):
        self.collapsed = False
        animations.MorphScalar(self, 'height', startVal=self.height, endVal=expandTo, duration=self.animationDuration)

    def Collapse(self):
        self.collapsed = True
        animations.MorphScalar(self, 'height', startVal=self.height, endVal=0, duration=self.animationDuration)
