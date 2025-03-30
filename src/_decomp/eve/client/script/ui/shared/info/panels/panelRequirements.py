#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelRequirements.py
import expertSystems.client
from carbonui import const as uiconst
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import infoIcon
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.client.script.ui.shared.tooltip.skillBtns import SkillActionContainer
from eve.client.script.ui.shared.tooltip.skill_requirement import AddTrainingTime, AlphaTrainingTimeContainer, OmegaTrainingTimeContainer, GetActivityTextForType
from eve.common.lib import appConst as const
import localization

class PanelRequirements(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.bottomContainer = ContainerAutoSize(parent=self, align=uiconst.TOBOTTOM, padding=const.defaultPadding)
        self.scroll = Scroll(name='scroll', parent=self, padding=const.defaultPadding)
        self.scroll.ignoreTabTrimming = True
        self.ConstructExpertSystemSection()

    def ConstructExpertSystemSection(self):
        self.expertSystemCont = DragResizeCont(parent=self, align=uiconst.TOBOTTOM, minSize=80, defaultSize=80, idx=0)
        headerCont = ContainerAutoSize(parent=self.expertSystemCont, align=uiconst.TOTOP, alignMode=uiconst.CENTERLEFT, minHeight=24, padLeft=6)
        Sprite(parent=headerCont, align=uiconst.TOPLEFT, width=24, height=24, texturePath=expertSystems.texture.badge_24)
        header = EveLabelMedium(parent=headerCont, align=uiconst.CENTERLEFT, left=24, text=localization.GetByLabel('UI/ExpertSystem/HeaderImproveWithExpertSystem'), padding=(8, 0, 8, 0))
        icon = infoIcon.MoreInfoIcon(parent=headerCont, align=uiconst.CENTERLEFT, hint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ExpertSystems/ExpertSystemDescription'))

        def updateInfoIconPosition():
            icon.left = header.left + header.width + header.padLeft + header.padRight
            icon.top = (header.height - icon.height) / 2

        header.OnSizeChanged = updateInfoIconPosition
        self.expertSystemScroll = Scroll(name='expertSystemScroll', parent=self.expertSystemCont, padding=const.defaultPadding)
        self.expertSystemScroll.ignoreTabTrimming = True
        self.expertSystemCont.display = False

    @classmethod
    def RequirementsVisible(cls, typeID):
        return bool(sm.GetService('skills').GetRequiredSkills(typeID))

    def Load(self):
        scrollList = sm.GetService('info').GetReqSkillInfo(self.typeID)
        self.scroll.Load(contentList=scrollList)
        self.LoadSkillTrainingTimeAndActions()
        if expertSystems.is_expert_systems_enabled():
            self.LoadAssociatedExpertSystems()

    def LoadSkillTrainingTimeAndActions(self):
        self.bottomContainer.Flush()
        if sm.GetService('skills').IsSkillRequirementMet(self.typeID):
            return
        totalTime = sm.GetService('skills').GetSkillTrainingTimeLeftToUseType(self.typeID, includeBoosters=False)
        omegaRestricted = ItemObject(self.typeID, None).NeedsOmegaUpgrade()
        if sm.GetService('cloneGradeSvc').IsOmega():
            OmegaTrainingTimeContainer(parent=self.bottomContainer, omegaTime=totalTime)
        else:
            omegaTime = totalTime / 2
            AlphaTrainingTimeContainer(parent=self.bottomContainer, isOmegaRestricted=omegaRestricted, alphaTime=totalTime, omegaTime=omegaTime, activityText=GetActivityTextForType(self.typeID))
        if not omegaRestricted:
            SkillActionContainer(parent=self.bottomContainer, padTop=8, align=uiconst.TOTOP, typeID=self.typeID)

    def LoadAssociatedExpertSystems(self):
        self.expertSystemCont.display = False
        if not expertSystems.has_associated_expert_system(self.typeID):
            return
        associatedExpertSystems = expertSystems.get_associated_expert_systems(self.typeID)
        relevantExpertSystems = filter(lambda system: expertSystems.expert_system_benefits_player(system.type_id), associatedExpertSystems)
        scrollEntries = []
        for expertSystem in relevantExpertSystems:
            data = {'label': expertSystem.name,
             'typeID': expertSystem.type_id,
             'showinfo': True}
            scrollEntries.append(GetFromClass(expertSystems.ExpertSystemEntry, data=data))

        if scrollEntries:
            self.expertSystemCont.display = True
            self.expertSystemScroll.Load(fixedEntryHeight=27, contentList=scrollEntries)
