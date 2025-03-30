#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\ship_restrictions_window.py
from collections import defaultdict
import localization
import evetypes
import eveui
import carbonui
import shipgroup
from carbonui.services.setting import UserSettingBool
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.shared.type_list_window import TypeListWindow, TypeEntry
from evedungeons.client.util import GetDungeonShipRestrictions, GetDungeonShipRestrictionsTypeListID
from evedungeons.client.data import GetDungeon
show_unlocked_ships_only = UserSettingBool(settings_key='ship_restrictions_show_unlocked_ships_only', default_value=False)
hide_restricted_ships = UserSettingBool(settings_key='ship_restrictions_hide_restricted_ships', default_value=True)
SHIP_GROUP_ORDER = {x:i for i, x in enumerate([shipgroup.groupRookie,
 shipgroup.groupFrigate,
 shipgroup.groupNavyFrigate,
 shipgroup.groupInterceptor,
 shipgroup.groupAssault,
 shipgroup.groupCovertOps,
 shipgroup.groupElectronicAttack,
 shipgroup.groupLogisticsFrigates,
 shipgroup.groupDestroyer,
 shipgroup.groupNavyDestroyers,
 shipgroup.groupInterdictor,
 shipgroup.groupCommandDestroyers,
 shipgroup.groupTacticalDestroyer,
 shipgroup.groupCruiser,
 shipgroup.groupNavyCruiser,
 shipgroup.groupRecon,
 shipgroup.groupHeavyAssault,
 shipgroup.groupHeavyInterdictor,
 shipgroup.groupLogistics,
 shipgroup.groupFlagCruiser,
 shipgroup.groupStrategicCruiser,
 shipgroup.groupBattlecruiser,
 shipgroup.groupNavyBattlecruiser,
 shipgroup.groupCommandship,
 shipgroup.groupBattleship,
 shipgroup.groupNavyBattleship,
 shipgroup.groupBlackOps,
 shipgroup.groupMarauder,
 shipgroup.groupDreadnought,
 shipgroup.groupNavyDreadnoughts,
 shipgroup.groupLancerDreadnought,
 shipgroup.groupCarrier,
 shipgroup.groupTitan,
 shipgroup.groupShuttle,
 shipgroup.groupMiningFrigate,
 shipgroup.groupExpeditionFrigate,
 shipgroup.groupMiningBarge,
 shipgroup.groupExhumers,
 shipgroup.groupIndustrial,
 shipgroup.groupOreIndustrial,
 shipgroup.groupTransport,
 shipgroup.groupIndustrialCommand,
 shipgroup.groupCapitalIndustrial,
 shipgroup.groupFreighter,
 shipgroup.groupJumpFreighter])}

