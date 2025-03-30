#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\omegaRestrictedEntryInfoPanel.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from clonegrade.const import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.cloneGrade.button import CloneGradeButtonMedium
from localization import GetByLabel
from carbonui.uicore import uicore

class OmegaRestrictedEntryInfoPanel(Container):
    default_name = 'OmegaRestrictedEntryInfoPanel'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.NOALIGN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = attributes.text or GetByLabel('UI/CloneState/RequiresOmegaClone')
        self.origin = attributes.origin
        self.reason = attributes.reason
        self.bgFill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.5)
        labelCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padBottom=5)
        EveLabelMediumBold(parent=labelCont, align=uiconst.TOPLEFT, text=text, color=COLOR_OMEGA_ORANGE, padLeft=2)
        cloneButtonCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP)
        self.icon = CloneGradeButtonMedium(parent=cloneButtonCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, padLeft=2)

    def OnClick(self):
        uicore.cmd.OpenCloneUpgradeWindow(self.origin, self.reason)

    def OnMouseEnter(self, *args):
        self.icon.OnMouseEnter()
        animations.FadeTo(self.bgFill, self.bgFill.opacity, 1.0, duration=0.3)

    def OnMouseExit(self, *args):
        self.icon.OnMouseExit()
        animations.FadeTo(self.bgFill, self.bgFill.opacity, 0.5, duration=0.3)
