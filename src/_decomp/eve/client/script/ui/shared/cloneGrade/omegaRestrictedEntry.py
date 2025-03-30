#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\omegaRestrictedEntry.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.uianimations import animations
from clonegrade.const import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.cloneGrade.button import CloneGradeButtonMedium
from localization import GetByLabel
from carbonui.uicore import uicore

class OmegaRestrictedEntry(Container):
    default_name = 'OmegaRestrictedEntry'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.NOALIGN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = attributes.text or GetByLabel('UI/CloneState/RequiresOmegaClone')
        self.origin = attributes.origin
        self.reason = attributes.reason
        self.bgFill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.5)
        EveLabelMediumBold(parent=self, align=uiconst.CENTERLEFT, text=text, color=COLOR_OMEGA_ORANGE, left=6)
        self.icon = CloneGradeButtonMedium(parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, left=4)

    def OnClick(self):
        uicore.cmd.OpenCloneUpgradeWindow(self.origin, self.reason)

    def OnMouseEnter(self, *args):
        self.icon.OnMouseEnter()
        animations.FadeTo(self.bgFill, self.bgFill.opacity, 1.0, duration=0.3)

    def OnMouseExit(self, *args):
        self.icon.OnMouseExit()
        animations.FadeTo(self.bgFill, self.bgFill.opacity, 0.5, duration=0.3)
