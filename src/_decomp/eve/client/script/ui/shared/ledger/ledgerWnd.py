#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\ledger\ledgerWnd.py
from carbonui.primitives.container import Container
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.ledger.ledgerPanel import LedgerPanelPersonal, LedgerPanelCorp
from eve.common.lib.appConst import corpRoleAccountant
from localization import GetByLabel
import carbonui.const as uiconst

class LedgerWindow(Window):
    __guid__ = 'LedgerWindow'
    __notifyevents__ = []
    default_width = 800
    default_height = 600
    default_minSize = (650, 600)
    default_windowID = 'ledger'
    default_captionLabelPath = 'UI/Ledger/LedgerWnd'
    default_descriptionLabelPath = 'Tooltips/Neocom/Ledger_desciption'
    default_iconNum = 'res:/ui/Texture/WindowIcons/miningLedger.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        shouldShowCorpLedger = bool(session.corprole & corpRoleAccountant)
        self.ledgerCont = Container(name='ledgerCont', parent=self.sr.main, padding=4)
        self.ledgerPanelPersonal = LedgerPanelPersonal(parent=self.ledgerCont, padding=4, addInfoIcon=not shouldShowCorpLedger)
        if shouldShowCorpLedger:
            self.ledgerPanelCorp = LedgerPanelCorp(parent=self.ledgerCont, padTop=4)
            tabs = ((GetByLabel('UI/Ledger/LedgerPersonal'),
              self.ledgerPanelPersonal,
              None,
              'personalLedger',
              None,
              GetByLabel('UI/Ledger/LedgerPersonalTabHint')), (GetByLabel('UI/Ledger/LedgerCorp'),
              self.ledgerPanelCorp,
              None,
              'corpLedger',
              None,
              GetByLabel('UI/Ledger/LedgerCorpTabHint')))
            self.tabs = TabGroup(parent=self.ledgerCont, tabs=tabs, height=26, labelPadding=12, idx=0, padLeft=0, groupID='StructureBrowser')
            moreinfoicon = MoreInfoIcon(left=2, top=-1, parent=self.tabs, idx=0, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)
            moreinfoicon.hint = GetByLabel('UI/Ledger/LedgerCacheHint')
        else:
            self.ledgerPanelPersonal.ReloadContent()
