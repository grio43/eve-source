#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipconfig.py
import evetypes
import localization
import carbonui.const as uiconst
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.userentry import User
from eve.client.script.ui.util import uix
from carbonui.control.tabGroup import TabGroup
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.eveCfg import InStructure
from eveservices.menu import GetMenuService

class ShipConfig(Window):
    default_windowID = 'shipconfig'
    default_captionLabelPath = 'UI/Ship/ShipConfig/ShipConfig'
    default_minSize = (300, 230)
    default_height = 400
    default_width = 300
    __notifyevents__ = ['ProcessSessionChange', 'OnShipCloneJumpUpdate']
    shipmodules = [('CloneFacility', 'canReceiveCloneJumps')]

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.shipid = eveCfg.GetActiveShip()
        self.shipItem = self.GetShipItem()
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=72, clipChildren=True)
        self.sr.top = Container(name='top', align=uiconst.TOTOP, parent=self.topParent, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         64))
        icon = eveIcon.Icon(parent=self.sr.top, align=uiconst.TOLEFT, left=const.defaultPadding, size=64, state=uiconst.UI_NORMAL, typeID=self.shipItem.typeID)
        icon.GetMenu = self.ShipMenu
        Container(name='push', align=uiconst.TOLEFT, pos=(5, 0, 5, 0), parent=self.sr.top)
        eveLabel.EveHeaderMedium(name='label', text=cfg.evelocations.Get(self.shipItem.itemID).name, parent=self.sr.top, align=uiconst.TOTOP, bold=True, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(name='label', text=evetypes.GetName(self.shipItem.typeID), parent=self.sr.top, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.ship = eveMoniker.GetShipAccess()
        self.conf = self.ship.GetShipConfiguration(self.shipid)
        modules = self.GetShipModules()
        for module in modules:
            self.sr.Set('%sPanel' % module.lower(), Container(name=module, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, parent=self.sr.main, pos=(0, 0, 0, 0)))

        tabs = [ [name,
         self.sr.Get('%sPanel' % module.lower(), None),
         self,
         module] for module, name in modules.iteritems() if self.sr.Get('%sPanel' % module.lower()) ]
        if tabs:
            self.sr.maintabs = TabGroup(name='tabparent', align=uiconst.TOTOP, height=18, parent=self.sr.main, idx=self.topParent.GetOrder() + 1, tabs=tabs, groupID='pospanel')
        else:
            eveLabel.CaptionLabel(text=localization.GetByLabel('UI/Ship/ShipConfig/ShipConfig'), parent=self.sr.main, size=18, uppercase=0, left=const.defaultPadding, width=const.defaultPadding, top=const.defaultPadding)

    def _OnClose(self, *args):
        self.shipid = None
        self.shipItem = None
        self.capacity = None
        self.tower = None

    def Load(self, key):
        eval('self.Show%s()' % key)

    def ShowCloneFacility(self):
        if not getattr(self, 'cloneinited', 0):
            self.InitCloneFacilityPanel()
        godmaSM = sm.GetService('godma').GetStateManager()
        self.panelsetup = 1
        cloneRS = sm.GetService('clonejump').GetShipClones()
        scrolllist = []
        for each in cloneRS:
            charinfo = cfg.eveowners.Get(each['ownerID'])
            scrolllist.append(GetFromClass(User, {'charID': each['ownerID'],
             'info': charinfo,
             'cloneID': each['jumpCloneID']}))

        self.sr.clonescroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Name')])
        self.sr.clonescroll.ShowHint([localization.GetByLabel('UI/Ship/ShipConfig/NoClonesInstalledAtShip'), None][bool(scrolllist)])
        numClones = int(len(cloneRS))
        totalClones = int(getattr(godmaSM.GetItem(self.shipItem.itemID), 'maxJumpClones', 0))
        self.sr.cloneInfo.text = localization.GetByLabel('UI/Ship/ShipConfig/NumJumpClones', numClones=numClones, totalClones=totalClones)
        self.panelsetup = 0

    def InitCloneFacilityPanel(self):
        panel = self.sr.clonefacilityPanel
        btns = [(localization.GetByLabel('UI/Ship/ShipConfig/Invite'),
          self.InviteClone,
          (),
          84), (localization.GetByLabel('UI/Ship/ShipConfig/Destroy'),
          self.DestroyClone,
          (),
          84)]
        self.cloneFacilityButtons = ButtonGroup(btns=btns, parent=panel)
        if not session.solarsystemid or InStructure():
            self.cloneFacilityButtons.buttons[0].Disable()
        numClones = int(0)
        totalClones = int(getattr(sm.GetService('godma').GetItem(self.shipItem.itemID), 'maxJumpClones', 0))
        text = localization.GetByLabel('UI/Ship/ShipConfig/NumJumpClones', numClones=numClones, totalClones=totalClones)
        self.sr.cloneInfo = eveLabel.EveLabelSmall(text=text, parent=panel, align=uiconst.TOTOP, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         0), state=uiconst.UI_NORMAL)
        self.sr.clonescroll = eveScroll.Scroll(name='clonescroll', parent=panel, padding=const.defaultPadding)
        self.cloneinited = 1

    def InviteClone(self, *args):
        if not sm.GetService('clonejump').HasCloneReceivingBay():
            eve.Message('InviteClone1')
            return
        godmaSM = sm.GetService('godma').GetStateManager()
        opDist = getattr(godmaSM.GetType(self.shipItem.typeID), 'maxOperationalDistance', 0)
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        charIDs = self._GetPotentialInvitees(bp, opDist)
        if not charIDs:
            eve.Message('InviteClone2')
            return
        lst = []
        for charID in charIDs:
            char = cfg.eveowners.Get(charID)
            lst.append((char.name, charID, char.typeID))

        chosen = uix.ListWnd(lst, 'character', localization.GetByLabel('UI/Ship/ShipConfig/SelectAPilot'), None, 1, minChoices=1, isModal=1)
        if chosen:
            sm.GetService('clonejump').OfferShipCloneInstallation(chosen[1])

    def _GetPotentialInvitees(self, bp, opDist):
        charIDs = set()
        for slimItem in bp.slimItems.itervalues():
            if not slimItem.charID or slimItem.charID == session.charid or idCheckers.IsNPC(slimItem.charID):
                continue
            if slimItem.categoryID == const.categoryStructure:
                continue
            if slimItem.surfaceDist <= opDist:
                charIDs.add(slimItem.charID)

        return charIDs

    def DestroyClone(self, *args):
        for each in self.sr.clonescroll.GetSelected():
            sm.GetService('clonejump').DestroyInstalledClone(each.cloneID)

    def GetShipItem(self):
        if session.stationid or InStructure():
            return sm.GetService('clientDogmaIM').GetDogmaLocation().GetShip()
        if session.solarsystemid:
            bp = sm.GetService('michelle').GetBallpark()
            if bp and self.shipid in bp.slimItems:
                return bp.slimItems[self.shipid]

    def GetShipModules(self):
        typeID = self.shipItem.typeID
        godmaSM = sm.GetService('godma').GetStateManager()
        hasModules = {}
        for module in self.shipmodules:
            if getattr(godmaSM.GetType(typeID), module[1], 0):
                nameString = ''
                if module[0] == 'CloneFacility':
                    nameString = localization.GetByLabel('UI/Ship/ShipConfig/CloneFacility')
                hasModules[module[0]] = nameString

        return hasModules

    def ShipMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(self.shipItem.itemID, self.shipItem.typeID)

    def ProcessSessionChange(self, isRemote, session, change):
        if session.shipid and 'shipid' in change:
            self.CloseByUser()
        elif 'solarsystemid' in change:
            self.CloseByUser()

    def OnShipCloneJumpUpdate(self):
        if self.sr.maintabs.GetSelectedArgs() == 'CloneFacility':
            self.ShowCloneFacility()
