#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveIcon.py
import eve.common.lib.appConst as const
import eveicon
import log
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.bunch import Bunch
from eve.client.script.ui.const.eveIconConst import IN_ICONS, IN_CORP_ICONS, IN_SMALL_ICONS, CORP_ICONS, RACE_ICONS
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from fsdBuiltData.common.iconIDs import GetIconFile

class Icon(Sprite):
    __guid__ = 'uicontrols.Icon'
    size_doc = 'Optional icon pixel size. Will override width and height with size.'
    typeID_doc = 'Optional param to override the icon path.  Will get a type based icon instead.'
    itemID_doc = "Optional param for char portraits or 'location' icons. Used with typeID."
    graphicID_doc = 'Optional param to get icon based on standard graphic record.'
    default_size = None
    default_typeID = None
    default_graphicID = None
    default_itemID = None
    default_icon = None
    default_ignoreSize = 0
    default_rect = None
    default_name = 'icon'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0

    def ApplyAttributes(self, attributes):
        if attributes.__gotShape__ and len(attributes.keys()) == 1:
            return
        for each in ('iconID', 'path'):
            if each in attributes:
                log.LogInfo('Someone creating icon with', each, 'as keyword', attributes.Get(each, 'None'))

        size = attributes.get('size', self.default_size)
        if attributes.get('align', self.default_align) != uiconst.TOALL:
            if size:
                attributes.width = attributes.height = size
        else:
            attributes.pos = (0, 0, 0, 0)
            attributes.width = attributes.height = 0
        icon = attributes.get('icon', self.default_icon)
        if 'icon' in attributes:
            del attributes['icon']
        Sprite.ApplyAttributes(self, attributes)
        ignoreSize = attributes.get('ignoreSize', self.default_ignoreSize)
        self.typeID = attributes.get('typeID', self.default_typeID)
        self.itemID = attributes.get('itemID', self.default_itemID)
        graphicID = attributes.get('graphicID', self.default_graphicID)
        isCopy = attributes.get('isCopy', False)
        if icon:
            self.LoadIcon(icon, ignoreSize=ignoreSize)
        elif self.typeID:
            self.LoadIconByTypeID(self.typeID, itemID=self.itemID, size=size, ignoreSize=ignoreSize, isCopy=isCopy)
        elif graphicID:
            self.LoadIconByIconID(graphicID, ignoreSize=ignoreSize)
        else:
            self.LoadTexture('res:/UI/Texture/None.dds')
        onClick = attributes.get('OnClick', None)
        if onClick:
            self.OnClick = onClick

    def LoadIconByIconID(self, graphicID, ignoreSize = False):
        iconFile = GetIconFile(graphicID)
        if iconFile:
            self.LoadIcon(iconFile, ignoreSize)

    def LoadIcon(self, icon, ignoreSize = False):
        if not icon:
            return
        if isinstance(icon, eveicon.IconData):
            self.SetTexturePath(icon)
            return
        if isinstance(icon, int):
            return self.LoadIconByIconID(icon, ignoreSize=ignoreSize)
        icon = Sprite.LoadIcon(self, icon, ignoreSize)
        if icon is not None:
            fullPathData = self.ConvertIconNoToResPath(icon)
            if fullPathData:
                resPath, iconSize = fullPathData
                self.LoadTexture(resPath)
                if not ignoreSize and self.GetAlign() != uiconst.TOALL and self.texture.atlasTexture:
                    self.width = iconSize
                    self.height = iconSize

    def LoadIconByTypeID(self, typeID, itemID = None, size = None, ignoreSize = False, isCopy = False):
        self.typeID = typeID
        sm.GetService('photo').GetIconByType(self, typeID, itemID=itemID, size=size, ignoreSize=ignoreSize, isCopy=isCopy)

    @staticmethod
    def ConvertIconNoToResPath(iconNo):
        resPath = None
        if iconNo.startswith('res:'):
            return (iconNo, 0)
        parts = iconNo.split('_')
        if len(parts) == 2:
            sheet, iconNum = parts
            iconSize = GetIconSize(sheet)
            resPath = 'res:/ui/texture/icons/%s_%s_%s.png' % (int(sheet), int(iconSize), int(iconNum))
        elif iconNo.startswith('ui_'):
            u, sheet, iconSize, iconNum = parts
            iconSize = int(iconSize)
            resPath = 'res:/ui/texture/icons/%s_%s_%s.png' % (int(sheet), int(iconSize), int(iconNum))
        elif iconNo.startswith('corps_'):
            resPath = 'res:/ui/texture/corps/' + iconNo[6:] + '.png'
            iconSize = 128
        elif iconNo.startswith('alliance_'):
            resPath = 'res:/ui/texture/alliance/' + iconNo[9:] + '.png'
            iconSize = 128
        elif iconNo.startswith('c_'):
            c, sheet, iconNum = parts
            resPath = 'res:/ui/texture/corps/%s_128_%s.png' % (int(sheet), int(iconNum))
            iconSize = 128
        elif iconNo.startswith('a_'):
            a, sheet, iconNum = parts
            resPath = 'res:/ui/texture/alliance/%s_128_%s.png' % (int(sheet), int(iconNum))
            iconSize = 128
        if resPath:
            return (resPath, iconSize)
        log.LogWarn('Icon: MISSING CONVERSION HANDLING FOR', iconNo)


