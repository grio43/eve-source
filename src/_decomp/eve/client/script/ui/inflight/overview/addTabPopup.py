#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\addTabPopup.py
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.inflight.overview import overviewUtil
from eve.client.script.ui.util.namedPopup import NamePopupWnd
from localization import GetByLabel
from overviewPresets import overviewSettingsConst

class AddTabPopup(NamePopupWnd):
    default_width = 360
    default_height = 350
    default_minSize = (default_width, default_height)
    default_maxLength = overviewSettingsConst.MAX_TAB_NAME_LENGTH
    default_body = GetByLabel('UI/Overview/AddTabInstructions')

    def ApplyAttributes(self, attributes):
        self.overview_service = sm.GetService('overviewPresetSvc')
        super(AddTabPopup, self).ApplyAttributes(attributes)

    def ConstructLayout(self):
        caption = GetByLabel('UI/Overview/AddTab')
        self.SetCaption(caption)
        self.label = GetByLabel('UI/Overview/TypeInLabel')
        super(AddTabPopup, self).ConstructLayout()

    def AddMainContainerOld(self):
        return Container(parent=self.sr.main, align=uiconst.TOALL, padding=16)

    def AddExtra(self, parent):
        container = ContainerAutoSize(name='extra_container', parent=parent, align=uiconst.TOTOP)
        self.overview_presets_combo = self._add_presets_configurator(parent=container, name='overview_presets', title=GetByLabel('UI/Overview/Filter'), description=GetByLabel('UI/Overview/ChooseOverviewPreset'), is_for_brackets=False)
        self.bracket_presets_combo = self._add_presets_configurator(parent=container, name='bracket_presets', title=GetByLabel('UI/Overview/BracketFilter'), description=GetByLabel('UI/Overview/ChooseBracketPreset'), is_for_brackets=True)
        self.new_window_checkbox = Checkbox(parent=container, padding=(0, 8, 0, 8), text=GetByLabel('UI/Overview/InNewWindow'))

    def _add_presets_configurator(self, parent, name, title, description, is_for_brackets):
        container = self._add_combo_container(parent, name)
        self._add_combo_title(container, name, title, description)
        combo = self._add_combo_dropdown(container, name, is_for_brackets)
        return combo

    def _add_combo_container(self, parent, name):
        return ContainerAutoSize(name=name + '_container', parent=parent, align=uiconst.TOTOP, padBottom=8)

    def _add_combo_title(self, parent, name, title, description):
        title_container = Container(name=name + 'title_container', parent=parent, align=uiconst.TOTOP, padding=(0, 16, 0, 8), height=16)
        EveLabelMedium(name=name + '_label', parent=title_container, align=uiconst.TOLEFT, text=title)
        icon_container = ContainerAutoSize(name=name + '_icon_container', parent=title_container, align=uiconst.TOLEFT, padLeft=8)
        MoreInfoIcon(name=name + '_description_icon', parent=icon_container, align=uiconst.CENTER, hint=description)

    def _add_combo_dropdown(self, parent, name, is_for_brackets):
        container = ContainerAutoSize(name=name + '_combo_container', parent=parent, align=uiconst.TOTOP)
        options = []
        if is_for_brackets:
            options += [(GetByLabel('UI/Overview/ShowAllBrackets'), overviewSettingsConst.BRACKET_FILTER_SHOWALL)]
            selected = overviewSettingsConst.BRACKET_FILTER_SHOWALL
        else:
            selected = overviewUtil.GetDefaultFiltersSorted()[0]
        options += overviewUtil.GetFilterComboOptions()
        combo = Combo(name=name + '_combo', parent=container, align=uiconst.TOTOP, options=options, select=selected)
        return combo

    def Confirm(self, *args):
        if not hasattr(self, 'newName'):
            return
        new_name = self.newName.GetValue()
        error = self.funcValidator(new_name)
        new_overview_preset = self.overview_presets_combo.GetValue()
        new_bracket_preset = self.bracket_presets_combo.GetValue()
        in_new_window = self.new_window_checkbox.GetValue()
        if error:
            eve.Message('CustomInfo', {'info': error})
        else:
            self.result = (new_name,
             new_overview_preset,
             new_bracket_preset,
             in_new_window)
            self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = (None, None, None)
        self.SetModalResult(0)
