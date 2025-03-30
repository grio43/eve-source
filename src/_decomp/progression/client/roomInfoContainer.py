#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\roomInfoContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelSmall
from localization import GetByLabel
from progression.client.const import COLOR_UI_HIGHLIGHTING, WIDGET_TEXT_BOLD_WHITE

class RoomInfoContainer(Container):

    def ApplyAttributes(self, attributes):
        super(RoomInfoContainer, self).ApplyAttributes(attributes)
        self._static_highlighted_space_object_ids = attributes.connecting_gate_ids
        self.uiHighlightingService = sm.GetService('uiHighlightingService')
        self.objectiveDescription = EveLabelSmall(name='objectiveDescription', parent=self, align=uiconst.TOTOP, text=GetByLabel('UI/Progression/GoToNextRoomDescription'), padding=(18, 4, 0, 0))
        roomCont = Container(name='roomCont', parent=self, align=uiconst.TOTOP, height=20, padLeft=2)
        Sprite(name='iconGrouping', parent=roomCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=6, height=6, texturePath='res:/UI/Texture/Classes/DungeonMessaging/ToDoBulletpoint.png', color=WIDGET_TEXT_BOLD_WHITE)
        self.label = EveLabelMediumBold(name='nextRoom', parent=roomCont, align=uiconst.TOLEFT, text=GetByLabel('UI/Progression/JumpThroughGateTask'), padding=(12, 3, 0, 0))

    def OnMouseEnter(self, *args):
        self.label.SetTextColor(COLOR_UI_HIGHLIGHTING)
        for space_object_id in self._static_highlighted_space_object_ids:
            self.uiHighlightingService.highlight_space_object_by_dungeon_object_id(space_object_id, '', '', None, None, False)

    def OnMouseExit(self, *args):
        self.label.SetTextColor(WIDGET_TEXT_BOLD_WHITE)
        self.uiHighlightingService.clear_space_object_highlighting()
