#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_gridutils.py
import blue
import evetypes
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_WORLDMOD
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.window import Window
from eve.common.lib import appConst as const
Progress = lambda title, text, current, total: sm.GetService('loading').ProgressWnd(title, text, current, total)
SERVICENAME = 'gridutils'
ORIENTATION = 1

class GridUtilService(Service):
    __notifyevents__ = ['ProcessRestartUI']
    __dependencies__ = []
    __guid__ = 'svc.gridutils'
    __servicename__ = SERVICENAME
    __displayname__ = 'Grid Utils'

    def Run(self, memStream = None):
        self.wnd = None

    def Stop(self, memStream = None):
        self.Hide()
        Service.Stop(self, memStream)

    def ConstructLayout(self):
        if self.wnd:
            self.wnd.Maximize()
            return
        self.wnd = wnd = Window.Open(windowID=SERVICENAME)
        wnd._OnClose = self.Hide
        wnd.sr.main = wnd.GetChild('main')
        wnd.SetCaption('Grid Utilities')
        self.Layout(wnd)

    def Layout(self, wnd):
        self.icons_container = ContainerAutoSize(parent=wnd.sr.main, align=uiconst.TOPLEFT, height=32)
        for icon, label, func in self.GetButtonIconList():
            ButtonIcon(name=label, parent=self.icons_container, align=uiconst.TOLEFT, texturePath=icon, iconSize=32, hint=label, func=func)

        wnd.MakeUnResizeable()
        wnd.Maximize(1)

    def GetButtonIconList(self):
        return [['res:/UI/Texture/Icons/56_64_4.png', 'Attract Jetcans', self.Attract],
         ['res:/UI/Texture/Icons/58_64_15.png', 'Loot Jetcans', lambda *x: self.CombineLoot(True)],
         ['res:/UI/Texture/Icons/26_64_11.png', 'Combine Containers', lambda *x: self.CombineLoot(False)],
         ['res:/UI/Texture/Icons/54_64_9.png', 'Scoop Containers', self.Scoop],
         ['res:/UI/Texture/Icons/56_64_2.png', 'Nuke Structures', self.NukeStructures],
         ['res:/UI/Texture/Icons/56_64_1.png', 'Nuke Shuttles', self.NukeShuttles],
         ['res:/UI/Texture/Icons/11_64_16.png', 'Nuke Cans/Drones', self.NukeGarbage]]

    def Hide(self, *args):
        if self.wnd:
            self.wnd.Close()
            self.wnd = None

    def ProcessRestartUI(self):
        if self.wnd:
            self.Hide()
            self.ConstructLayout()

    def Do(self, text = '', title = 'Grid Utils', filterFunc = None, actionFunc = None, delay = 500):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        targets = []
        for ballID in bp.balls.keys():
            if filterFunc(bp, ballID):
                targets.append(ballID)

        i = 0
        amount = len(targets)
        for ballID in targets:
            Progress(title, text, i, amount)
            actionFunc(bp, ballID)
            if delay:
                blue.pyos.synchro.SleepWallclock(delay)
            i += 1

        blue.pyos.synchro.SleepWallclock(1000)
        Progress(title, 'Done!', 1, 1)

    def Confirm(self, title, text):
        ret = sm.GetService('gameui').MessageBox(title=title, text=text, buttons=uiconst.OKCANCEL, icon=uiconst.WARNING)
        if ret[0] != uiconst.ID_OK:
            return False
        return True

    def RoleCheck(self, *roleSets):
        for roleNames in roleSets:
            flags = 0
            for roleName in roleNames:
                flags += globals()[roleName]

            if eve.session.role & flags == flags:
                return True

        summary = []
        for roleNames in roleSets:
            summary.append('<br>- '.join(roleNames))

        sm.GetService('gameui').MessageBox(title='Missing Roles', text='You require the following role(s) to use this function:<br>-  %s' % '<br><br>Or the following role(s):<br>- '.join(summary), buttons=uiconst.OK, icon=uiconst.INFO)

    def NukeStructures(self, *args):
        if not self.RoleCheck(['ROLE_HEALOTHERS']):
            return
        if len(args) and not self.Confirm('WARNING', 'This operation will <font color="#FF0000">DESTROY ALL POS STRUCTURES</font> in your current grid, not to mention cause a great shitload of graphic lag (which may require a restart to get rid of) for you and all spectators, depending on the number of structures deployed.<br><br>Proceed?'):
            return

        def f(bp, ballID):
            item = bp.GetInvItem(ballID)
            if item and item.categoryID == 23:
                return True

        def a(bp, ballID):
            sm.RemoteSvc('slash').SlashCmd('/heal %s 0' % ballID)

        self.Do('Nuking structures', filterFunc=f, actionFunc=a)

    def NukeShuttles(self, *args):
        if not self.RoleCheck(['ROLE_HEALOTHERS']):
            return
        if len(args) and not self.Confirm('WARNING', 'This operation will <font color="#FF0000">DESTROY ALL SHUTTLES</font> in your current grid, except currently occupied ones.<br><br>Proceed?'):
            return

        def f(bp, ballID):
            item = bp.GetInvItem(ballID)
            if item and item.typeID in (11134, 672, 11129, 11132):
                return True

        def a(bp, ballID):
            if ballID == eve.session.shipid:
                return
            try:
                if not bp.GetBall(ballID).isInteractive:
                    sm.RemoteSvc('slash').SlashCmd('/heal %s 0' % ballID)
            except:
                pass

        self.Do('Nuking shuttles...', filterFunc=f, actionFunc=a, delay=250)

    def NukeGarbage(self, *args):
        if not self.RoleCheck(['ROLE_HEALOTHERS']):
            return
        if len(args) and not self.Confirm('WARNING', 'This operation will <font color="#FF0000">DESTROY ALL DRONES/JETCANS</font> in your current grid.<br><br>Proceed?'):
            return

        def f(bp, ballID):
            item = bp.GetInvItem(ballID)
            if item:
                cat = evetypes.GetCategoryIDByGroup(item.groupID)
                grp = item.groupID
                if item.typeID == 23 or cat in [const.categoryDrone] or grp in [const.groupWreck]:
                    return True

        def a(bp, ballID):
            if ballID == eve.session.shipid:
                return
            try:
                sm.RemoteSvc('slash').SlashCmd('/heal %s 0' % ballID)
            except:
                pass

        self.Do('Nuking Garbage...', filterFunc=f, actionFunc=a, delay=250)

    def Attract(self, *args):
        if not self.RoleCheck(['ROLE_WORLDMOD']):
            return

        def f(bp, ballID):
            item = bp.GetInvItem(ballID)
            if item and (item.typeID == 23 or item.groupID == 186):
                return True

        def a(bp, ballID):
            sm.RemoteSvc('slash').SlashCmd('/fetch %s' % ballID)

        self.Do('Attracting cans/wrecks...', filterFunc=f, actionFunc=a, delay=5)

    def Scoop(self, *args):
        if not self.RoleCheck(['ROLE_GML']):
            return
        if len(args) and not self.Confirm('WARNING', 'This operation will scoop all unanchored cargo containers in your current grid that allow you to do so.<br>You have to make sure your ship has enough free cargo space to hold all of them (use a BH Mega Cargo Ship?)<br><br>Proceed?'):
            return
        secureCans = [448, 340, 12]

        def f(bp, ballID):
            item = bp.GetInvItem(ballID)
            if item and item.groupID in secureCans and item.typeID != 23:
                return True

        def a(bp, ballID):
            sm.RemoteSvc('slash').SlashCmd('/tr me %s' % ballID)
            blue.pyos.synchro.SleepSim(500)
            try:
                sm.GetService('menu').Scoop(ballID, bp.GetInvItem(ballID).typeID)
            except:
                pass

        self.Do('Scooping containers...', filterFunc=f, actionFunc=a, delay=100)

    def CombineLoot(self, useShipCargo, *args):
        if useShipCargo:
            if not self.RoleCheck(['ROLE_WORLDMOD'], ['ROLE_GML']):
                return
            action = ['Loot', 'Looting']
        else:
            if not self.RoleCheck(['ROLE_WORLDMOD']):
                return
            action = ['Combine', 'Combining']
        if len(args) and not self.Confirm('WARNING', 'This operation will %s all loot cans/wrecks in your current grid into %s.<br><br>Proceed?' % (action[0].lower(), ['one container', "your ship's cargohold"][useShipCargo])):
            return
        if useShipCargo:
            id = eve.session.shipid
        else:
            id = sm.RemoteSvc('slash').SlashCmd('/spawn "Cargo Container"')
            sm.RemoteSvc('slash').SlashCmd('/chowner %d %d' % (id, eve.session.charid))
        cargo = sm.GetService('invCache').GetInventoryFromId(id)

        def f(bp, ballID):
            item = bp.GetInvItem(ballID)
            if item and (item.typeID == 23 or item.groupID == 186) and ballID != id:
                if eve.session.role & ROLE_WORLDMOD and item.ownerID not in (eve.session.corpid, eve.session.charid):
                    sm.RemoteSvc('slash').SlashCmd('/chowner %d %d' % (item.itemID, eve.session.charid))
                return True

        def a(bp, ballID):
            sm.RemoteSvc('slash').SlashCmd('/fetch %s' % ballID)

        def b(bp, ballID):
            cargo.MultiAdd([ row.itemID for row in sm.GetService('invCache').GetInventoryFromId(ballID).List() ], ballID, flag=const.flagCargo)

        def c(bp, ballID):
            sm.RemoteSvc('slash').SlashCmd('/heal %s 0' % ballID)

        def gml(bp, ballID):
            sm.RemoteSvc('slash').SlashCmd('/tr me %s' % ballID)
            blue.pyos.synchro.SleepSim(500)
            b(bp, ballID)

        if eve.session.role & ROLE_WORLDMOD:
            stages = 3
            self.Do('%s cans/wrecks - Stage 1/3' % action[1], filterFunc=f, actionFunc=a, delay=5)
            self.Do('%s cans/wrecks - Stage 2/3' % action[1], filterFunc=f, actionFunc=b, delay=5)
        else:
            stages = 2
            self.Do('%s cans/wrecks - Stage 1/2' % action[1], filterFunc=f, actionFunc=gml, delay=100)
        self.Do('%s cans/wrecks - Stage %s/%s' % (action[1], stages, stages), filterFunc=f, actionFunc=c, delay=5)
