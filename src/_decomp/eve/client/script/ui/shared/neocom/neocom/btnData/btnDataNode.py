#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNode.py
import blue
import carbonui.const as uiconst
import localization
import uthread2
import utillib
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom import neocomConst, neocomSignals
from eve.client.script.ui.shared.neocom.neocom.highlightState import HighlightState
from eve.client.script.ui.shared.neocom.neocom.neocomSettings import neocom_allow_blink_setting
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst
from eve.common.script.sys import idCheckers
from globalConfig.getFunctions import AllowCharacterLogoff
from localization import GetByLabel
from menu import MenuLabel
from neocom2.btnIDs import PROJECT_DISCOVERY_ID
from signals import Signal
from uihider import get_ui_hider
NUM_BLINKS = 3
import signals
INFINITE_BLINKS = -1

class BtnDataNode(utillib.KeyVal):
    __guid__ = 'neocom.BtnDataNode'
    __notifyevents__ = []
    persistChildren = True

    def __init__(self, parent = None, children = None, iconPath = None, label = None, btnID = None, btnType = None, isRemovable = True, isDraggable = True, isOpen = False, isBlinking = False, labelAbbrev = None, wndCls = None, cmdName = None, **kw):
        sm.RegisterNotify(self)
        self._ConstructSignals()
        self._parent = parent
        self.iconPath = iconPath
        self._children = children or []
        self.label = label
        self.labelAbbrev = labelAbbrev
        self.btnType = btnType
        self.btnUI = None
        self.isRemovable = isRemovable
        self.isDraggable = isDraggable
        self._isOpen = isOpen
        self._isActive = False
        self._numBlinksLeft = 0
        self.id = btnID
        self.blinkHint = ''
        self.uniqueUiName = pConst.GetUniqueNeocomPointerName(kw.get('uniqueUiNameFromWnd', None) or self.id)
        self.cmdName = cmdName
        self.wndCls = wndCls
        self.highlightState = HighlightState.normal
        self._setHasNewActivityOffThread = None
        self.destroyed = False
        self.hasNewActivity = False
        if isBlinking:
            self.SetBlinkingOn()
        if not iconPath and wndCls:
            self.iconPath = wndCls.default_iconNum
        for attrname, val in kw.iteritems():
            setattr(self, attrname, val)

        if parent:
            parent._AddChild(self)
        self._UpdateHighlightState()
        self.OnBadgeCountChanged()
        neocomSignals.on_blink_pulse.connect(self.OnNeocomBlinkPulse)

    def OnNeocomBlinkPulse(self):
        if self.IsBlinking():
            self.on_blink()
            if self._numBlinksLeft > 0 and self._numBlinksLeft != INFINITE_BLINKS:
                self._numBlinksLeft -= 1
                if not self._numBlinksLeft:
                    self._UpdateHighlightState()

    def OnBadgeCountChanged(self):
        if neocom_allow_blink_setting.is_enabled() and self.HasUnseenItems():
            self.SetBlinkingOn()
            self.on_badge_count_changed()
        self._UpdateHighlightState()

    def _ConstructSignals(self):
        self.on_active_changed = Signal('on_deactivated')
        self.on_open_changed = Signal('on_open_changed')
        self.on_child_added = Signal('on_child_added')
        self.on_child_removed = Signal('on_child_removed')
        self.on_child_moved = Signal('on_child_moved')
        self.on_badge_count_changed = signals.Signal('on_badge_count_changed')
        self.on_highlight_state_changed = signals.Signal('on_indicator_state_changed')
        self.on_has_new_activity_changed = signals.Signal('on_has_new_activity_changed')
        self.on_blink = signals.Signal('on_blink')

    def _AddChild(self, child, idx = None):
        if idx is not None:
            self._children.insert(idx, child)
        else:
            self._children.append(child)
        child._parent = self
        self.CheckContinueBlinking()
        self.Persist()
        self.on_child_added(child)

    def IsPersistant(self):
        return self.persistChildren

    def GetChildren(self):
        return self._children

    children = property(GetChildren)

    def GetParent(self):
        return self._parent

    def SetParent(self, parent, idx = None):
        self.parent.RemoveChild(self)
        self.btnUI = None
        self._parent = parent
        parent._AddChild(self, idx)

    def IsRootNodePersistant(self):
        return self.GetRootNode().IsPersistant()

    parent = property(GetParent, SetParent)

    def __repr__(self):
        return '<BtnDataNode: {} - {} children, destroyed={}>'.format(repr(self.label), len(self._children), self.destroyed)

    def Persist(self):
        self.parent.Persist()

    def GetRawData(self):
        return utillib.KeyVal(btnType=self.btnType, id=self.id, iconPath=self.iconPath, children=self._GetRawChildren())

    def _GetRawChildren(self):
        rawChildren = None
        if self._children:
            rawChildren = []
            if self.IsPersistant():
                for btnData in self._children:
                    if btnData.btnType not in neocomConst.NOTPERSISTED_BTNTYPES:
                        rawChildren.append(btnData.GetRawData())

        return rawChildren

    def SwitchWith(self, other):
        if other.parent != self.parent:
            return
        lst = self.parent._children
        indexSelf = lst.index(self)
        indexOther = lst.index(other)
        lst.insert(indexOther, lst.pop(indexSelf))
        self.parent.on_child_moved(self)
        self.Persist()

    def GetIndex(self):
        lst = self.parent._children
        return lst.index(self)

    def GetBtnDataByTypeAndID(self, id, btnType = None, recursive = False):
        for btnData in self._children:
            if btnType is None or btnData.btnType == btnType:
                if btnData.id == id:
                    return btnData
            if recursive:
                subBtnData = btnData.GetBtnDataByTypeAndID(id, btnType, True)
                if subBtnData:
                    return subBtnData

    def GetBtnDataByUniqueUiName(self, uniqueUiName, recursive = False):
        for btnData in self._children:
            if btnData.uniqueUiName == uniqueUiName:
                return btnData
            if recursive:
                subBtnData = btnData.GetBtnDataByTypeAndID(uniqueUiName, True)
                if subBtnData:
                    return subBtnData

    def GetBtnDataByWndCls(self, wndCls, recursive = False):
        if wndCls is None:
            return
        for btnData in self._children:
            if getattr(btnData, 'wndCls', None) == wndCls:
                return btnData
            if recursive:
                subBtnData = btnData.GetBtnDataByWndCls(wndCls, True)
                if subBtnData:
                    return subBtnData

    def Remove(self):
        self.parent.RemoveChild(self)
        self.btnUI = None
        self._disconnect_signals()
        self.destroyed = True
        for child in self.children:
            child.Remove()

    def _disconnect_signals(self):
        self.on_blink.clear()
        self.on_active_changed.clear()
        self.on_open_changed.clear()
        self.on_child_added.clear()
        self.on_child_removed.clear()
        self.on_child_moved.clear()
        self.on_badge_count_changed.clear()
        self.on_highlight_state_changed.clear()
        self.on_has_new_activity_changed.clear()
        neocomSignals.on_blink_pulse.disconnect(self.OnNeocomBlinkPulse)

    def RemoveChild(self, btnData):
        if btnData not in self._children:
            return
        btnData._parent = None
        self._children.remove(btnData)
        self.Persist()
        self.on_child_removed(btnData)

    def MoveTo(self, newParent, index = None):
        if newParent == self:
            return
        if not self.IsRemovable():
            return
        if not newParent.IsRootNodePersistant():
            return
        self.SetParent(newParent, index)

    def IsRemovable(self):
        if self.isRemovable:
            for btnData in self._children:
                if not btnData.IsRemovable():
                    return False

        return True

    def GetRootNode(self):
        return self.parent.GetRootNode()

    def IsDescendantOf(self, btnData):
        return self.parent._IsDescendantOf(btnData)

    def _IsDescendantOf(self, btnData):
        if self == btnData:
            return True
        return self.parent._IsDescendantOf(btnData)

    def SetBlinkingOn(self, hint = ''):
        if not self.IsBlinkingEnabled() or self._numBlinksLeft:
            return
        self._numBlinksLeft = NUM_BLINKS
        self.blinkHint = hint or ''
        self.SetHasNewActivityOn()
        self._UpdateHighlightState()

    def SetHasNewActivityOn(self):
        if self.hasNewActivity:
            return
        self.hasNewActivity = True
        self._UpdateHighlightState()
        self.on_has_new_activity_changed()
        if self._setHasNewActivityOffThread:
            self._setHasNewActivityOffThread.kill()
        if self.parent:
            self.parent.SetHasNewActivityOn()
        self._setHasNewActivityOffThread = uthread2.start_tasklet(self.SleepAndSetHasNewActivityOff)

    def SleepAndSetHasNewActivityOff(self):
        uthread2.sleep(8.0)
        if not self.parent:
            return
        self.SetHasNewActivityOff()
        self._setHasNewActivityOffThread = None

    def SetHasNewActivityOff(self):
        if not self.hasNewActivity:
            return
        self.hasNewActivity = False
        self._UpdateHighlightState()
        self.on_has_new_activity_changed()
        if self._setHasNewActivityOffThread:
            self._setHasNewActivityOffThread.kill()
        self._setHasNewActivityOffThread = None

    def SetBlinkingOff(self):
        if self._numBlinksLeft:
            self._SetBlinkingOff()
        self.CheckContinueBlinking()

    def _SetBlinkingOff(self):
        self._numBlinksLeft = 0
        self._UpdateHighlightState()

    def ClearBlinkHint(self):
        self.blinkHint = ''
        self._UpdateHighlightState()

    def GetBlinkHint(self):
        hint = self.blinkHint
        unseenHint = self.GetUnseenItemsHint()
        if unseenHint:
            if hint:
                hint += '\n'
            hint += unseenHint
        return hint

    def GetUnseenItemsHint(self):
        numItems = self.GetItemCount()
        if numItems:
            return GetByLabel('UI/Neocom/UnseenItemsHint', numItems=numItems)

    def CheckContinueBlinking(self):
        self._UpdateHighlightState()
        if self.parent:
            self.parent.CheckContinueBlinking()

    def _IsAnyChildBlinking(self):
        for btnData in self._children:
            if btnData.IsBlinking():
                return True

        return False

    def SetActive(self):
        self._isActive = True
        self.on_active_changed()
        self._UpdateHighlightState()

    def IsActive(self):
        return self._isActive

    def SetInactive(self):
        self._isActive = False
        self.on_active_changed()
        self._UpdateHighlightState()

    def SetOpen(self):
        self._isOpen = True
        self.on_open_changed()
        self._UpdateHighlightState()

    def SetClosed(self):
        self._isOpen = False
        self._isActive = False
        self.on_open_changed()
        self._UpdateHighlightState()

    def IsOpen(self):
        return self._isOpen

    def _UpdateHighlightState(self):
        oldState = self.highlightState
        if self.IsActive():
            self.highlightState = HighlightState.active
        elif self.HasUnseenItems() or self.HasAnyChildUnseenItems() or self.IsBlinking() or self.HasNewActivity() or self.HasAnyChildNewActivity() or self.blinkHint:
            self.highlightState = HighlightState.important
        elif self.IsOpen():
            self.highlightState = HighlightState.open
        else:
            self.highlightState = HighlightState.normal
        if oldState != self.highlightState:
            self.on_highlight_state_changed()
        if self.parent:
            self.parent._UpdateHighlightState()

    def HasNewActivity(self):
        return self.hasNewActivity

    def HasAnyChildNewActivity(self):
        for btnData in self._children:
            if btnData.HasNewActivity() or btnData.HasAnyChildNewActivity():
                return True

        return False

    def HasAnyChildUnseenItems(self):
        for btnData in self._children:
            if btnData.HasUnseenItems() or btnData.HasAnyChildUnseenItems():
                return True

        return False

    def IsAvailable(self):
        return True

    def GetMenu(self):
        m = []
        if self.isRemovable and not self._isOpen:
            m.append((localization.GetByLabel('UI/Neocom/RemoveShortcut'), self.Remove))
        if session.role & ROLE_PROGRAMMER:
            m.append(('GM: Blink!', sm.GetService('neocom').Blink, (self.id, 'Blinking for no reason!')))
        if self.IsBlinkingEnabled():
            m.append((MenuLabel('UI/Neocom/ConfigBlinkOff'), self.DisableBlinking))
        else:
            m.append((MenuLabel('UI/Neocom/ConfigBlinkOn'), self.EnableBlinking))
        return m

    def IsBlinkingEnabled(self):
        return settings.char.ui.Get('neoblinkByID', {}).get(self.id, True)

    def EnableBlinking(self):
        self._SetBlink(True)

    def DisableBlinking(self):
        self._SetBlink(False)

    def IsBlinking(self):
        return self._numBlinksLeft or self._IsAnyChildBlinking()

    def _SetBlink(self, state):
        neoBlinkByID = settings.char.ui.Get('neoblinkByID', {})
        neoBlinkByID[self.id] = state
        settings.char.ui.Set('neoblinkByID', neoBlinkByID)

    def IsButtonInScope(self):
        if self.wndCls and get_ui_hider().is_ui_element_hidden(self.wndCls.default_windowID):
            return False
        if self.id in ('corpHangar', 'corpDeliveriesHangar') and idCheckers.IsNPCCorporation(session.corpid):
            return False
        if self.id == 'corpHangar' and not self._HasCorpOffice():
            return False
        if self.id == PROJECT_DISCOVERY_ID and not sm.GetService('projectDiscoveryClient').is_enabled():
            return False
        if self.id == 'logoff' and not AllowCharacterLogoff(sm.GetService('machoNet')):
            return False
        if self.btnType in neocomConst.COMMAND_BTNTYPES:
            if not uicore.cmd.GetCommandToExecute(self.cmdName):
                return False
        if not self.IsAvailable():
            return False
        if self.wndCls:
            scope = self.wndCls.default_scope
            if not scope or scope == uiconst.SCOPE_ALL:
                return True
            if session.stationid and scope & uiconst.SCOPE_STATION:
                return True
            if session.structureid:
                if session.shipid == session.structureid:
                    return scope & uiconst.SCOPE_INFLIGHT
                return scope & uiconst.SCOPE_STRUCTURE
            return session.solarsystemid and scope & uiconst.SCOPE_INFLIGHT
        return True

    def GetChildrenInScope(self):
        return [ btnData for btnData in self.children if btnData.IsButtonInScope() ]

    def _HasCorpOffice(self):
        return sm.GetService('officeManager').GetCorpOfficeAtLocation() is not None

    def RemoveChildWindow(self, wndInstanceID):
        for btnChildData in self.children:
            wnd = getattr(btnChildData, 'wnd', None)
            if not wnd or wnd.destroyed or wnd.windowInstanceID == wndInstanceID:
                btnChildData.Remove()
            elif not wnd.IsKillable() and not wnd.IsMinimized():
                btnChildData.Remove()

        if not self.children:
            if self.btnType == neocomConst.BTNTYPE_WINDOW:
                self.Remove()
            else:
                self.SetClosed()

    def HasUnseenItems(self):
        if not self.GetRootNode().IsTopLevel() and sm.GetService('neocom').GetTopLevelBtnData(self.id):
            return False
        return bool(self.GetItemCount())

    def GetItemCount(self):
        return 0
