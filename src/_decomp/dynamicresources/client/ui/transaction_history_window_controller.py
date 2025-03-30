#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ui\transaction_history_window_controller.py
import eveformat
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eveservices.menu import GetMenuService
from inventorycommon.const import typeCharacter

class TransactionHistoryWindowController(object):

    def __init__(self):
        self.dynamicResourceSvc = sm.GetService('dynamicResourceSvc')

    def GetMainBankAccessHistoryListItems(self):
        entries = []
        for entry in self.dynamicResourceSvc.GetESSAccessHistoryForCurrentSystem()['main']:
            charid = entry['characterID']
            amount = entry['amount']
            playerName = cfg.eveowners.Get(charid).name
            entry = GetFromClass(TransactionListEntry, {'label': '<t>%s<t>%s' % (playerName, eveformat.isk_readable(amount)),
             'sortValues': ['', playerName, amount],
             'charID': charid,
             'info': Bunch(typeID=typeCharacter, name=playerName)})
            entries.append(entry)

        return entries

    def GetReserveBankAccessHistoryListItems(self):
        entries = []
        for entry in self.dynamicResourceSvc.GetESSAccessHistoryForCurrentSystem()['reserve']:
            charid = entry['characterID']
            amount = entry['amount']
            date = entry['lastTheft']
            playerName = cfg.eveowners.Get(charid).name
            entry = GetFromClass(TransactionListEntry, {'label': '<t>%s<t>%s<t>%s' % (playerName, FmtDate(date), eveformat.isk_readable(amount)),
             'charID': charid,
             'sortValues': ['',
                            playerName,
                            date,
                            amount],
             'info': Bunch(typeID=typeCharacter, name=playerName)})
            entries.append(entry)

        return entries


class TransactionListEntry(Generic):
    __guid__ = 'listentry.User'
    isDragObject = True
    default_rowHeight = 32

    def Startup(self, *args):
        self.picCont = Container(parent=self, align=uiconst.TOLEFT_NOPUSH, width=32, height=32)
        self.portraitSprite = Sprite(parent=self.picCont, name='portraitSprite', state=uiconst.UI_DISABLED, width=32, height=32)
        self.sr.label = EveLabelLarge(align=uiconst.TOALL)
        Generic.Startup(self, args)
        self.charID = None

    def GetHeight(self, *args):
        return TransactionListEntry.default_rowHeight

    def Load(self, node):
        self.charID = node.charID
        Generic.Load(self, node)
        self.LoadPortrait(node)

    def LoadPortrait(self, node):
        self.photoSvc = sm.StartService('photo')
        self.photoSvc.GetPortrait(node.charID, 32, self.portraitSprite)

    def GetDragData(self):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)

    def GetMenu(self):
        menuSvc = GetMenuService()
        return menuSvc.GetMenuForOwner(self.charID)