class ShipRestrictionsWindow(TypeListWindow):
    default_name = 'ShipRestrictionsWindow'
    default_windowID = 'ship_restrictions'
    default_captionLabelPath = 'UI/Dungeons/ShipRestrictionsWindow'
    __notifyevents__ = TypeListWindow.__notifyevents__ + ['ProcessActiveShipChanged']

    def __init__(self, **kwargs):
        self._dungeon_id = None
        self._gate_id = None
        self._type_list_description_id = None
        self._restricted_types_by_group = defaultdict(set)
        super(ShipRestrictionsWindow, self).__init__(**kwargs)
        self._TYPE_ENTRY_CLASS = ShipTypeEntry
        show_unlocked_ships_only.on_change.connect(self._show_unlocked_ships_only_changed)
        hide_restricted_ships.on_change.connect(self._update_entries)

    @classmethod
    def Open(cls, dungeon_id = None, gate_id = None, header_text = '', *args, **kwargs):
        window = super(ShipRestrictionsWindow, cls).Open(type_ids=None, *args, **kwargs)
        window.set_dungeon(dungeon_id, gate_id, header_text)
        return window

    def Close(self, *args, **kwargs):
        super(TypeListWindow, self).Close(*args, **kwargs)
        show_unlocked_ships_only.on_change.disconnect(self._show_unlocked_ships_only_changed)
        hide_restricted_ships.on_change.disconnect(self._update_entries)
        self._restricted_types_by_group.clear()

    def ProcessActiveShipChanged(self, *args, **kwargs):
        self._update_info_label()

    def set_dungeon(self, dungeon_id, gate_id, header_text):
        self._dungeon_id = dungeon_id
        self._gate_id = gate_id
        type_list_id = GetDungeonShipRestrictionsTypeListID(dungeon_id, gate_id)
        if type_list_id:
            self._type_list_description_id = evetypes.GetTypeListDescriptionMessageID(type_list_id)
        else:
            self._type_list_description_id = None
        ship_restrictions = GetDungeonShipRestrictions(dungeonID=dungeon_id, gateID=gate_id)
        if not header_text:
            dungeon_data = GetDungeon(self._dungeon_id)
            header_text = localization.GetByMessageID(dungeon_data.dungeonNameID)
        self.set_type_ids(ship_restrictions.allowedShipTypes if ship_restrictions else [], header_text=header_text)

    def _construct_top_bar(self, parent):
        super(ShipRestrictionsWindow, self)._construct_top_bar(parent)
        checkbox_container = FlowContainer(name='checkbox_container', parent=parent, align=carbonui.Align.TOTOP, contentSpacing=(24, 0), padTop=8)
        Checkbox(parent=checkbox_container, align=carbonui.Align.NOALIGN, text=localization.GetByLabel('UI/Dungeons/ShipRestrictionShowUnlockedOnly'), setting=show_unlocked_ships_only)
        Checkbox(parent=checkbox_container, align=carbonui.Align.NOALIGN, text=localization.GetByLabel('UI/Dungeons/ShipRestrictionHideRestricted'), setting=hide_restricted_ships)

    def _show_unlocked_ships_only_changed(self, *args, **kwargs):
        self._update_types_by_group()
        self._update_entries()

    def _update_types_by_group(self):
        super(ShipRestrictionsWindow, self)._update_types_by_group()
        ignored_types_by_group = defaultdict(set)
        for group_id, type_ids in self._types_by_group.iteritems():
            group_type_ids = self._get_group_type_ids(group_id)
            for type_id in group_type_ids:
                if type_id not in type_ids and self._validate_type(type_id):
                    ignored_types_by_group[group_id].add(type_id)

        self._restricted_types_by_group = ignored_types_by_group

    def _validate_type(self, type_id):
        return evetypes.IsPublished(type_id) and evetypes.GetShipGroupID(type_id)

    def _get_group_id(self, type_id):
        return evetypes.GetShipGroupID(type_id)

    def _get_group_type_ids(self, group_id):
        return sm.GetService('shipTree').GetShipTypeIDsByGroupID(group_id)

    def _get_sorted_groups(self):
        return sorted([ (group_id, self._get_group_name(group_id)) for group_id in self._types_by_group ], key=lambda x: (SHIP_GROUP_ORDER.get(x[0], 999), x[1]))

    def _get_group_name(self, group_id):
        return localization.GetByMessageID(cfg.infoBubbleGroups[group_id]['nameID'])

    def _get_group_secondary_text(self, group_id):
        amount = len([ type_id for type_id in self._get_type_ids_to_sort(group_id) if type_id in self._types_by_group[group_id] ])
        total_amount = len(self._types_by_group[group_id]) + len(self._restricted_types_by_group[group_id])
        if amount == total_amount:
            return str(amount)
        else:
            return localization.GetByLabel('UI/Common/Formatting/Fraction', a=amount, b=total_amount)

    def _get_group_icon(self, group_id):
        return cfg.infoBubbleGroups[group_id]['icon']

    def _get_type_ids_to_sort(self, group_id):
        if not hide_restricted_ships.is_enabled():
            type_ids = self._types_by_group[group_id].union(self._restricted_types_by_group[group_id])
        else:
            type_ids = self._types_by_group[group_id]
        if show_unlocked_ships_only.is_enabled():
            return [ type_id for type_id in type_ids if sm.GetService('skills').IsSkillRequirementMet(type_id) or sm.GetService('skills').IsUnlockedWithExpertSystem(type_id) ]
        else:
            return type_ids

    def _get_type_entry_data(self, type_id, *args, **kwargs):
        data = super(ShipRestrictionsWindow, self)._get_type_entry_data(type_id, *args, **kwargs)
        is_restricted = False
        if not hide_restricted_ships.is_enabled():
            is_restricted = type_id in self._restricted_types_by_group[self._get_group_id(type_id)]
        data['is_restricted'] = is_restricted
        return data

    @eveui.skip_if_destroyed
    def _update_info_label(self):
        self._info_label.display = True
        if not self._type_ids:
            self._info_label.text = 'No ship restrictions found'
            return
        ship_type_id = None
        if session.shipid:
            item = sm.GetService('invCache').GetInventoryFromId(session.shipid).GetItem()
            if item:
                ship_type_id = item.typeID
        if not ship_type_id:
            text = localization.GetByLabel('UI/Agents/Dialogue/DungeonShipRestrictionsShowList')
        elif ship_type_id in self._type_ids:
            text = localization.GetByLabel('UI/Agents/Dialogue/DungeonShipRestrictionsListShipIsNotRestricted', shipTypeID=ship_type_id)
        else:
            text = localization.GetByLabel('UI/Agents/Dialogue/DungeonShipRestrictionsListShipIsRestricted', shipTypeID=ship_type_id)
        if self._type_list_description_id:
            text = u'{}\n\n{}'.format(text, localization.GetByMessageID(self._type_list_description_id))
        self._info_label.text = text


class ShipTypeEntry(TypeEntry):

    def Load(self, node):
        super(ShipTypeEntry, self).Load(node)
        if node.is_restricted:
            self._primary_label.color = carbonui.TextColor.DANGER
        else:
            self._primary_label.color = carbonui.TextColor.NORMAL
