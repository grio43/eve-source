#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_destroyableitems.py
import os
import sys
import blue
import evetypes
import uthread
from carbon.common.script.sys.service import Service
from carbon.common.script.util.format import FmtDist
from carbonui import uiconst
from carbonui.control.contextMenu.contextMenu import CreateMenuView
from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from carbonui.button.group import ButtonGroup
FILE_DESTROYABLES = 'Destroyables.txt'
FILE_POS_EXT = 'pos'

class InsiderDestroyables(Generic):
    __guid__ = 'listentry.InsiderDestroyables'

    def GetMenu(self, *args):
        node = self.sr.node
        selected = node.scroll.GetSelectedNodes(node)
        multiple = len(selected) > 1
        m = []
        if multiple:
            m += [('Destroy', [('Destroy all selected', self.HealZero, (selected,)), ('Unspawn all selected', self.Unspawn, (selected,))]), None]
            m += sm.GetService('menu').GetMenuFromItemIDTypeID(node.itemID, node.typeID)
            return m
        else:
            m += [('Destroy', [('Destroy this %s' % evetypes.GetName(node.typeID), self.HealZero, (selected,)), ('Unspawn this %s' % evetypes.GetName(node.typeID), self.Unspawn, (selected,))]), None]
            m += sm.GetService('menu').GetMenuFromItemIDTypeID(node.itemID, node.typeID)
            return m

    def Unspawn(self, nodes = None):
        if nodes is None:
            return
        if not settings.char.ui.Get('suppressDestroyableWarning', 0):
            if not eve.Message('CustomQuestion', {'header': 'Unspawn selected?',
             'question': 'Do you really want to unspawn these items?'}, uiconst.YESNO) == uiconst.ID_YES:
                return
        for node in nodes:
            sm.GetService('slash').SlashCmd('unspawn %d' % node.itemID)

    def HealZero(self, nodes = None):
        if nodes is None:
            return
        if not settings.char.ui.Get('suppressDestroyableWarning', 0):
            if not eve.Message('CustomQuestion', {'header': 'Destroy selected?',
             'question': 'Do you really want to destroy these items?'}, uiconst.YESNO) == uiconst.ID_YES:
                return
        for node in nodes:
            sm.GetService('slash').SlashCmd('heal %d 0' % node.itemID)


class DestroyableItemsWindow(Window):
    default_windowID = 'destroyableitems'
    default_iconNum = 'res:/UI/Texture/WindowIcons/terminate.png'
    default_caption = 'Destroyable Items'
    default_minSize = (370, 360)


