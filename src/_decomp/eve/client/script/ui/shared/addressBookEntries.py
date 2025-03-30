#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\addressBookEntries.py
import eveicon
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbonui import TextColor, uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.util import uix
import uthread
import localization
import blue
from eveservices.menu import GetMenuService
from menu import MenuLabel

class PlaceEntry(SE_BaseClassCore):
    __guid__ = 'listentry.PlaceEntry'
    __nonpersistvars__ = []
    isDragObject = True

    def Startup(self, *etc):
        self.sr.label = eveLabel.EveLabelMedium(text='', parent=self, left=6, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, idx=0, maxLines=1)
        self.sr.icon = eveIcon.Icon(icon=eveicon.location, parent=self, pos=(4, 1, 16, 16), align=uiconst.RELATIVE, ignoreSize=True, state=uiconst.UI_DISABLED)

    def Load(self, node):
        self.sr.node = node
        data = node
        sublevelCorrection = self.sr.node.scroll.sr.get('sublevelCorrection', 0)
        sublevel = max(0, data.Get('sublevel', 0) - sublevelCorrection)
        self.sr.label.left = 24 + sublevel * 16
        self.sr.icon.left = 4 + sublevel * 16
        self.sr.bm = data.bm
        self.sr.label.text = data.label
        self.id = self.sr.bm.bookmarkID
        self.groupID = self.sr.node.listGroupID
        if self.sr.node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        is_available = self.sr.node.Get('isBookmarkAvailable', True)
        alpha = 1.0 if is_available else 0.5
        if self.sr.bm.itemID and self.sr.bm.itemID == sm.GetService('starmap').GetDestination():
            color = tuple(eveColor.DESTINATION_YELLOW[:3]) + (alpha,)
            self.sr.label.SetRGBA(*color)
        elif self.sr.bm.locationID == session.solarsystemid2:
            color = tuple(eveThemeColor.THEME_FOCUS[:3]) + (alpha,)
            self.sr.label.SetRGBA(*color)
        else:
            color = TextColor.NORMAL if is_available else TextColor.SECONDARY
            self.sr.label.SetRGBA(*color)
        self.EnableDrag()
        dropDataFunc = getattr(node, 'DropData')
        if dropDataFunc is not None:
            self.OnDropData = dropDataFunc
        if getattr(node, 'isGroupPersonal', None) is not None:
            if node.isGroupPersonal:
                texturePath = eveicon.location
            else:
                texturePath = eveicon.shared_location
            self.sr.icon.texturePath = texturePath

    def GetHeight(_self, *args):
        node, width = args
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 4
        return node.height

    def OnMouseHover(self, *args):
        uthread.new(self.SetHint)

    def SetHint(self, *args):
        if not (self.sr and self.sr.node):
            return
        bookmark = self.sr.node.bm
        hint = self.sr.node.hint
        isBookmarkAvailable = self.sr.node.Get('isBookmarkAvailable', True)
        destination = sm.GetService('starmap').GetDestination()
        if destination is not None and destination == bookmark.itemID:
            hint = localization.GetByLabel('UI/PeopleAndPlaces/BookmarkHintCurrent', hintText=hint)
        elif not isBookmarkAvailable:
            hint = localization.GetByLabel('UI/AclBookmarks/BookmarkHintNotYetAvailable', hintText=hint)
        else:
            hint = localization.GetByLabel('UI/PeopleAndPlaces/BookmarkHint', hintText=hint)
        self.hint = hint

    def OnDblClick(self, *args):
        sm.GetService('addressbook').EditBookmark(self.sr.bm)

    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        eve.Message('ListEntryClick')
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(const.typeBookmark, self.sr.bm.bookmarkID)

    def GetDragData(self, *args):
        ret = []
        for each in self.sr.node.scroll.GetSelectedNodes(self.sr.node):
            if not hasattr(each, 'itemID'):
                continue
            if isinstance(each.itemID, tuple):
                self.DisableDrag()
                eve.Message('CantTradeMissionBookmarks')
                return []
            ret.append(each)

        return ret

    def GetMenu(self):
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        multi = len(selected) > 1
        m = []
        bmIDs = [ entry.bm.bookmarkID for entry in selected if entry.bm ]
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            if len(bmIDs) > 10:
                text = MenuLabel('UI/PeopleAndPlaces/BookmarkIDTooMany')
            else:
                idString = bmIDs
                text = MenuLabel('UI/PeopleAndPlaces/BookmarkIDs', {'bookmarkIDs': idString})
            m += [(text, self.CopyItemIDToClipboard, (bmIDs,)), None]
            m.append(None)
        eve.Message('ListEntryClick')
        if not multi:
            m += GetMenuService().BookmarkMenu(selected[0].bm)
        elif not all((isinstance(bmID, tuple) for bmID in bmIDs)):
            m.append((MenuLabel('UI/Inflight/RemoveBookmark'), self.Delete, (bmIDs,)))
        if self.sr.node.Get('GetMenu', None) is not None:
            m += self.sr.node.GetMenu(self.sr.node)
        return m

    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))

    def Approach(self, *args):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp:
            bp.CmdGotoBookmark(self.sr.bm.bookmarkID)

    def WarpTo(self, *args):
        sm.GetService('michelle').CmdWarpToStuff('bookmark', self.sr.bm.bookmarkID)

    def Delete(self, bmIDs = None):
        ids = bmIDs or [ entry.bm.bookmarkID for entry in self.sr.node.scroll.GetSelected() ]
        if ids:
            sm.GetService('addressbook').DeleteBookmarks(ids)

    def OnMouseDown(self, *args):
        bookMarkInfo = self.sr.bm
        GetMenuService().TryExpandActionMenu(itemID=bookMarkInfo.itemID, clickedObject=self, bookmarkInfo=bookMarkInfo)

    def GetRadialMenuIndicator(self, create = True, *args):
        indicator = getattr(self, 'radialMenuIndicator', None)
        if indicator and not indicator.destroyed:
            return indicator
        if not create:
            return
        self.radialMenuIndicator = Fill(bgParent=self, color=(1, 1, 1, 0.1), name='radialMenuIndicator')
        return self.radialMenuIndicator

    def ShowRadialMenuIndicator(self, slimItem, *args):
        indicator = self.GetRadialMenuIndicator(create=True)
        indicator.display = True

    def HideRadialMenuIndicator(self, slimItem, *args):
        indicator = self.GetRadialMenuIndicator(create=False)
        if indicator:
            indicator.display = False

    @classmethod
    def GetCopyData(cls, node):
        return node.label

    def OnColorThemeChanged(self):
        super(PlaceEntry, self).OnColorThemeChanged()
        if self.sr.node:
            self.Load(self.sr.node)