class DraggableIcon(Container):
    __guid__ = 'uicls.DraggableIcon'
    default_name = 'draggableIcon'
    default_opacity = 1.0
    default_location_icon = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.location_icon = attributes.get('location_icon', self.default_location_icon)
        if self.location_icon:
            self.sr.icon = Container(parent=self, name='icont', align=uiconst.TOALL, clipChildren=True)
        else:
            self.sr.icon = Icon(parent=self, name='icon', align=uiconst.TOALL)
        self.ChangeIcon(**attributes)

    def ChangeIcon(self, typeID = None, itemID = None, icon = None, isCopy = False, **kw):
        if self.location_icon and typeID is not None:
            self.typeID = typeID
            sm.GetService('photo').GetIconByType(self.sr.icon, typeID, itemID=itemID)
        elif icon:
            self.sr.icon.LoadIcon(icon, ignoreSize=True)
        elif typeID:
            self.sr.icon.LoadIconByTypeID(typeID, itemID=itemID, ignoreSize=True, isCopy=isCopy)
            from eve.client.script.ui.util.uix import GetTechLevelIcon
            techIcon = GetTechLevelIcon(None, typeID=typeID)
            if techIcon:
                techIcon.SetParent(self, 0)

    def LoadIcon(self, icon, *args, **kwds):
        self.ChangeIcon(icon=icon)

    def LoadIconByTypeID(self, typeID, itemID = None, isCopy = False, *args, **kwds):
        self.ChangeIcon(typeID=typeID, itemID=itemID, isCopy=isCopy)


class LogoIcon(Icon):
    __guid__ = 'uicls.LogoIcon'
    default_isSmall = None
    default_isSmall_doc = 'Should we use the small version for faction icons.'
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        itemID = attributes.get('itemID', None)
        icon = None
        if itemID is not None:
            if idCheckers.IsCorporation(itemID):
                if CheckCorpID(itemID):
                    icon = CORP_ICONS[itemID]
                else:
                    raise ValueError, 'LogoIcon class does not support custom corp icons.  Use CorpIcon for that'
            elif idCheckers.IsAlliance(itemID):
                raise ValueError, 'LogoIcon class does not support Alliance Logos.  Use GetLogoIcon or GetOwnerIcon'
            elif idCheckers.IsFaction(itemID):
                isSmall = attributes.get('isSmall', self.default_isSmall)
                icon = self.GetFactionIconID(itemID, isSmall)
            elif itemID in RACE_ICONS:
                icon = RACE_ICONS[itemID]
        if icon is None:
            icon = 'ui_1_16_256'
        attributes['icon'] = icon
        Icon.ApplyAttributes(self, attributes)

    @staticmethod
    def GetFactionIconID(factionID, isSmall = default_isSmall):
        if isSmall and factionID in IN_SMALL_ICONS:
            return IN_SMALL_ICONS.get(factionID)
        elif factionID in IN_ICONS:
            return IN_ICONS.get(factionID)
        elif factionID in IN_CORP_ICONS:
            return IN_CORP_ICONS.get(factionID)
        else:
            return None

    @staticmethod
    def GetFactionIconTexturePath(factionID, isSmall = True):
        iconNo = LogoIcon.GetFactionIconID(factionID, isSmall)
        texturePath, _ = Icon.ConvertIconNoToResPath(iconNo)
        return texturePath


