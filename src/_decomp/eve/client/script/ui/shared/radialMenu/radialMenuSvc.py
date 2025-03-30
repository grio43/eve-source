#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\radialMenu\radialMenuSvc.py
from eve.client.script.ui.util import uix
import carbon.common.script.sys.service as service
import uthread
import carbonui.const as uiconst
import geo2
from carbon.common.script.util import timerstuff
from carbonui.uicore import uicore
from eve.client.script.parklife import states as state
from eve.client.script.ui.shared.radialMenu import spaceRadialMenuFunctions, NORMAL_RADIAL_MENU, BROADCAST_RADIAL_MENU
from eve.client.script.ui.shared.radialMenu.broadcastRadialMenu import RadialMenuBroadcast
from eve.client.script.ui.shared.radialMenu.radialMenu import RadialMenuSpace
from eve.client.script.util.bubble import SlimItemFromCharID
from eve.common.script.sys import idCheckers
RADIAL_MENU_EXPAND_DELAY_MIN = 0
RADIAL_MENU_EXPAND_DELAY_MAX = 450
RADIAL_MENU_EXPAND_DELAY_DEFAULT = 150

class RadialMenuSvc(service.Service):
    __guid__ = 'svc.radialmenu'
    __startupdependencies__ = ['command_blocker']

    def Run(self, memStream = None):
        self.expandTimer = None

    def _ClampActionMenuExpandTime(self, expandTime):
        if expandTime > RADIAL_MENU_EXPAND_DELAY_MAX:
            settings.user.ui.Set('actionMenuExpandTime', RADIAL_MENU_EXPAND_DELAY_MAX)
        elif expandTime < RADIAL_MENU_EXPAND_DELAY_MIN:
            settings.user.ui.Set('actionMenuExpandTime', RADIAL_MENU_EXPAND_DELAY_MIN)

    def TryExpandActionMenu(self, itemID, clickedObject, *args, **kwargs):
        if self.command_blocker.is_blocked(['radialmenu', 'radialmenu.expand']):
            return 0
        if uicore.uilib.Key(uiconst.VK_MENU) or uicore.uilib.Key(uiconst.VK_CONTROL):
            return 0
        isRadialMenuButtonActive = spaceRadialMenuFunctions.IsRadialMenuButtonActive()
        if not isRadialMenuButtonActive:
            return 0
        x = uicore.uilib.x
        y = uicore.uilib.y
        expandTime = settings.user.ui.Get('actionMenuExpandTime', RADIAL_MENU_EXPAND_DELAY_DEFAULT)
        self._ClampActionMenuExpandTime(expandTime)
        menuType = NORMAL_RADIAL_MENU
        noDelay = False
        combatCmdLoaded = uicore.cmd.combatCmdLoaded
        if combatCmdLoaded:
            if combatCmdLoaded.name == 'CmdOpenBroadcastRadialMenu':
                menuType = BROADCAST_RADIAL_MENU
                noDelay = True
            elif combatCmdLoaded.name == 'CmdOpenRadialMenu':
                noDelay = True
        elif isRadialMenuButtonActive == BROADCAST_RADIAL_MENU:
            menuType = BROADCAST_RADIAL_MENU
        if noDelay or not expandTime:
            uthread.new(self._TryExpandActionMenu, itemID, x, y, clickedObject, menuType, **kwargs)
        else:
            self.expandTimer = timerstuff.AutoTimer(int(expandTime), self._TryExpandActionMenu, itemID, x, y, clickedObject, menuType, **kwargs)
        return 1

    def _TryExpandActionMenu(self, itemID, x, y, clickedObject, menuType = NORMAL_RADIAL_MENU, **kwargs):
        if getattr(clickedObject, 'isDragObject', False):
            if x != uicore.uilib.x or y != uicore.uilib.y:
                return
        self.expandTimer = None
        if clickedObject.destroyed:
            return
        v = geo2.Vector(uicore.uilib.x - x, uicore.uilib.y - y)
        if int(geo2.Vec2Length(v) > 12):
            return
        self.ExpandActionMenu(itemID, x, y, clickedObject, menuType, **kwargs)

    def ExpandActionMenu(self, itemID, x, y, clickedObject, menuType = NORMAL_RADIAL_MENU, **kwargs):
        slimItem = None
        if idCheckers.IsCharacter(itemID):
            kwargs['charID'] = itemID
            slimItem = SlimItemFromCharID(itemID)
            if slimItem:
                itemID = slimItem.itemID
        elif not itemID and 'bookmarkInfo' in kwargs:
            bookmarkInfo = kwargs['bookmarkInfo']
            bookmkarkItemID = getattr(bookmarkInfo, 'itemID', None)
            if bookmkarkItemID:
                slimItem = uix.GetBallparkRecord(bookmkarkItemID)
        else:
            slimItem = uix.GetBallparkRecord(itemID)
        isRadialMenuButtonActive = spaceRadialMenuFunctions.IsRadialMenuButtonActive()
        if not isRadialMenuButtonActive:
            return
        uicore.layer.menu.Flush()
        uicore.uilib.tooltipHandler.CloseTooltip()
        if menuType == BROADCAST_RADIAL_MENU:
            radialMenuClass = RadialMenuBroadcast
        else:
            radialMenuClass = kwargs.get('radialMenuClass', RadialMenuSpace)
        radialMenu = radialMenuClass(name='radialMenu', parent=uicore.layer.menu, state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT, updateDisplayName=True, slimItem=slimItem, itemID=itemID, x=x, y=y, clickedObject=clickedObject, **kwargs)
        uicore.layer.menu.radialMenu = radialMenu
        uicore.uilib.SetMouseCapture(radialMenu)
        isRadialMenuButtonActive = spaceRadialMenuFunctions.IsRadialMenuButtonActive()
        if not isRadialMenuButtonActive:
            radialMenu.Close()
            return
        sm.StartService('stateSvc').SetState(itemID, state.mouseOver, 0)
        radialMenu.state = uiconst.UI_NORMAL
        sm.ScatterEvent('OnRadialMenuExpanded')

    def GetRadialMenuOwner(self):
        radialMenu = getattr(uicore.layer.menu, 'radialMenu', None)
        if radialMenu and not radialMenu.destroyed:
            radialMenuOwner = getattr(radialMenu, 'clickedObject', None)
            if radialMenuOwner and not radialMenuOwner.destroyed:
                return radialMenuOwner
