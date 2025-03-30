#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_typebrowser.py
import blue
import evetypes
import uthread
import inventorycommon.typeHelpers
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.util import uix
from eve.client.script.ui.control import eveScroll
from carbonui.control.tabGroup import TabGroup
from eve.common.lib import appConst as const
from eve.common.script.util.eveFormat import FmtISK
from fsdBuiltData.common.graphicIDs import GetGraphic, GetGraphicFile

class TypeDBEntry(Generic):
    __guid__ = 'listentry.TypeDBEntry'

    def GetMenu(self, *args):
        if isinstance(self.sr.node.invtype, tuple):
            typeID = self.sr.node.invtype[0]
        else:
            typeID = self.sr.node.invtype
        groupID = evetypes.GetGroupID(typeID)
        catID = evetypes.GetCategoryIDByGroup(groupID)
        graphicID = evetypes.GetGraphicID(typeID)
        graphicFileMenu = []
        if evetypes.Exists(typeID) and evetypes.GetGraphicID(typeID) is not None:
            graphic = GetGraphic(evetypes.GetGraphicID(typeID))
            if graphic is not None:
                graphicFile = GetGraphicFile(graphic)
                graphicFileMenu = [['Copy graphicID (%s)' % graphicID, lambda *x: blue.pyos.SetClipboardData(str(graphicID)), ()], ['Copy graphicFile (%s)' % graphicFile, lambda *x: blue.pyos.SetClipboardData(graphicFile), ()]]
        averagePrice = inventorycommon.typeHelpers.GetAveragePrice(typeID)
        if averagePrice is None:
            averagePrice = 'n/a'
        else:
            averagePrice = FmtISK(averagePrice)
        menu = [['Preview', lambda *x: uthread.new(sm.StartService('preview').PreviewType, typeID), ()]]
        menu += graphicFileMenu
        menu += [['Copy typeID (%s)' % typeID, lambda *x: blue.pyos.SetClipboardData(str(typeID)), ()],
         ['Copy groupID (%s)' % groupID, lambda *x: blue.pyos.SetClipboardData(str(groupID)), ()],
         ['Copy categoryID (%s)' % catID, lambda *x: blue.pyos.SetClipboardData(str(catID)), ()],
         ['Average price: %s' % averagePrice, lambda *x: blue.pyos.SetClipboardData(averagePrice), ()],
         ['View market details', lambda *x: uthread.new(sm.StartService('marketutils').ShowMarketDetails, typeID, None), ()],
         None]
        menu += sm.GetService('menu').GetGMTypeMenu(typeID)
        return menu


