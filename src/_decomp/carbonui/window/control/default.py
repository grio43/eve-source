#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\control\default.py
import eveicon
import localization
import signals
from carbonui import uiconst
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.base import Base
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.window.control.action import WindowAction, WindowActionImportance, WindowMenuAction

class WindowControlsBase(Base):

    def __init__(self, on_reserved_width_changed = None, *args, **kwargs):
        self._on_reserved_width_changed = signals.Signal('{}.on_reserved_width_changed'.format(self.__class__.__name__))
        super(WindowControlsBase, self).__init__(*args, **kwargs)
        self.layout()
        if on_reserved_width_changed is not None:
            self._on_reserved_width_changed.connect(on_reserved_width_changed)

    def layout(self):
        pass

    @property
    def reserved_width(self):
        return self.width

    @property
    def on_reserved_width_changed(self):
        return self._on_reserved_width_changed

    def update(self):
        pass

    def _OnClose(self, *args, **kw):
        self._on_reserved_width_changed.clear()
        super(WindowControlsBase, self)._OnClose()


class DefaultWindowControls(WindowControlsBase, ContainerAutoSize):
    OFFSET_LEFT = -4

    def __init__(self, window, actions, get_menu = None, get_link_data = None, menu_unique_name = None, parent = None, align = uiconst.CENTERRIGHT, on_reserved_width_changed = None, display = True):
        self._window = window
        super(DefaultWindowControls, self).__init__(parent=parent, align=align, callback=self._on_size_changed, only_use_callback_when_size_changes=True, on_reserved_width_changed=on_reserved_width_changed)
        self.display = display
        _, _, content_pad_right, _ = window.content_padding
        self._window_controls = WindowControls(parent=self, align=uiconst.TOPRIGHT, left=content_pad_right + self.OFFSET_LEFT, actions=actions, get_menu=get_menu, get_menu_title=self._get_menu_title, get_link_data=get_link_data, menu_unique_name=menu_unique_name)
        window.on_content_padding_changed.connect(self._on_window_content_padding_changed)

    def _get_menu_title(self):
        if self._window.compact or self._window.is_stack:
            return self._window.caption

    @property
    def reserved_width(self):
        window_controls_width, _ = self._window_controls.GetAbsoluteSize()
        return self._window_controls.left * 2 + window_controls_width

    def update(self):
        self._window_controls.update()

    def _on_window_content_padding_changed(self, window):
        _, _, content_pad_right, _ = window.content_padding
        self._window_controls.left = content_pad_right + self.OFFSET_LEFT

    def _on_size_changed(self):
        self.on_reserved_width_changed()

    def Close(self):
        self._window.on_content_padding_changed.disconnect(self._on_window_content_padding_changed)
        self._window = None
        super(DefaultWindowControls, self).Close()


