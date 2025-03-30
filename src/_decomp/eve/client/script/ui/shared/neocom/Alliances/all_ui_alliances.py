#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\all_ui_alliances.py
import carbonui.const as uiconst
import localization
from carbonui.control.tabGroup import TabGroup
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import FormAlliancesApplications
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import FormAlliancesBulletins, FormAlliancesHome
from eve.client.script.ui.shared.neocom.Alliances.all_ui_members import FormAlliancesMembers
from eve.client.script.ui.shared.neocom.Alliances.all_ui_rankings import FormAlliancesRankings
from eve.client.script.ui.shared.neocom.Alliances.all_ui_sovereignty import FormAlliancesSovereignty
from eve.client.script.ui.shared.neocom.Alliances.all_ui_systems import FormAlliancesSystems
from eve.client.script.ui.shared.neocom.addressBook.contactsConst import TAB_ALLIANCECONTACTS
from eve.client.script.ui.shared.neocom.addressBook.contactsForm import ContactsForm
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from inventorycommon.util import IsNPC
from menucheckers import SessionChecker

class FormAlliances(Container):
    __guid__ = 'form.Alliances'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)

    def Load(self, key):
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.sr.wndViewParent = Container(name='wndViewParent', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self)
            if session.allianceid:
                self.contactsPanel = ContactsForm(name=CorpPanel.ALLIANCES_CONTACTS, parent=self, contactType=TAB_ALLIANCECONTACTS)
            else:
                self.contactsPanel = eveScroll.Scroll(name=CorpPanel.ALLIANCES_CONTACTS, parent=self)
            self.sr.tabs = TabGroup(name='tabparent', parent=self, idx=0)
            self.sr.tabs.Startup(self._GetTabs(), 'corpaccounts')
            return
        self.LoadViewClass(key)

    def GetHomeTabHint(self):
        tabHint = ''
        if session.allianceid is None:
            corporation = sm.GetService('corp').GetCorporation(session.corpid)
            if corporation.ceoID != session.charid:
                tabHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CEODeclareWarOnlyHint')
        if not SessionChecker(session, None).IsCorpDirector():
            tabHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/DirectorsCanEdit')
        return tabHint

    def _GetTabs(self):
        tabs = []
        tabs.append(self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Home', self.sr.wndViewParent, CorpPanel.ALLIANCES_HOME, self.GetHomeTabHint()))
        if session.allianceid is not None:
            tabs.extend([self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Bulletins', self.sr.wndViewParent, CorpPanel.ALLIANCES_BULLETINS),
             self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Members', self.sr.wndViewParent, CorpPanel.ALLIANCES_MEMBERS),
             self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/AllianceContacts', self.contactsPanel, CorpPanel.ALLIANCES_CONTACTS),
             self._BuildTabParams('UI/Neocom/Sovereignty', self.sr.wndViewParent, CorpPanel.ALLIANCE_SOVEREIGNTY),
             self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Systems', self.sr.wndViewParent, CorpPanel.ALLIANCES_SYSTEMS)])
        if not IsNPC(session.corpid):
            tabs.append(self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Applications', self.sr.wndViewParent, 'alliances_applications'))
        tabs.append(self._BuildTabParams('UI/Corporations/CorporationWindow/Alliances/Rankings', self.sr.wndViewParent, 'alliances_rankings', localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/RankingsCached15')))
        return tabs

    def _BuildTabParams(self, labelName, parent, tabArgs, hint = None):
        return [localization.GetByLabel(labelName),
         parent,
         self,
         tabArgs,
         None,
         hint]

    def LoadViewClass(self, tabName):
        self.sr.wndViewParent.Flush()
        if self.sr.tabs:
            if tabName == CorpPanel.ALLIANCES:
                tabName = self.sr.tabs.GetSelectedArgs()
        if tabName == CorpPanel.ALLIANCES_CONTACTS:
            if session.allianceid:
                self.contactsPanel.LoadPanel()
                return
            else:
                corpNotInAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/CorpNotInAlliance', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
                self.contactsPanel.Load(fixedEntryHeight=19, contentList=[], noContentHint=corpNotInAllianceLabel)
                return
        self.contactsPanel.state = uiconst.UI_HIDDEN
        if tabName == CorpPanel.ALLIANCES_HOME:
            panel = FormAlliancesHome(parent=self.sr.wndViewParent)
        if tabName == CorpPanel.ALLIANCES_SYSTEMS:
            panel = FormAlliancesSystems(parent=self.sr.wndViewParent)
        elif tabName == CorpPanel.ALLIANCES_BROWSE_ALL:
            panel = FormAlliancesRankings(parent=self.sr.wndViewParent)
        elif tabName == CorpPanel.ALLIANCES_APPLICATIONS:
            panel = FormAlliancesApplications(parent=self.sr.wndViewParent)
        elif tabName == CorpPanel.ALLIANCES_MEMBERS:
            panel = FormAlliancesMembers(parent=self.sr.wndViewParent)
        elif tabName == CorpPanel.ALLIANCES_BULLETINS:
            panel = FormAlliancesBulletins(parent=self.sr.wndViewParent)
        elif tabName == CorpPanel.ALLIANCE_SOVEREIGNTY:
            panel = FormAlliancesSovereignty(parent=self.sr.wndViewParent)
        panel.CreateWindow()
