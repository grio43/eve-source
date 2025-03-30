#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\treeViewEntries.py
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.control.buttonIcon import ButtonIcon
import eveicon
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelSmallBold
from eve.client.script.ui.control.themeColored import StretchSpriteHorizontalThemeColored
from eve.client.script.ui.control.treeViewEntry import TreeViewEntry, TreeViewEntryWithTag
from eve.common.script.sys import eveCfg
from inventorycommon.const import INVENTORY_ID_SHIP_CARGO, INVENTORY_ID_PLEX_VAULT, MAIN_PRIVATE_INVENTORY_IDS
import localization
import logging
import carbonui.const as uiconst
import uthread
logger = logging.getLogger(__name__)
COLOR_SELECTED = (0.1, 1.0, 0.1, 1.0)

def GetTreeViewEntryClassByDataType(treeData):
    treeEntryClass = TreeViewEntryInventory
    if not treeData:
        return treeEntryClass
    className = getattr(treeData, 'clsName', None)
    if not className:
        return treeEntryClass
    if className == INVENTORY_ID_SHIP_CARGO:
        treeEntryClass = TreeViewEntryInventoryCargo
    elif className in ('ShipMaintenanceBay', 'ShipFleetHangar') and treeData.invController.itemID == eveCfg.GetActiveShip():
        treeEntryClass = TreeViewEntryAccessConfig
    elif className in ('StationCorpHangar', 'POSCorpHangar', 'StationContainer', 'StructureCorpHangar'):
        treeEntryClass = TreeViewEntryAccessRestricted
    elif className == INVENTORY_ID_PLEX_VAULT:
        treeEntryClass = TreeViewEntryPlexVault
    elif className in MAIN_PRIVATE_INVENTORY_IDS:
        treeEntryClass = TreeViewEntryWithTag
    return treeEntryClass


class TreeViewEntryInventory(TreeViewEntry):
    default_name = 'TreeViewEntryInventory'

    def GetTreeViewEntryClassByTreeData(self, treeData):
        return GetTreeViewEntryClassByDataType(treeData)


class TreeViewEntryInventoryCargo(TreeViewEntryWithTag):
    default_name = 'TreeViewEntryInventoryCargo'

    def GetTreeViewEntryClassByTreeData(self, treeData):
        return GetTreeViewEntryClassByDataType(treeData)


class TreeViewEntryAccessConfig(TreeViewEntry):
    default_name = 'TreeViewEntryAccessConfig'

    def ApplyAttributes(self, attributes):
        self.iconCont = None
        TreeViewEntry.ApplyAttributes(self, attributes)
        self.iconCont = ContainerAutoSize(parent=self.topRightCont, align=uiconst.CENTERLEFT, height=16)
        self.fleetAccessBtn = ButtonIcon(name='fleetAccessBtn', parent=self.iconCont, align=uiconst.TOLEFT, width=14, iconSize=14, texturePath='res:/UI/Texture/classes/Inventory/fleetAccess.png', func=self.OnFleetAccessBtn, colorSelected=COLOR_SELECTED)
        self.corpAccessBtn = ButtonIcon(name='corpAccessBtn', parent=self.iconCont, align=uiconst.TOLEFT, width=14, padLeft=1, iconSize=12, texturePath='res:/UI/Texture/classes/Inventory/corpAccess.png', func=self.OnCorpAccessBtn, colorSelected=COLOR_SELECTED)
        self.UpdateFleetIcon()
        self.UpdateCorpIcon()

    def OnFleetAccessBtn(self, *args):
        if self.data.clsName == 'ShipMaintenanceBay':
            sm.GetService('shipConfig').ToggleShipMaintenanceBayFleetAccess()
            self.PlayButtonSound(sm.GetService('shipConfig').IsShipMaintenanceBayFleetAccessAllowed())
        elif self.data.clsName == 'ShipFleetHangar':
            sm.GetService('shipConfig').ToggleFleetHangarFleetAccess()
            self.PlayButtonSound(sm.GetService('shipConfig').IsFleetHangarFleetAccessAllowed())
        self.UpdateFleetIcon()

    def UpdateFleetIcon(self):
        if self.data.clsName == 'ShipMaintenanceBay':
            isAllowed = sm.GetService('shipConfig').IsShipMaintenanceBayFleetAccessAllowed()
        elif self.data.clsName == 'ShipFleetHangar':
            isAllowed = sm.GetService('shipConfig').IsFleetHangarFleetAccessAllowed()
        if isAllowed:
            hint = localization.GetByLabel('UI/Inventory/DisableAccessToFleetMembers')
        else:
            hint = localization.GetByLabel('UI/Inventory/EnableAccessToFleetMembers')
        self._UpdateButton(self.fleetAccessBtn, isAllowed, hint)

    def OnCorpAccessBtn(self, *args):
        if self.data.clsName == 'ShipMaintenanceBay':
            sm.GetService('shipConfig').ToggleShipMaintenanceBayCorpAccess()
            self.PlayButtonSound(sm.GetService('shipConfig').IsShipMaintenanceBayCorpAccessAllowed())
        elif self.data.clsName == 'ShipFleetHangar':
            sm.GetService('shipConfig').ToggleFleetHangarCorpAccess()
            self.PlayButtonSound(sm.GetService('shipConfig').IsFleetHangarCorpAccessAllowed())
        self.UpdateCorpIcon()

    def UpdateCorpIcon(self):
        if self.data.clsName == 'ShipMaintenanceBay':
            isAllowed = sm.GetService('shipConfig').IsShipMaintenanceBayCorpAccessAllowed()
        elif self.data.clsName == 'ShipFleetHangar':
            isAllowed = sm.GetService('shipConfig').IsFleetHangarCorpAccessAllowed()
        if isAllowed:
            hint = localization.GetByLabel('UI/Inventory/DisableAccessToCorpMembers')
        else:
            hint = localization.GetByLabel('UI/Inventory/EnableAccessToCorpMembers')
        self._UpdateButton(self.corpAccessBtn, isAllowed, hint)

    def _UpdateButton(self, button, isAllowed, hint):
        if isAllowed:
            button.SetSelected()
        else:
            button.SetDeselected()
        button.hint = hint

    def UpdateLabel(self):
        TreeViewEntry.UpdateLabel(self)
        if self.iconCont:
            self.iconCont.left = self.label.left + self.label.width + 3

    def PlayButtonSound(self, buttonState):
        if buttonState:
            sm.GetService('audio').SendUIEvent('msg_DiodeClick_play')
        else:
            sm.GetService('audio').SendUIEvent('msg_DiodeDeselect_play')


