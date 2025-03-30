#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\type_list_window.py
from collections import defaultdict
import evetypes
import localization
import uthread2
import expertSystems.client
import eveicon
from carbon.common.script.sys.serviceManager import ServiceManager
import eveui
import carbonui
from carbonui.uiconst import IdealSize
from carbonui.uianimations import animations
from carbonui.control.window import Window
from carbonui.control.scroll import Scroll
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.info.infoConst import TAB_REQUIREMENTS
from eve.client.script.ui.shared.cloneGrade.omegaCloneIcon import OmegaCloneIcon
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SHIPRESTRICTIONS

class TypeListWindow(Window):
    default_name = 'TypeListWindow'
    default_windowID = 'type_list_window'
    default_captionLabelPath = 'UI/Generic/Types'
    default_width = IdealSize.SIZE_480
    default_height = IdealSize.SIZE_480
    default_minSize = (IdealSize.SIZE_240, IdealSize.SIZE_480)
    default_iconNum = 'res:/ui/Texture/WindowIcons/info.png'
    __notifyevents__ = ['OnSkillsChanged', 'OnExpertSystemsUpdated_Local']

    def __init__(self, **kwargs):
        super(TypeListWindow, self).__init__(**kwargs)
        self._TYPE_ENTRY_CLASS = TypeEntry
        self._type_ids = set()
        self._types_by_group = defaultdict(set)
        self._search_text = ''
        self._header_text = ''
        self._info_text = ''
        self._layout()

    @classmethod
    def Open(cls, type_ids = None, header_text = '', info_text = '', window_caption = None, *args, **kwargs):
        window = super(TypeListWindow, cls).Open(*args, **kwargs)
        window.caption = window_caption or localization.GetByLabel(cls.default_captionLabelPath)
        if type_ids is not None:
            window.set_type_ids(type_ids, header_text, info_text)
        return window

    @classmethod
    def OpenTypeList(cls, type_list_id, header_text = '', window_caption = None, info_text = None, *args, **kwargs):
        kwargs['type_ids'] = evetypes.GetTypeIDsByListID(type_list_id)
        if window_caption is None:
            window_caption = evetypes.GetTypeListDisplayName(type_list_id)
        if info_text is None:
            message_id = evetypes.GetTypeListDescriptionMessageID(type_list_id)
            if message_id:
                info_text = localization.GetByMessageID(message_id)
        return cls.Open(header_text=header_text, info_text=info_text, window_caption=window_caption, *args, **kwargs)

    @classmethod
    def OpenGroup(cls, group_id, window_caption = None, *args, **kwargs):
        kwargs['type_ids'] = evetypes.GetTypeIDsByGroup(group_id)
        if window_caption is None:
            window_caption = evetypes.GetGroupNameByGroup(group_id)
        return cls.Open(window_caption=window_caption, *args, **kwargs)

    @classmethod
    def OpenCategory(cls, category_id, window_caption = None, *args, **kwargs):
        kwargs['type_ids'] = evetypes.GetTypeIDsByCategory(category_id)
        if window_caption is None:
            window_caption = evetypes.GetCategoryNameByCategory(category_id)
        return cls.Open(window_caption=window_caption, *args, **kwargs)

    def Close(self, *args, **kwargs):
        super(TypeListWindow, self).Close(*args, **kwargs)
        self._type_ids.clear()
        self._types_by_group.clear()

    def OnSkillsChanged(self, *args, **kwargs):
        self._update_entries()

    def OnExpertSystemsUpdated_Local(self, *args, **kwargs):
        self._update_entries()

    def _layout(self):
        self._construct_top_info()
        self._construct_top_bar(ContainerAutoSize(parent=self.content, align=carbonui.Align.TOTOP, padBottom=16, padTop=16))
        self._results_scroll = Scroll(parent=self.content, align=carbonui.Align.TOALL, rowPadding=4)

    def _construct_top_info(self):
        self._header_label = carbonui.TextHeader(parent=self.content, align=carbonui.Align.TOTOP, text='', padBottom=4, display=False, color=carbonui.TextColor.HIGHLIGHT)
        self._info_label = carbonui.TextBody(parent=self.content, align=carbonui.Align.TOTOP, text='', padBottom=4, display=False)

    def _construct_top_bar(self, parent):
        self._search_field = SingleLineEditText(parent=parent, align=carbonui.Align.TOTOP, hintText=localization.GetByLabel('UI/Common/Search'), icon=eveicon.search, OnChange=self._on_search_field_text_changed, maxLength=50)
        self._search_field.ShowClearButton(icon=eveicon.close)

    @uthread2.debounce(0.2)
    def _on_search_field_text_changed(self, text):
        new_text = self._search_field.GetText().lower()
        if new_text != self._search_text:
            self._search_text = new_text
            self._update_entries()

    def set_type_ids(self, type_ids, header_text = '', info_text = ''):
        self._type_ids = set(type_ids)
        self._search_text = ''
        self._search_field.Clear()
        self._update_types_by_group()
        self._header_text = header_text or ''
        self._info_text = info_text or ''
        self._update_header_label()
        self._update_info_label()
        self._update_entries()

    def _update_types_by_group(self):
        self._types_by_group = defaultdict(set)
        for type_id in self._type_ids:
            if self._validate_type(type_id):
                self._types_by_group[self._get_group_id(type_id)].add(type_id)

    def _validate_type(self, type_id):
        return evetypes.IsPublished(type_id)

    def _get_group_id(self, type_id):
        return evetypes.GetGroupID(type_id)

    def _get_group_type_ids(self, group_id):
        return evetypes.GetTypeIDsByGroup(group_id)

    def _update_header_label(self):
        if self._header_text:
            self._header_label.text = self._header_text
            self._header_label.display = True
        else:
            self._header_label.display = False

    def _update_info_label(self):
        if self._info_text:
            self._info_label.text = self._info_text
            self._info_label.display = True
        else:
            self._info_label.display = False

    @eveui.skip_if_destroyed
    def _update_entries(self, *args, **kwargs):
        entries = self._get_entries()
        self._results_scroll.LoadContent(contentList=entries, noContentHint=localization.GetByLabel('UI/Common/NothingFound'))

    def _get_entries(self):
        if not self._type_ids:
            return []
        if self._search_text:
            return self._get_entries_with_search()
        return self._get_group_entries()

    def _get_group_entries(self):
        groups = self._get_sorted_groups()
        return [ GetFromClass(GroupEntry, {'id': (name, group_id),
         'label': name,
         'iconID': self._get_group_icon(group_id),
         'showicon': 'hide',
         'showlen': False,
         'sublevel': 0,
         'BlockOpenWindow': True,
         'forceOpen': len(self._types_by_group) == 1,
         'state': 'locked',
         'GetSubContent': lambda node, _group_id = group_id: self._get_type_entries_for_group(_group_id),
         'rightAlignExpander': True,
         'secondaryText': self._get_group_secondary_text(group_id)}) for group_id, name in groups ]

    def _get_sorted_groups(self):
        return localization.util.Sort([ (group_id, self._get_group_name(group_id)) for group_id in self._types_by_group ], key=lambda x: x[1])

    def _get_group_name(self, group_id):
        return evetypes.GetGroupNameByGroup(group_id)

    def _get_group_secondary_text(self, group_id):
        return str(len(self._types_by_group[group_id]))

    def _get_group_icon(self, group_id):
        return None

    def _get_type_entries_for_group(self, group_id):
        types = self._get_sorted_types(group_id)
        return [ GetFromClass(self._TYPE_ENTRY_CLASS, self._get_type_entry_data(type_id, name, 1)) for type_id, name in types ]

    def _get_sorted_types(self, group_id):
        type_ids = self._get_type_ids_to_sort(group_id)
        return localization.util.Sort([ (type_id, evetypes.GetName(type_id)) for type_id in type_ids ], key=lambda x: x[1])

    def _get_entries_with_search(self):
        all_type_ids = set()
        for group_id in self._types_by_group:
            all_type_ids.update(self._get_type_ids_to_sort(group_id))

        types = [ (type_id, evetypes.GetName(type_id)) for type_id in all_type_ids ]
        sorted_types = localization.util.Sort([ (type_id, name) for type_id, name in types if self._filter(name) ], key=lambda x: x[1])
        return [ GetFromClass(self._TYPE_ENTRY_CLASS, self._get_type_entry_data(type_id, name, 0)) for type_id, name in sorted_types ]

    def _get_type_entry_data(self, type_id, name, sublevel):
        return {'label': name,
         'type_id': type_id,
         'sublevel': sublevel}

    def _get_type_ids_to_sort(self, group_id):
        return self._types_by_group[group_id]

    def _filter(self, name):
        if not self._search_text:
            return True
        return self._search_text in name.lower()


