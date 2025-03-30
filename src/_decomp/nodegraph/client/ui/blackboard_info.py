#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\blackboard_info.py
from eve.client.script.ui.util import uix
import carbonui.const as uiconst
import eveui
from .collapse_section import CollapseSection
from .util import copy_value

class BlackboardInfo(CollapseSection):
    default_name = 'BlackboardInfo'

    def __init__(self, node_graph_context, can_edit = True, **kwargs):
        self._node_graph_context = node_graph_context
        self._can_edit = can_edit
        self._list_items = {}
        self._node_graph_context.subscribe_to_all_values(self._blackboard_updated)
        super(BlackboardInfo, self).__init__(title='Blackboard Info', **kwargs)

    def close(self):
        self._node_graph_context.unsubscribe_from_all_values(self._blackboard_updated)

    def _blackboard_updated(self, key, value, **kwargs):
        if not self.is_content_constructed:
            return
        if key in self._list_items:
            self._list_items[key].update_value(value)
        else:
            self._construct_param(key, value)

    def construct_content(self):
        self._no_params_label = eveui.EveLabelMedium(parent=self.content_container, state=eveui.State.hidden, align=eveui.Align.to_top, text='No blackboard params')
        if not self._node_graph_context.values:
            self._no_params_label.state = eveui.State.disabled
        else:
            for key, value in self._node_graph_context.values.iteritems():
                self._construct_param(key, value)

    def _construct_param(self, key, value):
        self._list_items[key] = BlackboardListItem(parent=self.content_container, key=key, value=value, update_value_func=self._node_graph_context.update_value if self._can_edit else None)
        if not self._node_graph_context.values:
            self._no_params_label.state = eveui.State.disabled
        else:
            self._no_params_label.state = eveui.State.hidden


class BlackboardListItem(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top

    def __init__(self, key, value, update_value_func, **kwargs):
        super(BlackboardListItem, self).__init__(**kwargs)
        self._key = key
        self._value = value
        self._update_value_func = update_value_func
        self._bg_fill = eveui.Fill(bgParent=self, opacity=0)
        text_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, padding=(8, 4, 8, 4))
        self._key_label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, text=key)
        self._value_label = eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, text=_value_as_string(value), padLeft=4, maxLines=1)

    def update_value(self, value):
        self._value = value
        self._value_label.text = _value_as_string(value)

    def GetMenu(self, *args):
        result = list([('Copy value', lambda : copy_value(self._value)), ('Copy key', lambda : copy_value(self._key))])
        if self._update_value_func:
            result.insert(0, ('Edit blackboard value', self._edit_blackboard_value))
        result.append(_key_value_entry(self._key, self._value))
        return result

    def _edit_blackboard_value(self, *args, **kwargs):
        format = [{'type': 'text',
          'text': self._key},
         {'type': 'text',
          'text': self._value},
         {'type': 'edit',
          'key': 'new_value',
          'setvalue': unicode(self._value),
          'label': '_hide'},
         {'type': 'errorcheck',
          'errorcheck': self._edit_error_check}]
        retval = uix.HybridWnd(format, caption='Edit Blackboard Value', windowID='edit_blackboard_value', modal=1, buttons=uiconst.OKCANCEL, minW=300, minH=50)
        if not retval:
            return
        try:
            new_value = type(self._value)(retval['new_value'])
        except:
            new_value = None

        self._update_value_func(self._key, new_value)

    def _edit_error_check(self, retval):
        new_value = retval['new_value']
        if self._value is not None and new_value:
            try:
                check_type = type(self._value)(new_value)
            except:
                return 'You cannot change the type!'

        return ''

    def OnMouseEnter(self, *args):
        eveui.fade_in(self._bg_fill, end_value=0.05, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade_out(self._bg_fill, duration=0.1)


def _value_as_string(value):
    if isinstance(value, list):
        return u'{} {}'.format(len(value), value)
    else:
        return unicode(value)


def _key_value_entry(key, value):
    from carbonui.control.contextMenu.menuEntryData import MenuEntryData
    from functools import partial

    def copy_value(value):
        import json
        import blue
        if isinstance(value, dict):
            try:
                clipboard_data = json.dumps(value, indent=2, sort_keys=True)
            except:
                clipboard_data = unicode(dict(value))

        else:
            clipboard_data = unicode(value)
        blue.pyos.SetClipboardData(clipboard_data)

    from utillib import KeyVal
    if isinstance(value, KeyVal):
        value = value.__dict__
    if isinstance(value, dict):
        sub_menu = []
        for value_key, value_value in value.iteritems():
            sub_menu.append(_key_value_entry(value_key, value_value))

        return MenuEntryData(key, func=partial(copy_value, value), subMenuData=sub_menu)
    elif isinstance(value, list):
        sub_menu = []
        for index, value_value in enumerate(value):
            sub_menu.append(_key_value_entry(index, value_value))

        return MenuEntryData(u'{} ({})'.format(key, len(value)), func=partial(copy_value, value), subMenuData=sub_menu)
    else:
        return MenuEntryData(u'{}: {}'.format(key, value), func=partial(copy_value, value))
