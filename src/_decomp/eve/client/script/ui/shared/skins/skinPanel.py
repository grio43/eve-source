#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skins\skinPanel.py
import blue
import contextlib
import eveformat
import evetypes
import gametime
import locks
import log
import logging
import math
import numbers
import sys
import uthread
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_GML
import carbonui
from carbonui import ButtonStyle, ButtonVariant, const as uiconst, Density
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.themeColored import FillThemeColored, GradientThemeColored
from eve.client.script.ui.plex.textures import PLEX_12_SOLID_WHITE
from eve.client.script.ui.shared.skins.controller import SkinNotAvailableForType
from eve.client.script.ui.shared.skins.devMenuFunctions import GiveSkin, GivePermanentSkin, GiveLimitedSkin, RemoveSkin, GetSkinUsedWithTypeAndMaterial, GiveExpiredSkin
from eve.client.script.ui.shared.skins.uiutil import OPEN_SKINR_BUTTON_ANALYTIC_ID
from eve.client.script.ui.shared.skins.event import LogBuySkinIsk, LogBuySkinAur
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from inventorycommon.const import typeSkinMaterial
from cosmetics.common.ships.skins.static_data.slot_configuration import is_skinnable_ship
from localization import GetByLabel
logger = logging.getLogger(__name__)
ENTRY_DEFAULT_HEIGHT = 106
ENTRY_COMPACT_HEIGHT = 80
COMPACT_THRESHOLD = 350

