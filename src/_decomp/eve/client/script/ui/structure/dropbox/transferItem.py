#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\dropbox\transferItem.py
import evetypes
import trinity
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uiconst import CENTER
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.tooltip.item import InventoryItemTooltip
from eve.client.script.ui.structure.dropbox.const import ICON_SIZE
from eve.client.script.ui.util import uix
from localization import GetByLabel
from utillib import KeyVal

class TransferItem(Container):
    default_width = 64
    default_height = 64
    default_align = uiconst.TOALL
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isSelected = False
        self.dropboxController = attributes.dropboxController
        self.item = attributes.item
        self.itemID = self.item.itemID
        self.typeID = self.item.typeID
        self.quantity = self.item.quantity
        self.stacksize = self.item.stacksize
        self.isSingleton = self.item.singleton
        self.isRemovable = attributes.isRemovable
        isBlueprint = evetypes.GetCategoryID(self.typeID) == const.categoryBlueprint
        isCopy = isBlueprint and self.isSingleton == const.singletonBlueprintCopy
        self.BuildIcons()
        self.AddEntryHiliteAndBg()
        self.BuildQtyUI()
        self.icon.LoadIconByTypeID(typeID=self.typeID, ignoreSize=True, isCopy=isCopy)
        self._SetQtyText()
        self.getTypeAttribute = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute
        self.onMouseEnter = None
        self.onMouseExit = None

    def BuildIcons(self):
        self.spriteCont = Container(name='spriteCont', parent=self, align=CENTER, width=ICON_SIZE, height=ICON_SIZE, state=uiconst.UI_PICKCHILDREN)
        self.icon = Icon(name='type_%s' % self.typeID, parent=self.spriteCont, pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE), align=CENTER, state=uiconst.UI_DISABLED, saturation=1.0, effectOpacity=0.0, spriteEffect=trinity.TR2_SFX_SOFTLIGHT)
        self.hint = self.typeID
        self.techIcon = Sprite(name='techIcon', parent=self.spriteCont, pos=(0, 0, 16, 16), idx=0, saturation=1.0, effectOpacity=0.0, spriteEffect=trinity.TR2_SFX_SOFTLIGHT)
        uix.GetTechLevelIcon(self.techIcon, 0, self.typeID)
        self.removeIcon = ButtonIcon(name='removeIcon', parent=self.spriteCont, pos=(2, 2, 12, 12), idx=0, texturePath='res:/ui/texture/icons/73_16_45.png', align=uiconst.TOPRIGHT, iconSize=12)
        self.removeIcon.OnMouseExit = self.OnButtonIconMouseExit
        if not self.isRemovable:
            self.removeIcon.display = False

    def OnButtonIconMouseExit(self):
        self.OnMouseExit()
        ButtonIcon.OnMouseExit(self.removeIcon)

    def AddEntryHiliteAndBg(self):
        self.entryHilite = Sprite(name='hilite', align=uiconst.TOALL, parent=self.spriteCont, texturePath='res:/UI/Texture/classes/InvItem/bgHover.png', blendMode=trinity.TR2_SBM_ADD, opacity=0.0, idx=0, state=uiconst.UI_DISABLED)
        self.entryHilite.hint = evetypes.GetName(self.typeID)
        bgSprite = Sprite(bgParent=self.spriteCont, name='background', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')

    def BuildQtyUI(self):
        self.quantityParent = Container(parent=self, idx=0, name='qtyCont', pos=(3, 38, 32, 11), align=uiconst.TOPRIGHT, bgColor=(0, 0, 0, 0.95), state=uiconst.UI_DISABLED)
        self.quantityParent.display = False
        self.qtyLabel = Label(parent=self.quantityParent, left=2, maxLines=1, fontsize=9)

    def _SetQtyText(self):
        if self.isSingleton:
            self.quantityParent.display = False
            return
        if self.stacksize:
            numberOfItems = self.stacksize
        else:
            numberOfItems = self.quantity
        self.qtyLabel.text = FmtAmt(numberOfItems, 'ss')
        if numberOfItems:
            self.quantityParent.display = True
        else:
            self.quantityParent.display = False

    def ShowHilited(self):
        uicore.animations.FadeIn(self.entryHilite, duration=0.2)

    def ShowNotHilited(self):
        uicore.animations.FadeOut(self.entryHilite, duration=0.2)

    def OnMouseEnter(self, *args):
        self.ShowHilited()
        if uicore.uilib.leftbtn:
            return

    def OnMouseExit(self, *args):
        if uicore.uilib.mouseOver != self and not uicore.uilib.mouseOver.IsUnder(self):
            self.ShowNotHilited()

    def GetDragData(self):
        return [KeyVal(itemID=self.itemID, __guid__='xtriui.TypeIcon', typeID=self.typeID, isReprocessingItem=True)]

    def GetMenu(self):
        m = sm.GetService('menu').InvItemMenu(self.item)
        m.append(None)
        m.append((GetByLabel('UI/Generic/RemoveItem'), self.dropboxController.RemoveItems, ([self.itemID],)))
        return m

    def LoadTooltipPanel(self, tooltipPanel, *args):
        item = self.dropboxController.GetItem(self.itemID)
        InventoryItemTooltip(tooltipPanel=tooltipPanel, item=item)

    def Close(self):
        self.dropboxController = None
        Container.Close(self)
