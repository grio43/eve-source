#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelConst.py
from eve.client.script.ui.shared.info.shipInfoConst import TAB_OVERVIEW, TAB_ATTRIBUTES, TAB_FITTING, TAB_SKILLS, TAB_VARIATIONS, TAB_INDUSTRY, TAB_SKINS
from eve.client.script.ui.shared.info.shipInfoPanels.panelAttributes import PanelAttributes
from eve.client.script.ui.shared.info.shipInfoPanels.panelFitting import PanelFitting
from eve.client.script.ui.shared.info.shipInfoPanels.panelIndustry import PanelIndustry
from eve.client.script.ui.shared.info.shipInfoPanels.panelOverview import PanelOverview
from eve.client.script.ui.shared.info.shipInfoPanels.panelSkills import PanelSkills
from eve.client.script.ui.shared.info.shipInfoPanels.panelSkin import PanelSkins
from eve.client.script.ui.shared.info.shipInfoPanels.panelVariations import PanelVariations
SHIP_INFO_PANELS = {TAB_OVERVIEW: PanelOverview,
 TAB_ATTRIBUTES: PanelAttributes,
 TAB_FITTING: PanelFitting,
 TAB_SKILLS: PanelSkills,
 TAB_VARIATIONS: PanelVariations,
 TAB_INDUSTRY: PanelIndustry,
 TAB_SKINS: PanelSkins}