class destroyableItems(Service):
    __module__ = __name__
    __exportedcalls__ = {}
    __notifyevents__ = ['ProcessRestartUI', 'Update', 'DoBallRemove']
    __dependencies__ = ['stateSvc']
    __guid__ = 'svc.destroyableItems'
    __servicename__ = 'destroyableItems'
    __displayname__ = 'destroyableItems'

    def Run(self, memStream = None):
        self.wnd = None

    def Stop(self, memStream = None):
        self.Hide()
        Service.Stop(self, memStream)

    def BallRemoveThread(self, ball, slimItem, terminal):
        if not hasattr(self, 'wnd') or not self.wnd or self.wnd.destroyed:
            return
        self.LogInfo('***destroyableItems::DoBallRemove Starting Long Run***', slimItem.itemID)
        if not hasattr(self, 'scroll') or not hasattr(self.scroll, 'GetNodes'):
            return
        nodes = self.scroll.GetNodes()
        for i in nodes:
            if i.itemID == slimItem.itemID:
                self.scroll.RemoveNodes([i])

    def DoBallRemove(self, ball, slimItem, terminal):
        uthread.worker('DestroyableItems::DoBallRemove', self.BallRemoveThread, ball, slimItem, terminal)

    def ConstructLayout(self):
        self.Layout()

    def Layout(self):
        if self.wnd:
            self.wnd.Maximize()
            return
        self.wnd = wnd = DestroyableItemsWindow.Open()
        self.wnd._OnClose = self.Hide
        self.main_container = Container(name='direction', parent=wnd.GetChild('main'), align=uiconst.TOALL)
        self.directionSettingsBox = ContainerAutoSize(name='direction', parent=self.main_container, align=uiconst.TOTOP)
        self.ConstructTopContainer()
        self.ConstructBottomContainer()
        self.ApplyWindowMinSize()

    def ConstructBottomContainer(self):
        eveLabel.Label(text=u'Range (km)', state=uiconst.UI_DISABLED, parent=self.directionSettingsBox, align=uiconst.TOTOP)
        self.destroyable_items_container = Container(name='maincont', parent=self.main_container, padTop=4)
        self.scroll = eveScroll.Scroll(parent=self.destroyable_items_container)
        self.scroll.sr.id = 'resultsscroll'
        self.scroll.Load(contentList=[])
        self.maintabs = TabGroup(name='tabparent', parent=self.destroyable_items_container, idx=0)
        self.maintabs.AddTab(u'All items', self.scroll, self, 'allitems')
        self.maintabs.AddTab(u'Drones', self.scroll, self, 'drones')
        self.maintabs.AddTab(u'Container', self.scroll, self, 'containers')
        self.maintabs.AddTab(u'Ships', self.scroll, self, 'ships')
        self.maintabs.AddTab(u'Structures', self.scroll, self, 'structures')
        self.maintabs.AddTab('Deployables', self.scroll, self, 'deployable')
        self.maintabs.AddTab('%s/%s' % (u'NPC', u'Entity'), self.scroll, self, 'npcs')
        self.maintabs.AutoSelect()

    def ConstructTopContainer(self):
        self.suppress = Checkbox(text='Suppress warning messages', settingsKey='', checked=settings.char.ui.Get('suppressDestroyableWarning', 0), align=uiconst.TOTOP, callback=self.OnSuppressCheckbox, parent=self.directionSettingsBox)
        self.verbose = Checkbox(text='List all details', settingsKey='', checked=settings.char.ui.Get('verboseDestroyables', 0), align=uiconst.TOTOP, parent=self.directionSettingsBox, callback=self.OnVerboseCheckbox)
        self.range_button_container = ContainerAutoSize(parent=self.directionSettingsBox, align=uiconst.TOTOP, height=32)
        self.dir_rangeinput = SingleLineEditInteger(name='rangeedit', parent=self.range_button_container, minValue=1, align=uiconst.TOLEFT, width=100, setvalue='2147483647', padRight=8)
        self.button_group = ButtonGroup(parent=self.range_button_container, align=uiconst.TOLEFT)
        self.button_group.AddButton(u'Scan', self.Update)
        self.button_group.AddButton(u'Select All', self.SelectAll)
        self.button_group.AddButton(u'Destroy', self.Pwn)
        self.button_group.AddButton(u'Export', self.OpenExportMenu)

    def OpenExportMenu(self, button):
        exportMenu = []
        exportMenu.append(('Generate List Dump', self.Dump))
        exportMenu.append(('Generate POSer', self.DumpPOSer))
        mv = CreateMenuView(CreateMenuDataFromRawTuples(exportMenu), None, None)
        x, y, w, h = button.GetAbsolute()
        x = max(x, 0)
        y = y + h
        if y + mv.height > uicore.desktop.height:
            mv.top = button.GetAbsolute()[1] - mv.height
        else:
            mv.top = y
        mv.left = min(uicore.desktop.width - mv.width, x)
        Frame(parent=mv, color=(1.0, 1.0, 1.0, 0.2))
        uicore.layer.menu.children.insert(0, mv)

    def OnSuppressCheckbox(self, cb):
        checked = cb.GetValue()
        settings.char.ui.Set('suppressDestroyableWarning', checked)
        cb.state = uiconst.UI_HIDDEN
        cb.state = uiconst.UI_NORMAL

    def OnVerboseCheckbox(self, cb):
        checked = cb.GetValue()
        settings.char.ui.Set('verboseDestroyables', checked)
        cb.state = uiconst.UI_HIDDEN
        cb.state = uiconst.UI_NORMAL

    def ApplyWindowMinSize(self):
        width, height = self.wnd.GetWindowSizeForContentSize(height=self.directionSettingsBox.height, width=self.range_button_container.width)
        self.wnd.SetMinSize([width, height + self.maintabs.height])

    def Hide(self, *args):
        if self.wnd:
            self.wnd = None

    def ProcessRestartUI(self):
        if self.wnd:
            self.Hide()
            self.ConstructLayout()

    def Load(self, key, *args):
        if key == 'allitems':
            self.Search(group='all')
        elif key == 'drones':
            self.Search(group=[const.categoryDrone, const.categoryFighter])
        elif key == 'containers':
            self.Search(group=const.categoryCelestial)
        elif key == 'ships':
            self.Search(group=const.categoryShip)
        elif key == 'structures':
            self.Search(group=const.categoryStarbase)
        elif key == 'deployable':
            self.Search(group=const.categoryDeployable)
        elif key == 'npcs':
            self.Search(group=const.categoryEntity)

    def Update(self, *args):
        wnd = DestroyableItemsWindow.GetIfOpen()
        if wnd and wnd.IsMinimized() == False:
            tabparent = wnd.GetChild('tabparent')
            if tabparent.IsVisible():
                tabparent.ReloadVisible()

    def SelectAll(self, *args):
        if not self.scroll.GetSelected():
            self.scroll.SelectAll()
        else:
            self.scroll.DeselectAll()

    def Pwn(self, *args):
        selected = self.scroll.GetSelected()
        multiple = len(selected) > 1
        if multiple:
            self.MultipleRemove(selected)
        elif selected:
            self.SingleRemove(selected)

    def DumpPOSer(self, *args):
        if eve.Message('CustomQuestion', {'header': 'Save current data?',
         'question': 'This will save the current data entered in the window.<br><br>Are you sure that you want to save this?'}, uiconst.YESNO) == uiconst.ID_YES:
            filename = '%s.%s' % (sm.GetService('insider').GetTimestamp(), FILE_POS_EXT)
            wnd = DestroyableItemsWindow.GetIfOpen()
            if wnd:
                scroll = wnd.GetChild('scroll')
                f = blue.classes.CreateInstance('blue.ResFile')
                TARGET = os.path.join(sm.GetService('insider').GetInsiderDir(), filename)
                if not f.Open(TARGET, 0):
                    f.Create(TARGET)
                scroll.SelectAll()
                data = scroll.GetSelected()
                scroll.DeselectAll()
                for entry in data:
                    if sm.GetService('michelle').GetBallpark().GetInvItem(entry.itemID).categoryID == const.categoryStarbase:
                        f.Write('% 6d % 6d % 6d = %s' % (entry.x,
                         entry.y,
                         entry.z,
                         entry.typeID))
                        f.Write('\r\n')

            f.Close()

    def Dump(self, *args):
        if eve.Message('CustomQuestion', {'header': 'Save current data?',
         'question': 'This will save the current data entered in the window.<br><br>Are you sure that you want to save this?'}, uiconst.YESNO) == uiconst.ID_YES:
            filename = '%s.%s' % (sm.GetService('insider').GetTimestamp(), FILE_DESTROYABLES)
            wnd = DestroyableItemsWindow.GetIfOpen()
            if wnd:
                scroll = wnd.GetChild('scroll')
                f = blue.classes.CreateInstance('blue.ResFile')
                TARGET = os.path.join(sm.GetService('insider').GetInsiderDir(), filename)
                if not f.Open(TARGET, 0):
                    f.Create(TARGET)
                scroll.SelectAll()
                data = scroll.GetSelected()
                scroll.DeselectAll()
                headers = scroll.GetColumns()
                for header in headers:
                    f.Write('%s\t' % header)

                f.Write('\r\n')
                for entry in data:
                    f.Write('%s' % entry.label.replace('<t>', '\t').encode('utf8'))
                    f.Write('\r\n')

                f.Close()

    def SingleRemove(self, nodes = None):
        if not settings.char.ui.Get('suppressDestroyableWarning', 0):
            if eve.Message('CustomQuestion', {'header': 'Destroy selected?',
             'question': 'Do you really want to destroy this %s?' % evetypes.GetName(nodes[0].typeID)}, uiconst.YESNO) == uiconst.ID_YES:
                for node in nodes:
                    sm.GetService('slash').SlashCmd('heal %d 0' % node.itemID)

        else:
            for node in nodes:
                sm.GetService('slash').SlashCmd('heal %d 0' % node.itemID)

    def MultipleRemove(self, nodes = None):
        if not settings.char.ui.Get('suppressDestroyableWarning', 0):
            if eve.Message('CustomQuestion', {'header': 'Destroy selected?',
             'question': 'Do you really want to destroy these selected items?'}, uiconst.YESNO) == uiconst.ID_YES:
                if not nodes:
                    nodes = [self.sr.node]
                for node in nodes:
                    sm.GetService('slash').SlashCmd('heal %d 0' % node.itemID)

        else:
            if not nodes:
                nodes = [self.sr.node]
            for node in nodes:
                sm.GetService('slash').SlashCmd('heal %d 0' % node.itemID)

    def Collate(self, list, group = None, players = None, *args):
        m = []
        bp = sm.GetService('michelle').GetBallpark()
        you = bp.GetBall(session.shipid)
        if group.__class__ == int:
            group = [group]
        verbose = settings.char.ui.Get('verboseDestroyables', 0)
        for item in list:
            owner = cfg.eveowners.Get(item.ownerID)
            if verbose:
                ball = bp.GetBall(item.itemID)
                distance = ball.surfaceDist
                x = int(ball.x + 0.5 - (you.x + 0.5))
                y = int(ball.y + 0.5 - (you.y + 0.5))
                z = int(ball.z + 0.5 - (you.z + 0.5))
            else:
                distance = x = y = z = 0
                ball = bp.GetBall(item.itemID)
                if ball:
                    distance = ball.surfaceDist
            state = '-'
            for groups in group:
                if item.categoryID == groups and item.categoryID == const.categoryDrone:
                    if item.ownerID not in players:
                        m.append((u'Drones',
                         evetypes.GetGroupNameByGroup(owner.groupID),
                         item.typeID,
                         item.itemID,
                         owner.name,
                         distance,
                         'Abandoned',
                         x,
                         y,
                         z))
                if item.categoryID == groups and item.categoryID == const.categoryFighter:
                    if item.ownerID not in players:
                        m.append((u'Fighters',
                         evetypes.GetGroupNameByGroup(owner.groupID),
                         item.typeID,
                         item.itemID,
                         owner.name,
                         distance,
                         'Abandoned',
                         x,
                         y,
                         z))
                elif item.categoryID == groups and item.categoryID == const.categoryCelestial and owner.IsNPC() == False and item.groupID != const.groupBeacon:
                    if evetypes.GetGroupNameByGroup(item.groupID) == 'Wreck':
                        if self.stateSvc.CheckWreckEmpty(item):
                            state = u'Empty'
                        else:
                            state = 'Not Empty'
                        m.append((evetypes.GetGroupNameByGroup(item.groupID),
                         evetypes.GetGroupNameByGroup(owner.groupID),
                         item.typeID,
                         item.itemID,
                         owner.name,
                         distance,
                         state,
                         x,
                         y,
                         z))
                    elif evetypes.GetGroupNameByGroup(item.groupID) == 'Biomass':
                        m.append((evetypes.GetGroupNameByGroup(item.groupID),
                         evetypes.GetGroupNameByGroup(owner.groupID),
                         item.typeID,
                         item.itemID,
                         owner.name,
                         distance,
                         'Popsicle',
                         x,
                         y,
                         z))
                    else:
                        if evetypes.GetIsGroupAnchorableByGroup(item.groupID):
                            if not bp.GetBall(item.itemID).isFree:
                                state = u'Anchored'
                            else:
                                state = u'Unanchored'
                        m.append((u'Container',
                         evetypes.GetGroupNameByGroup(owner.groupID),
                         item.typeID,
                         item.itemID,
                         owner.name,
                         distance,
                         state,
                         x,
                         y,
                         z))
                elif item.categoryID == groups and item.categoryID == const.categoryShip and not bp.GetBall(item.itemID).isInteractive:
                    m.append((u'Ships',
                     evetypes.GetGroupNameByGroup(owner.groupID),
                     item.typeID,
                     item.itemID,
                     owner.name,
                     distance,
                     u'Empty',
                     x,
                     y,
                     z))
                elif item.categoryID == groups and groups == const.categoryStarbase:
                    try:
                        state = sm.GetService('pwn').GetStructureState(item)[0].title()
                    except:
                        sys.exc_clear()

                    m.append((u'Structures',
                     evetypes.GetGroupNameByGroup(owner.groupID),
                     item.typeID,
                     item.itemID,
                     owner.name,
                     distance,
                     state,
                     x,
                     y,
                     z))
                elif item.categoryID == groups and groups == const.categoryDeployable:
                    if evetypes.GetIsGroupAnchorableByGroup(item.groupID):
                        if not bp.GetBall(item.itemID).isFree:
                            state = u'Anchored'
                        else:
                            state = u'Unanchored'
                    m.append(('Deployables',
                     evetypes.GetGroupNameByGroup(owner.groupID),
                     item.typeID,
                     item.itemID,
                     owner.name,
                     distance,
                     state,
                     x,
                     y,
                     z))
                elif item.categoryID == groups and item.categoryID == const.categoryEntity:
                    m.append(('%s/%s' % (u'NPC', u'Entity'),
                     evetypes.GetGroupNameByGroup(owner.groupID),
                     item.typeID,
                     item.itemID,
                     owner.name,
                     distance,
                     state,
                     x,
                     y,
                     z))

        return m

    def Search(self, group = None, *args):
        ignoredGroups = [const.groupPlanet,
         const.groupMoon,
         const.groupAsteroidBelt,
         const.groupSun,
         const.groupSecondarySun,
         const.groupStargate,
         const.groupCapturePointTower,
         const.groupControlBunker,
         const.groupSentryGun,
         const.groupBillboard,
         const.groupDestructibleStationServices,
         const.groupMoonMiningBeacon,
         const.groupMoonChunk,
         const.groupAbyssalTraces]
        ignoredTypes = [48583]
        wnd = DestroyableItemsWindow.GetIfOpen()
        bp = sm.GetService('michelle').GetBallpark()
        targets = []
        self.ballParkData = []
        playersPresent = []
        if idCheckers.IsSolarSystem(session.locationid):
            for ballID in bp.balls.keys():
                try:
                    item = bp.GetInvItem(ballID)
                    if item and item.groupID not in ignoredGroups and item.typeID not in ignoredTypes:
                        self.ballParkData.append(item)
                        if item.categoryID == const.categoryShip and bp.GetBall(ballID).isInteractive:
                            playersPresent.append(item.charID)
                except:
                    sys.exc_clear()
                    continue

            if group == 'all':
                groups = [const.categoryDrone,
                 const.categoryFighter,
                 const.categoryCelestial,
                 const.categoryShip,
                 const.categoryStarbase,
                 const.categoryDeployable,
                 const.categoryEntity]
                targets += self.Collate(self.ballParkData, group=groups, players=playersPresent)
            else:
                targets += self.Collate(self.ballParkData, group=group, players=playersPresent)
        nodes = []
        verbose = settings.char.ui.Get('verboseDestroyables', 0)
        maxRange = self.dir_rangeinput.GetValue() * 1000
        if targets:
            for each in targets:
                ownertype = each[1]
                ownername = each[4]
                distance = each[5]
                if maxRange and maxRange < distance:
                    continue
                itemname = evetypes.GetName(each[2])
                displayname = cfg.evelocations.Get(each[3]).name
                if not displayname:
                    displayname = '-'
                if verbose:
                    x = each[7]
                    y = each[8]
                    z = each[9]
                    label = u'%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (each[0],
                     each[6],
                     each[3],
                     FmtDist(distance, maxdemicals=1),
                     itemname,
                     displayname,
                     ownername,
                     ownertype,
                     x,
                     y,
                     z)
                    hint = u'Name: %s<br>Type: %s<br>Owner: %s<br>State: %s<br>Relative Position: [%s, %s, %s]' % (displayname,
                     itemname,
                     ownername,
                     each[6],
                     x,
                     y,
                     z)
                    entry = GetFromClass(InsiderDestroyables, {'label': label,
                     'hint': hint,
                     'entrytype': each[0],
                     'ownertype': ownertype,
                     'itemname': itemname,
                     'typeID': each[2],
                     'itemID': each[3],
                     'ownername': ownername,
                     'name': displayname,
                     u'Distance': FmtDist(distance, maxdemicals=1),
                     u'sort_Distance': distance,
                     'x': x,
                     'y': y,
                     'z': z})
                else:
                    label = u'%s<t>%s<t>%s' % (each[0], each[3], itemname)
                    hint = u'Name: %s<br>Type: %s<br>Owner: %s<br>State: %s' % (displayname,
                     itemname,
                     ownername,
                     each[6])
                    entry = GetFromClass(InsiderDestroyables, {'label': label,
                     'hint': hint,
                     'entrytype': each[0],
                     'ownertype': ownertype,
                     'itemname': itemname,
                     'typeID': each[2],
                     'itemID': each[3],
                     'ownername': ownername,
                     'name': displayname})
                nodes.append(entry)

        if verbose:
            self.scroll.Load(contentList=nodes, headers=['Entry Type',
             'State',
             'Item ID',
             'Distance',
             'Type',
             'Name',
             'Owner Name',
             'Owner Type',
             'x (m)',
             'y (m)',
             'z (m)'], fixedEntryHeight=18)
        else:
            self.scroll.Load(contentList=nodes, headers=['Entry Type', 'Item ID', 'Type'], fixedEntryHeight=18)
        if not nodes:
            self.scroll.ShowHint(u'No items found')
        else:
            self.scroll.ShowHint()

    exports = {'destroyableItems.ConstructLayout': ConstructLayout,
     'destroyableItems.Search': Search,
     'destroyableItems.Hide': Hide}
