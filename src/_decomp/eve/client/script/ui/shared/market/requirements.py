#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\requirements.py
import carbonui.const as uiconst
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
import dogma.const as dconst
from eve.client.script.ui.control.eveLabel import EveLabelSmallBold
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.shared.info import infoConst
from eve.common.script.sys.eveCfg import GetActiveShip
import evetypes
import inventorycommon.const as invconst
from expertSystems.client import AssociatedExpertSystemIcon, is_expert_systems_enabled
from inventorycommon.util import IsFittingModule
import localization
ICON_SIZE = 24

class RequirementsContainer(FlowContainer):
    default_name = 'RequirementsContainer'

    def __init__(self, typeID = None, **kwargs):
        super(RequirementsContainer, self).__init__(contentSpacing=(2, 2), **kwargs)
        self.typeID = typeID
        if self.typeID is not None:
            self.LoadTypeRequirements(self.typeID)

    def LoadTypeRequirements(self, typeID):
        if self.typeID is not None:
            self.Flush()
        self.typeID = typeID
        if typeID is None:
            return
        categoryID = evetypes.GetCategoryID(typeID)
        isSkill = categoryID == invconst.categorySkill
        haveSkill = sm.GetService('skills').GetSkill(typeID) is not None
        requiredSkills = sm.GetService('clientDogmaStaticSvc').GetRequiredSkills(typeID)
        if isSkill and haveSkill:
            SkillBar(parent=self, align=uiconst.NOALIGN, skillID=typeID)
        elif requiredSkills:
            texturePath, hint = sm.GetService('skills').GetRequiredSkillsLevelTexturePathAndHint(requiredSkills.items(), typeID=typeID)
            skillIcon = Sprite(name='skillIcon', parent=self, align=uiconst.NOALIGN, width=ICON_SIZE, height=ICON_SIZE, texturePath=texturePath, hint=hint, useSizeFromTexture=False)
            if is_expert_systems_enabled():
                AssociatedExpertSystemIcon(parent=self, align=uiconst.NOALIGN, type_id=self.typeID, on_click=lambda : sm.GetService('info').ShowInfo(typeID=typeID, selectTabType=infoConst.TAB_REQUIREMENTS))
            skillSvc = sm.GetService('skills')

            def OpenRequirementsInfoTab():
                info = sm.GetService('info')
                info.ShowInfo(typeID, selectTabType=infoConst.TAB_REQUIREMENTS)

            skillIcon.OnClick = OpenRequirementsInfoTab
        if IsFittingModule(categoryID):
            godma = sm.GetService('godma')
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            shipID = GetActiveShip()
            powerContainer = ContainerAutoSize(name='powerContainer', parent=self, align=uiconst.NOALIGN)
            textPadding = 4
            modulePowerLoad = godma.GetTypeAttribute(typeID, dconst.attributePower, 0)
            powerOutput = dogmaLocation.GetAttributeValue(shipID, dconst.attributePowerOutput) - dogmaLocation.GetAttributeValue(shipID, dconst.attributePowerLoad)
            havePower = shipID is not None and powerOutput >= modulePowerLoad
            if havePower:
                icon = 'res:/UI/Texture/classes/Market/powerRequirementMet.png'
                hint = 'UI/Market/Marketbase/PowerRequirementMet'
            else:
                icon = 'res:/UI/Texture/classes/Market/powerRequirementNotMet.png'
                hint = 'UI/Market/Marketbase/PowerRequirementNotMet'
            powerIcon = Sprite(name='powerIcon', parent=powerContainer, align=uiconst.CENTERTOP, texturePath=icon, width=ICON_SIZE, height=ICON_SIZE, ignoreSize=True, hint=localization.GetByLabel(hint))
            powerLabel = EveLabelSmallBold(name='powerLabel', parent=powerContainer, align=uiconst.CENTERTOP, top=ICON_SIZE + 2, text=FmtAmt(modulePowerLoad, fmt='ln'), padRight=textPadding)
            cpuContainer = ContainerAutoSize(parent=self, align=uiconst.NOALIGN)
            moduleCpuLoad = godma.GetTypeAttribute(typeID, dconst.attributeCpu, 0)
            cpuOutput = dogmaLocation.GetAttributeValue(shipID, dconst.attributeCpuOutput) - dogmaLocation.GetAttributeValue(shipID, dconst.attributeCpuLoad)
            haveCpu = shipID is not None and cpuOutput >= moduleCpuLoad
            if haveCpu:
                icon = 'res:/UI/Texture/classes/Market/cpuRequirementMet.png'
                hint = 'UI/Market/Marketbase/CpuRequirementMet'
            else:
                icon = 'res:/UI/Texture/classes/Market/cpuRequirementNotMet.png'
                hint = 'UI/Market/Marketbase/CpuRequirementNotMet'
            cpuIcon = Sprite(name='cpuIcon', parent=cpuContainer, align=uiconst.CENTERTOP, texturePath=icon, ignoreSize=True, width=ICON_SIZE, height=ICON_SIZE, hint=localization.GetByLabel(hint))
            cpuLabel = EveLabelSmallBold(name='cpuLabel', parent=cpuContainer, align=uiconst.CENTERTOP, top=ICON_SIZE + 2, text=FmtAmt(moduleCpuLoad, fmt='ln'), padRight=textPadding)
