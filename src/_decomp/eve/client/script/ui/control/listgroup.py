#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\listgroup.py
import logging
import eveicon
import localization
import telemetry
from carbon.common.script.util.commonutils import GetAttrs
from carbonui import uiconst
from carbonui.control.scrollentries import SE_ListGroupCore
from carbonui.window.widget import WidgetWindow
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.util import utilWindows
from menu import MenuLabel
log = logging.getLogger(__name__)

class VirtualGroupWindow(WidgetWindow):
    __guid__ = 'form.VirtualGroupWindow'

    def ApplyAttributes(self, attributes):
        super(VirtualGroupWindow, self).ApplyAttributes(attributes)
        node = attributes.node
        caption = attributes.caption or 'List window'
        self.SetScope(uiconst.SCOPE_INGAME)
        self.SetMinSize((200, 200))
        self.sr.data = node.copy()
        main = self.GetChild('main')
        main.Flush()
        icon = getattr(node, 'showicon', '')
        if icon == 'hide':
            self.icon = 'res:/ui/Texture/WindowIcons/smallfolder.png'
        elif isinstance(icon, eveicon.IconData):
            self.icon = icon
        elif icon and icon[0] == '_':
            self.icon = icon[1:]
        else:
            self.icon = 'res:/ui/Texture/WindowIcons/smallfolder.png'
        self.SetCaption(caption)
        self.sr.scroll = Scroll(name='scroll', parent=main, align=uiconst.TOALL)
        self.sr.scroll.sr.iconMargin = getattr(self.sr.data, 'iconMargin', 0)
        ignoreTabTrimming = GetAttrs(node, 'scroll', 'sr', 'ignoreTabTrimming') or 0
        self.sr.scroll.sr.ignoreTabTrimming = ignoreTabTrimming
        minColumnWidth = GetAttrs(node, 'scroll', 'sr', 'minColumnWidth') or {}
        self.sr.scroll.sr.minColumnWidth = minColumnWidth
        self.sr.scroll.sr.content.OnDropData = self.OnDropData
        sublevel = node.Get('sublevel', 0)
        self.sr.scroll.sr.sublevelCorrection = sublevel + 1

    def _OnClose(self, *args):
        self.sr.data = None

    def LoadContent(self, newNode = None, newCaption = None):
        if not self or self.destroyed:
            return
        if newNode:
            self.sr.data = newNode.Copy()
        if newCaption:
            self.SetCaption(newCaption)
        if self.sr.data.GetSubContent:
            content = self.sr.data.GetSubContent(self.sr.data, 1)
        else:
            raise RuntimeError('LoadContent: WTF')
        if self.sr.data.scroll.sr.id:
            self.sr.scroll.sr.id = '%s_%s' % (self.sr.data.scroll.sr.id, self.sr.data.id)
        self.sr.scroll.sr.fixedColumns = self.sr.data.scroll.sr.fixedColumns.copy()
        self.sr.scroll.Load(contentList=content, headers=self.sr.data.scroll.GetColumns(), fixedEntryHeight=self.sr.data.scroll.sr.fixedEntryHeight, scrolltotop=0)

    def OnDropData(self, dragObj, nodes):
        if getattr(self.sr.data, 'DropData', None):
            self.sr.data.DropData(self.sr.data.id, nodes)
            return
        ids = []
        myListGroupID = self.sr.data.id
        for node in nodes:
            guid = getattr(node, '__guid__', None)
            if guid not in self.sr.data.get('allowGuids', []):
                log.warning('dropnode.__guid__ has to be listed in group.node.allowGuids %s %s', guid, getattr(self.sr.data, 'allowGuids', []))
                continue
            if not getattr(node, 'itemID', None):
                log.warning('dropitem data has to have itemID')
                continue
            currentListGroupID = getattr(node, 'listGroupID', None)
            ids.append((node.itemID, currentListGroupID, myListGroupID))

        for itemID, currentListGroupID, myListGroupID in ids:
            if currentListGroupID and itemID:
                uicore.registry.RemoveFromListGroup(currentListGroupID, itemID)
            uicore.registry.AddToListGroup(myListGroupID, itemID)

        uicore.registry.ReloadGroupWindow(myListGroupID)
        if getattr(self.sr.data, 'RefreshScroll', None):
            self.sr.data.RefreshScroll()


