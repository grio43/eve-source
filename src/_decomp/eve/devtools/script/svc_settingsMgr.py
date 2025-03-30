#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_settingsMgr.py
import os
import blue
from carbonui import fontconst
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.util.uix import HybridWnd
from eve.common.lib import appConst as const
from eveprefs import prefs

class PrefsEntry(Generic):
    __guid__ = 'listentry.PrefsEntry'

    def OnDblClick(self, *args):
        self.EditAttribute()

    def GetMenu(self):
        ret = [('Add Entry', self.AddEntry, ()), ('Modify Entry', self.EditAttribute, ()), ('Delete Entry', self.DeleteKey, ())]
        return ret

    def AddEntry(self):
        n = self.sr.node
        n.AddEntry()

    def EditAttribute(self):
        n = self.sr.node
        n.EditAttribute(n.key, n.value)

    def DeleteKey(self):
        n = self.sr.node
        n.DeleteKey(n.key)


class ValuePopup:
    __wndname__ = 'ValuePopup'

    def __init__(self, default = None, caption = None, label = None):
        if default is None:
            default = '0'
        if caption is None:
            caption = u'Type in name'
        if label is None:
            label = u'Type in name'
        format = [{'type': 'btline'},
         {'type': 'labeltext',
          'label': label,
          'text': '',
          'frame': 1,
          'labelwidth': 180},
         {'type': 'edit',
          'setvalue': '%s' % default,
          'key': 'qty',
          'label': '_hide',
          'required': 1,
          'frame': 1,
          'setfocus': 1,
          'selectall': 1},
         {'type': 'bbline'}]
        OKCANCEL = 1
        self.popup = HybridWnd(format, caption, windowID='settingsValuePopup', modal=1, buttons=OKCANCEL, location=None, minW=240, minH=80)

    def __getitem__(self, *args):
        return args

    def Wnd(self, *args):
        return self.popup


class AddPopup:
    __wndname__ = 'AddPopup'

    def __init__(self, caption = None, labeltop = None, labelbtm = None):
        if caption is None:
            caption = u'Type in name'
        if labeltop is None:
            labeltop = u'Type in name'
        if labelbtm is None:
            labelbtm = u'Type in name'
        format = [{'type': 'btline'},
         {'type': 'labeltext',
          'label': labeltop,
          'text': '',
          'frame': 1,
          'labelwidth': 180},
         {'type': 'edit',
          'setvalue': '',
          'key': 'name',
          'label': '_hide',
          'required': 1,
          'frame': 1,
          'setfocus': 1,
          'selectall': 1},
         {'type': 'labeltext',
          'label': labelbtm,
          'text': '',
          'frame': 1,
          'labelwidth': 180},
         {'type': 'edit',
          'setvalue': '',
          'key': 'value',
          'label': '_hide',
          'required': 1,
          'frame': 1,
          'setfocus': 1,
          'selectall': 1},
         {'type': 'bbline'}]
        OKCANCEL = 1
        self.popup = HybridWnd(format, caption, windowID='settingsAddPopup', modal=1, buttons=OKCANCEL, location=None, minW=240, minH=80)

    def __getitem__(self, *args):
        return args

    def Wnd(self, *args):
        return self.popup


class SettingsMgr(Window):
    __guid__ = 'form.SettingsMgr'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.prefs = prefs
        self.SetCaption('Settings Manager')
        self.SetMinSize([550, 300])
        margin = const.defaultPadding
        main = Container(name='main', parent=self.content)
        Frame(parent=main, color=(1.0, 1.0, 1.0, 0.2), idx=0)
        bottom = Container(name='btm', parent=main, height=Button.default_height + 24, align=uiconst.TOBOTTOM)
        btns = [['Refresh', self.Refresh],
         ['Add', self.AddEntry],
         ['Modify', self.EditAttribute],
         ['Delete', self.DeleteButtonClicked],
         ['Open', self.OpenPrefsFile]]
        ButtonGroup(btns=btns, parent=bottom)
        Container(parent=bottom, align=uiconst.TOLEFT, width=2)
        Container(parent=bottom, align=uiconst.TOTOP, height=margin)
        locstr = 'Current file location...'
        text = Label(text=locstr, parent=bottom, align=uiconst.TOTOP, height=18, fontsize=fontconst.EVE_SMALL_FONTSIZE, letterspace=1, linespace=9, uppercase=1, state=uiconst.UI_NORMAL)
        text.OnClick = self.OpenPrefsFolder
        text.GetMenu = self.TextMenu
        text.hint = 'The current location for the prefs.ini is:<br><br>%s<br><br><b>Click</b> to open.' % self.prefs.ini.filename
        Container(name='div', parent=main, height=0, align=uiconst.TOTOP)
        self.scroll = Scroll(parent=main)
        self.scroll.sr.id = 'PrefsScroll'
        self.Refresh()

    def Refresh(self, *args):
        contentList = []
        p = self.prefs.GetKeys()
        p.sort()
        for key in p:
            value = self.prefs.GetValue(key)
            contentList.append(GetFromClass(PrefsEntry, {'label': u'%s<t>%s' % (key, value),
             'key': key,
             'value': value,
             'AddEntry': self.AddEntry,
             'EditAttribute': self.EditAttribute,
             'DeleteKey': self.DeleteKey}))

        for key, value in sm.GetService('machoNet').GetGlobalConfig().iteritems():
            contentList.append(GetFromClass(Generic, {'label': u'zsystem.clientConfig: %s<t>%s' % (key, value)}))

        self.scroll.Load(contentList=contentList, headers=['Key', 'Value'], fixedEntryHeight=18)
        self.scroll.Sort('Key')

    def GetNode(self, *args):
        node = self.scroll.GetSelected()
        if not node:
            return (None, None)
        node = node[0]
        return (node.key, node.value)

    def AddEntry(self, *args):
        a = AddPopup(caption='Prefs.ini', labeltop='Name', labelbtm='Value')
        ret = a.Wnd()
        if ret:
            prefs.SetValue(ret['name'], ret['value'])
            self.Refresh()

    def EditAttribute(self, k = None, v = None):
        if k is None or v is None:
            k, v = self.GetNode()
            if k is None or v is None:
                return
        a = ValuePopup(default=v, caption='Prefs.ini', label="Set value for '%s'" % k)
        ret = a.Wnd()
        if ret:
            newValue = ret['qty']
            prefs.SetValue(k, newValue)
            self.Refresh()

    def DeleteButtonClicked(self, *args):
        self.DeleteKey()

    def DeleteKey(self, k = None):
        if k is None:
            k, v = self.GetNode()
            if k is None or v is None:
                return
        header = 'Delete entry?'
        question = "Are you sure you wish to <b>permanently delete</b> the '%s' entry from your prefs.ini?" % k
        if eve.Message('CustomQuestion', {'header': header,
         'question': question}, uiconst.YESNO) == uiconst.ID_YES:
            prefs.DeleteValue(k)
            self.Refresh()

    def OpenPrefsFolder(self, *args):
        blue.os.ShellExecute(os.path.dirname(self.prefs.ini.filename))

    def OpenPrefsFile(self, *args):
        blue.os.ShellExecute(self.prefs.ini.filename)

    def TextMenu(self, *args):
        m = []

        def Copy(obj):
            blue.pyos.SetClipboardData(obj)

        m.append(('Copy File Location', Copy, (self.prefs.ini.filename,)))
        m.append(('Copy Directory', Copy, (os.path.dirname(self.prefs.ini.filename),)))
        return m
