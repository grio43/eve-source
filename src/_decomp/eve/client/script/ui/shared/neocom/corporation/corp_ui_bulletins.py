#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_bulletins.py
import mathext
from carbon.client.script.util.misc import GetAttrs
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelSmall, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.themeColored import SpriteThemeColored, LineThemeColored
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsNPC
from eveexceptions import UserError
from globalConfig import IsContentComplianceControlSystemActive
from localization import GetByLabel
from menucheckers import SessionChecker

class CorpUIBulletins(Container):
    is_loaded = False
    sortOrderCont = None

    def Load(self, *args):
        if self.is_loaded:
            return
        self.is_loaded = True
        isContentControlled = IsContentComplianceControlSystemActive(sm.GetService('machoNet'))
        if SessionChecker(session, None).IsCorpDirector() and not isContentControlled:
            bulletinBtnGroup = ButtonGroup(parent=self)
            bulletinBtnGroup.AddButton(GetByLabel('UI/Corporations/CorpUIHome/AddBulletin'), self.AddBulletin)
            self.sortOrderCont = Container(name='sortOrderCont', parent=self, align=uiconst.TOTOP, height=20)
            UtilMenu(menuAlign=uiconst.TOPRIGHT, parent=self.sortOrderCont, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/Icons/77_32_49.png', pos=(4, 0, 20, 20), GetUtilMenu=self.GetSortOrderMenu, iconSize=24)
        if not IsNPC(session.corpid):
            self.messageArea = Scroll(parent=self, padding=const.defaultPadding)
            self.LoadBulletins()

    def LoadBulletins(self):
        scrollEntries = sm.GetService('corp').GetBulletinEntries()
        if self.sortOrderCont:
            self.sortOrderCont.display = len(scrollEntries) > 1
        self.messageArea.LoadContent(contentList=scrollEntries, noContentHint=GetByLabel('UI/Corporations/BaseCorporationUI/NoBulletins'))

    def AddBulletin(self, *args):
        sm.GetService('corp').EditBulletin(None, isAlliance=False)

    def GetSortOrderMenu(self, menuParent):
        cont = menuParent.AddContainer(align=uiconst.TOTOP, height=50, padding=const.defaultPadding)
        bulletins = sm.GetService('corp').GetBulletins(False)
        orderCont = BulletinsOrder(parent=cont, align=uiconst.TOTOP, bulletins=bulletins, saveFunc=self.SaveSortOrder)
        orderContContentWidth = orderCont.GetContentWidth()
        cont.GetEntryWidth = lambda mc = cont: orderContContentWidth

    def SaveSortOrder(self, sortOrder):
        sm.GetService('corp').UpdateBulletinOrder(sortOrder)
        self.LoadBulletins()


class BulletinsOrder(Container):
    default_align = uiconst.TOTOP
    default_width = 200
    default_height = 130
    default_padding = 4

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bulletins = attributes.bulletins or []
        self.saveFunc = attributes.saveFunc
        self.headerLabel = EveLabelMediumBold(parent=self, align=uiconst.TOTOP, text=GetByLabel('UI/Corporations/CorpUIHome/BulletinDisplayOrder'))
        self.applyBtn = Button(parent=self, align=uiconst.CENTERBOTTOM, label=GetByLabel('UI/Commands/Apply'), func=self.ApplyCurrentOrder)
        self.scroll = Scroll(parent=self, padBottom=0)
        self.scroll.sr.content.OnDropData = self.MoveStuff
        toSort = [ ((eachEntry.sortOrder, -eachEntry.editDateTime), eachEntry.bulletinID) for eachEntry in self.bulletins ]
        self.sortOrder = SortListOfTuples(toSort)
        self.LoadBulletins()
        self.height = len(self.bulletins) * 20 + 70

    def LoadBulletins(self):
        scrollList = []
        for each in self.bulletins:
            bulletinID = each.bulletinID
            entry = GetFromClass(DraggableGenericEntry, {'label': each.title,
             'canDrag': True,
             'bulletinID': bulletinID})
            idx = self.sortOrder.index(bulletinID) if bulletinID in self.sortOrder else None
            scrollList.append((idx, entry))

        scrollList = SortListOfTuples(scrollList)
        if scrollList:
            scrollList.append(GetFromClass(NonDraggableGenericEntry, {'canDrag': False}))
        self.scroll.LoadContent(contentList=scrollList)

    def MoveStuff(self, dragObj, entries, idx = -1, *args):
        self._CleanupIndicators()
        selected = self.scroll.GetSelected()
        if not selected:
            return
        selected = selected[0]
        bulletinID = selected.bulletinID
        if idx is not None:
            if idx != selected.idx:
                if selected.idx < idx:
                    newIdx = idx - 1
                else:
                    newIdx = idx
            else:
                return
        else:
            newIdx = max(0, selected.idx - 1)
        try:
            self.sortOrder.remove(bulletinID)
        except ValueError:
            pass

        self.sortOrder.insert(newIdx, bulletinID)
        self.LoadBulletins()

    def _CleanupIndicators(self):
        for eachNode in self.scroll.GetNodes():
            if eachNode.panel:
                eachNode.panel.HideIndicator()

    def ApplyCurrentOrder(self, *args):
        sortOrder = [ (each.idx, each.bulletinID) for each in self.scroll.GetNodes() ]
        sortOrder = filter(None, SortListOfTuples(sortOrder))
        self.saveFunc(sortOrder)

    def GetContentWidth(self):
        entryWidth = 0
        for eachNode in self.scroll.GetNodes():
            if eachNode.panel:
                entryWidth = max(entryWidth, eachNode.panel.sr.label.textwidth + 10)

        entryWidth = mathext.clamp(50, entryWidth, 100)
        headerWidth, h = EveLabelMediumBold.MeasureTextSize(text=self.headerLabel.text)
        return max(headerWidth + 20, entryWidth, self.applyBtn.width) + self.padLeft + self.padRight


class DraggableGenericEntry(Generic):
    __guid__ = 'listentry.General'
    isDragObject = True
    default_cursor = uiconst.UICURSOR_TOP_BOTTOM_DRAG

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.sr.posIndicatorCont = Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=2)
        self.sr.posIndicator = Fill(parent=self.sr.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.posIndicator.state = uiconst.UI_HIDDEN
        self.canDrag = False

    def GetDragData(self, *args):
        if not self.sr.node.canDrag:
            return
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]

    def OnDropData(self, dragObj, nodes, *args, **kwars):
        if GetAttrs(self, 'parent', 'OnDropData'):
            node = nodes[0]
            if GetAttrs(node, 'panel'):
                self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)

    def ShowIndicator(self):
        self.sr.posIndicator.Show()

    def HideIndicator(self):
        self.sr.posIndicator.Hide()

    def OnDragEnter(self, dragObj, nodes, *args):
        self.ShowIndicator()

    def OnDragExit(self, *args):
        self.HideIndicator()


