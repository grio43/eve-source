#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_direct_enlistment_mgt.py
import carbonui
import localization
from carbonui import uiconst, TextColor
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveColor
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelSmall
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.services.corporation.corp_util import HasRole
from eve.common.lib import appConst
from eve.common.script.util.facwarCommon import GetAllFWFactions
from localization.formatters import FormatGenericList
import locks

class CorpDirectEnlistmentMgt(Container):
    __notifyevents__ = ['OnCorporationChanged']
    is_loaded = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.corpSvc = sm.GetService('corp')

    def Load(self, *args):
        if self.is_loaded:
            return
        self.is_loaded = True
        WhitelistManagement(parent=self, canEdit=HasRole(appConst.corpRoleDirector))


class WhitelistManagement(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.inited = False
        self.fwEnlistmentSvc = sm.GetService('fwEnlistmentSvc')
        self.canEdit = attributes.get('canEdit')
        allFactions = GetAllFWFactions()
        self.allFactions = sorted(allFactions, key=lambda x: cfg.eveowners.Get(x).name)
        self.allowedFactionIDs = []
        self.cbByFactionID = {}
        self.ConstructLayout()

    def OnSettingChange(self, checkbox):
        self.UpdateWarnCont()

    def UpdateWarnCont(self):
        allowedFactionIDs, notAllowedFactionIDs = self.GetAllowedNotAllowedFromCheckboxes()
        if set(allowedFactionIDs) == set(self.allowedFactionIDs):
            self.warnCont.Hide()
        else:
            self.warnCont.Show()

    def ConstructLayout(self):
        with locks.TempLock('WhitelistManagementLayout'):
            if not self.inited:
                self._ConstructLayout()
                self.inited = True

    def _ConstructLayout(self):
        self.Flush()
        carbonui.TextBody(parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Corporations/FWDirectEnlistment/WhiteListInfo'), color=TextColor.SECONDARY)
        cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padTop=16)
        self.allowedFactionIDs = self.fwEnlistmentSvc.GetCorpAllowedEnlistmentFactions(session.corpid)
        for factionID in self.allFactions:
            rowCont = Container(parent=cont, align=uiconst.TOTOP, height=30)
            checked = factionID in self.allowedFactionIDs
            checkbox = Checkbox(parent=rowCont, align=uiconst.TOLEFT, callback=self.OnSettingChange, checked=checked, text=cfg.eveowners.Get(factionID).name, settingsKey=factionID)
            self.cbByFactionID[factionID] = checkbox
            if not self.canEdit:
                checkbox.Disable()

        if not self.canEdit:
            EveLabelSmall(parent=self, text=localization.GetByLabel('UI/Corporations/FWDirectEnlistment/CEOsOnly'), align=uiconst.TOTOP, color=eveColor.CHERRY_RED)
        self.warnCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP)
        self.warnCont.Hide()
        detailsCont = ContainerAutoSize(parent=self.warnCont, align=uiconst.TOTOP, padTop=10, padBottom=20)
        Fill(bgParent=detailsCont, color=(0.0, 0.0, 0.0, 0.25))
        self.changesButtonGroup = ButtonGroup(button_size_mode=ButtonSizeMode.STRETCH, parent=self.warnCont, align=uiconst.TOTOP, padTop=5)
        Button(parent=self.changesButtonGroup, label=localization.GetByLabel('UI/Corporations/FWDirectEnlistment/ApplyLabel'), func=self.ApplyChanges)
        Button(parent=self.changesButtonGroup, label=localization.GetByLabel('UI/Corporations/FWDirectEnlistment/CancelLabel'), func=self.BinChanges)

    def ApplyChanges(self, *args):
        allowedFactionIDs, notAllowedFactionIDs = self.GetAllowedNotAllowedFromCheckboxes()
        if notAllowedFactionIDs:
            notAllowedNames = FormatGenericList([ cfg.eveowners.Get(factionId).name for factionId in notAllowedFactionIDs ], useConjunction=True)
            ret = eve.Message('ApplyDirectEnlistmentBlacklistSettings', {'factions': notAllowedNames}, uiconst.YESNO)
            if ret != uiconst.ID_YES:
                return
        else:
            allowedName = FormatGenericList([ cfg.eveowners.Get(factionId).name for factionId in allowedFactionIDs ], useConjunction=True)
            ret = eve.Message('ApplyDirectEnlistmentSettings', {'factions': allowedName}, uiconst.YESNO)
            if ret != uiconst.ID_YES:
                return
        self.fwEnlistmentSvc.SetCorpAllowedEnlistmentFactions(allowedFactionIDs)
        self.allowedFactionIDs = self.fwEnlistmentSvc.GetCorpAllowedEnlistmentFactions(session.corpid)
        self.ReconstructLayout()

    def ReconstructLayout(self):
        self.inited = False
        self.ConstructLayout()

    def GetAllowedNotAllowedFromCheckboxes(self):
        allowedFactionIDs = []
        notAllowed = []
        for factionID, cb in self.cbByFactionID.iteritems():
            if cb.checked:
                allowedFactionIDs.append(factionID)
            else:
                notAllowed.append(factionID)

        return (allowedFactionIDs, notAllowed)

    def BinChanges(self, *args):
        self.ReconstructLayout()
