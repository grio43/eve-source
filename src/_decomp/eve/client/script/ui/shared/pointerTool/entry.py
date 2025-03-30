#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\entry.py
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.pointerTool.favorites import AddElementsToGroup, FindPointerObjectsForNodes
from localization import GetByLabel
from carbonui.uicore import uicore
from utillib import KeyVal
ICON_SIZE = 32

class PointerWndEntry(SE_BaseClassCore):
    __guid__ = 'listentry.PointerWndEntry'
    isDragObject = True

    def Startup(self, *etc):
        self.labelleft = 32
        self.labelCont = Container(name='labelCont', parent=self, align=uiconst.TOALL, padLeft=40, padRight=35)
        self.label = EveLabelMedium(text='', parent=self.labelCont, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, autoFadeSides=35)
        self.iconCont = Container(name='iconCont', parent=self, pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE), align=uiconst.CENTERLEFT)
        self.icon = Sprite(parent=self.iconCont, pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE), align=uiconst.CENTER, state=uiconst.UI_DISABLED, opacity=0.75)
        self.playBtn = ButtonIcon(name='playBtn', parent=self, iconSize=20, align=uiconst.CENTERRIGHT, left=5, texturePath='res:/ui/texture/classes/HelpPointer/highlightElement.png', func=self.DoPoint)

    def Load(self, node):
        self.sr.node = node
        data = node
        text = data.label
        if data.useLongName and data.longName:
            text = data.longName
        self.label.text = text
        if data.texturePath:
            self.icon.SetTexturePath(data.texturePath)
            self.icon.LoadIcon(data.texturePath, ignoreSize=True)
            if data.iconSizes:
                self.icon.SetSize(*data.iconSizes)
            else:
                self.SetIconSize()
        elif data.iconData:
            maxIconDataSize = max(data.iconData.sizes)
            iconSize = min(maxIconDataSize, ICON_SIZE)
            self.icon.width = iconSize
            self.icon.height = iconSize
            self.icon.SetTexturePath(data.iconData)
        if node.Get('hint', None):
            self.hint = data.hint
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        self.playBtn.hint = GetByLabel('UI/Help/PointerWndPointTo', elementName=data.label)
        sublevel = node.sublevel or 0
        indent = 16 * sublevel
        self.icon.left = indent
        self.labelCont.padLeft = 40 + indent

    def SetIconSize(self):
        try:
            textureWidth = self.icon.renderObject.texturePrimary.atlasTexture.width
            textureHeight = self.icon.renderObject.texturePrimary.atlasTexture.height
            newWidth = min(ICON_SIZE, max(16, textureWidth))
            newHeight = min(ICON_SIZE, max(16, textureHeight))
            widthRatio = newWidth / float(textureWidth)
            heightRatio = newHeight / float(textureHeight)
            if widthRatio != heightRatio:
                smallerRatio = min(widthRatio, heightRatio)
                newWidth = int(smallerRatio * textureWidth)
                newHeight = int(smallerRatio * textureHeight)
            self.icon.width = newWidth
            self.icon.height = newHeight
        except StandardError as e:
            pass

    def GetHeight(self, *args):
        node, width = args
        node.height = 32
        return node.height

    def GetDragData(self, *args):
        pointerObj = self.sr.node.pointerObject
        return [KeyVal(__guid__='listentry.PointerWndEntry', pointerObjects=[pointerObj])]

    def OnDblClick(self, *args):
        if self.sr.node.openElement:
            pointerObject = self.sr.node.pointerObject
            if pointerObject and pointerObject.cmdName:
                uicore.cmd.GetCommandAndExecute(pointerObject.cmdName)
                return
        self.DoPoint()

    def DoPoint(self, *args):
        sourceLocation = self.sr.node.sourceLocation
        sm.GetService('helpPointer').ActivateHelperPointer(self.sr.node.uiElementName, sourceLocation)

    def GetHint(self):
        node = self.sr.node
        return node.longName or node.label

    def GetMenu(self):
        if self.sr.get('node', None) and self.sr.node.get('OnGetMenu', None):
            return self.sr.node.OnGetMenu(self)
        return []


class FavoritePointerWndEntry(PointerWndEntry):

    def Startup(self, *args):
        PointerWndEntry.Startup(self, args)
        self.posIndicatorCont = Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=2)
        self.posIndicator = Fill(parent=self.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_DISABLED)
        self.posIndicator.Hide()

    def OnDropData(self, dragObj, nodes, *args):
        node = self.sr.node
        self.posIndicator.Hide()
        if not self.IsOfRightTypeForDragging(nodes):
            return
        nodeDragged = nodes[0]
        parentGroup = self.sr.node.parentGroup
        parentGroupID = parentGroup.groupID
        uiElementsInGroup = parentGroup.uiElementNames
        if node.uiElementName in uiElementsInGroup:
            idxInGroup = uiElementsInGroup.index(node.uiElementName)
        else:
            idxInGroup = None
        AddElementsToGroup(parentGroupID, [nodeDragged], idxInGroup)

    def OnDragEnter(self, dragObj, nodes, *args):
        if self.IsOfRightTypeForDragging(nodes):
            self.posIndicator.Show()

    def IsOfRightTypeForDragging(self, nodes):
        if len(nodes) != 1:
            return False
        return bool(FindPointerObjectsForNodes(nodes))

    def OnDragExit(self, *args):
        self.posIndicator.Hide()


class FavoriteListGroup(ListGroup):
    isDragObject = True

    def GetDragData(self):
        node = self.sr.node
        groupKeyVal = node.groupKeyVal
        allPointers = sm.GetService('helpPointer').GetAllPointersByElementName()
        pointerObjects = []
        for uiElementName in groupKeyVal.uiElementNames:
            pointerObj = allPointers.get(uiElementName, None)
            if pointerObj:
                pointerObjects.append(pointerObj)

        if pointerObjects:
            fakeNode = KeyVal(__guid__='listentry.PointerWndEntry', pointerObjects=pointerObjects)
            return [fakeNode]
        return []
