#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\itemIcon.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui.control.eveIcon import Icon
import evetypes
import trinity
from eve.client.script.ui.shared.cloneGrade import cloneStateUtil
from eve.common.script.util.eveFormat import FmtISK
from inventorycommon.typeHelpers import GetAveragePrice
from localization import GetByLabel
from utillib import KeyVal
from eveservices.menu import GetMenuService

class ItemIcon(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_width = 32
    default_height = 32
    default_showOmegaOverlay = True
    isDragObject = True
    __notifyevents__ = ['OnSubscriptionChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.itemID = attributes.Get('itemID', None)
        self.bpData = attributes.Get('bpData', False)
        self.isCopy = attributes.Get('isCopy', False)
        self.showOmegaOverlay = attributes.Get('showOmegaOverlay', self.default_showOmegaOverlay)
        self.showPrice = attributes.Get('showPrice', False)
        textureSecondaryPath = attributes.Get('textureSecondaryPath', None)
        self.omegaOverlay = None
        self.techIcon = Sprite(name='techIcon', parent=self, width=16, height=16)
        self.icon = Icon(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, textureSecondaryPath=textureSecondaryPath, spriteEffect=trinity.TR2_SFX_MODULATE if textureSecondaryPath else trinity.TR2_SFX_COPY)
        self.SetTypeID(self.typeID, self.bpData)
        sm.RegisterNotify(self)

    def OnSubscriptionChanged(self):
        self.UpdateOmegaOverlay()

    def SetTypeIDandItemID(self, typeID, itemID, bpData = None, isCopy = None):
        self.itemID = itemID
        self.SetTypeID(typeID, bpData, isCopy)

    def SetTypeID(self, typeID, bpData = None, isCopy = None):
        self.typeID = typeID
        self.bpData = bpData
        if isCopy is not None:
            self.isCopy = isCopy
        self.icon.LoadIconByTypeID(typeID, size=min(self.width, self.height), ignoreSize=True, isCopy=self.IsBlueprintCopy())
        from eve.client.script.ui.util.uix import GetTechLevelIconPathAndHint
        texturePath, hint = GetTechLevelIconPathAndHint(typeID)
        if texturePath:
            self.techIcon.texturePath = texturePath
            self.techIcon.hint = hint
            self.techIcon.Show()
        else:
            self.techIcon.Hide()
        self.isUnlockedWithExpertSystem = sm.GetService('skills').IsUnlockedWithExpertSystem(self.typeID)
        self.UpdateOmegaOverlay()

    def SetTexturePath(self, texturePath):
        self.icon.texturePath = texturePath
        self.techIcon.Hide()
        self.HideOmegaOverlay()

    def UpdateOmegaOverlay(self):
        if self.showOmegaOverlay and self.typeID:
            if sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(self.typeID) and not sm.GetService('cloneGradeSvc').IsOmega():
                self.ShowOmegaOverlay()
            else:
                self.HideOmegaOverlay()

    def HideOmegaOverlay(self):
        if self.omegaOverlay:
            self.omegaOverlay.Hide()

    def _isUnlockedWithExpertSystems(self):
        return sm.GetService('skills').IsUnlockedWithExpertSystem(self.typeID)

    def ShowOmegaOverlay(self):
        if self._isUnlockedWithExpertSystems():
            return
        if not self.omegaOverlay:
            from eve.client.script.ui.shared.cloneGrade.omegaCloneOverlayIcon import OmegaCloneOverlayIcon
            wndID = self.GetWindowAboveID()
            self.omegaOverlay = OmegaCloneOverlayIcon(parent=self, align=uiconst.TOALL, idx=1, iconSize=int(0.7 * self.width), origin=wndID, reason=self.typeID)
        self.omegaOverlay.state = uiconst.UI_DISABLED

    def GetWindowAboveID(self):
        wndAbove = GetWindowAbove(self)
        if wndAbove:
            return wndAbove.windowID

    def IsBlueprintCopy(self):
        if self.isCopy:
            return True
        if not self.bpData:
            return False
        return not self.bpData.original

    def GetMenu(self):
        self.SetBpDataForCopy()
        return GetMenuService().GetMenuFromItemIDTypeID(self.itemID, self.typeID, includeMarketDetails=True, abstractInfo=KeyVal(fullBlueprintData=self.bpData))

    def OnClick(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.SetBpDataForCopy()
        sm.GetService('info').ShowInfo(self.typeID, self.itemID, abstractinfo=KeyVal(fullBlueprintData=self.bpData))

    def SetBpDataForCopy(self):
        if self.isCopy and not self.bpData:
            self.bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(self.typeID, original=False)

    def GetHint(self):
        if self.typeID:
            name = evetypes.GetName(self.typeID)
            description = evetypes.GetDescription(self.typeID)
            ret = u'<b>%s</b>' % name
            if description:
                ret += u'\n%s' % description
            if self.showPrice:
                price = GetAveragePrice(self.typeID)
                if price:
                    ret += '\n\n%s' % GetByLabel('UI/SkillTrading/EstimatedPrice', price=FmtISK(price, False))
            return ret

    def GetDragData(self):
        return [KeyVal(__guid__='uicls.GenericDraggableForTypeID', typeID=self.typeID, label=evetypes.GetName(self.typeID), bpData=self.bpData, isCopy=self.IsBlueprintCopy())]

    def OnMouseEnter(self, *args):
        if self.IsOmegaOverlayVisible():
            self.omegaOverlay.OnMouseEnter()

    def OnMouseExit(self, *args):
        if self.IsOmegaOverlayVisible():
            self.omegaOverlay.OnMouseExit()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.IsOmegaOverlayVisible() and not sm.GetService('cloneGradeSvc').IsOmega():
            cloneStateUtil.LoadTooltipPanel(tooltipPanel, origin=self.GetWindowAboveID(), reason=self.typeID)
        else:
            tooltipPanel.LoadGeneric1ColumnTemplate()
        import expertSystems.client
        expertSystems.add_type_unlocked_by_expert_systems(tooltipPanel, self.typeID)

    def IsOmegaOverlayVisible(self):
        return self.omegaOverlay and self.omegaOverlay.display