class TypeBrowser(Service):
    __guid__ = 'svc.itemdb'

    def __init__(self):
        Service.__init__(self)

    def Show(self):
        self.wnd = wnd = Window.GetIfOpen(windowID='typedb')
        if wnd:
            self.wnd.Maximize()
            return
        self.wnd = wnd = Window.Open(windowID='typedb')
        wnd.SetMinSize((420, 560))
        wnd.SetCaption('Type Browser')
        mainpar = wnd.GetChild('main')
        wnd.sr.tabs = TabGroup(name='tabsparent', parent=mainpar)
        main = Container(name='main', parent=mainpar, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        body = Container(name='body', parent=main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        wnd.sr.browser = eveScroll.Scroll(name='scroll', parent=body, pos=(0, 0, 0, 0))
        wnd.sr.browser.multiSelect = False
        wnd.sr.browser.Startup()
        searchParent = Container(name='search', parent=body, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        searchTop = Container(name='search', parent=searchParent, height=32, align=uiconst.TOTOP)
        btn = Button(parent=searchTop, label='Search', func=self.Search, align=uiconst.TORIGHT)
        wnd.sr.input = SingleLineEditText(name='Search', parent=searchTop, align=uiconst.TOALL, width=0, padRight=4)
        Container(name='div', parent=searchParent, height=5, align=uiconst.TOTOP)
        wnd.sr.input.OnReturn = self.Search
        wnd.sr.scroll = eveScroll.Scroll(parent=searchParent)
        wnd.sr.scroll.multiSelect = False
        wnd.sr.tabs.Startup([['Browse',
          wnd.sr.browser,
          self,
          0], ['Search',
          searchParent,
          self,
          1]], 'typebrowsertabs')
        self.Search()
        stuff = self.GetContent(None, False)
        wnd.sr.browser.Load(contentList=stuff, headers=['Name', 'typeID'])
        wnd.sr.browser.Sort('Name')

    def GetContent(self, node, newitems = 0):
        rows = []
        if node is None:
            for categoryID in evetypes.IterateCategories():
                rows.append((categoryID, evetypes.GetCategoryNameByCategory(categoryID)))

            level = 0
        elif node.sublevel == 0:
            for groupID in evetypes.GetGroupIDsByCategory(node.id[1]):
                rows.append((groupID, evetypes.GetGroupNameByGroup(groupID)))

            level = 1
        else:
            for typeID in evetypes.GetTypeIDsByGroup(node.id[1]):
                rows.append((typeID, evetypes.GetName(typeID)))

            level = 2
        stuff = []
        if level != 2:
            rows = sorted(rows, key=lambda row: row[1])
            for row in rows:
                stuff.append(GetFromClass(ListGroup, {'GetSubContent': self.GetContent,
                 'MenuFunction': self.Menu,
                 'label': row[1],
                 'id': (row[1], row[0]),
                 'groupItems': [],
                 'showlen': False,
                 'sublevel': level,
                 'state': 'locked',
                 'selected': 0,
                 'hideExpander': True,
                 'BlockOpenWindow': 1,
                 'hideFill': True}))

        else:
            for row in rows:
                stuff.append(GetFromClass(TypeDBEntry, {'sublevel': 2,
                 'label': '%s<t>%d' % (row[1], row[0]),
                 'invtype': row,
                 'showinfo': 1,
                 'typeID': row[0]}))

        return stuff

    def Menu(self, node, *args):
        ids = []
        if node.sublevel == 0:
            categoryID = node.id[1]
            for typeID in evetypes.GetTypeIDsByCategory(categoryID):
                ids.append(typeID)

        else:
            groupID = node.id[1]
            for typeID in evetypes.GetTypeIDsByGroup(groupID):
                ids.append(typeID)

        def _crea(listOftypeIDs, what = '/createitem', qty = 1, maxValue = 2147483647):
            if uicore.uilib.Key(uiconst.VK_SHIFT):
                result = uix.QtyPopup(maxvalue=maxValue, minvalue=1, caption=what, label=u'Quantity', hint='')
                if result:
                    qty = result['qty']
                else:
                    return
            for typeID in listOftypeIDs:
                sm.StartService('slash').SlashCmd('/createitem %d %d' % (typeID, qty))

        def _load(listOftypeIDs, what = '/load', qty = 1, maxValue = 2147483647):
            if uicore.uilib.Key(uiconst.VK_SHIFT):
                result = uix.QtyPopup(maxvalue=maxValue, minvalue=1, caption=what, label=u'Quantity', hint='')
                if result:
                    qty = result['qty']
                else:
                    return
            for typeID in listOftypeIDs:
                sm.StartService('slash').SlashCmd('/load me %d %d' % (typeID, qty))

        l = [None, ('WM: create all of these', lambda *x: _crea(ids)), ('GM: load me all of these', lambda *x: _load(ids))]
        return l

    def Load(self, *args):
        pass

    def Search(self, *args):
        scroll = self.wnd.sr.scroll
        scroll.sr.id = 'searchreturns'
        search = self.wnd.sr.input.GetValue().lower()
        if not search:
            scroll.Load(contentList=[GetFromClass(Generic, {'label': u'Type in search string and press "Search"'})])
            return
        scroll.Load(contentList=[])
        scroll.ShowHint(u'Searching')
        matches = sm.GetService('slash').MatchTypes(search, smart=False)
        if matches:
            matches.sort()
            stuff = []
            for name, typeID in matches:
                stuff.append(GetFromClass(TypeDBEntry, {'label': '%d<t>%s' % (typeID, name),
                 'invtype': typeID,
                 'showinfo': 1,
                 'typeID': typeID}))
                blue.pyos.BeNice()

        else:
            stuff = [GetFromClass(Generic, {'label': u'Nothing found with "%(search)s" in its name' % {'search': search}})]
        scroll.ShowHint()
        scroll.Load(contentList=stuff, headers=['typeID', 'Name'])

    def Hide(self):
        if self.wnd:
            self.wnd.Close()
            self.wnd = None
