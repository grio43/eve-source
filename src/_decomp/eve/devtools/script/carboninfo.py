#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\carboninfo.py
import blue
import localization
from carbonui.button.group import ButtonGroup
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.control.window import Window
from carbonui import const as uiconst
from cherrypy.lib.cptools import log_traceback
from eve.client.script.ui.control.eveScroll import Scroll
import carbonversion

class CarbonInfo(Window):
    __guid__ = 'form.CarbonInfo'
    default_caption = 'Carbon Engine'
    default_minSize = (400, 520)
    default_windowID = 'CarbonInfo'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.carbon_version = carbonversion.get_carbon_version()
        self.SetCaption('CARBON Engine {}'.format(self.carbon_version.get_version()))
        self.SetCaption(localization.GetByLabel('UI/CarbonInfoWindow/CarbonEngineVersion', engineVersion=self.carbon_version.get_version()))
        self.add_copy_button()
        self.add_scroll()

    def add_scroll(self):
        self.scroll = Scroll(parent=self.sr.main, align=uiconst.TOALL, padding=(5, 5, 5, 5), height=30)
        content_list = []
        for library in sorted(self.carbon_version.get_libraries()):
            label = '%s<t>%s<t>%s' % (library, self.carbon_version.get_library_version(library), self.carbon_version.get_library_tag(library))
            entry = ScrollEntryNode(id=library, name=library, label=label)
            content_list.append(entry)

        self.scroll.Load(contentList=content_list, headers=[localization.GetByLabel('UI/CarbonInfoWindow/Library'), localization.GetByLabel('UI/CarbonInfoWindow/Version'), localization.GetByLabel('UI/CarbonInfoWindow/FullTag')])

    def add_copy_button(self):
        btns = ((localization.GetByLabel('UI/Generic/Copy'), self.copy_to_clipboard, ()),)
        ButtonGroup(parent=self.sr.main, btns=btns)

    def copy_to_clipboard(self, *args):
        lines = ['CARBON ENGINE: %s\n' % self.carbon_version.get_version()]
        for library in sorted(self.carbon_version.get_libraries()):
            lines.append('%s\t%s\t%s' % (library, self.carbon_version.get_library_version(library), self.carbon_version.get_library_tag(library)))

        blue.pyos.SetClipboardData('\n'.join(lines))
