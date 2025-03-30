#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\fwInformationTab.py
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium, EveCaptionSmall, EveLabelLarge
from eve.client.script.ui.skillPlan.skillPlanInfoIcon import SkillPlanInfoIcon
from eveui import Sprite
from localization import GetByLabel

class FWInformationTab(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(FWInformationTab, self).ApplyAttributes(attributes)
        scrollCont = ScrollContainer(parent=self, align=uiconst.TOALL, padding=(64, 66, 64, 22))
        self.mainCont = ContainerAutoSize(parent=scrollCont, align=uiconst.TOTOP, clipChildren=True)
        self.ConstructLayout()

    def ConstructLayout(self):
        titleCont = Container(parent=self.mainCont, align=uiconst.TOTOP, height=30, padBottom=32)
        EveCaptionLarge(parent=titleCont, align=uiconst.TOLEFT, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/objectives'))
        SkillPlanInfoIcon(parent=titleCont, align=uiconst.TOLEFT, hint=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/advantageObjectivesDescription'), padLeft=5)
        DeployableObjectiveDescRow(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, title=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/propagandaBroadcastStructure'), desc=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/propagandaBroadcastStructureDesc'), padBottom=32, typeID=73225)
        DeployableObjectiveDescRow(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, title=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/listeningOutput'), desc=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/listeningOutpostDesc'), padBottom=32, typeID=73270)
        DungeonDescRow(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, title=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/supplyDepot'), desc=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/supplyDepotDesc'), padBottom=32)
        DungeonDescRow(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, title=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/supplyCache'), desc=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/supplyCacheDesc'), padBottom=32)
        DungeonDescRow(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, title=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/rendezvouzPoint'), desc=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/rendezvouzPointDesc'), padBottom=32)
        DungeonDescRow(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, title=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/operationCenters'), desc=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/operationCentersDesc'), padBottom=32)
        DungeonDescRow(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, title=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/battlefieldComplexes'), desc=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/battlefieldComplexesDesc'))
        Container(height=100, parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)


class DungeonDescRow(ContainerAutoSize):
    default_height = 100

    def ApplyAttributes(self, attributes):
        super(DungeonDescRow, self).ApplyAttributes(attributes)
        self.title = attributes.get('title')
        self.desc = attributes.get('desc')
        self.ConstructLayout()

    def ConstructLayout(self):
        spriteCont = ContainerAutoSize(parent=self, align=uiconst.TOLEFT, alignMode=uiconst.TOPLEFT)
        Sprite(parent=spriteCont, align=uiconst.TOPLEFT, width=16, height=16, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/Brackets/beacon.png', top=4)
        textCont = ContainerAutoSize(parent=self, padLeft=12, align=uiconst.TOTOP)
        EveCaptionSmall(align=uiconst.TOTOP, parent=textCont, text=self.title)
        EveLabelMedium(parent=textCont, align=uiconst.TOTOP, text=self.desc, padding=(16, 5, 0, 0))


class DeployableObjectiveDescRow(ContainerAutoSize):
    default_height = 145

    def ApplyAttributes(self, attributes):
        super(DeployableObjectiveDescRow, self).ApplyAttributes(attributes)
        self.spriteTexturePath = attributes.get('spriteTexturePath')
        self.title = attributes.get('title')
        self.desc = attributes.get('desc')
        self.typeID = attributes.get('typeID')
        self.ConstructLayout()

    def ConstructLayout(self):
        spriteCont = ContainerAutoSize(parent=self, align=uiconst.TOLEFT, alignMode=uiconst.TOPLEFT)
        Icon(parent=spriteCont, align=uiconst.TOPLEFT, typeID=self.typeID, width=64, height=64, state=uiconst.UI_DISABLED)
        textCont = ContainerAutoSize(parent=self, padLeft=12, align=uiconst.TOTOP)
        EveCaptionSmall(align=uiconst.TOTOP, parent=textCont, text=self.title)
        EveLabelMedium(parent=textCont, align=uiconst.TOTOP, text=self.desc, padding=(8, 5, 0, 0))
