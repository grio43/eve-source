#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\contextMenu\contextMenu.py
import logging
import types
import weakref
from collections import defaultdict
import log
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.control.contextMenu.contextMenuMixin import ContextMenuMixin
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples
from carbonui.control.contextMenu.menuEntryData import MenuEntryDataCaption, MenuEntryDataLabel, MenuEntryDataCheckbox, MenuEntryDataRadioButton, MenuEntryDataSlider
from carbonui.control.contextMenu.menuEntryView import MenuEntryView, MenuEntryViewCaption, MenuEntryViewLabel, MenuEntryViewCheckbox, MenuEntryViewRadioButton, MenuEntryViewSlider
from carbonui.control.contextMenu.menuUtil import CloseContextMenus
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.uicore import uicore
from carbonui.util.mouseTargetObject import MouseTargetObject
from carbonui.decorative.menuUnderlay import MenuUnderlay
from uihider import CommandBlockerService
logger = logging.getLogger(__name__)

class ContextMenu(ContainerAutoSize, ContextMenuMixin):
    default_alignMode = uiconst.TOTOP
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    __notifyevents__ = ['OnMenuHighlightActivated', 'OnMenuHighlightsCleared']

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.menuData = attributes.menuData
        minWidth = attributes.minWidth
        self.entries = []
        self.entries_by_internal_name = defaultdict(list)
        self.highlights_svc = sm.GetService('uiHighlightingService')
        self.mainCont = ContainerAutoSize(parent=self, name='mainCont', align=uiconst.TOTOP, padding=8)
        self.Prepare_Background_()
        self.ConstructEntries()
        self.UpdateSize(minWidth)
        self.SetupHighlights()
        log.LogInfo('Menu.Setup Completed', id(self))
        MouseTargetObject(self)

    def UpdateSize(self, minWidth):
        if len(self.mainCont.children):
            maxChildWidth = max([ entry.GetRequiredWidth() for entry in self.entries ])
            self.width = max(maxChildWidth + 8, minWidth or 0) + self.mainCont.padLeft + self.mainCont.padRight
        else:
            self.width = 100
        self.mainCont.SetSizeAutomatically()
        self.SetSizeAutomatically()

    def ConstructEntries(self):
        entries = self.menuData.GetEntries()
        wasLine = 0
        while len(entries):
            if entries[-1] is None:
                entries.pop(-1)
            else:
                break

        for i, menuEntryData in enumerate(entries):
            if menuEntryData is None:
                if not len(self.mainCont.children) or i == len(entries) - 1 or wasLine:
                    continue
                self._ConstructLine()
                wasLine = 1
            else:
                self._ConstructMenuEntry(menuEntryData)
                wasLine = 0

    def _ConstructMenuEntry(self, menuEntryData):
        menuEntryViewClass = self._GetMenuEntryViewClass(menuEntryData)
        menuEntry = menuEntryViewClass(name=u'context_menu_{}'.format(menuEntryData.internalName or menuEntryData.text), align=uiconst.TOTOP, state=uiconst.UI_NORMAL, parent=self.mainCont, menuEntryData=menuEntryData, iconSize=self.menuData.GetIconSize(), uniqueUiName=getattr(menuEntryData, 'uniqueUiName', None))
        self.entries.append(menuEntry)
        if menuEntryData.internalName:
            self.entries_by_internal_name[menuEntryData.internalName, menuEntryData.typeID].append(menuEntry)

    def _ConstructLine(self):
        Line(align=uiconst.TOTOP, parent=self.mainCont, opacity=0.1, padding=(0, 6, 0, 6))

    def _GetMenuEntryViewClass(self, menuEntryData):
        if menuEntryData.menuClass:
            return menuEntryData.menuClass
        elif isinstance(menuEntryData, MenuEntryDataCaption):
            return MenuEntryViewCaption
        elif isinstance(menuEntryData, MenuEntryDataLabel):
            return MenuEntryViewLabel
        elif isinstance(menuEntryData, MenuEntryDataRadioButton):
            return MenuEntryViewRadioButton
        elif isinstance(menuEntryData, MenuEntryDataCheckbox):
            return MenuEntryViewCheckbox
        elif isinstance(menuEntryData, MenuEntryDataSlider):
            return MenuEntryViewSlider
        else:
            return MenuEntryView

    def Prepare_Background_(self, *args):
        MenuUnderlay(bgParent=self)

    def _OnClose(self):
        Container._OnClose(self)
        for each in self.mainCont.children[:]:
            if hasattr(each, 'Collapse'):
                each.Collapse()

        self.menuData = None

    def SetupHighlights(self):
        for restriction, entryViews in self.entries_by_internal_name.iteritems():
            internalName, typeID = restriction
            if self.highlights_svc.is_menu_highlighted(internalName, typeID):
                for entryView in entryViews:
                    entryView.Highlight()

    def OnMenuHighlightActivated(self, menuName, menuTypeID):
        self.HighlightEntries(menuName, menuTypeID)

    def OnMenuHighlightsCleared(self):
        self.ClearHighlights()

    def HighlightEntries(self, menuName, menuTypeID):
        for restriction, entryViews in self.entries_by_internal_name.iteritems():
            if restriction == (menuName, menuTypeID):
                for entryView in entryViews:
                    entryView.Highlight()

    def ClearHighlights(self):
        for entryViews in self.entries_by_internal_name.values():
            for entryView in entryViews:
                entryView.ClearHighlight()

    def Collapse(self):
        if not self.destroyed:
            for each in self.mainCont.children:
                if hasattr(each, 'Collapse'):
                    each.Collapse()

            self.Close()


