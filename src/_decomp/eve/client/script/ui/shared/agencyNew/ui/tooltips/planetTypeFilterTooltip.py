#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\planetTypeFilterTooltip.py
from carbonui import uiconst
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.planet import planetConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class PlanetTypeFilterTooltip(TooltipBaseWrapper):

    def __init__(self, planetCountByType):
        super(PlanetTypeFilterTooltip, self).__init__()
        self.planetCountByType = planetCountByType

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/PlanetaryProduction/planetTypesFilteredOut'))
        self.tooltipPanel.AddDivider()
        for planetType, planetCount in self.planetCountByType.iteritems():
            planetName = GetByLabel(planetConst.PLANETTYPE_NAMES[planetType])
            self.tooltipPanel.AddLabelMedium(text='%sx %s' % (planetCount, planetName))

        return self.tooltipPanel
