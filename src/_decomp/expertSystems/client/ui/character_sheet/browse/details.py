#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\browse\details.py
import eveformat
import evetypes
import itertoolsext
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel, infoIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.traits import HasTraits, TraitsContainer
from expertSystems.client import texture
from expertSystems.client.ui.skill_list import SkillList
from expertSystems.client.ui.skill_scroll_cont import SkillScrollCont
from expertSystems.client.util import browse_expert_systems

class ExpertSystemDetails(Container):

    def __init__(self, page_controller, **kwargs):
        self.controller = page_controller
        super(ExpertSystemDetails, self).__init__(**kwargs)
        self.layout()
        self.update()
        self.controller.on_selected_expert_system_changed.connect(self.update)

    def layout(self):
        pass

    def update(self):
        self.Flush()
        expert_system = self.controller.selected_expert_system
        if expert_system is None:
            return
        title_container = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        title_label = eveLabel.EveCaptionSmall(parent=title_container, align=uiconst.TOTOP, text=expert_system.name, padRight=20 if expert_system.description else 0)
        info_icon = infoIcon.InfoIcon(parent=title_container, align=uiconst.TOPLEFT, top=4, typeID=expert_system.type_id)

        def reposition_info_icon():
            info_icon.left = title_label.textwidth + 8

        title_label.OnSizeChanged = reposition_info_icon
        benefits_container = FlowContainer(parent=self, align=uiconst.TOTOP, top=8, contentSpacing=(8, 4))
        skill_benefit = ContainerAutoSize(parent=benefits_container, align=uiconst.NOALIGN, alignMode=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, minHeight=24, hint=localization.GetByLabel('UI/ExpertSystem/SkillCountHint', skill_count=len(expert_system.skills)))
        Sprite(parent=Container(parent=skill_benefit, align=uiconst.TOLEFT, width=24), align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=16, height=16, texturePath=texture.benefit_icon_skill, opacity=0.7)
        eveLabel.EveLabelMedium(parent=skill_benefit, align=uiconst.CENTERLEFT, left=24, text=localization.GetByLabel('UI/ExpertSystem/SkillCount', skill_count=len(expert_system.skills)))
        duration_benefit = ContainerAutoSize(parent=benefits_container, align=uiconst.NOALIGN, alignMode=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, minHeight=24, hint=localization.GetByLabel('UI/ExpertSystem/DurationHint', days=expert_system.duration.days))
        Sprite(parent=Container(parent=duration_benefit, align=uiconst.TOLEFT, width=24), align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=16, height=16, texturePath=texture.benefit_icon_duration, opacity=0.7)
        eveLabel.EveLabelMedium(parent=duration_benefit, align=uiconst.CENTERLEFT, left=24, text=localization.GetByLabel('UI/ExpertSystem/Duration', days=expert_system.duration.days))
        if expert_system.associated_type_ids:
            ship_benefit = ContainerAutoSize(parent=benefits_container, align=uiconst.NOALIGN, alignMode=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, minHeight=24, hint=localization.GetByLabel('UI/ExpertSystem/ShipUnlockHint', ship_count=len(expert_system.associated_type_ids)))
            Sprite(parent=Container(parent=ship_benefit, align=uiconst.TOLEFT, width=24), align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=16, height=16, texturePath=texture.benefit_icon_ship_unlock, opacity=0.7)
            left = 24
            count = len(expert_system.associated_type_ids)
            extra = 0
            if count > 5:
                extra = count - 4
                count = 4
            for type_id in itertoolsext.take(expert_system.associated_type_ids, count):
                ShipTypeIcon(parent=ship_benefit, align=uiconst.CENTERLEFT, left=left, typeID=type_id)
                left += 28

            if extra:
                MoreShipsIcon(parent=ship_benefit, align=uiconst.CENTERLEFT, left=left, type_ids=expert_system.associated_type_ids[count:])
        Button(parent=ContainerAutoSize(parent=self, align=uiconst.TOBOTTOM, padTop=8), align=uiconst.CENTER, label=localization.GetByLabel('UI/InfoWindow/ViewExpertSystemInStore'), fixedheight=32, sidePadding=32, func=self._ViewInStoreButtonClick)
        skill_scroll = SkillScrollCont(copyCallback=self.CopyCallback, selectAllCallback=self.SelectAllCallback, parent=self, align=uiconst.TOALL, padTop=16)
        self.skillList = SkillList(parent=skill_scroll, align=uiconst.TOTOP, max_cell_width=400, skills=expert_system.skills)

    def CopyCallback(self):
        self.skillList.Copy()

    def SelectAllCallback(self):
        self.skillList.SelectAll()

    def _ViewInStoreButtonClick(self, *args):
        browse_expert_systems(self.controller.selected_expert_system.type_id)


class ShipTypeIcon(ItemIcon):

    def __init__(self, **kwargs):
        super(ShipTypeIcon, self).__init__(width=24, height=24, showOmegaOverlay=False, **kwargs)
        self.techIcon.width = 8
        self.techIcon.height = 8

    def LoadTooltipPanel(self, tooltip_panel, *args):
        tooltip_panel.LoadGeneric1ColumnTemplate()
        if HasTraits(self.typeID):
            tooltip_panel.state = uiconst.UI_NORMAL
            tooltip_panel.AddLabelLarge(text=eveformat.bold(evetypes.GetName(self.typeID)))
            tooltip_panel.AddSpacer(width=300, height=1)
            TraitsContainer(parent=tooltip_panel, typeID=self.typeID, traitAttributeIcons=True)


class MoreShipsIcon(ContainerAutoSize):
    default_height = 24
    default_state = uiconst.UI_NORMAL

    def __init__(self, type_ids, **kwargs):
        self.type_ids = type_ids
        super(MoreShipsIcon, self).__init__(minWidth=24, **kwargs)
        self.layout()

    def layout(self):
        eveLabel.EveLabelMedium(parent=self, align=uiconst.CENTER, text=u'+{}'.format(len(self.type_ids)))

    def LoadTooltipPanel(self, tooltip_panel, _):
        tooltip_panel.LoadGeneric2ColumnTemplate()
        tooltip_panel.cellSpacing = 8
        tooltip_panel.state = uiconst.UI_NORMAL
        for type_id in self.type_ids:
            ShipTypeIcon(parent=tooltip_panel, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, typeID=type_id)
            tooltip_panel.AddLabelMedium(align=uiconst.CENTERLEFT, text=evetypes.GetName(type_id))