class ListGroup(SE_ListGroupCore):
    __guid__ = 'listentry.Group'
    default_iconSize = 16

    @telemetry.ZONE_METHOD
    def Startup(self, *etc):
        self._ConstructExpander()
        self._ConstructIcon()
        self._ConstructLabel()
        self._ConstructFill()
        Container(parent=self, name='mainLinePar', align=uiconst.TOALL, idx=0, pos=(0, 0, 0, 0), state=uiconst.UI_DISABLED)

    def _ConstructExpander(self):
        self.sr.expanderParent = Container(name='expanderParent', parent=self, pos=(4, 0, 16, 16), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=16)
        self.sr.expander = GlowSprite(parent=self.sr.expanderParent, pos=(0, 0, 16, 16), name='expander', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/expanderDown.png', align=uiconst.CENTER)
        self.sr.expander.OnClick = self.Toggle

    def _ConstructIcon(self):
        self.sr.icon = Icon(parent=self, pos=(4, 0, 16, 16), name='icon', state=uiconst.UI_DISABLED, icon=eveicon.folder, align=uiconst.CENTERLEFT, ignoreSize=True)

    def _ConstructLabel(self):
        self.sr.labelClipper = Container(parent=self, name='labelClipper', align=uiconst.TOALL, clipChildren=1)
        self.sr.labelClipper.OnClick = self.OnClick
        self.sr.labelClipper.GetMenu = self.GetMenu
        self.sr.label = EveLabelMedium(text='', parent=self.sr.labelClipper, left=5, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT, autoFadeSides=16)

    def _ConstructFill(self):
        if self.sr.node.sublevel > 0:
            self.sr.fill = None
        else:
            self.sr.fill = Fill(bgParent=self, opacity=0.05)

    def GetHeight(self, *args):
        node, _ = args
        height = max(24, uicore.font.GetTextHeight(node.label, maxLines=1))
        node.height = height
        return node.height

    @telemetry.ZONE_METHOD
    def Load(self, node):
        self.sr.node = node
        self.sr.id = node.id
        self.sr.subitems = node.get('subitems', []) or node.get('groupItems', [])
        self.UpdateLabel()
        self.hint = node.Get('hint', '')
        if node.Get('rightAlignExpander', False):
            self.sr.expanderParent.align = uiconst.TORIGHT
        else:
            self.sr.expanderParent.left = self._GetSublevelLeft() + 4
            self.sr.expanderParent.align = uiconst.CENTERLEFT
        self.sr.node.selectable = node.Get('selectGroup', 0)
        if node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.sr.expanderParent.display = not bool(node.Get('hideExpander', 0))
        if self.sr.fill:
            self.sr.fill.state = [uiconst.UI_DISABLED, uiconst.UI_HIDDEN][node.Get('hideFill', False)]
        if self.sr.expander.state == uiconst.UI_HIDDEN:
            self.sr.labelClipper.width = 0
        for k, v in node.Get('labelstyle', {}).iteritems():
            setattr(self.sr.label, k, v)

        self._LoadIconState()
        self._LoadIconLeft()
        self._LoadLabelLeft()
        if node.panel is not self or self is None:
            return
        self.ShowOpenState(node.get('forceOpen', False) or uicore.registry.GetListGroupOpenState(self.sr.id, default=node.Get('openByDefault', False)))
        self.RefreshGroupWindow(0)

    def _GetSublevel(self):
        sublevelCorrection = self.sr.node.scroll.sr.get('sublevelCorrection', 0) if self.sr.node.scroll else 0
        sublevel = max(0, self.sr.node.Get('sublevel', 0) - sublevelCorrection)
        return sublevel

    def _GetSublevelLeft(self):
        return 16 * self._GetSublevel()

    def _LoadIconState(self):
        icon = self.sr.node.Get('showicon', '')
        iconID = self.sr.node.Get('iconID', None)
        iconSize = self.sr.node.Get('iconSize', self.default_iconSize)
        iconColor = self.sr.node.Get('iconColor', None)
        if iconID:
            self.sr.icon.LoadIcon(iconID, ignoreSize=True)
            self.sr.icon.SetSize(iconSize, iconSize)
            self.sr.icon.state = uiconst.UI_DISABLED
        elif isinstance(icon, eveicon.IconData):
            self.sr.icon.texturePath = icon
            self.sr.icon.SetSize(iconSize, iconSize)
            self.sr.icon.state = uiconst.UI_DISABLED
        elif icon == 'hide':
            self.sr.icon.state = uiconst.UI_HIDDEN
        elif icon and icon[0] == '_':
            self.sr.icon.LoadIcon(icon[1:], ignoreSize=True)
            self.sr.icon.SetSize(iconSize, iconSize)
            self.sr.icon.state = uiconst.UI_DISABLED
        else:
            if icon:
                self.sr.icon.LoadIcon(icon, ignoreSize=True)
                self.sr.icon.SetSize(iconSize, iconSize)
            else:
                self.sr.icon.LoadIcon(eveicon.folder.resolve(iconSize), ignoreSize=True)
                self.sr.icon.SetSize(iconSize, iconSize)
            self.sr.icon.state = uiconst.UI_DISABLED
            self.sr.icon.width = iconSize
        if iconColor is not None:
            self.sr.icon.SetRGBA(*iconColor)

    def _LoadIconLeft(self):
        if self._IsExpanderLeft():
            self.sr.icon.left = self._GetSublevelLeft() + 22
        else:
            self.sr.icon.left = self._GetSublevelLeft() + 4

    def _LoadLabelLeft(self):
        if self.sr.icon.display:
            self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4
        elif self._IsExpanderLeft():
            self.sr.label.left = self.sr.icon.left
        else:
            self.sr.label.left = self.sr.icon.left + 2

    def _IsExpanderLeft(self):
        return self.sr.expanderParent.display and self.sr.expanderParent.align == uiconst.CENTERLEFT

    def OnDblClick(self, *args):
        if self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
            return
        if self.sr.node.Get('BlockOpenWindow', 0):
            return
        self.RefreshGroupWindow(create=1)

    def RefreshGroupWindow(self, create):
        if self.sr.node:
            if create:
                wnd = VirtualGroupWindow.Open(windowID=unicode(self.sr.node.id), node=self.sr.node, caption=self.sr.node.label.replace('<t>', '-'))
            else:
                wnd = VirtualGroupWindow.GetIfOpen(windowID=unicode(self.sr.node.id))
            if wnd:
                wnd.LoadContent(self.sr.node, newCaption=self.sr.node.label)
                if create:
                    wnd.Maximize()
                if not self or self.destroyed:
                    return
                node = self.sr.node
                if node.open:
                    self.Toggle()

    def GetNoItemEntry(self):
        return GetFromClass(Generic, {'label': localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem'),
         'sublevel': self.sr.node.Get('sublevel', 0) + 1})

    def GetMenu(self):
        m = []
        if not self.sr.node.Get('BlockOpenWindow', 0):
            wnd = VirtualGroupWindow.GetIfOpen(windowID=unicode(self.sr.node.id))
            if wnd:
                m = [(MenuLabel('/Carbon/UI/Controls/ScrollEntries/ShowWindow'), self.RefreshGroupWindow, (1,))]
            else:
                m = [(MenuLabel('/Carbon/UI/Controls/ScrollEntries/OpenGroupWindow'), self.RefreshGroupWindow, (1,))]
        node = self.sr.node
        expandable = node.Get('expandable', 1)
        if expandable:
            if not node.open:
                m += [(MenuLabel('UI/Common/Expand'), self.Toggle, ())]
            else:
                m += [(MenuLabel('UI/Common/Collapse'), self.Toggle, ())]
        if node.Get('state', None) != 'locked':
            m += [(MenuLabel('/Carbon/UI/Controls/ScrollEntries/ChangeLabel'), self.ChangeLabel)]
            m += [(MenuLabel('/Carbon/UI/Controls/ScrollEntries/DeleteFolder'), self.DeleteFolder)]
        if node.Get('MenuFunction', None):
            cm = node.MenuFunction(node)
            m += cm
        return m

    def GetNewGroupName(self):
        return utilWindows.NamePopup(localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/TypeInNewName'), localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/TypeInNewFolderName'))

    def CloseWindow(self, windowID):
        VirtualGroupWindow.CloseIfOpen(windowID=windowID)

    def OnDragEnter(self, dragObj, drag, *args):
        if self.sr.node.Get('DragEnterCallback', None):
            self.sr.node.DragEnterCallback(self, drag)
        elif drag and getattr(drag[0], '__guid__', None) in self.sr.node.Get('allowGuids', []) + ['xtriui.DragIcon']:
            self.Select()

    def OnDragExit(self, dragObj, drag, *args):
        if not self.sr.node.selected:
            self.Deselect()

    def ShowOpenState(self, open_):
        if self.sr.expander:
            if open_:
                self.sr.expander.LoadIcon('res:/UI/Texture/Icons/38_16_229.png')
            else:
                self.sr.expander.LoadIcon('res:/UI/Texture/Icons/38_16_228.png')

    def OnMouseEnter(self, *args):
        SE_ListGroupCore.OnMouseEnter(self, *args)
        self.sr.expander.OnMouseEnter()

    def OnMouseExit(self, *args):
        SE_ListGroupCore.OnMouseExit(self, *args)
        self.sr.expander.OnMouseExit()

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