class CorpIcon(Container):
    __guid__ = 'uicls.CorpIcon'
    isDragObject = True
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 128
    default_size = None
    size_doc = 'Optional icon pixel size. Will override width and height with size.'
    default_name = 'corplogo'
    default_state = uiconst.UI_DISABLED
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        if attributes.get('align', self.default_align) != uiconst.TOALL:
            size = attributes.get('size', self.default_size)
            if size:
                attributes.width = attributes.height = size
        else:
            attributes.pos = (0, 0, 0, 0)
            attributes.width = attributes.height = 0
        Container.ApplyAttributes(self, attributes)
        self.colorIDs = [None, None, None]
        self.shapeIDs = [None, None, None]
        Sprite(parent=self, name='layerTopSampl', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.0), ignoreColorBlindMode=True)
        Sprite(parent=self, name='layerTopSampl', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.0), ignoreColorBlindMode=True)
        Sprite(parent=self, name='layerTopSampl', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.0), ignoreColorBlindMode=True)
        self.corpID = attributes.get('corpID', None)
        if attributes.dontUseThread:
            self.DoLayout(self.corpID, attributes)
        else:
            uthread.new(self.DoLayout, self.corpID, attributes)

    def Load(self, corpID, **kwargs):
        self.corpID = corpID
        attributes = Bunch(**kwargs)
        if attributes.dontUseThread:
            self.DoLayout(self.corpID, attributes)
        else:
            uthread.new(self.DoLayout, self.corpID, attributes)

    def DoLayout(self, corpID, attributes):
        big = attributes.get('big', False)
        onlyValid = attributes.get('onlyValid', False)
        logoData = attributes.get('logoData', None)
        if corpID in CORP_ICONS:
            return CORP_ICONS[corpID]
        if logoData is None:
            if not corpID:
                return
            logoData = cfg.corptickernames.Get(corpID)
        if logoData:
            log.LogInfo('LogoIcon.GetCorpIconID', 'corpID:', corpID, 'shape1:', logoData.shape1, 'shape2:', logoData.shape2, 'shape3:', logoData.shape3, 'color1:', logoData.color1, 'color2:', logoData.color2, 'color3:', logoData.color3)
            shapeIDs = (logoData.shape1, logoData.shape2, logoData.shape3)
            colorIDs = (logoData.color1, logoData.color2, logoData.color3)
            for i in xrange(3):
                shapeID = shapeIDs[i]
                colorID = colorIDs[i]
                if shapeID is not None and shapeID == int(shapeID):
                    self.SetLayerShapeAndColor(i, shapeID, colorID, big)

        elif onlyValid:
            raise RuntimeError('not valid corpID')

    def SetLayerShapeAndColor(self, layerNum, shapeID = None, colorID = None, isBig = False):
        if self.destroyed:
            return
        layer = self.children[layerNum]
        if shapeID is None:
            shapeID = self.shapeIDs[layerNum]
        else:
            self.shapeIDs[layerNum] = shapeID
        if colorID is None:
            colorID = self.colorIDs[layerNum]
        else:
            self.colorIDs[layerNum] = colorID
        texturePath = const.graphicCorpLogoLibShapes.get(shapeID, const.graphicCorpLogoLibShapes[const.graphicCorpLogoLibNoShape])
        if isBig:
            texturePath = '%s/large/%s' % tuple(texturePath.rsplit('/', 1))
        if colorID is not None and colorID == int(colorID):
            color, blendMode = const.graphicCorpLogoLibColors.get(colorID, const.CORPLOGO_DEFAULT_COLOR)
        else:
            color, blendMode = const.CORPLOGO_DEFAULT_COLOR
        if blendMode == const.CORPLOGO_BLEND:
            layer.SetTexturePath(texturePath)
            layer.SetSecondaryTexturePath(None)
            layer.spriteEffect = trinity.TR2_SFX_COPY
            layer.SetRGBA(*color)
        elif blendMode == const.CORPLOGO_SOLID:
            layer.SetTexturePath('res:/UI/Texture/fill.dds')
            layer.SetSecondaryTexturePath(texturePath)
            layer.spriteEffect = trinity.TR2_SFX_MASK
            layer.SetRGBA(*color)
        elif blendMode == const.CORPLOGO_GRADIENT:
            layer.SetTexturePath('res:/UI/Texture/corpLogoLibs/%s.png' % colorID)
            layer.SetSecondaryTexturePath(texturePath)
            layer.spriteEffect = trinity.TR2_SFX_MASK
            layer.SetRGBA(1.0, 1.0, 1.0, 1.0)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        sm.GetService('info').ShowInfo(typeID=const.typeCorporation, itemID=self.corpID)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)


