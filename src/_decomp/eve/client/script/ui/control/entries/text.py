#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\text.py
import blue
from carbon.common.script.util import commonutils
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.util.stringManip import GetAsUnicode
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.util import uix
from eve.client.script.ui.util.linkUtil import IsLink
from eveservices.menu import GetMenuService
from menu import MenuLabel

class Text(SE_BaseClassCore):
    __guid__ = 'listentry.Text'
    __params__ = ['text']
    default_showHilite = False

    def Startup(self, *args):
        self.sr.text = self.sr.label = self._ConstructLabel()
        self.sr.infoicon = InfoIcon(left=2, parent=self, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.sr.icon = Icon(parent=self, pos=(1, 2, 24, 24), align=uiconst.TOPLEFT, idx=0, ignoreSize=True)

    def _ConstructLabel(self):
        return EveLabelMedium(text='', parent=self, left=8, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT)

    def Load(self, node):
        self.sr.node = node
        data = node
        if node.tabs:
            self.sr.text.tabs = node.tabs
        if node.tabMargin:
            self.sr.text.SetTabMargin(node.tabMargin)
        self.sr.text.text = unicode(data.text)
        self.typeID = data.Get('typeID', None)
        self.itemID = data.Get('itemID', None)
        self.isStation = data.Get('isStation', 0)
        if node.Get('hint', None):
            self.hint = node.hint
        if self.typeID or self.isStation and self.itemID:
            self.sr.infoicon.state = uiconst.UI_NORMAL
        else:
            self.sr.infoicon.state = uiconst.UI_HIDDEN
        gid = node.Get('iconID', None)
        iid = node.Get('icon', None)
        if gid or iid:
            if gid:
                self.sr.icon.LoadIcon(node.iconID, ignoreSize=True)
            elif iid:
                self.sr.icon.LoadIcon(node.icon, ignoreSize=True)
            iconsize = node.Get('iconsize', 24)
            self.sr.icon.SetSize(iconsize, iconsize)
            self.sr.icon.state = uiconst.UI_NORMAL
            self.sr.text.left = self.height + 4
        else:
            self.sr.icon.state = uiconst.UI_HIDDEN
            self.sr.text.left = 8
        if IsLink(self.sr.text.text):
            self.sr.text.state = uiconst.UI_NORMAL
        else:
            self.sr.text.state = uiconst.UI_DISABLED

    def OnClick(self, *args):
        OnClick = self.sr.node.Get('OnClick', None)
        if OnClick:
            if callable(OnClick):
                OnClick()
            else:
                OnClick[0](*OnClick[1:])

    def OnDblClick(self, *args):
        if self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
        elif self.sr.node.Get('canOpen', None):
            uix.TextBox(self.sr.node.canOpen, GetAsUnicode(self.sr.node.text).replace('<t>', '<br>').replace('\r', ''), preformatted=1)

    def ShowInfo(self, *args):
        if self.sr.node.Get('isStation', 0) and self.itemID:
            stationinfo = sm.GetService('ui').GetStationStaticInfo(self.itemID)
            sm.GetService('info').ShowInfo(stationinfo.stationTypeID, self.itemID)
            return
        if self.sr.node.Get('typeID', None):
            sm.GetService('info').ShowInfo(self.sr.node.typeID, self.sr.node.Get('itemID', None))

    def GetHeight(self, *args):
        node, width = args
        iconsize = node.Get('iconsize', 24)
        node.height = max(uix.GetTextHeight(node.text, maxLines=1) + 6, iconsize)
        return node.height

    def CopyText(self):
        text = GetAsUnicode(self.sr.node.text)
        blue.pyos.SetClipboardData(commonutils.StripTags(text.replace('<t>', ' ')))

    def GetMenu(self):
        m = []
        if self.sr.node.GetMenu:
            m = self.sr.node.GetMenu()
        typeID = self.sr.node.Get('typeID', None)
        abstractinfo = self.sr.node.Get('abstractinfo', None)
        if self.sr.node.Get('isStation', 0) and self.itemID or typeID is not None:
            try:
                if self.itemID and typeID is not None:
                    m += GetMenuService().GetMenuFromItemIDTypeID(self.itemID, typeID, abstractInfo=abstractinfo)
                else:
                    hasShowInfo = False
                    for item in m:
                        if item is not None and item[0][0] == 'UI/Commands/ShowInfo':
                            hasShowInfo = True
                            break

                    if not hasShowInfo:
                        m += [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo), None]
            except:
                pass

        return m + [(MenuLabel('UI/Common/Copy'), self.CopyText)]

    @classmethod
    def GetCopyData(cls, node):
        return node.text
