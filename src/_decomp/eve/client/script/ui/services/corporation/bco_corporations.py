#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corporation\bco_corporations.py
import uthread
import blue
import localization
from carbonui.control.window import Window
from eve.client.script.ui.services.corporation.bco_base import BaseCorpObject
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.common.lib import appConst as const
from eve.common.script.sys.rowset import IndexRowset, Rowset

class CorporationsO(BaseCorpObject):
    __guid__ = 'corpObject.corporations'

    def __init__(self, boundObject):
        BaseCorpObject.__init__(self, boundObject)
        self.corporationByCorporationID = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'charid' in change:
            self.corporationByCorporationID = None
        if 'corpid' in change:
            oldID, newID = change['corpid']
            if newID is not None:
                if self.corporationByCorporationID is not None and self.corporationByCorporationID.has_key(newID):
                    del self.corporationByCorporationID[newID]

    def Reset(self):
        if self.has_key(eve.session.corpid):
            del self.corporationByCorporationID[eve.session.corpid]

    def has_key(self, corpID):
        if self.corporationByCorporationID is not None:
            return self.corporationByCorporationID.has_key(corpID)

    def GetCorporation(self, corpid = None, new = 0):
        if corpid is None:
            corpid = eve.session.corpid
        if self.corporationByCorporationID is not None and self.corporationByCorporationID.has_key(corpid) and not new:
            return self.corporationByCorporationID[corpid]
        if corpid == eve.session.corpid:
            corporation = self.GetCorpRegistry().GetCorporation()
        else:
            corporation = sm.RemoteSvc('corpmgr').GetCorporations(corpid)
        self.LoadCorporation(corporation)
        return self.corporationByCorporationID[corpid]

    def GetCorporations(self, corporations, new = 0):
        rows = Rowset(self.GetCorporation().header)
        for corporationID in corporations:
            try:
                rows.lines.append(self.GetCorporation(corporationID))
            except Exception:
                self.LogWarn('GetCorporations() could not get corporation with id = %s. Probably invalid.' % corporationID)

        return rows

    def LoadCorporation(self, corporation):
        if self.corporationByCorporationID is None:
            if type(corporation) == blue.DBRow:
                self.corporationByCorporationID = IndexRowset(corporation.__columns__, [list(corporation)], 'corporationID')
            else:
                self.corporationByCorporationID = IndexRowset(corporation.header, [corporation.line], 'corporationID')
        else:
            line = []
            for columnName in self.corporationByCorporationID.header:
                line.append(getattr(corporation, columnName))

            self.corporationByCorporationID[corporation.corporationID] = line

    def OnCorporationChanged(self, corpID, change):
        bAdd, bRemove = self.GetAddRemoveFromChange(change)
        if self.corporationByCorporationID is not None:
            if bAdd:
                if len(change) != len(self.corporationByCorporationID.header):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return
                line = []
                for columnName in self.corporationByCorporationID.header:
                    line.append(change[columnName][1])

                self.corporationByCorporationID[corpID] = line
            else:
                if not self.corporationByCorporationID.has_key(corpID):
                    return
                if bRemove:
                    del self.corporationByCorporationID[corpID]
                else:
                    corporation = self.corporationByCorporationID[corpID]
                    for columnName in corporation.header:
                        if not change.has_key(columnName):
                            continue
                        setattr(corporation, columnName, change[columnName][1])

                    if cfg.corptickernames.data.has_key(corpID):
                        header = cfg.corptickernames.header
                        line = cfg.corptickernames.data[corpID]
                        i = -1
                        for columnName in header:
                            i = i + 1
                            if not change.has_key(columnName):
                                continue
                            line[i] = change[columnName][1]

            updateDivisionNames = 0
            loadLogo = 0
            showOffices = 0
            loadButtons = 0
            resetCorpWindow = 0
            if eve.session.corpid == corpID:
                if 'division1' in change or 'division2' in change or 'division3' in change or 'division4' in change or 'division5' in change or 'division6' in change or 'division7' in change:
                    updateDivisionNames = 1
            if 'shape1' in change or 'shape2' in change or 'shape3' in change or 'color1' in change or 'color2' in change or 'color3' in change or 'typeface' in change:
                if eve.session.corpid == corpID:
                    loadLogo = 1
            if sm.GetService('officeManager').GetCorpOfficeAtLocation():
                showOffices = 1
            if 'ceoID' in change and session.corpid == corpID:
                if session.charid in change['ceoID']:
                    loadButtons = 1
                sm.GetService('corpvotes').canRunForCEO = None
                resetCorpWindow = 1
                showOffices = 1
            if resetCorpWindow:
                sm.GetService('corpui').ResetWindow(1)
            corpUISignals.on_corporation_changed(corpID)
            if updateDivisionNames:
                uthread.new(self.__UpdateDivisionNamesInTheUI).context = 'svc.corp.OnCorporationChanged'

    def GetDivisionNames(self):
        corp = self.GetCorporation()
        return {0: localization.GetByLabel('UI/Inventory/GoalDeliveriesHangar'),
         1: corp.division1 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionFirst'),
         2: corp.division2 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionSecond'),
         3: corp.division3 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionThird'),
         4: corp.division4 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionFourth'),
         5: corp.division5 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionFifth'),
         6: corp.division6 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionSixth'),
         7: corp.division7 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionSeventh'),
         8: localization.GetByLabel('UI/Corporations/Common/CorporateDivisionMasterWallet'),
         9: corp.walletDivision2 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionWalletSecond'),
         10: corp.walletDivision3 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionWalletThird'),
         11: corp.walletDivision4 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionWalletFourth'),
         12: corp.walletDivision5 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionWalletFifth'),
         13: corp.walletDivision6 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionWalletSixth'),
         14: corp.walletDivision7 or localization.GetByLabel('UI/Corporations/Common/CorporateDivisionWalletSeventh'),
         15: localization.GetByLabel('UI/Inventory/GoalDeliveriesHangar')}

    def __UpdateDivisionNamesInTheUI(self):
        wndid = None
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        if office is None:
            self.LogInfo('There are no offices here.')
            return
        wndid = 'corpHangar_%s' % office.officeID
        self.LogInfo("Char's corp has a hangar wndid", wndid)
        wnd = Window.GetIfOpen(windowID=wndid)
        if not wnd:
            self.LogInfo("Can't find char's corp hangar window")
        else:
            divisions = self.GetDivisionNames()
            self.LogInfo("Found char's corp hangar window, applying new division names", divisions)
            wnd.SetDivisionalHangarNames(divisions)

    def GetCostForCreatingACorporation(self):
        return const.corporationStartupCost

    def UpdateCorporationAbilities(self):
        return self.GetCorpRegistry().UpdateCorporationAbilities()

    def UpdateLogo(self, shape1, shape2, shape3, color1, color2, color3, typeface):
        return self.GetCorpRegistry().UpdateLogo(shape1, shape2, shape3, color1, color2, color3, typeface)

    def UpdateCorporation(self, description, url, iskTaxRate, isRecruiting, loyaltyPointTaxRate):
        return self.GetCorpRegistry().UpdateCorporation(description, url, iskTaxRate, isRecruiting, loyaltyPointTaxRate)

    def GetSuggestedTickerNames(self, corporationName):
        return self.GetCorpRegistry().GetSuggestedTickerNames(corporationName)

    def AddCorporation(self, corporationName, tickerName, description, url = '', iskTaxRate = 0.0, shape1 = None, shape2 = None, shape3 = None, color1 = None, color2 = None, color3 = None, typeface = None, applicationsEnabled = 1, friendlyFireEnabled = False, loyaltyPointTaxRate = 0.0):
        return self.GetCorpRegistry().AddCorporation(corporationName, tickerName, description, url, iskTaxRate, shape1, shape2, shape3, color1, color2, color3, typeface, applicationsEnabled, friendlyFireEnabled, loyaltyPointTaxRate)