class NonDraggableGenericEntry(DraggableGenericEntry):
    __guid__ = 'listentry.General'


MAX_BULLETIN_LENGTH = 4000

class EditCorpBulletin(Window):
    __guid__ = 'form.EditCorpBulletin'
    default_windowID = 'EditCorpBulletin'
    default_iconNum = 'res:/ui/Texture/WindowIcons/corporation.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        isAlliance = attributes.isAlliance
        bulletin = attributes.bulletin
        self.scope = uiconst.SCOPE_INGAME
        self.bulletin = bulletin
        self.bulletinID = None
        self.editDateTime = None
        self.isAlliance = isAlliance
        self.SetMinSize([420, 300])
        self.SetCaption(GetByLabel('UI/Corporations/EditCorpBulletin/EditBulletinCaption'))
        main = self.GetMainArea()
        main.pos = (const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding)
        self.topParent = Container(name='topParent', parent=main, align=uiconst.TOTOP, height=45, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(0, -10, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        titleInput = SingleLineEditText(name='titleInput', parent=self.topParent, align=uiconst.TOBOTTOM, padLeft=120, maxLength=100)
        titleInput.OnDropData = self.OnDropData
        self.sr.titleInput = titleInput
        l = EveLabelSmall(text=GetByLabel('UI/Corporations/EditCorpBulletin/BulletinTitle'), parent=titleInput, width=64, height=12, left=48, top=4, state=uiconst.UI_DISABLED)
        l.left = -l.textwidth - 6
        Container(parent=main, height=const.defaultPadding, align=uiconst.TOTOP, name='push')
        self.sr.bottom = ContainerAutoSize(name='bottom', parent=main, align=uiconst.TOBOTTOM, padTop=16)
        ButtonGroup(btns=[[GetByLabel('UI/Common/Buttons/Submit'),
          self.ClickSend,
          None,
          None], [GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          None,
          None]], parent=self.sr.bottom, line=False)
        self.sr.messageEdit = EditPlainText(setvalue='', parent=main, maxLength=MAX_BULLETIN_LENGTH, showattributepanel=1)
        if bulletin is not None:
            self.sr.titleInput.SetValue(bulletin.title)
            self.sr.messageEdit.SetValue(bulletin.body)
            self.bulletinID = bulletin.bulletinID
            self.editDateTime = bulletin.editDateTime

    def OnCancel(self, *args):
        self.Close()

    def _OnClose(self, *args):
        self.messageEdit = None

    def IsAlliance(self):
        return self.isAlliance

    def ClickSend(self, *args):
        if getattr(self, 'sending', False):
            return
        title = self.sr.titleInput.GetValue()
        body = self.sr.messageEdit.GetValue(html=0).strip()
        self.sending = True
        try:
            if title == '' or body == '':
                raise UserError('CorpBulletinMustFillIn')
            if self.bulletinID is None:
                sm.GetService('corp').AddBulletin(title, body, self.isAlliance)
            else:
                sm.GetService('corp').UpdateBulletin(self.bulletinID, title, body, self.isAlliance, self.editDateTime)
        finally:
            self.sending = False

        if not self or self.destroyed:
            return
        self.Close()


class BulletinEntry(SE_BaseClassCore):
    __guid__ = 'listentry.BulletinEntry'
    default_showHilite = False

    def Startup(self, *args):
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM)
        self.text = EveLabelMedium(parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padding=const.defaultPadding, linkStyle=uiconst.LINKSTYLE_REGULAR)
        self.postedBy = EveLabelMedium(parent=self, align=uiconst.BOTTOMRIGHT, state=uiconst.UI_NORMAL, maxLines=1, top=const.defaultPadding, left=const.defaultPadding)

    def Load(self, node):
        self.text.text = node.text
        self.postedBy.text = node.postedBy

    def GetDynamicHeight(node, width):
        textWidth, textHeight = EveLabelMedium.MeasureTextSize(text=node.text, width=width - const.defaultPadding * 2)
        height = textHeight + const.defaultPadding * 2
        postedWidth, postedHeight = EveLabelMedium.MeasureTextSize(text=node.postedBy, maxLines=1)
        height += postedHeight + const.defaultPadding
        return height
