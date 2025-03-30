#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\generic.py
import evetypes
import utillib
from carbonui import fontconst, uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetAttrs
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.util import uix
from eve.common.script.util.industryCommon import IsBlueprintCategory
from eveservices.menu import GetMenuService
events = ('OnClick', 'OnMouseDown', 'OnMouseUp', 'OnDblClick', 'OnMouseHover')

class Generic(SE_BaseClassCore):
    __guid__ = 'listentry.Generic'
    __params__ = ['label']

    def _OnClose(self):
        for eventName in events:
            setattr(self.sr, eventName, None)

        SE_BaseClassCore._OnClose(self)

    def Startup(self, *args):
        self.sr.label = EveLabelMedium(name='entryLabel', text='', parent=self, left=self.labelLeftDefault, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT)
        for eventName in events:
            setattr(self.sr, eventName, None)

        self.sr.infoicon = None

    def Load(self, node):
        self.sr.node = node
        data = node
        self.UpdateHint()
        self.confirmOnDblClick = data.Get('confirmOnDblClick', 0)
        self.typeID = data.Get('typeID', None)
        self.itemID = data.Get('itemID', None)
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        if node.showinfo and node.typeID:
            if not self.sr.infoicon:
                self.sr.infoicon = InfoIcon(left=1, parent=self, idx=0, align=uiconst.CENTERRIGHT)
                self.sr.infoicon.OnClick = self.ShowInfo
            self.sr.infoicon.state = uiconst.UI_NORMAL
        elif self.sr.infoicon:
            self.sr.infoicon.state = uiconst.UI_HIDDEN
        for eventName in events:
            if data.Get(eventName, None):
                setattr(self.sr, eventName, data.Get(eventName, None))

        preAutoUpdateFlag = self.sr.label.autoUpdate
        self.sr.label.autoUpdate = False
        sublevelCorrection = self.sr.node.scroll.sr.get('sublevelCorrection', 0) if self.sr.node.scroll else 0
        sublevel = max(0, data.Get('sublevel', 0) - sublevelCorrection)
        self.sr.label.maxLines = data.Get('maxLines', 1)
        self.sr.label.left = self.labelLeftDefault + 16 * sublevel
        self.sr.label.fontsize = data.Get('fontsize', fontconst.EVE_MEDIUM_FONTSIZE)
        self.sr.label.letterspace = data.Get('hspace', 0)
        self.sr.label.SetTextColor(data.Get('fontColor', EveLabelMedium.default_color))
        self.sr.label.text = self._GetText()
        self.sr.label.Update()
        self.sr.label.SetState(data.Get('labelState', uiconst.UI_DISABLED))
        self.sr.label.maxWidth = data.Get('labelMaxWidth', None)
        self.sr.label.autoUpdate = preAutoUpdateFlag

    def _GetText(self):
        return self.sr.node.label

    def UpdateHint(self):
        data = self.sr.node
        hint = data.hint
        if hint is not None:
            self.hint = hint

    def GetHeight(self, *args):
        node, width = args
        if node.vspace is not None:
            node.height = uix.GetTextHeight(node.label, maxLines=node.maxLines) + node.vspace
        else:
            node.height = uix.GetTextHeight(node.label, maxLines=node.maxLines, width=node.labelMaxWidth) + 4
        return node.height

    def OnMouseHover(self, *args):
        if self.sr.node and self.sr.node.Get('OnMouseHover', None):
            self.sr.node.OnMouseHover(self)

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        if self.sr.node:
            eve.Message('ListEntryEnter')
            if self.sr.node.Get('OnMouseEnter', None):
                self.sr.node.OnMouseEnter(self)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        if self.sr.node:
            if self.sr.node.Get('OnMouseExit', None):
                self.sr.node.OnMouseExit(self)

    def OnClick(self, *args):
        if GetAttrs(self, 'sr', 'node'):
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if not self or self.destroyed:
                return
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)

    def OnDblClick(self, *args):
        if self.sr.node:
            self.sr.node.scroll.SelectNode(self.sr.node)
            if self.sr.node.Get('OnDblClick', None):
                if isinstance(self.sr.node.OnDblClick, tuple):
                    func = self.sr.node.OnDblClick[0]
                    func(self, *self.sr.node.OnDblClick[1:])
                else:
                    self.sr.node.OnDblClick(self)
            elif getattr(self, 'confirmOnDblClick', None):
                uicore.registry.Confirm()
            elif self.sr.node.Get('typeID', None):
                self.ShowInfo()

    def OnMouseDown(self, *args):
        SE_BaseClassCore.OnMouseDown(self, *args)
        if self.sr.node and self.sr.node.Get('OnMouseDown', None):
            self.sr.node.OnMouseDown(self)

    def OnMouseUp(self, *args):
        SE_BaseClassCore.OnMouseUp(self, *args)
        if not self or self.destroyed:
            return
        if self.sr.node and self.sr.node.Get('OnMouseUp', None):
            self.sr.node.OnMouseUp(self)

    def ShowInfo(self, *args):
        if self.sr.node.Get('isStation', 0):
            stationinfo = sm.GetService('ui').GetStationStaticInfo(self.itemID)
            sm.GetService('info').ShowInfo(stationinfo.stationTypeID, self.itemID)
            return
        if self.sr.node.Get('typeID', None):
            abstractinfo = self.sr.node.Get('abstractinfo', utillib.KeyVal())
            typeID = self.sr.node.Get('typeID', None)
            itemID = self.sr.node.Get('itemID', None) or None
            if IsBlueprintCategory(evetypes.GetCategoryID(typeID)):
                isCopy = self.sr.node.isCopy
                abstractinfo.bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(typeID=typeID, original=not isCopy)
            sm.GetService('info').ShowInfo(typeID, itemID, abstractinfo=abstractinfo)

    def GetMenu(self):
        if not self.sr.node.Get('ignoreRightClick', 0):
            self.OnClick()
        if hasattr(self, 'sr'):
            if self.sr.node and self.sr.node.Get('GetMenu', None):
                return self.sr.node.GetMenu(self)
            if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
                return GetMenuService().GetMenuFromItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None))
        return []

    def OnDropData(self, dragObj, nodes):
        data = self.sr.node
        if data.OnDropData:
            data.OnDropData(dragObj, nodes)

    def OnDragEnter(self, dragSource, dragData):
        data = self.sr.node
        if data.OnDragEnter:
            data.OnDragEnter(dragSource, dragData)

    def OnDragExit(self, dragSource, dragData):
        data = self.sr.node
        if data.OnDragExit:
            data.OnDragExit(dragSource, dragData)

    def DoSelectNode(self, toggle = 0):
        self.sr.node.scroll.GetSelectedNodes(self.sr.node, toggle=toggle)

    def GetRadialMenuIndicator(self, create = True, *args):
        indicator = getattr(self, 'radialMenuIndicator', None)
        if indicator and not indicator.destroyed:
            return indicator
        if not create:
            return
        self.radialMenuIndicator = Fill(bgParent=self, color=(1, 1, 1, 0.25), name='radialMenuIndicator')
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
