#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\tooltips\scanResultTooltip.py
import carbonui.const as uiconst
import dogma.const
import evetypes
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import GetScanDifficultyText
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel
from probescanning.const import COMBAT_TARGETS
from probescanning.explorationSites import is_exploration_site, get_exploration_site_name, get_exploration_site_description
import inventorycommon.const as invConst
GAS_SITE = dogma.const.attributeScanLadarStrength
RELIC_SITE = dogma.const.attributeScanMagnetometricStrength
DATA_SITE = dogma.const.attributeScanRadarStrength
WORMHOLE = dogma.const.attributeScanWormholeStrength
COMBAT_SITE = dogma.const.attributeScanAllStrength
ORE_SITE = dogma.const.attributeScanGravimetricStrength
DATA_AND_RELIC_SITES_CONTAINER_ICON = 'res:/UI/Texture/Shared/Brackets/scatterContainerUnopened.png'

class ScanResultTooltip(TooltipBaseWrapper):

    def __init__(self, node):
        super(ScanResultTooltip, self).__init__()
        self.node = node

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        site_type = self.GetSiteType()
        if is_exploration_site(site_type):
            archetype_id = self.GetArchetype()
            self.CreateExplanation(name=get_exploration_site_name(site_type, archetype_id), text=get_exploration_site_description(site_type, archetype_id))
        elif self.node.result.scanGroupID in COMBAT_TARGETS:
            name = GetByLabel('UI/Inflight/Scanner/UnknownSite')
            text = GetByLabel('UI/Inflight/Scanner/UnknownSiteTooltip')
            if self.node.result.groupID:
                name = evetypes.GetGroupNameByGroup(self.node.result.groupID)
                text = GetByLabel('UI/Inflight/Scanner/UnknownType')
                if self.node.result.typeID:
                    text = evetypes.GetName(self.node.result.typeID)
            self.CreateExplanation(name, text)
        elif site_type is None:
            name = GetByLabel('UI/Inflight/Scanner/UnknownSite')
            text = GetByLabel('UI/Inflight/Scanner/UnknownSiteTooltip')
            self.CreateExplanation(name, text)
        return self.tooltipPanel

    def GetSiteType(self):
        return self.node.result.strengthAttributeID

    def GetArchetype(self):
        return self.node.result.archetypeID

    def CreateIconLabel(self, iconPath, label):
        nameIconContainer = ContainerAutoSize(align=uiconst.CENTERLEFT, height=16)
        Sprite(parent=nameIconContainer, align=uiconst.TOLEFT, width=16, height=16, texturePath=iconPath)
        Label(parent=nameIconContainer, text=label, align=uiconst.TOLEFT, bold=True, color=Color.GRAY, left=5)
        self.tooltipPanel.AddCell(nameIconContainer, colSpan=1)
        self.AddDifficultyLabel()

    def AddDifficultyLabel(self):
        difficulty = self.node.result.difficulty
        text = GetScanDifficultyText(difficulty) if difficulty else ''
        self.tooltipPanel.AddLabelMedium(text=text, colSpan=2, align=uiconst.TORIGHT)

    def CreateExplanation(self, name, text):
        if self.GetSiteType() is not None:
            self.CreateIconLabel(iconPath=self.node.sortValues[0], label=name)
        else:
            self.tooltipPanel.AddLabelMedium(text=name, colSpan=2, bold=True, color=Color.GRAY)
        self.tooltipPanel.AddSpacer(1, 6, 2)
        self.tooltipPanel.AddLabelMedium(text=text, wrapWidth=200, state=uiconst.UI_NORMAL, colSpan=2)