class WindowControls(ContainerAutoSize):
    BUTTON_SIZE = 24

    def __init__(self, actions, get_menu = None, get_menu_title = None, get_link_data = None, menu_unique_name = None, parent = None, align = uiconst.TOPLEFT, left = 0):
        self._actions = actions
        self._action_order = {}
        self._get_menu = get_menu
        self._get_menu_title = get_menu_title
        self._get_link_data = get_link_data
        self._menu_button = None
        self._share_link_button = None
        self._button_cont = None
        self._menu_unique_name = menu_unique_name
        super(WindowControls, self).__init__(parent=parent, align=align, alignMode=uiconst.TORIGHT, left=left, height=self.BUTTON_SIZE)
        self._button_cont = ContainerAutoSize(parent=self, align=uiconst.TORIGHT, alignMode=uiconst.TORIGHT)
        self._menu_cont = ContainerAutoSize(parent=self, align=uiconst.TORIGHT)
        self._content_button_cont = ContainerAutoSize(parent=self, align=uiconst.TORIGHT, alignMode=uiconst.TORIGHT)
        for i, action in enumerate(self._actions):
            self._action_order[action] = i
            if action.available and action.importance == WindowActionImportance.core:
                self._create_action_button(action)
            if action.available and action.importance == WindowActionImportance.content:
                self._create_content_action_button(action)
            action.on_available_changed.connect(self._on_available_changed)
            action.on_importance_changed.connect(self._on_importance_changed)

        self.update()

    def update(self):
        for action in self._actions:
            action.update()

        self._update_more_menu_button()
        self._update_share_link_button()

    def _update_more_menu_button(self):
        if self._has_more_menu_options():
            self._show_menu_button()
        else:
            self._hide_menu_button()

    def _has_more_menu_options(self):
        for action in self._actions:
            if action.importance == WindowActionImportance.extra and action.available:
                return True

        if self._get_menu is not None:
            menu = self._get_menu()
            return len(menu) > 0
        return False

    def _show_menu_button(self):
        if self._menu_button is None:
            self._create_menu_button()
        else:
            self._menu_button.display = True

    def _hide_menu_button(self):
        if self._menu_button is not None:
            self._menu_button.display = False

    def _create_menu_button(self):
        if self._menu_button is None:
            self._menu_button = MenuButtonIcon(parent=self._menu_cont, align=uiconst.CENTER, get_menu_func=self._get_menu_entries, hint=localization.GetByLabel('UI/Common/More'), uniqueUiName=self._menu_unique_name)

    def _update_share_link_button(self):
        if self._has_link_data():
            self._show_share_link()
        else:
            self._hide_share_link()

    def _has_link_data(self):
        if self._get_link_data is not None:
            data = self._get_link_data()
            return data is not None
        return False

    def _show_share_link(self):
        if self._share_link_button is None:
            self._create_share_link_button()
        else:
            self._share_link_button.display = True

    def _hide_share_link(self):
        if self._share_link_button is not None:
            self._share_link_button.display = False

    def _create_share_link_button(self):
        if self._share_link_button is None:
            self._share_link_button = ButtonIcon(name='link_button', parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.link, hint=localization.GetByLabel('UI/Common/DragToShareLinkWindow'))
            self._share_link_button.isDragObject = True
            self._share_link_button.GetDragData = self._get_link_data

    def _create_action_button(self, action, index = -1):
        WindowControlButton(parent=self._button_cont, align=uiconst.TORIGHT, index=index, action=action, size=self.BUTTON_SIZE)

    def _create_content_action_button(self, action, index = -1):
        WindowControlButton(parent=self._content_button_cont, align=uiconst.TORIGHT, index=index, action=action, size=self.BUTTON_SIZE)

    def _add_action_button(self, action):
        my_order = self._action_order[action]
        for i, button in enumerate(self._button_cont.children):
            if button.action == action:
                break
            order = self._action_order[button.action]
            if my_order < order:
                self._create_action_button(action, index=i)
                break
        else:
            self._create_action_button(action)

    def _remove_action_button(self, action):
        for button in self._button_cont.children:
            if button.action == action:
                button.Close()
                return

        for button in self._content_button_cont.children:
            if button.action == action:
                button.Close()
                return

    def _add_content_action_button(self, action):
        my_order = self._action_order[action]
        for i, button in enumerate(self._content_button_cont.children):
            if button.action == action:
                break
            order = self._action_order[button.action]
            if my_order < order:
                self._create_content_action_button(action, index=i)
                break
        else:
            self._create_content_action_button(action)

    def _get_menu_entries(self):
        menu = MenuData()
        if self._get_menu_title:
            menu_title = self._get_menu_title()
            if menu_title:
                menu.AddCaption(menu_title)
        for action in self._actions:
            if isinstance(action, WindowAction):
                self._add_action_to_menu(action, menu)

        menu.AddSeparator()
        for action in self._actions:
            if not isinstance(action, WindowAction):
                self._add_action_to_menu(action, menu)

        extra_options = []
        if self._get_menu is not None:
            extra_options = self._get_menu()
        if len(menu) > 0 and len(extra_options) > 0:
            menu.AddSeparator()
        menu += extra_options
        return menu

    def _add_action_to_menu(self, action, menu):
        if action.available and action.importance == WindowActionImportance.extra:
            menu.AddEntry(text=action.label, func=action.execute, texturePath=action.icon)

    def _on_available_changed(self, action):
        if action.available and action.importance == WindowActionImportance.core:
            self._add_action_button(action)
        elif action.available and action.importance == WindowActionImportance.content:
            self._add_content_action_button(action)
        else:
            self._remove_action_button(action)
        self._update_more_menu_button()

    def _on_importance_changed(self, action):
        if action.importance == WindowActionImportance.core:
            self._add_action_button(action)
        elif action.importance == WindowActionImportance.content:
            self._add_content_action_button(action)
        else:
            self._remove_action_button(action)
        self._update_more_menu_button()

    def _OnClose(self, *args, **kw):
        for action in self._actions:
            action.on_available_changed.disconnect(self._on_available_changed)

        super(WindowControls, self)._OnClose()


class WindowControlButton(ContainerAutoSize):

    def __init__(self, action, parent = None, align = uiconst.TOPLEFT, index = -1, size = 24, icon_size = 16):
        self._action = action
        self._size = size
        self._icon_size = size
        super(WindowControlButton, self).__init__(parent=parent, align=align, alignMode=uiconst.CENTER, idx=index)
        if isinstance(action, WindowMenuAction):
            self._button = MenuButtonIcon(name=action.ui_name, parent=self, align=uiconst.CENTER, width=size, height=size, texturePath=self._resolve_icon(action.icon), iconSize=icon_size, get_menu_func=action.execute, hint=action.label)
        else:
            self._button = ButtonIcon(name=action.ui_name, parent=self, align=uiconst.CENTER, width=size, height=size, texturePath=self._resolve_icon(action.icon), iconSize=icon_size, func=action.execute, hint=action.label)
        self._on_enabled_changed(action)
        action.on_enabled_changed.connect(self._on_enabled_changed)
        action.on_icon_changed.connect(self._on_icon_changed)
        action.on_label_changed.connect(self._on_label_changed)

    @property
    def action(self):
        return self._action

    def _on_enabled_changed(self, action):
        if action.enabled:
            self._button.Enable()
        else:
            self._button.Disable()

    def _resolve_icon(self, icon):
        if isinstance(icon, eveicon.IconData):
            return icon.resolve(self._icon_size)
        else:
            return icon

    def _on_icon_changed(self, action):
        self._button.SetTexturePath(self._resolve_icon(action.icon))

    def _on_label_changed(self, action):
        self._button.hint = action.label

    def Close(self):
        self._action.on_enabled_changed.disconnect(self._on_enabled_changed)
        self._action.on_icon_changed.disconnect(self._on_icon_changed)
        self._action.on_label_changed.disconnect(self._on_label_changed)
        super(WindowControlButton, self).Close()
