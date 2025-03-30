#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\baseInfoWindow.py
import uthread
from carbonui.control.window import Window
from eve.client.script.ui.control.historyBuffer import HistoryBuffer

class BaseInfoWindow(Window):

    def ApplyAttributes(self, attributes):
        self.infoType = None
        self.typeID = None
        self.itemID = None
        self.rec = None
        self.isLoading = False
        self.pendingLoadData = None
        self.isBrowsing = False
        self.maintabs = None
        self.isUnlockedWithExpertSystem = None
        self.history = HistoryBuffer()
        super(BaseInfoWindow, self).ApplyAttributes(attributes)
        if len(self.__notifyevents__) > 0:
            sm.RegisterNotify(self)
        typeID = attributes.get('typeID', None)
        itemID = attributes.get('itemID', None)
        rec = attributes.get('rec', None)
        parentID = attributes.get('parentID', None)
        abstractinfo = attributes.get('abstractinfo', None)
        selectTabType = attributes.get('selectTabType', None)
        params = attributes.get('params', None)
        self.ConstructLayout()
        uthread.new(self.ReconstructInfoWindow, typeID, itemID, rec=rec, parentID=parentID, abstractinfo=abstractinfo, selectTabType=selectTabType, params=params)

    def ConstructLayout(self):
        pass

    def ReconstructInfoWindow(self, typeID, itemID = None, rec = None, parentID = None, abstractinfo = None, tabNumber = None, branchHistory = True, selectTabType = None, params = None):
        if self.isLoading:
            self.pendingLoadData = (typeID,
             itemID,
             rec,
             parentID,
             abstractinfo,
             tabNumber,
             branchHistory,
             selectTabType,
             params)
            return
        self._ReconstructInfoWindow(typeID, itemID, rec, parentID, abstractinfo, tabNumber, branchHistory, selectTabType, params)
        if self.pendingLoadData:
            pendingData = self.pendingLoadData
            self.pendingLoadData = None
            self.ReconstructInfoWindow(*pendingData)

    def _ReconstructInfoWindow(self, typeID, itemID = None, rec = None, parentID = None, abstractinfo = None, tabNumber = None, branchHistory = True, selectTabType = None, params = None):
        pass

    def UpdateHistoryData(self):
        self.history.UpdateCurrent(self.GetHistoryData())

    def GetHistoryData(self):
        return (self.typeID,
         self.itemID,
         self.rec,
         self.parentID,
         self.abstractinfo,
         self.GetSelectedTabIdx())

    def GetSelectedTabIdx(self):
        if self.maintabs:
            return self.maintabs.GetSelectedIdx()
        else:
            return 0

    def Close(self, *args, **kwargs):
        try:
            sm.GetService('info').UnregisterWindow(self)
        finally:
            Window.Close(self, *args, **kwargs)

    def IsUpgradeable(self):
        try:
            godmaType = sm.GetService('godma').GetType(self.typeID)
            return godmaType.constructionType != 0
        except AttributeError:
            return False