class ContextSubMenu(ContextMenu):

    def ApplyAttributes(self, attributes):
        self.parentEntry = attributes.parentEntry
        super(ContextSubMenu, self).ApplyAttributes(attributes)

    def SetSizeAutomatically(self):
        super(ContextSubMenu, self).SetSizeAutomatically()
        self._UpdatePosition()

    def _UpdatePosition(self):
        aL, aT, aW, aH = self.parentEntry.GetAbsolute()
        if aL + aW + self.width <= uicore.desktop.width:
            self.left = aL + aW + 2
        else:
            self.left = aL - self.width + -2
        self.top = max(0, min(uicore.desktop.height - self.height, aT)) - 8


def CreateMenuView(menuData, parent = None, minwidth = None):
    if menuData is None:
        return
    if not parent:
        CloseContextMenus()
    return ContextMenu(name='menuview', align=uiconst.TOPLEFT, menuData=menuData, minWidth=minwidth)


def ShowMenu(object, auxObject = None):
    command_blocker = CommandBlockerService.instance()
    if command_blocker.is_blocked(['menucore', 'menucore.expand']) and not getattr(object, 'ignore_command_blocker', False):
        logger.info('ShowMenu: Menus disabled')
        return
    CloseContextMenus()
    m = None
    menuFunc = getattr(object, 'GetMenu', None)
    if menuFunc:
        if type(menuFunc) == types.TupleType:
            func, args = menuFunc
            m = func(args)
        else:
            m = menuFunc()
    hasAuxOptions = auxObject and hasattr(auxObject, 'GetAuxiliaryMenuOptions')
    if _IsEmptyList(m):
        if hasAuxOptions:
            m = auxObject.GetAuxiliaryMenuOptions()
        else:
            logger.info('ShowMenu: No Menu!')
            return
    elif hasAuxOptions:
        m = m + auxObject.GetAuxiliaryMenuOptions()
    if getattr(object, 'showingMenu', 0):
        logger.info('ShowMenu: Already showing a menu')
        return
    object.showingMenu = 1
    uicore.contextMenuOwner = weakref.ref(object)
    try:
        menuData = CreateMenuDataFromRawTuples(m)
        if not menuData or not menuData.GetEntries():
            return
        mv = CreateMenuView(menuData=menuData, minwidth=getattr(object, 'minwidth', None))
        if mv is not None:
            object.menuObject_weakref = weakref.ref(mv)
            uicore.layer.menu.children.insert(0, mv)
            width, height = mv.GetAbsoluteSize()
            mv.left, mv.top = _GetMenuViewPosition(width, height, object)
            PlaySound(uiconst.SOUND_EXPAND)
            sm.ScatterEvent('OnMenuShown')
    finally:
        object.showingMenu = 0

    logger.info('ShowMenu finished OK')


def _IsEmptyList(m):
    if isinstance(m, MenuData):
        return False
    return not m or not filter(None, m)


def _GetMenuViewPosition(width, height, object):
    topLeft = 1
    func = getattr(object, 'GetMenuPosition', None)
    if func is not None:
        ret = func(object)
        if len(ret) == 2:
            x, y = ret
        else:
            x, y, topLeft = ret
    else:
        x, y = uicore.uilib.x + 10, uicore.uilib.y
    d = uicore.desktop
    if topLeft:
        x, y = min(d.width - width, x), min(d.height - height, y)
    else:
        x, y = min(d.width - width, x - width), min(d.height - height, y)
    return (x, y)
