#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\installationActivityIcon.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.industryUIConst import ACTIVITY_ICONS_SMALL
from eve.client.script.ui.shared.industry.views.industryTooltips import FacilityActivityTooltip
import localization

class InstallationActivityIcon(Container):
    default_state = uiconst.UI_NORMAL
    default_iconColor = Color.WHITE

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isEnabled = attributes.isEnabled
        self.activityID = attributes.activityID
        self.facilityData = attributes.facilityData
        self.opacity = 0.3
        if self.isEnabled:
            self.opacity = 1.0
            if not attributes.isFilterTarget:
                self.opacity = 0.7
        self.icon = Sprite(name='icon', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=ACTIVITY_ICONS_SMALL[self.activityID], opacity=self.opacity)
        if self.facilityData:
            if self.facilityData.HasFacilityModifiers(self.activityID):
                Sprite(name='plusIcon', parent=self, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Icons/plus.png', color=Color.WHITE, pos=(-3, -1, 6, 6), idx=0)

    def LoadTooltipPanel(self, panel, *args):
        if self.facilityData:
            if self.facilityData.rigModifiers:
                self.facilityData = sm.GetService('facilitySvc').GetFreshFacility(self.facilityData.facilityID)
            FacilityActivityTooltip(self.facilityData, self.activityID, panel)
        else:
            text = localization.GetByLabel(industryUIConst.ACTIVITY_NAMES.get(self.activityID))
            panel.AddLabelMedium(text=text, cellPadding=8)