class GroupEntry(ListGroup):
    _secondary_text_label = None

    def Startup(self, *args):
        super(GroupEntry, self).Startup(*args)
        right_container = ContainerAutoSize(parent=self, align=carbonui.Align.TORIGHT, idx=2)
        self._secondary_text_label = EveLabelMedium(parent=right_container, align=carbonui.Align.CENTERRIGHT, color=carbonui.TextColor.SECONDARY, padLeft=4, padRight=4, text='')

    def Load(self, node):
        super(GroupEntry, self).Load(node)
        self._secondary_text_label.text = node.secondaryText or ''
        if self._secondary_text_label.text:
            self._secondary_text_label.display = True
        else:
            self._secondary_text_label.display = False


class TypeEntry(SE_BaseClassCore):
    isDragObject = True
    _icon_cont = None
    _info_icon = None
    _icon = None
    _primary_label = None
    _untrained_icon_container = None
    _untrained_icon = None
    _expert_system_container = None
    _omega_container = None

    def Startup(self, *args):
        if not sm.GetService('cloneGradeSvc').IsOmega():
            self._omega_container = Container(name='omega_container', parent=self, align=carbonui.Align.TORIGHT, width=24, padLeft=2, padRight=4, display=False)
        self._untrained_icon_container = Container(name='untrained_icon_container', parent=self, align=carbonui.Align.TORIGHT, width=24, display=False)
        self._untrained_icon = Sprite(parent=self._untrained_icon_container, align=carbonui.Align.CENTER, height=24, width=24)
        self._untrained_icon.OnClick = self._on_skill_icon_click
        self._icon_cont = Container(parent=self, align=carbonui.Align.TOLEFT, width=32, padRight=8)
        self._info_icon = InfoIcon(parent=Container(parent=self, align=carbonui.Align.TORIGHT, width=24), align=carbonui.Align.CENTER, opacity=0)
        self._primary_label = carbonui.TextBody(parent=Container(parent=self, align=carbonui.Align.TOALL), align=carbonui.Align.CENTERLEFT, autoFadeSides=8)

    def Load(self, node):
        self.sr.node = node
        type_id = node.type_id
        self._load_icon(type_id)
        sub_level = node.get('sublevel', 0)
        self._icon_cont.left = sub_level * 16 + (8 if sub_level > 0 else 0)
        self._info_icon.SetTypeID(type_id)
        self._primary_label.text = node.label
        self._update_untrained_icon(type_id)
        self._update_omega_restriction(type_id)
        self.EnableDrag()

    def _load_icon(self, type_id):
        if self._icon is None:
            self._icon = ItemIcon(parent=self._icon_cont, align=carbonui.Align.CENTER, width=32, height=32, typeID=type_id, showOmegaOverlay=False)
        else:
            self._icon.SetTypeID(type_id)

    def _update_untrained_icon(self, type_id):
        if sm.GetService('skills').IsSkillRequirementMet(type_id):
            self._untrained_icon_container.display = False
        elif sm.GetService('skills').IsUnlockedWithExpertSystem(type_id):
            self._untrained_icon.texturePath = 'res:/UI/Texture/classes/ExpertSystems/logo_simple_24.png'
            self._untrained_icon.hint = localization.GetByLabel('UI/ExpertSystem/AssociatedSystemActive')
            self._untrained_icon.SetSize(16, 16)
            self._untrained_icon_container.display = True
        else:
            skills = sm.GetService('skills').GetRequiredSkills(type_id).items()
            texture_path, hint = sm.GetService('skills').GetRequiredSkillsLevelTexturePathAndHint(skills, typeID=type_id)
            self._untrained_icon.texturePath = texture_path
            self._untrained_icon.hint = hint
            self._untrained_icon.SetSize(24, 24)
            self._untrained_icon_container.display = True

    def _update_omega_restriction(self, type_id):
        if self._omega_container is None:
            return
        if sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(type_id):
            OmegaCloneIcon(parent=self._omega_container, align=carbonui.Align.CENTER, width=24, height=24, origin=ORIGIN_SHIPRESTRICTIONS, reason=type_id)
            self._omega_container.display = True
        else:
            self._omega_container.Flush()
            self._omega_container.display = False

    def GetHeight(self, *args):
        return 32

    def GetMenu(self):
        menu_service = ServiceManager.Instance().GetService('menu')
        return menu_service.GetMenuFromItemIDTypeID(typeID=self.sr.node.type_id, itemID=None, includeMarketDetails=True)

    def OnDblClick(self):
        sm.GetService('info').ShowInfo(self.sr.node.type_id)

    @classmethod
    def GetCopyData(cls, node):
        return evetypes.GetName(node.type_id)

    def GetDragData(self):
        return [eveui.dragdata.ItemType(self.sr.node.type_id)]

    def OnMouseEnter(self, *args):
        super(TypeEntry, self).OnMouseEnter(*args)
        animations.FadeTo(self._info_icon, startVal=self._info_icon.opacity, endVal=1, duration=0.3)

    def OnMouseExit(self, *args):
        super(TypeEntry, self).OnMouseExit(*args)
        animations.FadeTo(self._info_icon, startVal=self._info_icon.opacity, endVal=0, duration=0.3)

    def _on_skill_icon_click(self, *args, **kwargs):
        sm.GetService('info').ShowInfo(typeID=self.sr.node.type_id, selectTabType=TAB_REQUIREMENTS)
