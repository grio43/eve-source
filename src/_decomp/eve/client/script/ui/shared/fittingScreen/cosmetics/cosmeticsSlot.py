#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\cosmetics\cosmeticsSlot.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from eve.client.script.ui.control.message import ShowQuickMessage
from eveui import Sprite
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class CosmeticsSlot(Transform):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_width = 44
    default_height = 54

    def ApplyAttributes(self, attributes):
        super(CosmeticsSlot, self).ApplyAttributes(attributes)
        self.slotController = attributes.get('controller', None)
        self.radCosSin = attributes.radCosSin
        self.texturePath = None
        self.ConstructLayout()
        self.SetupSlot()

    def ConstructLayout(self):
        self.content = Container(name='content', parent=self, align=uiconst.TOALL)
        self.logoContainer = ContainerAutoSize(name='logoContainer', parent=self.content, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.UpdateLogo()
        self.frame = Sprite(bgParent=self.content, name='frame', state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath='res:/UI/Texture/classes/Fitting/moduleFrame.png', opacity=0.3)
        self.fill = Sprite(bgParent=self.content, name='fill', state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath='res:/UI/Texture/classes/Fitting/moduleSlotFill.png', color=(0.0, 0.0, 0.0, 0.2))
        self.fill.Hide()

    def UpdateLogo(self, size = 32):
        self.logoContainer.Flush()
        if self.texturePath:
            self.backgroundIcon = Sprite(name='backgroundIcon', parent=self.logoContainer, texturePath=self.texturePath)
        else:
            self.CreateEmptySlotIcon()
        self.backgroundIcon.SetSize(size, size)

    def CreateEmptySlotIcon(self):
        if self.slotController:
            self.texturePath = self.slotController.backgroundIconPath
        self.backgroundIcon = Sprite(name='backgroundIcon', parent=self.logoContainer, texturePath=self.texturePath)

    def SetupSlot(self, texturePath = None, size = 32):
        self.texturePath = texturePath
        if not self.slotController:
            self.fill.Show()
            return
        self.UpdateLogo(size)

    def GetHint(self):
        if not self.slotController:
            return GetByLabel('UI/Fitting/FittingWindow/Cosmetic/ReservedSlot')
        return self.slotController.hint

    def OnMouseEnter(self, *args):
        self.frame.SetAlpha(0.5)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def OnMouseExit(self, *args):
        self.frame.SetAlpha(0.3)

    def GetTooltipPosition(self):
        rect, point = self.PositionHint()
        return rect

    def GetTooltipPointer(self):
        rect, point = self.PositionHint()
        return point

    def PositionHint(self, *_args):
        sl, st, sw, sh = self.parent.GetAbsolute()
        cX = sl + sw / 2.0
        cY = st + sh / 2.0
        rad, cos, sin, oldcX, oldcY = self.radCosSin
        hintLeft = int(round(rad * cos))
        hintTop = int(round(rad * sin))
        cap = rad * 0.7
        if hintLeft < -cap:
            point = uiconst.POINT_RIGHT_2
        elif hintLeft > cap:
            point = uiconst.POINT_LEFT_2
        elif hintTop < -cap:
            if hintLeft < 0:
                point = uiconst.POINT_BOTTOM_3
            else:
                point = uiconst.POINT_BOTTOM_1
        elif hintLeft < 0:
            point = uiconst.POINT_TOP_3
        else:
            point = uiconst.POINT_TOP_1
        return ((hintLeft + cX - 15,
          hintTop + cY - 15,
          30,
          30), point)


class CosmeticAllianceLogoSlot(CosmeticsSlot):

    def UpdateLogo(self, size = 32):
        self.logoContainer.Flush()
        if eve.session.allianceid and self.texturePath:
            self.backgroundIcon = Sprite(name='backgroundIcon', parent=self.logoContainer, texturePath=self.texturePath)
        else:
            self.CreateEmptySlotIcon()
        self.backgroundIcon.SetSize(size, size)
        self.backgroundIcon.rotation = -self.rotation


class CosmeticCorporationLogoSlot(CosmeticsSlot):

    def UpdateLogo(self, size = 32):
        self.logoContainer.Flush()
        if self.texturePath:
            self.backgroundIcon = Sprite(name='backgroundIcon', parent=self.logoContainer, texturePath=self.texturePath)
        else:
            self.CreateEmptySlotIcon()
        self.backgroundIcon.SetSize(size, size)
        self.backgroundIcon.rotation = -self.rotation


class CosmeticSkinSlot(CosmeticsSlot):

    def UpdateLogo(self, size = 32):
        super(CosmeticSkinSlot, self).UpdateLogo(size)
        self.backgroundIcon.rotation = -self.rotation

    def GetHint(self):
        if not self.slotController:
            return GetByLabel('UI/Fitting/FittingWindow/Cosmetic/ReservedSlot')
        itemID = session.shipid
        skin = sm.GetService('cosmeticsSvc').GetAppliedSkinStateForCurrentSession(itemID)
        if skin:
            if skin.skin_type == ShipSkinType.FIRST_PARTY_SKIN:
                skin_name = sm.GetService('cosmeticsSvc').GetFirstPartySkinMaterialDisplayName(skin.skin_data.skin_id)
                return GetByLabel('UI/ShipCosmetics/ActiveSkin', skinName=skin_name)
            if skin.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                try:
                    skin_license = get_ship_skin_license_svc().get_license(skin.skin_data.skin_id, skin.character_id)
                except (GenericException, TimeoutException):
                    ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
                    skin_license = None

                if skin_license:
                    return GetByLabel('UI/ShipCosmetics/ActiveSkin', skinName=skin_license.skin_design.full_name)
                else:
                    return ''
        return GetByLabel('UI/ShipCosmetics/NoSkinActive')


class CosmeticBlankSlot(CosmeticsSlot):

    def ApplyAttributes(self, attributes):
        super(CosmeticBlankSlot, self).ApplyAttributes(attributes)
        self.content.opacity = 0.05

    def OnMouseEnter(self, *args):
        pass

    def OnMouseExit(self, *args):
        pass

    def GetHint(self):
        return None