def CheckCorpID(corpID):
    return corpID in CORP_ICONS


def GetLogoIcon(itemID = None, **kw):
    if idCheckers.IsAlliance(itemID):
        logo = Icon(icon=None, **kw)
        sm.GetService('photo').GetAllianceLogo(itemID, 128, logo)
        return logo
    elif not idCheckers.IsCorporation(itemID) or CheckCorpID(itemID):
        return LogoIcon(itemID=itemID, **kw)
    else:
        return CorpIcon(corpID=itemID, **kw)


def GetOwnerLogo(parent, ownerID, size = 64, noServerCall = False, callback = False, orderIfMissing = True, **kwargs):
    if idCheckers.IsCharacter(ownerID) or idCheckers.IsAlliance(ownerID):
        logo = Icon(icon=None, parent=parent, width=size, height=size, ignoreSize=True, **kwargs)
        if idCheckers.IsAlliance(ownerID):
            path = sm.GetService('photo').GetAllianceLogo(ownerID, 128, logo, callback=callback, orderIfMissing=orderIfMissing)
        else:
            path = sm.GetService('photo').GetPortrait(ownerID, size, logo, callback=callback, orderIfMissing=orderIfMissing)
        return path is not None
    if idCheckers.IsCorporation(ownerID) or idCheckers.IsFaction(ownerID):
        GetLogoIcon(itemID=ownerID, parent=parent, width=size, height=size, ignoreSize=True, **kwargs)
    else:
        raise RuntimeError('ownerID %d is not of an owner type!!' % ownerID)
    return True