class TreeViewEntryAccessRestricted(TreeViewEntry):
    default_name = 'TreeViewEntryAccessRestricted'
    ICONSIZE = 16
    COLOR_RED = (0.867, 0.0, 0.0, 1.0)
    COLOR_YELLOW = (0.984, 0.702, 0.22, 1.0)

    def ApplyAttributes(self, attributes):
        self.iconCont = None
        TreeViewEntry.ApplyAttributes(self, attributes)
        canTake = self.data.CheckCanTake()
        canQuery = self.data.CheckCanQuery()
        if not canQuery:
            texturePath = eveicon.block_ban
            hint = localization.GetByLabel('UI/Inventory/DropAccessOnly')
            color = eveColor.DANGER_RED
        else:
            texturePath = eveicon.triangle
            hint = localization.GetByLabel('UI/Inventory/ViewAccessOnly')
            color = eveColor.WARNING_ORANGE
        if not canTake or not canQuery:
            self.iconCont = ContainerAutoSize(parent=self.topRightCont, align=uiconst.CENTERLEFT, height=self.ICONSIZE)
            Sprite(name='restrictedIcon', parent=self.iconCont, align=uiconst.TOLEFT, texturePath=texturePath, width=self.ICONSIZE, color=color, hint=hint)

    def UpdateLabel(self):
        TreeViewEntry.UpdateLabel(self)
        if self.iconCont:
            self.iconCont.left = self.topRightCont.width + self.label.left + self.label.width + 3


class TreeViewEntryPlexVault(TreeViewEntryWithTag):

    def ApplyAttributes(self, attributes):
        self.balanceCont = None
        super(TreeViewEntryPlexVault, self).ApplyAttributes(attributes)
        self.Layout()
        uthread.new(self.UpdateBalance, animate=False)
        self.GetAccount().accountAurumBalanceChanged.connect(self.UpdateBalance)

    def Layout(self):
        self.balanceCont = ContainerAutoSize(name='PlexBalanceContainer', parent=self.topRightCont, align=uiconst.CENTERLEFT, state=uiconst.UI_HIDDEN, callback=self._UpdateBalanceContPosition)
        StretchSpriteHorizontalThemeColored(name='PlexBalanceSprite', bgParent=self.balanceCont, colorType=uiconst.COLORTYPE_UIBASE, texturePath='res:/UI/Texture/Shared/counterFrame.png', leftEdgeSize=8, rightEdgeSize=8)
        self.balanceLabel = EveLabelSmallBold(name='PlexBalanceLabel', parent=self.balanceCont, align=uiconst.TOPLEFT, padding=(6, 2, 6, 1))

    def GetAccount(self):
        return sm.GetService('vgsService').GetStore().GetAccount()

    def GetBalance(self):
        account = self.GetAccount()
        try:
            return account.GetAurumBalance()
        except Exception:
            logger.warning('Failed to retrieve the PLEX balance', exc_info=True)
            return 0

    def UpdateBalance(self, balance = None, animate = True, *args, **kwargs):
        if balance is None:
            balance = self.GetBalance()
        self.balanceLabel.SetText(FmtAmt(balance, fmt='sn'))
        if balance > 0:
            self.balanceCont.state = uiconst.UI_PICKCHILDREN
            if animate:
                animations.BlinkIn(self.balanceCont)
        else:
            self.balanceCont.Hide()

    def UpdateLabel(self):
        super(TreeViewEntryPlexVault, self).UpdateLabel()
        self._UpdateBalanceContPosition()

    def _UpdateBalanceContPosition(self, *args):
        if self.balanceCont:
            self.balanceCont.left = self.topRightCont.width + self.label.left + self.label.width + 4
