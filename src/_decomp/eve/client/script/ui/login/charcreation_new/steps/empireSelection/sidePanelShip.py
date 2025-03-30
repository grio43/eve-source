#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\sidePanelShip.py
import math
import evetypes
import trinity
import uthread
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.uianimations import animations
from characterdata.races import get_race_name
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionLarge
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionConst import FACTIONSELECT_ANIMATION_DURATION, COLOR_BY_FACTIONID, SHIP_VIDEO_BY_FACTIONID
from eve.client.script.ui.login.charcreation_new.charCreationSignals import onEmpireFactionSelected
from eve.common.lib import appConst
from eveui import Sprite
from localization import GetByLabel
SHIP_TYPEID_BY_FACTIONID = {appConst.factionMinmatarRepublic: 588,
 appConst.factionGallenteFederation: 606,
 appConst.factionAmarrEmpire: 596,
 appConst.factionCaldariState: 601}

class SidePanelShip(Container):

    def ApplyAttributes(self, attributes):
        super(SidePanelShip, self).ApplyAttributes(attributes)
        factionID = attributes.factionID
        onEmpireFactionSelected.connect(self.OnEmpireFactionSelected)
        x = 0.75
        self.videoSprite = StreamingVideoSprite(name='icon', parent=self, align=uiconst.CENTERTOP, pos=(0,
         -110,
         x * 896,
         x * 597), spriteEffect=trinity.TR2_SFX_COPY)
        textCont = ContainerAutoSize(parent=self, align=uiconst.TOBOTTOM, padLeft=30, top=30)
        self.shipNameLabel = EveCaptionLarge(parent=textCont, align=uiconst.TOTOP)
        self.factionShipHintLabel = EveLabelLarge(parent=textCont, align=uiconst.TOTOP, padTop=4)
        Sprite(name='bottomLine', parent=self, align=uiconst.TOBOTTOM, height=2, texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionGradientLine.png', idx=0)
        Sprite(name='selectionNotch', parent=self, align=uiconst.CENTERBOTTOM, pos=(0, 2, 50, 4), texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionNotch.png', rotation=math.pi)
        Sprite(name='shipBG', bgParent=self, texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/shipBG.png', color=(0, 0, 0, 0.8))
        if factionID:
            self._UpdateFaction(factionID)
            self.opacity = 1.0

    def OnEmpireFactionSelected(self, factionID):
        uthread.new(self._OnEmpireFactionSelected, factionID)

    def _OnEmpireFactionSelected(self, factionID):
        duration = FACTIONSELECT_ANIMATION_DURATION / 2
        animations.FadeTo(self, self.opacity, 0.0, duration=duration, sleep=True)
        self._UpdateFaction(factionID)
        animations.FadeIn(self, duration=duration, timeOffset=duration)

    def _UpdateFaction(self, factionID):
        typeID = SHIP_TYPEID_BY_FACTIONID[factionID]
        self.videoSprite.SetVideoPath(SHIP_VIDEO_BY_FACTIONID[factionID], videoLoop=True)
        self.shipNameLabel.text = evetypes.GetName(typeID)
        self.shipNameLabel.SetRGBA(*COLOR_BY_FACTIONID[factionID])
        raceName = get_race_name(appConst.raceByFaction[factionID])
        self.factionShipHintLabel.text = GetByLabel('UI/CharacterCreation/EmpireSelection/BeginnerShipHint', raceName=raceName)
