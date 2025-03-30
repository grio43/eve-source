#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\SideNavigation.py
import carbonui
import eveicon
from carbonui.control.sideNavigation import SideNavigation, SideNavigationSplitView
from carbonui import uiconst, Align, TextColor
from carbonui.primitives.fill import Fill
from carbonui.services.setting import CharSettingBool
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample
ID_1 = 1
ID_2 = 2
ID_3 = 3
is_expanded_setting = CharSettingBool('SideNavigationIsExpanded', True)

class Sample1(Sample):
    name = 'Basic Side Navigation'
    description = ''

    def construct_sample(self, parent):
        split_view = SideNavigationSplitView(parent=parent, align=uiconst.TOPLEFT, width=500, height=300, is_always_expanded_setting=is_expanded_setting, expanded_panel_width=200)
        header = carbonui.TextHeader(parent=split_view.content, align=Align.CENTER, color=TextColor.HIGHLIGHT)
        Fill(parent=split_view.content, color=eveColor.MATTE_BLACK, opacity=0.8)
        side_navigation = SideNavigation(parent=split_view.panel, is_expanded_func=split_view.is_expanded, is_always_expanded_setting=is_expanded_setting)
        split_view.on_expanded_changed.connect(side_navigation.on_expanded_changed)
        side_navigation.add_header('First section')
        side_navigation.add_entry(ID_1, 'Entry 1', lambda *args: on_entry_clicked(ID_1), eveicon.copy)
        side_navigation.add_entry(ID_2, 'Entry 2', lambda *args: on_entry_clicked(ID_2), eveicon.pause)
        side_navigation.add_header('Second section')
        side_navigation.add_entry(ID_3, 'Entry 3', lambda *args: on_entry_clicked(ID_3), eveicon.skill_book)

        def on_entry_clicked(entry_id):
            side_navigation.set_entry_selected(entry_id)
            header.text = 'Entry {} selected'.format(entry_id)
