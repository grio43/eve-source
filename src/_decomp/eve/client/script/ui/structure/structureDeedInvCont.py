#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureDeedInvCont.py
import localization
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from dogma.const import attributeStructureRequiresDeedType
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.container import _InvContBase

class StructureDeedInvCont(_InvContBase):
    __guid__ = 'invCont.StructureDeedInvCont'
    __invControllerClass__ = None
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        _InvContBase.ApplyAttributes(self, attributes)

    def ConstructUI(self):
        self.ConstructDeedSlotUI()
        _InvContBase.ConstructUI(self)

    def ConstructDeedSlotUI(self):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        requireTypeID = int(dogmaLocation.GetAttributeValue(self.itemID, attributeStructureRequiresDeedType))
        if not requireTypeID:
            dogmaLocation.LogWarn("ConstructDeedSlotUI - structure does not have the necessary value for attribute 'StructureRequiresDeedType'", self.itemID)
            return
        topCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, maxHeight=60)
        FillThemeColored(bgParent=topCont, colorType=uiconst.COLORTYPE_UIHILIGHT)
        StructureDeedInvContDescriptionLabel(parent=topCont, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Structures/DeedInventoryRequirementsDescription', typeID=requireTypeID), autoFitToText=True, padding=(3, 2, 3, 2), toolTipTextHeightThreshold=51)


class StructureDeedInvContDescriptionLabel(EveLabelMedium):

    def ApplyAttributes(self, attributes):
        self.toolTipTextHeightThreshold = attributes.get('toolTipTextHeightThreshold', 0)
        EveLabelMedium.ApplyAttributes(self, attributes)
        self.SetBottomAlphaFade(fadeEnd=self.toolTipTextHeightThreshold, maxFadeHeight=10)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.textheight > self.toolTipTextHeightThreshold:
            tooltipPanel.LoadGeneric1ColumnTemplate()
            tooltipPanel.AddLabelMedium(text=self.text, wrapWidth=200)
