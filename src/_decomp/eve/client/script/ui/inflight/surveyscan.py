#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\surveyscan.py
import sys
import evetypes
import localization
import utillib
from carbon.common.script.util.format import FmtAmt, FmtDist
from carbonui import uiconst
from carbonui.uicore import uicore
from dogma import units
from eve.client.script.parklife import states as state
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.inflight.bracketsAndTargets.targetIconCont import TargetIconCont
from eve.common.lib import appConst as const
from eveservices.menu import GetMenuService

class SurveyScanView(Window):
    __guid__ = 'form.SurveyScanView'
    default_windowID = 'SurveyScanView'
    __notifyevents__ = ['OnStateChange']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.targetSvc = sm.GetService('target')
        self.scope = uiconst.SCOPE_INFLIGHT
        self.SetCaption(localization.GetByLabel('UI/Inflight/Scanner/SurveyScanResults'))
        self.DefineButtons(uiconst.OK, okLabel=localization.GetByLabel('UI/Inventory/Clear'), okFunc=self.ClearAll)
        self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'surveyscan_scroll'
        sm.RegisterNotify(self)

    def _OnClose(self, *args):
        sm.GetService('surveyScan').Clear()

    def ClearAll(self, *args):
        sm.GetService('surveyScan').Clear()

    def Clear(self):
        self.sr.scroll.Load(contentList=[])

    def SetEntries(self, entries):
        scrolllist = []
        asteroidTypes = {}
        headers = [localization.GetByLabel('UI/Common/Ore'),
         localization.GetByLabel('UI/Common/Quantity'),
         localization.GetByLabel('UI/Common/Volume'),
         localization.GetByLabel('UI/Common/Distance')]
        for ballID, (typeID, qty) in entries.iteritems():
            if not asteroidTypes.has_key(typeID):
                asteroidTypes[typeID] = [(ballID, qty)]
            else:
                asteroidTypes[typeID].append((ballID, qty))

        currentTargets = self.targetSvc.GetTargets()
        scrolllist = []
        for asteroidType in asteroidTypes:
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetTypeSubContent,
             'label': evetypes.GetName(asteroidType),
             'id': ('TypeSel', asteroidType),
             'groupItems': asteroidTypes[asteroidType],
             'typeID': asteroidType,
             'showlen': 1,
             'sublevel': 0,
             'state': 'locked',
             'currentTargetIDs': currentTargets.keys()}))

        scrolllist = localization.util.Sort(scrolllist, key=lambda x: x.label)
        self.sr.scroll.Load(contentList=scrolllist, headers=headers)

    def GetTypeSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        bp = sm.GetService('michelle').GetBallpark()
        for ballID, qty in nodedata.groupItems:
            try:
                dist = bp.GetBall(ballID).surfaceDist
            except AttributeError:
                dist = 0
                import traceback
                traceback.print_exc()
                sys.exc_clear()

            data = utillib.KeyVal()
            evetypes.GetVolume(nodedata.typeID)
            volume = evetypes.GetVolume(nodedata.typeID) * qty
            volumeText = localization.GetByLabel('UI/InfoWindow/ValueAndUnit', value=FmtAmt(volume, showFraction=0), unit=units.get_display_name(const.unitVolume))
            rightLabelParts = [FmtAmt(qty), volumeText, FmtDist(dist)]
            data.label = '%s<t><right>%s' % (evetypes.GetName(nodedata.typeID), '<t><right>'.join(rightLabelParts))
            data.itemID = ballID
            data.typeID = nodedata.typeID
            data.GetMenu = self.OnGetEntryMenu
            data.OnClick = self.OnEntryClick
            data.showinfo = 1
            data.isTarget = ballID in nodedata.currentTargetIDs
            data.sublevel = 1
            data.Set('sort_' + localization.GetByLabel('UI/Common/Distance'), dist)
            data.Set('sort_' + localization.GetByLabel('UI/Common/Quantity'), qty)
            data.Set('sort_' + localization.GetByLabel('UI/Common/Volume'), volume)
            entry = GetFromClass(SurveyScanEntry, data)
            scrolllist.append(entry)

        return scrolllist

    def OnEntryClick(self, entry, *args):
        sm.GetService('stateSvc').SetState(entry.sr.node.itemID, state.selected, 1)
        if self.targetSvc.IsTarget(entry.sr.node.itemID):
            sm.GetService('stateSvc').SetState(entry.sr.node.itemID, state.activeTarget, 1)
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            self.targetSvc.TryLockTarget(entry.sr.node.itemID)
        elif uicore.uilib.Key(uiconst.VK_MENU):
            GetMenuService().TryLookAt(entry.sr.node.itemID)

    def OnGetEntryMenu(self, entry, *args):
        return GetMenuService().CelestialMenu(entry.sr.node.itemID)

    def OnStateChange(self, itemID, flag, newState, *args):
        if flag not in (state.targeting, state.targeted):
            return
        for node in self.sr.scroll.GetNodes():
            if node.itemID == itemID and node.panel is not None:
                node.panel.OnChangingState(flag, newState)
                return


class SurveyScanEntry(Generic):

    def ApplyAttributes(self, attributes):
        Generic.ApplyAttributes(self, attributes)
        self.targetIconCont = TargetIconCont(parent=self, pos=(2, 0, 16, 16), iconSize=16, align=uiconst.CENTERLEFT)

    def Load(self, node):
        sublevelCorrection = self.sr.node.scroll.sr.get('sublevelCorrection', 0) if self.sr.node.scroll else 0
        node.sublevel += sublevelCorrection
        Generic.Load(self, node)
        targeting, targeted = sm.GetService('stateSvc').GetStates(node.itemID, [state.targeting, state.targeted])
        if targeting:
            self.targetIconCont.StartTargeting()
        elif targeted:
            self.targetIconCont.SetTargetedIcon()

    def OnChangingState(self, flag, newState):
        if flag == state.targeting:
            self.targetIconCont.HandleTargetingChanges(newState)
        elif flag == state.targeted:
            self.targetIconCont.HandleTargetedChanges(newState)