class OwnerIcon(Container):
    default_name = 'OwnerIcon'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_size = 128
    default_isSmall = False
    default_spriteEffect = None
    default_textureSecondaryPath = None
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.ownerID = attributes.ownerID
        self.size = attributes.get('size', self.default_size)
        self.isSmall = attributes.get('isSmall', self.default_isSmall)
        self.spriteEffect = attributes.get('spriteEffect', self.default_spriteEffect)
        self.textureSecondaryPath = attributes.get('textureSecondaryPath', self.default_textureSecondaryPath)
        if self.ownerID:
            self.icon = self.ConstructIcon()

    def ConstructIcon(self):
        self.Flush()
        icon = self._ConstructIcon()
        icon.align = uiconst.TOALL
        icon.width = icon.height = 0
        icon.state = uiconst.UI_DISABLED
        if self.textureSecondaryPath:
            icon.SetSecondaryTexturePath(self.textureSecondaryPath)
        if self.spriteEffect:
            icon.spriteEffect = self.spriteEffect
        return icon

    def _ConstructIcon(self):
        if idCheckers.IsCharacter(self.ownerID) or idCheckers.IsAlliance(self.ownerID):
            icon = Icon(icon=None, parent=self, ignoreSize=True)
            if idCheckers.IsAlliance(self.ownerID):
                sm.GetService('photo').GetAllianceLogo(self.ownerID, 128, icon, orderIfMissing=True)
            else:
                sm.GetService('photo').GetPortrait(self.ownerID, self.size, icon, orderIfMissing=True)
        elif idCheckers.IsCorporation(self.ownerID) or idCheckers.IsFaction(self.ownerID):
            icon = GetLogoIcon(itemID=self.ownerID, parent=self, ignoreSize=True, isSmall=self.isSmall)
        else:
            raise RuntimeError('ownerID %d is not of an owner type!!' % self.ownerID)
        return icon

    def GetMenu(self):
        return sm.GetService('menu').GetMenuForOwner(self.ownerID)

    def SetOwnerID(self, ownerID):
        self.ownerID = ownerID
        self.icon = self.ConstructIcon()

    def OnClick(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        typeID = cfg.eveowners.Get(self.ownerID).typeID
        sm.GetService('info').ShowInfo(typeID, self.ownerID)

    def GetHint(self):
        if self.hint:
            return self.hint
        if self.ownerID:
            return cfg.eveowners.Get(self.ownerID).ownerName

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        animations.FadeTo(self, self.opacity, 1.5, duration=0.3)

    def OnMouseExit(self, *args):
        animations.FadeTo(self, self.opacity, 1.0, duration=0.3)

    def GetDragData(self):
        dragData = Bunch()
        dragData.__guid__ = 'listentry.User'
        dragData.itemID = self.ownerID
        dragData.charID = self.ownerID
        dragData.info = Bunch(typeID=self.GetTypeID(), name=cfg.eveowners.Get(self.ownerID).name)
        return [dragData]

    def GetTypeID(self):
        if idCheckers.IsCharacter(self.ownerID):
            return appConst.typeCharacter
        if idCheckers.IsAlliance(self.ownerID):
            return appConst.typeAlliance
        if idCheckers.IsCorporation(self.ownerID):
            return appConst.typeCorporation
        if idCheckers.IsFaction(self.ownerID):
            return appConst.typeFaction


class PreviewIcon(Icon):
    __guid__ = 'uicls.PreviewIcon'
    default_size = 16
    default_typeID = None

    def ApplyAttributes(self, attributes):
        typeID = attributes.get('typeID', self.default_typeID)
        icon = 'ui_38_16_89'
        attributes['icon'] = icon
        Icon.ApplyAttributes(self, attributes)
        self.OnClick = (self.Preview, typeID)

    def Preview(self, typeID, *args):
        sm.GetService('preview').PreviewType(typeID)


class MenuIcon(Icon):
    __guid__ = 'uicontrols.MenuIcon'
    default_size = 16

    def ApplyAttributes(self, attributes):
        size = attributes.get('size', self.default_size)
        if size <= 16:
            icon = 'ui_73_16_50'
        else:
            icon = 'ui_77_32_49'
        attributes['icon'] = icon
        Icon.ApplyAttributes(self, attributes)
        self.SetAlpha(0.8)
        self.expandOnLeft = 1

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.SetAlpha(1.0)

    def OnMouseExit(self, *args):
        self.SetAlpha(0.8)


def GetIconSize(sheetNum):
    sheetNum = int(sheetNum)
    one = [90,
     91,
     92,
     93]
    two = [17,
     18,
     19,
     28,
     29,
     32,
     33,
     59,
     60,
     61,
     65,
     66,
     67,
     80,
     85,
     86,
     87,
     88,
     89,
     102,
     103,
     104]
    eight = [22,
     44,
     75,
     77,
     105,
     112]
    sixteen = [38, 73]
    if sheetNum in one:
        return 256
    if sheetNum in two:
        return 128
    if sheetNum in eight:
        return 32
    if sheetNum in sixteen:
        return 16
    return 64


class OwnerIconAndLabel(ContainerAutoSize):
    default_name = 'OwnerIconAndLabel'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        ownerID = attributes.ownerID
        iconSize = attributes.iconSize
        iconAlign = attributes.iconAlign
        text = attributes.get('text', cfg.eveowners.Get(ownerID).ownerName)
        iconCont = Container(parent=self, align=iconAlign, pos=(0,
         0,
         iconSize,
         iconSize))
        self.ownerIcon = OwnerIcon(parent=iconCont, state=uiconst.UI_DISABLED, ownerID=ownerID, size=iconSize, align=uiconst.TOALL)
        labelContainer = ContainerAutoSize(parent=self, align=iconAlign, left=5)
        EveLabelMedium(name='fromStandingOwnerLabel', parent=labelContainer, align=uiconst.CENTERLEFT, text=text)

    def GetHint(self):
        return self.ownerIcon.GetHint()

    def OnClick(self, *args):
        self.ownerIcon.OnClick()

    def GetMenu(self):
        return self.ownerIcon.GetMenu()

    def OnMouseEnter(self, *args):
        animations.FadeTo(self, self.opacity, 1.5, duration=0.3)

    def OnMouseExit(self, *args):
        animations.FadeTo(self, self.opacity, 1.0, duration=0.3)
