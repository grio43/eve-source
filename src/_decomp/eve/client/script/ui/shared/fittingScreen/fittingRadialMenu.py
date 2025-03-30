#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingRadialMenu.py
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.radialMenu.radialMenu import RadialMenu
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction, RadialMenuOptionsInfo, RadialMenuSizeInfo
from eve.client.script.ui.inflight.radialMenuShipUI import RadialMenuShipUI
import carbonui.const as uiconst
from carbonui.uicore import uicore
RMO_SizeInfo = RadialMenuSizeInfo(width=220, height=220, shadowSize=256, rangeSize=128, sliceCount=8, buttonWidth=100, buttonHeight=70, buttonPaddingTop=12, buttonPaddingBottom=6, actionDistance=110)

class RadialMenuFitting(RadialMenuShipUI):
    default_width = RMO_SizeInfo.width
    default_height = RMO_SizeInfo.height
    sizeInfo = RMO_SizeInfo
    shadowTexture = 'res:/UI/Texture/classes/RadialMenu/menuShadow2.png'

    def ApplyAttributes(self, attributes):
        self.slotList = attributes.slotList
        self.isStructure = attributes.isStructure
        RadialMenuShipUI.ApplyAttributes(self, attributes)

    def GetMyActions(self, *args):
        iconOffset = 1
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        allWantedMenuOptions = [SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/Activate', func=ghostFittingSvc.ActivateAllHighSlots, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/active.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/Overheat', func=ghostFittingSvc.OverheatAllInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/heat.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='', func=None, iconPath='', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/UnloadModules', func=ghostFittingSvc.UnfitAllModulesInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/unload.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/UnloadAmmo', func=ghostFittingSvc.UnfitAllAmmoInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/unloadAmmo.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/Offline', func=ghostFittingSvc.OfflineAllInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/offline.png', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='', func=None, iconPath='', iconOffset=iconOffset),
         SimpleRadialMenuAction(option1='UI/Fitting/FittingWindow/RadialMenu/Online', func=ghostFittingSvc.OnlineAllInRack, funcArgs=(self.slotList,), iconPath='res:/UI/Texture/classes/RadialMenuActions/fitting/online.png', iconOffset=iconOffset)]
        activeSingleOptions = {menuAction.option1Path:menuAction for menuAction in allWantedMenuOptions if menuAction.option1Path}
        if self.isStructure:
            activeSingleOptions.pop('UI/Fitting/FittingWindow/RadialMenu/Overheat', None)
        optionsInfo = RadialMenuOptionsInfo(allWantedMenuOptions=allWantedMenuOptions, activeSingleOptions=activeSingleOptions)
        return optionsInfo

    def SetPosition(self):
        left, top, width, height = self.anchorObject.GetAbsolute()
        originalX = self.currentCenterX = left + width / 2
        originalY = self.currentCenterY = top + height / 2
        halfWidth = self.width / 2
        halfHeight = self.height / 2
        if originalX - halfWidth < 0:
            return RadialMenu.SetPosition(self)
        if originalX + halfWidth > uicore.desktop.width:
            return RadialMenu.SetPosition(self)
        if originalY - halfHeight < 0:
            return RadialMenu.SetPosition(self)
        if originalY + halfHeight > uicore.desktop.height:
            return RadialMenu.SetPosition(self)
        return RadialMenuShipUI.SetPosition(self)

    def AddOptionText(self):
        return RadialMenu.AddOptionText(self)

    def AdjustTextShadow(self, *args):
        return RadialMenu.AdjustTextShadow(self, *args)

    def HiliteOneButton(self, btnCont, buttonLayer):
        RadialMenu.HiliteOneButton(self, btnCont, buttonLayer)
        self.AdjustTextShadow()


class RadialMenuIcon(ButtonIcon):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        self.mouseUpCookie = None
        self.flags = attributes.flags
        self.originalHint = attributes.hint
        self.hint = self.originalHint
        self.mouseDownFunc = attributes.mouseDownFunc

    def OnMouseDown(self, mouseButton):
        self.SetHint('')
        uicore.uilib.tooltipHandler.RefreshTooltipForOwner(self)
        if self.mouseDownFunc:
            self.mouseDownFunc(self, self.flags, mouseButton)
        ButtonIcon.OnMouseDown(self, mouseButton)
        self.mouseUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalClick)

    def OnGlobalClick(self, *args):
        if self.mouseUpCookie:
            uicore.event.UnregisterForTriuiEvents(self.mouseUpCookie)
        self.OnMouseExit()
        self.hint = self.originalHint
