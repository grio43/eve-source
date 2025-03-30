#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingPanels\attributePanel.py
import dogma.data as dogma_data
from carbonui import const as uiconst
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fittingScreen.fittingPanels.basePanel import BaseMenuPanel
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from localization import GetByMessageID

class AttributePanel(BaseMenuPanel):

    def ApplyAttributes(self, attributes):
        BaseMenuPanel.ApplyAttributes(self, attributes)

    def LoadPanel(self, initialLoad = False):
        self.Flush()
        self.ResetStatsDicts()

    def AddAttributeCont(self, attribute, parentGrid, attributeID = None, texturePath = None):
        if attributeID is None:
            attributeID = attribute.attributeID
        attributeCont = self.GetValueCont(self.iconSize)
        parentGrid.AddCell(cellObject=attributeCont)
        if texturePath:
            graphicID = None
        else:
            graphicID = attribute.iconID
        displayName = dogma_data.get_attribute_display_name(attribute.attributeID)
        icon = Icon(graphicID=graphicID, pos=(3,
         0,
         self.iconSize,
         self.iconSize), hint=displayName, name=displayName, ignoreSize=True, state=uiconst.UI_DISABLED, icon=texturePath, align=uiconst.CENTERLEFT)
        attributeCont.AddCell(cellObject=icon)
        label = EveLabelMedium(text='', left=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        attributeCont.AddCell(cellObject=label)
        attributeCont.hint = displayName
        tooltipTitleID = attribute.tooltipTitleID
        if tooltipTitleID:
            tooltipTitle = GetByMessageID(tooltipTitleID)
            tooltipDescr = GetByMessageID(attribute.tooltipDescriptionID)
            SetTooltipHeaderAndDescription(targetObject=attributeCont, headerText=tooltipTitle, descriptionText=tooltipDescr)
        self.statsLabelsByIdentifier[attributeID] = label
        self.statsIconsByIdentifier[attributeID] = icon
        self.statsContsByIdentifier[attributeID] = attributeCont
        return (icon, label, attributeCont)
