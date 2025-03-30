#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\factionWarfare\complexTypeTooltip.py
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class ComplexTypesTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/ComplexTypes'), wrapWidth=250, colSpan=2)
        self.tooltipPanel.AddSpacer(height=10, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/Type'), value=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/AllowedShips'), opacity=0.75)
        self.tooltipPanel.AddSpacer(height=5, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/NoviceComplex'), value=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/NoviceComplexRestrictions'), wrapWidth=160)
        self.tooltipPanel.AddSpacer(height=5, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/SmallComplex'), value=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/SmallComplexRestrictions'), wrapWidth=160)
        self.tooltipPanel.AddSpacer(height=5, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/MediumComplex'), value=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/MediumComplexRestrictions'), wrapWidth=160)
        self.tooltipPanel.AddSpacer(height=5, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/LargeComplex'), value=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/LargeComplexRestrictions'), wrapWidth=160)
        self.tooltipPanel.AddSpacer(height=5, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/SmallADVComplex'), value=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/SmallADVComplexRestrictions'), wrapWidth=160)
        self.tooltipPanel.AddSpacer(height=5, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/MediumADVComplex'), value=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/MediumADVComplexRestrictions'), wrapWidth=160)
        self.tooltipPanel.AddSpacer(height=5, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/LargeADVComplex'), value=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/LargeADVComplexRestrictions'), wrapWidth=160)
        return self.tooltipPanel
