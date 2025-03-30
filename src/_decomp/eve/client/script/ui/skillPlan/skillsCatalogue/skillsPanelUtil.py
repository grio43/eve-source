#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillsCatalogue\skillsPanelUtil.py
import carbonui.const as uiconst
import dogma.data as dogma_data
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGridCell
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from clonegrade.const import COLOR_OMEGA_GOLD
from eve.client.script.ui.control.eveLabel import Label
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
from skills.skillConst import ATTRIBUTES_BY_GROUPID

def LoadSkillGroupTooltipPanel(controller, tooltipPanel):
    tooltipPanel.LoadStandardSpacing()
    tooltipPanel.columns = 2
    tooltipPanel.AddMediumHeader(text=controller.GetName())
    tooltipPanel.AddLabelMedium(text=controller.GetDescription(), width=300, colSpan=2)
    AddLevelsTrained(controller, tooltipPanel)
    AddPointsTrained(controller, tooltipPanel)
    AddCertificatesClaimed(controller, tooltipPanel)
    AddAttributes(controller, tooltipPanel)


def AddAttributes(controller, tooltipPanel):
    attributeID1, attributeID2 = ATTRIBUTES_BY_GROUPID[controller.groupID]
    tooltipPanel.AddCell(AttributeCont(attrID=attributeID1), cellClass=CellBG)
    tooltipPanel.AddCell(AttributeCont(attrID=attributeID2), cellClass=CellBG)


def AddCertificatesClaimed(controller, tooltipPanel):
    certsTotal = controller.GetAccumulatedCertificateLevelsTotal()
    if certsTotal:
        certsTrained = controller.GetAccumulatedCertificateLevelsTrained()
        skillPointsText = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/CertificatesClaimedPerGroup', certsTrained=certsTrained, certsTotal=certsTotal)
        tooltipPanel.AddLabelMedium(text=skillPointsText, colSpan=2)


def AddSpPerMin(controller, tooltipPanel):
    attributeID1, attributeID2 = ATTRIBUTES_BY_GROUPID[controller.groupID]
    spPerMin = controller.GetSpPerMinute(attributeID1, attributeID2)
    skillPointsText = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SpPerMinute', spPerMin=spPerMin)
    tooltipPanel.AddLabelMedium(text=skillPointsText, colSpan=2)


def AddLevelsTrained(controller, tooltipPanel):
    levelsTrained = controller.GetAccumulatedLevelsTrainedAndEnabled()
    levelsTotal = controller.GetAccumulatedLevelsTotal()
    levelsDisabled = controller.GetAccumulatedLevelsTrainedAndDisabled()
    if levelsDisabled:
        color = Color.RGBtoHex(*COLOR_OMEGA_GOLD)
        skillPointsText = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillLevelsPerGroupDisabled', levelsTrained=levelsTrained, levelsTotal=levelsTotal, levelsDisabled=levelsDisabled, color=color)
    else:
        skillPointsText = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillLevelsPerGroup', levelsTrained=levelsTrained, levelsTotal=levelsTotal)
    tooltipPanel.AddLabelMedium(text=skillPointsText, colSpan=2)


def AddPointsTrained(controller, tooltipPanel):
    pointsTrained = controller.GetAccumulatedSkillPointsTrained()
    pointsTotal = controller.GetAccumulatedSkillPointsTotal()
    skillPointsText = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillPointsPerGroup', pointsTrained=pointsTrained, pointsTotal=pointsTotal)
    tooltipPanel.AddLabelMedium(text=skillPointsText, colSpan=2)


class AttributeCont(ContainerAutoSize):
    default_align = uiconst.CENTER
    default_padTop = -3
    default_padBottom = -3

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        attrID = attributes.attrID
        iconID = dogma_data.get_attribute_icon_id(attrID)
        attributeDisplayName = dogma_data.get_attribute_display_name(attrID)
        texturePath = GetIconFile(iconID)
        Sprite(parent=self, align=uiconst.CENTERLEFT, pos=(-12, 0, 32, 32), texturePath=texturePath)
        Label(parent=self, align=uiconst.CENTERLEFT, left=24, text=attributeDisplayName)


class CellBG(LayoutGridCell):

    def ApplyAttributes(self, attributes):
        LayoutGridCell.ApplyAttributes(self, attributes)
        Fill(parent=self, padRight=2, color=(1, 1, 1, 0.1))
