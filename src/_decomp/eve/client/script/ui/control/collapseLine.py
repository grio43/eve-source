#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\collapseLine.py
import math
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.transform import Transform
from carbonui.services.setting import UserSettingBool
from carbonui.uianimations import animations
from signals import Signal
ANIM_DURATION = 0.5
SIDE_ALIGNMENTS = (uiconst.TOLEFT,
 uiconst.TORIGHT,
 uiconst.TOLEFT_NOPUSH,
 uiconst.TORIGHT_NOPUSH,
 uiconst.TOTOP_PROP,
 uiconst.TOBOTTOM_PROP)
HORIZONTAL_ALIGNMENT = (uiconst.TOTOP,
 uiconst.TOBOTTOM,
 uiconst.TOTOP_NOPUSH,
 uiconst.TOBOTTOM_NOPUSH,
 uiconst.TOTOP_PROP,
 uiconst.TOBOTTOM_PROP)

class CollapseLine(Container):
    default_name = 'collapseLine'
    default_align = uiconst.TORIGHT
    default_height = 20
    default_width = 20

    def ApplyAttributes(self, attributes):
        super(CollapseLine, self).ApplyAttributes(attributes)
        settingKey = attributes.get('settingKey', 'collapseLine')
        self.isCollapsedSetting = UserSettingBool(settings_key=settingKey, default_value=False)
        isCollapsed = attributes.get('isCollapsed', None)
        if isCollapsed is None:
            isCollapsed = self.isCollapsedSetting.get()
        self.isCollapsed = isCollapsed
        self.collapsingSection = attributes.get('collapsingSection')
        self.useCustomTransition = attributes.get('useCustomTransition', False)
        self.collapsingSectionSize = attributes.get('collapsingSectionWidth', 10)
        self.on_section_expand = Signal(signalName='on_section_expand')
        self.on_section_collapse = Signal(signalName='on_section_collapse')
        self.ContstructUI()
        self.DoCollapseOrExpand(False)

    def ContstructUI(self):
        rotation = self._GetRotation()
        self.btnCont = Transform(parent=self, align=uiconst.CENTER, rotationCenter=(0.5, 0.5), pos=(0, 0, 20, 20), rotation=rotation)
        self.collapseBtn = ButtonIcon(name='collapseBtn', parent=self.btnCont, align=uiconst.CENTER, width=20, height=20, iconSize=20, texturePath='res:/UI/Texture/shared/collapser.png', func=self.CollapseExpand)

    def _GetRotation(self):
        rotation = math.pi if self.isCollapsed else 0
        if self.align in (uiconst.TOLEFT, uiconst.TOLEFT_PROP):
            rotation -= math.pi
        if self.align in HORIZONTAL_ALIGNMENT:
            rotation -= math.pi / 2
        return rotation

    def SetHint(self, hint):
        self.collapseBtn.SetHint(hint)

    def SetCollapsingSectionSize(self, value):
        self.collapsingSectionSize = value

    def CollapseExpand(self, *args):
        if self.isCollapsed:
            self.SetExpanded()
        else:
            self.SetCollapsed()

    def SetExpanded(self, animate = True):
        self.isCollapsed = False
        self.isCollapsedSetting.set(False)
        self.UpdateIcon(animate)
        self.on_section_expand(animate)
        self.DoCollapseOrExpand(animate=animate)

    def SetCollapsed(self, animate = True):
        self.isCollapsed = True
        self.isCollapsedSetting.set(True)
        self.UpdateIcon(animate)
        self.on_section_collapse(animate)
        self.DoCollapseOrExpand(animate=animate)

    def UpdateIcon(self, animate = True):
        rotation = self._GetRotation()
        if animate:
            animations.MorphScalar(self.btnCont, 'rotation', self.btnCont.rotation, rotation, duration=0.2)
        else:
            self.btnCont.SetRotation(rotation)

    def DoCollapseOrExpand(self, animate = True):
        if self.useCustomTransition:
            return
        if self.align in SIDE_ALIGNMENTS:
            if self.isCollapsed:
                self.CollapseSideBar(animate=animate)
            else:
                self.ExpandSideBar(animate=animate)
        if self.align in HORIZONTAL_ALIGNMENT:
            if self.isCollapsed:
                self.CollapseHorizontalBar(animate=animate)
            else:
                self.ExpandHorizontalBar(animate=animate)

    def ExpandSideBar(self, animate = True):
        if animate:
            animations.MorphScalar(self.collapsingSection, 'width', startVal=0, endVal=self.collapsingSectionSize, duration=ANIM_DURATION)
        else:
            self.collapsingSection.width = self.collapsingSectionSize

    def CollapseSideBar(self, animate = True):
        if animate:
            animations.MorphScalar(self.collapsingSection, 'width', startVal=self.collapsingSection.width, endVal=0, duration=ANIM_DURATION)
        else:
            self.collapsingSection.width = 0

    def ExpandHorizontalBar(self, animate = True):
        if animate:
            animations.MorphScalar(self.collapsingSection, 'height', startVal=0, endVal=self.collapsingSectionSize, duration=ANIM_DURATION)
        else:
            self.collapsingSection.height = self.collapsingSectionSize

    def CollapseHorizontalBar(self, animate = True):
        if animate:
            animations.MorphScalar(self.collapsingSection, 'height', startVal=self.collapsingSection.height, endVal=0, duration=ANIM_DURATION)
        else:
            self.collapsingSection.height = 0