class SkinPanel(ScrollContainer):
    default_settingsPrefix = 'SkinPanel'

    def ApplyAttributes(self, attributes):
        super(SkinPanel, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.settingsPrefix = attributes.settingsPrefix or self.default_settingsPrefix
        self._logContext = attributes.get('logContext', None)
        self.whatchlist = []
        self.loaded = False
        self._loadingLock = locks.Lock()
        self.controller.onSkinsChange.connect(self.OnSkinsChange)
        self.controller.on_position_changed.connect(self.OnPositionChanged)
        self._licensedSkinGroup = None
        self._unlicensedSkinGroup = None
        self._previewType = None
        self._forcedCompact = attributes.get('compact', False)
        self._compactMode = False
        self._paragonHubSection = None

    def Reload(self):
        with self._loadingLock:
            self.loaded = False
            self.Flush()
        self.Load()

    def Load(self, selectedSkin = None):
        if self.loaded:
            return
        self._compactMode = self._forcedCompact or self.GetAbsoluteSize()[0] < COMPACT_THRESHOLD
        with self._loadingLock:
            self.Flush()
            now = gametime.GetWallclockTime()
            skins = sorted(self.controller.skins, key=lambda skin: skin.name.lower())
            self._paragonHubSection = OpenParagonHubSection(parent=self, align=uiconst.TOTOP, padBottom=8, display=False)
            licensedLabel = GetByLabel('UI/ShipCosmetics/LicensedSkins', shipTypeName='')
            settingName = '%s_LicensedSkins' % self.settingsPrefix
            licensed = [ skin for skin in skins if skin.licensed and (skin.expires is None or skin.expires > now) ]
            self._licensedSkinGroup = self.AddSkinGroup(licensedLabel, licensed, settingName=settingName, selectedSkin=selectedSkin)
            unlicensed = [ skin for skin in skins if not skin.licensed or skin.expires and skin.expires < now ]
            unlicensedLabel = GetByLabel('UI/ShipCosmetics/UnlicensedSkins', shipTypeName='')
            settingName = '%s_UnlicensedSkins' % self.settingsPrefix
            self._unlicensedSkinGroup = self.AddSkinGroup(unlicensedLabel, unlicensed, settingName=settingName, selectedSkin=selectedSkin)
            for i, entry in enumerate(self.mainCont.children):
                if hasattr(entry, 'AnimShow') and entry.display:
                    entry.AnimShow(delay=i * 0.05)

            self.loaded = True
            self.SetPreviewType(self._previewType)

    def AddSkinGroup(self, label, skins, settingName = None, selectedSkin = None):
        group = SkinGroupEntry(parent=self, text=label, collapsedSettingName=settingName)
        if len(skins) == 0:
            message = carbonui.TextHeader(parent=self, align=uiconst.TOTOP, padding=(25, 12, 0, 20), text=GetByLabel('UI/Skins/NoSkins'), color=carbonui.TextColor.SECONDARY)
            group.AddEntry(message)
        for skin in skins:
            entry = SkinEntrySlot(parent=self, align=uiconst.TOTOP, padTop=8, controller=self.controller, skin=skin, logContext=self._logContext, selectedSkin=selectedSkin)
            if self._compactMode:
                entry.SetCompact()
            group.AddEntry(entry)

        return group

    def SetPreviewType(self, typeID):
        self._previewType = typeID
        if self.loaded and self._previewType:
            self._SetPreviewText()
            self._paragonHubSection.display = is_skinnable_ship(typeID)
            self._paragonHubSection.shipTypeID = typeID

    def SetCompactMode(self, compact):
        self._forcedCompact = compact
        if self._forcedCompact:
            self._SetCompact()
            return
        width = self.GetAbsoluteSize()[0]
        compactMode = width < COMPACT_THRESHOLD
        if self._compactMode != compactMode:
            if width < COMPACT_THRESHOLD:
                self._SetCompact()
            else:
                self._SetExpanded()

    def _SetPreviewText(self):
        shipTypeName = evetypes.GetName(self._previewType)
        licensedLabel = GetByLabel('UI/ShipCosmetics/LicensedSkins', shipTypeName=shipTypeName)
        unlicensedLabel = GetByLabel('UI/ShipCosmetics/UnlicensedSkins', shipTypeName=shipTypeName)
        self._licensedSkinGroup.SetLabelText(licensedLabel)
        self._unlicensedSkinGroup.SetLabelText(unlicensedLabel)

    def OnSkinsChange(self):
        self.Reload()

    def OnPositionChanged(self):
        skinPreviewed = self.controller.previewed
        groupEntry, skinEntrySlot = self._FindGroupAndSkinElements(skinPreviewed)
        if groupEntry and hasattr(groupEntry, 'collapsed') and groupEntry.collapsed:
            groupEntry.ToggleCollapse()
        if skinEntrySlot:
            clipperTop = self.clipCont.GetAbsoluteTop()
            _, clipperHeight = self.clipCont.GetAbsoluteSize()
            skinEntryTop = skinEntrySlot.GetAbsoluteTop()
            if skinEntryTop > clipperTop + clipperHeight:
                rel = skinEntryTop - clipperTop
                totalHeight = self.mainCont.height
                pos = min(1.0, max(0, rel / float(totalHeight)))
                self.ScrollToVertical(pos)

    def _FindGroupAndSkinElements(self, skinPreviewed):
        for eachChild in self.mainCont.children:
            if not isinstance(eachChild, SkinGroupEntry):
                continue
            for eachEntry in eachChild._entries:
                if not isinstance(eachEntry, SkinEntrySlot):
                    continue
                if eachEntry.entry.skin == skinPreviewed:
                    return (eachChild, eachEntry)

        return (None, None)

    def Close(self):
        super(SkinPanel, self).Close()
        self.controller.Close()

    def _OnSizeChange_NoBlock(self, width, height):
        super(SkinPanel, self)._OnSizeChange_NoBlock(width, height)
        if self._forcedCompact:
            return
        if width < COMPACT_THRESHOLD:
            self._SetCompact()
        else:
            self._SetExpanded()

    def _SetCompact(self):
        if self._compactMode:
            return
        self._compactMode = True
        for eachChild in self.mainCont.children:
            if not isinstance(eachChild, SkinGroupEntry):
                continue
            for eachEntry in eachChild._entries:
                if not isinstance(eachEntry, SkinEntrySlot):
                    continue
                eachEntry.SetCompact()

    def _SetExpanded(self):
        if not self._compactMode:
            return
        self._compactMode = False
        for eachChild in self.mainCont.children:
            if not isinstance(eachChild, SkinGroupEntry):
                continue
            for eachEntry in eachChild._entries:
                if not isinstance(eachEntry, SkinEntrySlot):
                    continue
                eachEntry.SetExpanded()


class EntryMixin(object):

    def AnimShow(self, delay = 0.0):
        animations.FadeTo(self, duration=0.2, timeOffset=delay)
        animations.MoveInFromTop(self, curveType=uiconst.ANIM_OVERSHOT, duration=0.3, timeOffset=delay)


class SkinEntrySlot(Container, EntryMixin):
    default_name = 'SkinEntrySlot'
    default_alignMode = uiconst.TOTOP
    default_height = ENTRY_DEFAULT_HEIGHT

    def ApplyAttributes(self, attributes):
        super(SkinEntrySlot, self).ApplyAttributes(attributes)
        selectedSkin = attributes.get('selectedSkin', None)
        controller = attributes.controller
        skin = attributes.skin
        logContext = attributes.get('logContext', None)
        if skin.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
            self.entry = ThirdPartySkinEntry(parent=self, controller=controller, skin=skin, logContext=logContext, name='SkinEntry_{}'.format(skin.name.encode('utf-8')))
        else:
            self.entry = SkinEntry(parent=self, controller=controller, skin=skin, logContext=logContext, name='SkinEntry_{}'.format(skin.materialID))
        if selectedSkin:
            if selectedSkin.materialID == skin.materialID:
                self.entry.SetSkinState(BaseSkinEntry.STATE_PREVIEWED)

    def GetAbsoluteScrollPosition(self):
        _, top, _, height = self.GetAbsolute()
        return (top, top + height)

    def AnimShow(self, delay = 0.0):
        super(SkinEntrySlot, self).AnimShow(delay=delay)
        if self.entry.parent == self:
            self.entry.AnimShow(delay=delay)

    def SetCompact(self):
        self.entry.SetCompact()
        self.height = ENTRY_COMPACT_HEIGHT

    def SetExpanded(self):
        self.entry.SetExpanded()
        self.height = ENTRY_DEFAULT_HEIGHT


@Component(ButtonEffect(opacityIdle=0.0, opacityHover=0.2, opacityMouseDown=0.3, bgElementFunc=lambda parent, _: parent.blinkFill, audioOnEntry=uiconst.SOUND_ENTRY_HOVER, audioOnClick='fitting_window_skin_select_play'))

class BaseSkinEntry(Container):
    default_align = uiconst.TOALL
    default_bgColor = (0.0, 0.0, 0.0, 0.25)
    default_state = uiconst.UI_NORMAL
    STATE_IDLE = 1
    STATE_APPLIED = 2
    STATE_PENDING = 3
    STATE_PREVIEWED = 4

    def ApplyAttributes(self, attributes):
        super(BaseSkinEntry, self).ApplyAttributes(attributes)
        self.cosmeticsSvc = sm.GetService('cosmeticsSvc')
        self.controller = attributes.controller
        self.skin = attributes.skin
        self.skinstate = self.STATE_IDLE
        self._logContext = attributes.get('logContext', None)
        self.warningSprite = None
        self.Layout()
        self.UpdateSkinState(0)
        self.controller.onChange.connect(self.UpdateSkinState)

    @property
    def iconTexturePath(self):
        return self.skin.iconTexturePath

    def Layout(self):
        self._ConstructSelectionCont()
        self._ConstructIcon()
        self._ConstructMain()
        self._ConstructState()
        self._ConstructFrame()

    def _ConstructSelectionCont(self):
        self.selectionFrameCont = Container(parent=self, align=uiconst.TOALL)

    def _ConstructIcon(self):
        self.iconContainer = ContainerAutoSize(name='iconContainer', parent=self, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, padding=(32, 0, 32, 0))
        self.iconInnerContainer = Container(name='iconInnerContainer', parent=self.iconContainer, align=uiconst.CENTER, width=45, height=45)
        self.iconGlow = Sprite(name='iconGlow', parent=self.iconInnerContainer, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/skins/skin-icon-glow.png', opacity=0.0)
        Sprite(name='iconTexture', parent=self.iconInnerContainer, align=uiconst.TOALL, texturePath=self.iconTexturePath)
        self.iconShadow = Sprite(name='iconShadow', parent=self.iconInnerContainer, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/skins/icon-shadow.png')
        self.iconBG = Sprite(name='iconBackground', parent=self.iconContainer, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/skins/skin_background.png', color=eveColor.SAND_YELLOW, opacity=0.05, width=80, height=80)

    def _ConstructMain(self):
        self.textCont = VerticalCenteredContainer(name='textCont', parent=self, align=uiconst.TOALL, left=0, padRight=10)
        carbonui.TextBody(name='title', parent=self.textCont, align=uiconst.TOTOP, text=self.skin.name, color=carbonui.TextColor.HIGHLIGHT, maxLines=2)

    def _ConstructState(self):
        self.pendingIcon = Sprite(name='pendingIcon', parent=self, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, pos=(9, 9, 16, 16), texturePath='res:/UI/Texture/classes/skins/pending.png', opacity=0.0)
        animations.MorphScalar(self.pendingIcon, 'rotation', startVal=0.0, endVal=-2 * math.pi, duration=1.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        self.appliedIcon = Sprite(name='appliedIcon', parent=self, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, pos=(0, 0, 34, 34), texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png', opacity=0.0)
        self.previewedIcon = Sprite(name='previewedIcon', parent=self, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, pos=(9, 9, 18, 16), texturePath='res:/UI/Texture/classes/skins/previewed.png', opacity=0.0)
        self.stateIconLight = GradientThemeColored(name='stateIconLight', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, rotation=0, alphaData=[(0.0, 0.0),
         (0.25, 0.01),
         (0.5, 0.1),
         (0.6, 0.2),
         (0.7, 0.4),
         (0.8, 0.8),
         (0.9, 1.0)], colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.0)

    def _ConstructFrame(self):
        self.selectionFrame = Frame(name='selectionFrame', parent=self.selectionFrameCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/Heraldry/selectionFrame.png', color=eveColor.SUCCESS_GREEN, cornerSize=10, uiScaleVertices=True, fillCenter=False, padding=(-8, -8, -8, -8), opacity=0.0)
        self.selectionGradient = FillThemeColored(name='selectionGradient', bgParent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        self.blinkFill = FillThemeColored(name='blinkFill', bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)

    def UpdateSkinState(self, delay = None):
        if self.controller.applied == self.skin:
            delay = delay if delay is not None else self.controller.GetTimeUntilNextAllowedSkinChange()
            skinState = self.STATE_APPLIED
        elif self.controller.pending == self.skin:
            skinState = self.STATE_PENDING
        elif self.controller.previewed == self.skin:
            skinState = self.STATE_PREVIEWED
        else:
            skinState = self.STATE_IDLE
        self.SetSkinState(skinState, delay)

    def SetSkinState(self, state, delay = None):
        if state == self.skinstate:
            return
        if state == self.STATE_IDLE:
            self.AnimCollapse()
        elif self.skinstate == self.STATE_IDLE:
            self.AnimExpand()
        if state == self.STATE_APPLIED:
            if self.warningSprite:
                self.warningSprite.display = False
            self.AnimStateApplied(delay)
        elif state == self.STATE_PENDING:
            self.AnimStatePending()
        elif state == self.STATE_PREVIEWED:
            self.AnimStatePreviewed()
        elif state == self.STATE_IDLE:
            self.AnimStateIdle()
        self.skinstate = state

    def AnimShow(self, delay = 0.0):
        animations.FadeIn(self.blinkFill, endVal=0.4, curveType=uiconst.ANIM_WAVE, duration=0.4, timeOffset=delay * 1.4 + 0.4)

    def AnimExpand(self):
        animations.FadeIn(self.selectionFrame, endVal=1.0, duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
        animations.FadeIn(self.selectionGradient, endVal=0.15, duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
        self._AnimShowIconGlow()

    def AnimCollapse(self):
        animations.FadeOut(self.selectionFrame, duration=0.1)
        animations.FadeOut(self.selectionGradient, duration=0.1)
        self._AnimHideIconGlow()
        self._FadeOutSmallIcons()

    def _FadeOutSmallIcons(self):
        for eachIcon in (self.pendingIcon, self.previewedIcon, self.appliedIcon):
            animations.FadeOut(eachIcon, duration=0.05)

    def _AnimShowIconGlow(self):
        self.iconGlow.opacity = 0.05
        animations.SpMaskIn(self.iconGlow, duration=0.4)

    def _AnimHideIconGlow(self):
        animations.FadeOut(self.iconGlow, duration=0.3)

    def AnimStateIdle(self):
        for icon in (self.pendingIcon, self.previewedIcon, self.pendingIcon):
            animations.StopAllAnimations(icon)
            animations.FadeOut(icon, duration=0.15)

    def AnimStateApplied(self, delay = None):
        if delay <= 0:
            self._AnimStateApplied()
        else:
            uthread2.call_after_wallclocktime_delay(self._AnimStateApplied, delay)

    def _AnimStateApplied(self):
        animations.FadeOut(self.pendingIcon, duration=0.15)
        animations.FadeOut(self.previewedIcon, duration=0.15)
        self._AnimShowStateIcon(self.appliedIcon)

    def AnimStatePending(self):
        animations.FadeOut(self.appliedIcon, duration=0.15)
        animations.FadeOut(self.previewedIcon, duration=0.15)
        animations.FadeIn(self.pendingIcon, duration=0.15)

    def AnimStatePreviewed(self):
        animations.FadeOut(self.appliedIcon, duration=0.15)
        animations.FadeOut(self.pendingIcon, duration=0.15)
        self._AnimShowStateIcon(self.previewedIcon)

    def _AnimShowStateIcon(self, icon):

        def continue_glowExpand():
            animations.MorphScalar(icon, 'glowExpand', startVal=0.0, endVal=20.0, duration=0.5, curveType=uiconst.ANIM_SMOOTH)
            animations.SpColorMorphTo(icon, attrName='glowColor', startColor=(1.0, 1.0, 1.0, 0.5), endColor=(0.0, 0.0, 0.0, 0.0), duration=0.25, curveType=uiconst.ANIM_SMOOTH)

        animations.FadeIn(icon, duration=0.15, timeOffset=0.15)
        animations.SpColorMorphTo(icon, attrName='glowColor', startColor=(0.3, 0.3, 0.3, 0.0), endColor=(1.0, 1.0, 1.0, 0.5), duration=0.15, timeOffset=0.2, curveType=uiconst.ANIM_SMOOTH)
        animations.MorphScalar(icon, 'glowExpand', startVal=30.0, endVal=0.0, duration=0.2, timeOffset=0.15, curveType=uiconst.ANIM_SMOOTH, callback=continue_glowExpand)
        animations.FadeTo(self.stateIconLight, startVal=0.0, endVal=0.15, duration=0.55, timeOffset=0.15, curveType=uiconst.ANIM_BOUNCE)

    def Pick(self):
        try:
            self.controller.PickSkin(self.skin)
        except SkinNotAvailableForType:
            logger.warning('PickSkin failed with SkinNotAvailableForType. Most likely due to the shipID changing in the controller before the UI is torn down.')
            sys.exc_clear()

    def OnClick(self, *args):
        self.Pick()

    def SetCompact(self):
        self.iconContainer.padding = (12, 0, 8, 0)
        self.iconInnerContainer.SetSize(24, 24)
        self.iconBG.SetSize(40, 40)
        self.textCont.padRight = 30

    def SetExpanded(self):
        self.iconContainer.padding = (32, 0, 32, 0)
        self.iconInnerContainer.SetSize(46, 46)
        self.iconBG.SetSize(80, 80)
        self.textCont.padRight = 10


class SkinEntry(BaseSkinEntry):

    def _ConstructMain(self):
        super(SkinEntry, self)._ConstructMain()
        self.warningSprite = Sprite(parent=self, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, pos=(2, 2, 16, 16), texturePath='res:/ui/texture/icons/44_32_7.png', hint=GetByLabel('UI/Skins/WarningNoPermissionToChangeSkin'))
        self.warningSprite.display = False
        if self.skin.licensed and not self.skin.expired:
            SkinDurationLabel(name='durationText', parent=self.textCont, align=uiconst.TOTOP, skin=self.skin, padTop=3)
            if self.controller.IsSkinAccessRestricted():
                self.warningSprite.hint = GetByLabel('UI/Skins/WarningNoPermissionToChangeSkin')
                self.warningSprite.display = True
            elif self.controller.IsDisabledDueToDamage():
                self.warningSprite.display = True
                self.warningSprite.hint = GetByLabel('UI/Skins/WarningTooDamagedToChangeSkin')
        else:
            buttonCont = Container(name='buttonCont', parent=self.textCont, align=uiconst.TOTOP, height=24, padTop=8)
            is_single_use = self._AreAllLicensesSingleUse()
            SkinBuyButtonPlex(parent=buttonCont, align=uiconst.TOLEFT, typeID=self.controller.typeID, materialID=self.skin.materialID, logContext=self._logContext, padRight=4, display=False)
            SkinBuyButtonIsk(parent=buttonCont, align=uiconst.TOLEFT, typeID=self.controller.typeID, materialID=self.skin.materialID, logContext=self._logContext, state=uiconst.UI_HIDDEN if is_single_use else uiconst.UI_NORMAL, padRight=4)
            if is_single_use:
                MoreInfoIcon(name='SingleUseSkinsInfoIcon', parent=buttonCont, align=uiconst.TOLEFT, hint=GetByLabel('UI/Skins/SingleUseHint'), padRight=4)

    def _AreAllLicensesSingleUse(self):
        return self.cosmeticsSvc.static.AreAllLicensesSingleUse(self.controller.typeID, self.skin.materialID)

    def GetMenu(self):
        entries = []
        gmEntries = self._GetGMMenuEntries()
        if len(gmEntries) > 0:
            entries.extend(gmEntries)
            entries.append(None)
        entries.extend([[GetByLabel('UI/Commands/ShowInfo'), self.ShowMaterialInfo], None, [GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), self.OpenMarketWindow]])
        return entries

    def _GetGMMenuEntries(self):
        if session.role & ROLE_GML != ROLE_GML:
            return []
        elif self.skin.skinID is None:
            skinInfo = GetSkinUsedWithTypeAndMaterial(self.skin.materialID, self.controller.typeID)
            ownerText = 'my corp' if skinInfo.isStructureSkin else 'me'
            m = [['GM: Give %s time-limited' % ownerText, GiveSkin, (self.skin.materialID, self.controller.typeID)], ['GM: Give %s single-use' % ownerText, GiveLimitedSkin, (self.skin.materialID, self.controller.typeID)], ['GM: Give %s permanently' % ownerText, GivePermanentSkin, (self.skin.materialID, self.controller.typeID)]]
            m += [['GM: skinID: %s' % skinInfo.skinID, blue.pyos.SetClipboardData, (str(skinInfo.skinID),)]]
            return m
        else:
            m = [['GM: Remove SKIN', RemoveSkin, (self.skin.skinID,)]]
            m += [['GM: Set SKIN as expired (processed on next login)', GiveExpiredSkin, (self.skin.skinID,)]]
            m += [['GM: skinID: %s' % self.skin.skinID, blue.pyos.SetClipboardData, (str(self.skin.skinID),)]]
            return m

    def OpenMarketWindow(self):
        self.cosmeticsSvc.OpenMarketForTypeWithMaterial(self.controller.typeID, self.skin.materialID)
        LogBuySkinIsk(self.controller.typeID, self.skin.materialID, self._logContext)

    def ShowMaterialInfo(self):
        sm.GetService('info').ShowInfo(typeSkinMaterial, itemID=self.skin.materialID)


class ThirdPartySkinEntry(BaseSkinEntry):

    def _ConstructIcon(self):
        super(ThirdPartySkinEntry, self)._ConstructIcon()
        self.iconShadow.display = False

    def _ConstructMain(self):
        super(ThirdPartySkinEntry, self)._ConstructMain()
        prefixText = eveformat.color(GetByLabel('Achievements/UI/active'), carbonui.TextColor.NORMAL)
        expiresText = eveformat.color(GetByLabel('UI/Skins/SkinDurationPermanent'), carbonui.TextColor.SECONDARY)
        carbonui.TextDetail(name='durationText', parent=self.textCont, align=uiconst.TOTOP, text='%s: %s' % (prefixText, expiresText), padTop=3)
        try:
            creatorName = cfg.eveowners.Get(self.skin.skin_data.creator_character_id).ownerName
        except:
            creatorName = None

        if creatorName:
            prefixText = eveformat.color(GetByLabel('UI/Personalization/ShipSkins/SKINR/MadeBy'), carbonui.TextColor.NORMAL)
            creatorText = eveformat.color(creatorName, carbonui.TextColor.SECONDARY)
            carbonui.TextDetail(name='madeBy', parent=self.textCont, align=uiconst.TOTOP, text='%s: %s' % (prefixText, creatorText), padTop=3)


class SkinGroupEntry(ContainerAutoSize, EntryMixin):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        super(SkinGroupEntry, self).ApplyAttributes(attributes)
        self.text = attributes.text
        self._entries = set()
        self.Layout()

    def AddEntry(self, entry):
        self._entries.add(entry)

    def Layout(self):
        panel = ContainerAutoSize(name='panel', parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=10)
        panel.DelegateEvents(self)
        self.label = carbonui.TextBody(parent=panel, align=uiconst.TOTOP, text=self.text, maxlines=2, bold=True)

    def SetLabelText(self, text):
        self.label.text = text

    def _GetEntrySortKey(self, entry):
        return entry.parent.children.index(entry)


class SkinDurationLabel(carbonui.TextDetail):

    def ApplyAttributes(self, attributes):
        super(SkinDurationLabel, self).ApplyAttributes(attributes)
        self.skin = attributes.skin
        self.text = self._GetExpiryText()
        if not self.skin.permanent:
            uthread.new(self._UpdateLabelThread)

    def _UpdateLabelThread(self):
        while True:
            blue.synchro.SleepWallclock(1000)
            if self.destroyed:
                break
            self.text = self._GetExpiryText()

    def _GetExpiryText(self):
        prefixText = eveformat.color(GetByLabel('Achievements/UI/active'), carbonui.TextColor.NORMAL)
        expiresText = eveformat.color(self.skin.GetExpiresLabel(), carbonui.TextColor.SECONDARY)
        return '%s: %s' % (prefixText, expiresText)


class SkinBuyButton(Button):
    default_iconSize = 12
    default_density = Density.COMPACT

    def ApplyAttributes(self, attributes):
        super(SkinBuyButton, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        self.materialID = attributes.materialID
        self.logContext = attributes.logContext


class SkinBuyButtonIsk(SkinBuyButton):
    default_name = 'SkinBuyButtonIsk'
    default_variant = ButtonVariant.PRIMARY
    default_label = GetByLabel('UI/Skins/BuyWithIsk')
    default_texturePath = 'res:/UI/Texture/classes/skins/isk_12.png'

    def OnClick(self, *args):
        if not self.enabled:
            return
        sm.GetService('cosmeticsSvc').OpenMarketForTypeWithMaterial(self.typeID, self.materialID)
        LogBuySkinIsk(self.typeID, self.materialID, self.logContext)


class SkinBuyButtonPlex(SkinBuyButton):
    default_name = 'SkinBuyButtonPlex'
    default_style = ButtonStyle.MONETIZATION
    default_label = GetByLabel('UI/Skins/BuyWithAur')
    default_texturePath = PLEX_12_SOLID_WHITE
    default_pickState = carbonui.PickState.ON

    def ApplyAttributes(self, attributes):
        super(SkinBuyButtonPlex, self).ApplyAttributes(attributes)
        self.types = self.GetLicenseTypesForMaterial()
        self.offers = None
        if callable(self.types):
            self.types = self.types()
        if isinstance(self.types, numbers.Number):
            self.types = [self.types]
        if self.types is not None:
            uthread.new(self.FindOffersAndReveal)

    def FindOffersAndReveal(self):
        try:
            store = sm.GetService('vgsService').GetStore()
            self.offers = store.SearchOffersByTypeIDs(self.types)
            self.display = len(self.offers) > 0
        except Exception as e:
            if len(e.args) >= 1 and e.args[0] == 'tokenMissing':
                log.LogInfo('Failed to search the NES for offers due to missing token')
            else:
                log.LogException('Failed to search the NES for offers')

    def GetLicenseTypesForMaterial(self):
        licenses = sm.GetService('cosmeticsSvc').static.GetLicensesForTypeWithMaterial(self.typeID, self.materialID)
        return [ license.licenseTypeID for license in licenses ]

    def OnClick(self, *args):
        if not self.enabled:
            return
        sm.GetService('vgsService').OpenStore(typeIds=self.types)
        LogBuySkinAur(self.typeID, self.materialID, self.logContext)


class VerticalCenteredContainer(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP

    def __init__(self, **kwargs):
        kwargs['callback'] = self._on_size_change
        super(VerticalCenteredContainer, self).__init__(**kwargs)

    @contextlib.contextmanager
    def auto_size_disabled(self):
        was_enabled = self.isAutoSizeEnabled
        self.DisableAutoSize()
        try:
            yield self
        finally:
            if was_enabled:
                self.EnableAutoSize()

    def _on_size_change(self):
        to_top_aligned_children = filter(lambda child: child.align == uiconst.TOTOP, self.children)
        if to_top_aligned_children:
            content_height = 0
            for i, child in enumerate(to_top_aligned_children):
                content_height += child.height + child.padTop + child.padBottom
                if i > 0:
                    content_height += child.top

            if content_height <= 0:
                return
            _, height = self.GetCurrentAbsoluteSize()
            adjusted_top = max(0.0, math.floor((height - content_height) / 2.0))
            to_top_aligned_children[0].top = adjusted_top

    def SetSizeAutomatically(self):
        if self.align == uiconst.TOALL:
            self._on_size_change()
        else:
            super(VerticalCenteredContainer, self).SetSizeAutomatically()


class OpenParagonHubSection(ContainerAutoSize):
    default_align = carbonui.Align.TOTOP
    default_alignMode = carbonui.Align.TOTOP

    def __init__(self, shipTypeID = None, *args, **kwargs):
        super(OpenParagonHubSection, self).__init__(*args, **kwargs)
        self.shipTypeID = shipTypeID
        Line(parent=self, align=carbonui.Align.TOTOP, weight=2, color=eveColor.PARAGON_BLUE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, opacity=0.6)
        container = ContainerAutoSize(parent=self, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, bgColor=eveColor.Color(eveColor.PARAGON_BLUE).SetOpacity(0.1).GetRGBA())
        Sprite(parent=container, state=carbonui.uiconst.UI_DISABLED, align=carbonui.Align.CENTERLEFT, texturePath='res:/UI/texture/classes/paintTool/paragon_logo.png', height=32, width=34, left=8)
        carbonui.TextBody(parent=container, align=carbonui.Align.TOTOP, padding=(50, 16, 8, 0), text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/Title'))
        carbonui.TextDetail(parent=container, align=carbonui.Align.TOTOP, padding=(50, 0, 8, 16), text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ShortDescription'))
        open_store_btn = Button(parent=self, align=carbonui.Align.TOTOP, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ViewStoreButton'), frame_type=carbonui.ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, func=self._open_store)
        open_store_btn.analyticID = OPEN_SKINR_BUTTON_ANALYTIC_ID

    def _open_store(self, *args, **kwargs):
        from eve.client.script.ui.cosmetics.ship.shipSKINRWindow import ShipSKINRWindow
        from eve.client.script.ui.cosmetics.ship.const import SkinrPage
        ShipSKINRWindow.open_on_paragon_hub(ship_type_id=self.shipTypeID)
