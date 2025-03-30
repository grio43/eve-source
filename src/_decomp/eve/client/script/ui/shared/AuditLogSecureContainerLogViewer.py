#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\AuditLogSecureContainerLogViewer.py
import sys
import blue
import carbon.common.script.util.logUtil as log
import eveicon
import evetypes
import localization
from carbon.common.script.util.format import FmtDate, ParseDate
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.common.script.sys import idCheckers
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from menu import MenuLabel

class AuditLogSecureContainerLogViewer(Window):
    default_windowID = 'alsclogviewer'
    default_minSize = (400, 400)
    default_width = 700
    default_height = 400
    default_captionLabelPath = 'UI/AuditContainerLogViewer/AuditLogTitle'

    def ApplyAttributes(self, attributes):
        super(AuditLogSecureContainerLogViewer, self).ApplyAttributes(attributes)
        itemID = attributes.itemID
        self.container = sm.GetService('invCache').GetInventoryFromId(itemID)
        self.itemID = itemID
        self.logIDmax = None
        self.logIDmin = None
        self.logOptions = Container(name='logOptions', parent=self.sr.main, align=uiconst.TOTOP, height=SingleLineEditText.default_height, idx=1, padTop=8)
        navButtonCont = Container(name='navButtonCont', parent=self.logOptions, align=uiconst.TORIGHT, width=54)
        self.wndBackBtn = ButtonIcon(parent=navButtonCont, align=uiconst.CENTERLEFT, texturePath=eveicon.navigate_back, iconSize=16, hint=localization.GetByLabel('UI/Common/Previous'), func=lambda : self.BrowseLog(0), args=())
        self.wndFwdBtn = ButtonIcon(parent=navButtonCont, align=uiconst.CENTERLEFT, left=24, texturePath=eveicon.navigate_forward, iconSize=16, hint=localization.GetByLabel('UI/Common/More'), func=lambda : self.BrowseLog(1), args=())
        self.fromDate = self.GetNow()
        self.wndFromDate = SingleLineEditText(name='fromdate', parent=self.logOptions, setvalue=self.fromDate, align=uiconst.TOPLEFT, pos=(0, 0, 80, 0), maxLength=16)
        self.wndFromDate.OnReturn = self.GetDate
        dateLabel = localization.GetByLabel('UI/Common/Date')
        eveLabel.EveHeaderSmall(text=dateLabel, parent=self.wndFromDate, width=200, top=-12, state=uiconst.UI_NORMAL)
        self.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(0, 8, 0, 0))
        self.ViewLogForContainer()

    def GetDate(self):
        self.ViewLogForContainer(ParseDate(self.wndFromDate.GetValue()))

    def GetNow(self):
        return FmtDate(blue.os.GetWallclockTime(), 'sn')

    def BrowseLog(self, direction, *args):
        fromDate = None
        if self.fromDate != self.wndFromDate.GetValue():
            fromDate = ParseDate(self.wndFromDate.GetValue())
        if direction == 1:
            fromLogID = self.logIDmax
        else:
            fromLogID = self.logIDmin
        self.ViewLogForContainer(fromDate=fromDate, fromLogID=fromLogID, forward=direction)

    def ViewLogForContainer(self, fromDate = None, fromLogID = None, forward = 1):
        log.LogInfo('ViewLogForContainer fromDate:', fromDate, 'fromLogID:', fromLogID, 'forward:', forward)
        if self is None or self.destroyed:
            return
        try:
            if fromDate is None and fromLogID is None:
                if forward == 1:
                    fromLogID = self.logIDmax
                else:
                    fromLogID = self.logIDmin
                if fromLogID is None:
                    fromLogID = 1
            scrolllist = []
            self.ShowLoad()
            headers = [localization.GetByLabel('UI/Common/Date'),
             localization.GetByLabel('UI/Common/Location'),
             localization.GetByLabel('UI/AuditContainerLogViewer/SubLocation'),
             localization.GetByLabel('UI/AuditContainerLogViewer/Who'),
             localization.GetByLabel('UI/AuditContainerLogViewer/Action'),
             localization.GetByLabel('UI/AuditContainerLogViewer/Status'),
             localization.GetByLabel('UI/Common/Type'),
             localization.GetByLabel('UI/AuditContainerLogViewer/QuantityOwner')]
            logs = self.container.ALSCLogGet(fromDate, fromLogID, forward)
            log.LogInfo('result count:', len(logs))
            if len(logs):
                self.logIDmax = None
                self.logIDmin = None
            for contLog in logs:
                log.LogInfo('log:', contLog)
                subLocation = None
                if self.logIDmax is None or self.logIDmax < contLog.logID:
                    self.logIDmax = contLog.logID
                if self.logIDmin is None or self.logIDmin > contLog.logID:
                    self.logIDmin = contLog.logID
                if contLog.inventoryMgrLocationID == contLog.locationID:
                    if contLog.flagID == const.flagHangar:
                        subLocation = localization.GetByLabel('UI/AuditContainerLogViewer/PersonalHangar')
                elif contLog.flagID in const.corpDivisionsByFlag:
                    division = const.corpDivisionsByFlag[contLog.flagID]
                    subLocation = sm.GetService('corp').GetDivisionNames()[division + 1]
                if subLocation is None:
                    location = cfg.evelocations.GetIfExists(contLog.locationID)
                    if location is not None:
                        subLocation = location.locationName
                    else:
                        subLocation = '%s' % contLog.flagID
                action = '%s' % contLog.actionID
                arg1 = '%s' % contLog.arg1
                arg2 = '%s' % contLog.arg2
                if contLog.actionID == const.ALSCActionAssemble:
                    action = localization.GetByLabel('UI/AuditContainerLogViewer/Assembled')
                    arg1 = evetypes.GetName(contLog.arg2)
                    arg2 = cfg.eveowners.Get(contLog.arg1).ownerName
                elif contLog.actionID == const.ALSCActionRepackage:
                    action = localization.GetByLabel('UI/AuditContainerLogViewer/Repackaged')
                    arg1 = arg2 = localization.GetByLabel('UI/Generic/NotAvailableShort')
                elif contLog.actionID == const.ALSCActionSetName:
                    action = localization.GetByLabel('UI/AuditContainerLogViewer/SetName')
                    arg1 = arg2 = localization.GetByLabel('UI/Generic/NotAvailableShort')
                elif contLog.actionID == const.ALSCActionSetPassword:
                    action = localization.GetByLabel('UI/AuditContainerLogViewer/SetPassword')
                    if contLog.arg1 == const.SCCPasswordTypeGeneral:
                        arg1 = localization.GetByLabel('UI/Generic/General')
                    elif contLog.arg1 == const.SCCPasswordTypeConfig:
                        arg1 = localization.GetByLabel('UI/AuditContainerLogViewer/Configuration')
                    arg2 = localization.GetByLabel('UI/Generic/NotAvailableShort')
                elif contLog.actionID == const.ALSCActionLock:
                    action = localization.GetByLabel('UI/AuditContainerLogViewer/Lock')
                    arg1 = evetypes.GetName(contLog.arg1)
                    arg2 = '%s' % contLog.arg2
                elif contLog.actionID == const.ALSCActionUnlock:
                    action = localization.GetByLabel('UI/AuditContainerLogViewer/Unlock')
                    arg1 = evetypes.GetName(contLog.arg1)
                    arg2 = '%s' % contLog.arg2
                elif contLog.actionID == const.ALSCActionEnterPassword:
                    action = localization.GetByLabel('UI/AuditContainerLogViewer/EnterPassword')
                    if contLog.arg1 == const.SCCPasswordTypeGeneral:
                        arg1 = localization.GetByLabel('UI/Generic/General')
                    elif contLog.arg1 == const.SCCPasswordTypeConfig:
                        arg1 = localization.GetByLabel('UI/AuditContainerLogViewer/Configuration')
                    arg2 = localization.GetByLabel('UI/Generic/NotAvailableShort')
                elif contLog.actionID == const.ALSCActionConfigure:
                    action = localization.GetByLabel('UI/AuditContainerLogViewer/Configure')
                    arg1 = arg2 = localization.GetByLabel('UI/Generic/NotAvailableShort')
                failLabel = localization.GetByLabel('UI/AuditContainerLogViewer/Fail')
                successLabel = localization.GetByLabel('UI/AuditContainerLogViewer/Success')
                failSucceed = [(failLabel, '0xffff0000'), (successLabel, '0xff00ff00')][contLog.status]
                label = '%s' % FmtDate(contLog.logDate)
                label += '<t>%s' % cfg.evelocations.Get(contLog.inventoryMgrLocationID).locationName
                label += '<t>%s' % subLocation
                label += '<t>%s' % cfg.eveowners.Get(contLog.actorID).ownerName
                label += '<t>%s' % action
                label += '<t><color=%s>%s</color>' % (failSucceed[1], failSucceed[0])
                label += '<t>%s' % arg1
                label += '<t>%s' % arg2
                scrolllist.append(GetFromClass(Generic, {'label': label,
                 'entryData': contLog,
                 'GetMenu': self.GetDataMenu}))

            self.scroll.Load(None, scrolllist, headers=headers)
            if len(logs) == 50:
                self.wndBackBtn.Enable()
                self.wndFwdBtn.Enable()
            if forward == 1 and len(logs) < 50:
                self.wndBackBtn.Enable()
                self.wndFwdBtn.Disable()
            if forward == 0 and len(logs) < 50:
                self.wndBackBtn.Disable()
                self.wndFwdBtn.Enable()
        except UserError as e:
            eve.Message(e.msg, e.dict)
            sys.exc_clear()
            self.Close()
        finally:
            if not self.destroyed:
                self.HideLoad()

    def GetDataMenu(self, entry):
        m = []
        if entry.sr.node.entryData:
            contLog = entry.sr.node.entryData
            if idCheckers.IsSolarSystem(contLog.locationID):
                itemID, typeID = contLog.inventoryMgrLocationID, const.typeSolarSystem
            else:
                itemID, typeID = contLog.inventoryMgrLocationID, const.groupStation
            m.append(MenuEntryData(MenuLabel('UI/Common/Location'), subMenuData=GetMenuService().CelestialMenu(itemID=itemID, mapItem=None, typeID=typeID), texturePath=eveicon.location))
            m += [None]
            operatorLabel = MenuLabel('UI/AuditContainerLogViewer/Operator', {'ownerName': cfg.eveowners.Get(contLog.actorID)})
            m.append(MenuEntryData(operatorLabel, subMenuData=GetMenuService().CharacterMenu(contLog.actorID), texturePath=eveicon.person))
            m += [None]
        return m
