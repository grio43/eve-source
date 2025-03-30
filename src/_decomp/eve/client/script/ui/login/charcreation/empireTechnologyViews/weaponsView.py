#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireTechnologyViews\weaponsView.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.uicore import uicore
from charactercreator.client.scalingUtils import SMALL_SCREEN_HEIGHT, BIG_SCREEN_HEIGHT
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.login.charcreation.empireTechnologyViews.technologyView import TechnologyView
from eve.client.script.ui.login.charcreation.technologyViewUtils import LineDecoration, LINE_DECORATION_GRADIENT_HEIGHT
from eve.client.script.ui.util.uix import GetTextHeight
import trinity
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
ELEMENTS_PADDING_TOP = -100
LINE_DECORATION_WIDTH = 1000
LINE_DECORATION_HEIGHT = 4
WEAPONS_DESCRIPTION_WIDTH = 400
WEAPONS_DESCRIPTION_FONTSIZE = 16
WEAPONS_DESCRIPTION_PAD_TOP = 60
TURRET_VIEW_WIDTH = 450
TURRET_VIEW_HEIGHT = 308
TURRET_PAD_LEFT = 30
ATTRIBUTE_COLUMN_WIDTH = 400
ATTRIBUTE_TEXT_WIDTH = 400
ATTRIBUTE_TEXT_FONTSIZE = 16
SCALE_FACTOR_AT_SMALL_SCREEN_HEIGHT = 0.71
INTERNAL_MARGIN_H = 40
INTERNAL_MARGIN_V = 40
ATTRIBUTE_ICON_SIZE = 30
ATTRIBUTE_ICON_SEPARATION = 8
ATTRIBUTE_ROWS_SEPARATION = 20
ATTRIBUTE_TEXTS_SEPARATION = 4
ATTRIBUTE_ICON_FILL_COLOR = (0.0, 0.0, 0.0, 0.25)
ATTRIBUTE_ICON_FILL_LIGHT_COLOR = (1.0, 1.0, 1.0, 0.25)

class Attribute(object):

    def __init__(self, order, iconPath, title, description, textWidth, fontsize):
        self.order = order
        self.iconPath = iconPath
        self.title = title
        self.description = description
        self.fontsize = fontsize
        self.textHeight = self._CalculateTextHeight(textWidth)

    def _CalculateTextHeight(self, textWidth):
        titleTextHeight = GetTextHeight(strng=self.title, width=textWidth, fontsize=self.fontsize, uppercase=1)
        descriptionTextHeight = GetTextHeight(strng=self.description, width=textWidth, fontsize=self.fontsize)
        textHeight = titleTextHeight + ATTRIBUTE_TEXTS_SEPARATION + descriptionTextHeight
        return max(textHeight, ATTRIBUTE_ICON_SIZE)


class AttributeView(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        iconPath = attributes.Get('iconPath')
        title = attributes.Get('title')
        description = attributes.Get('description')
        fontsize = attributes.Get('fontsize')
        self.AddIcon(iconPath)
        self.AddText(title, description, fontsize)

    def AddIcon(self, iconPath):
        iconContainer = Container(name='attributeIconContainer', parent=self, align=uiconst.TOLEFT, width=ATTRIBUTE_ICON_SIZE, height=ATTRIBUTE_ICON_SIZE, padRight=ATTRIBUTE_ICON_SEPARATION)
        iconWrapperContainer = Container(name='iconWrapperContainer', parent=iconContainer, align=uiconst.TOTOP, width=ATTRIBUTE_ICON_SIZE, height=ATTRIBUTE_ICON_SIZE)
        self.iconFill = Fill(bgParent=iconWrapperContainer, color=ATTRIBUTE_ICON_FILL_COLOR)
        self.icon = Sprite(name='attributeIcon', parent=iconWrapperContainer, align=uiconst.TOTOP, width=ATTRIBUTE_ICON_SIZE, height=ATTRIBUTE_ICON_SIZE, texturePath=iconPath, spriteEffect=trinity.TR2_SFX_COLOROVERLAY)

    def AddText(self, title, description, fontsize):
        textContainer = Container(name='textContainer', parent=self, align=uiconst.TOLEFT, width=self.width - ATTRIBUTE_ICON_SIZE, height=self.height)
        Label(name='attributeTitleLabel', parent=textContainer, align=uiconst.TOTOP, text=title, padBottom=ATTRIBUTE_TEXTS_SEPARATION, fontsize=fontsize)
        Label(name='attributeDescriptionLabel', parent=textContainer, align=uiconst.TOTOP, text=description, fontsize=fontsize)


class WeaponsView(TechnologyView):
    racialAnimationSounds = {raceAmarr: 'sfx_es_weaponry_amarr_play',
     raceCaldari: 'sfx_es_weaponry_caldari_play',
     raceGallente: 'sfx_es_weaponry_gallente_play',
     raceMinmatar: 'sfx_es_weaponry_minmatar_play'}

    def ApplyAttributes(self, attributes):
        self.attributeViews = []
        TechnologyView.ApplyAttributes(self, attributes)
        centralContainer = Container(name='centralContainer', parent=self, align=uiconst.ANCH_TOPLEFT, width=self.width, height=self.height)
        self._PrepareAttributes()
        weaponsDescriptionText = self.technology.GetMainText(self.raceID)
        turretWidth, turretHeight = self._GetTurretViewSize()
        weaponsWidth, weaponsHeight = self._GetWeaponsDescriptionSize(weaponsDescriptionText)
        weaponsHeight += WEAPONS_DESCRIPTION_PAD_TOP * self._GetScaleFactor()
        attributesWidth, attributesHeight = self._GetAttributesSize()
        topViewHeight = max(turretHeight, weaponsHeight)
        lineViewHeight = 2 * INTERNAL_MARGIN_V + LINE_DECORATION_GRADIENT_HEIGHT
        centralViewWidth = (2 * ATTRIBUTE_COLUMN_WIDTH + INTERNAL_MARGIN_H) * self._GetScaleFactor()
        centralViewHeight = topViewHeight + lineViewHeight + attributesHeight
        centralView = Container(name='centralView', parent=centralContainer, align=uiconst.CENTER, width=centralViewWidth, height=centralViewHeight, top=ELEMENTS_PADDING_TOP * self._GetScaleFactor())
        self.BuildTopView(parent=centralView, width=centralViewWidth, height=topViewHeight, turretWidth=turretWidth, turretHeight=turretHeight, weaponsText=weaponsDescriptionText, weaponsWidth=weaponsWidth)
        self.BuildLineView(parent=centralView, width=centralViewWidth, height=lineViewHeight)
        self.BuildBottomView(parent=centralView, width=centralViewWidth, height=attributesHeight)
        self.PlayTurretVideoAndSound()

    def _PrepareAttributes(self):
        attributeTextWidth = self._GetAttributeTextWidth()
        attributeFontsize = self._GetAttributeFontsize()
        numberOfAttributes = self.technology.GetNumberOfExamples()
        self.attributesLeft = []
        self.attributesRight = []
        maxOrderLeft = numberOfAttributes / 2
        for order, attribute in self.technology.GetTechExamples():
            attribute = Attribute(order=order, iconPath=attribute.GetIcon(self.raceID), title=attribute.GetTitle(self.raceID), description=attribute.GetSubtitle(self.raceID), textWidth=attributeTextWidth, fontsize=attributeFontsize)
            if order <= maxOrderLeft:
                self.attributesLeft.append(attribute)
            else:
                self.attributesRight.append(attribute)

    def BuildTopView(self, parent, width, height, turretWidth, turretHeight, weaponsText, weaponsWidth):
        self.topView = Container(name='topView', parent=parent, align=uiconst.TOTOP, width=width, height=height, opacity=1.0)
        self.AddTurretView(turretWidth, turretHeight)
        self.AddWeaponsDescription(weaponsText, weaponsWidth, height)

    def AddWeaponsDescription(self, text, width, height):
        topLeftView = Container(name='topLeftView', parent=self.topView, align=uiconst.TOLEFT, width=self.topView.width / 2, height=self.topView.height)
        weaponsDescriptionContainer = Container(name='weaponsDescriptionContainer', parent=topLeftView, width=width, height=height, align=uiconst.TORIGHT)
        Label(name='weaponsDescriptionLabel', parent=weaponsDescriptionContainer, width=width, height=height, text=text, fontsize=self._GetWeaponsDescriptionFontsize(), top=WEAPONS_DESCRIPTION_PAD_TOP * self._GetScaleFactor())

    def AddTurretView(self, turretWidth, turretHeight):
        topRightView = Container(name='topRightView', parent=self.topView, align=uiconst.TORIGHT, width=self.topView.width / 2, height=self.topView.height)
        turretView = self.technology.GetMainView(self.raceID)
        if not turretView:
            return
        turretViewContainer = Container(name='turretViewContainer', parent=topRightView, align=uiconst.TOPLEFT, width=turretWidth, height=turretHeight, padLeft=TURRET_PAD_LEFT)
        self.turretVideo = StreamingVideoSprite(parent=turretViewContainer, name='turretView', videoPath=turretView, videoLoop=False, align=uiconst.TOALL, state=uiconst.UI_DISABLED, spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True, opacity=0.0)
        self.turretVideo.Pause()

    def BuildLineView(self, parent, width, height):
        lineView = Container(name='lineView', parent=parent, align=uiconst.TOTOP, width=width, height=height)
        self.line = LineDecoration(name='lineDecoration', parent=lineView, align=uiconst.TOTOP, width=width, height=LINE_DECORATION_HEIGHT, lineWidth=width, opacity=1.0, padTop=INTERNAL_MARGIN_V)

    def BuildBottomView(self, parent, width, height):
        self.bottomView = Container(name='bottomView', parent=parent, align=uiconst.TOTOP, width=width, height=height)
        self.AddAttributes(width, height)

    def AddAttributes(self, width, height):
        attributesContainer = Container(name='attributesContainer', parent=self.bottomView, align=uiconst.CENTER, width=width, height=height)
        attributesContainerWidth = width / 2 - INTERNAL_MARGIN_H
        attributesContainerLeft = Container(name='attributesContainerLeft', parent=attributesContainer, align=uiconst.TOLEFT, width=attributesContainerWidth, height=height, padRight=INTERNAL_MARGIN_H)
        attributesContainerRight = Container(name='attributesContainerRight', parent=attributesContainer, align=uiconst.TOLEFT, width=attributesContainerWidth, height=height, padLeft=INTERNAL_MARGIN_H)
        self.AddAttributesColumn(self.attributesLeft, attributesContainerLeft)
        self.AddAttributesColumn(self.attributesRight, attributesContainerRight)

    def AddAttributesColumn(self, attributes, attributesColumn):
        isFirstAttribute = True
        for attribute in attributes:
            attributeView = AttributeView(name='attributeView%s' % attribute.order, parent=attributesColumn, align=uiconst.TOTOP, width=ATTRIBUTE_COLUMN_WIDTH * self._GetScaleFactor(), height=attribute.textHeight, iconPath=attribute.iconPath, title=attribute.title, description=attribute.description, fontsize=attribute.fontsize, padTop=0 if isFirstAttribute else ATTRIBUTE_ROWS_SEPARATION, opacity=1.0)
            isFirstAttribute = False
            self.attributeViews.append(attributeView)

    def _GetLineDecorationWidth(self):
        scaleFactor = self._GetScaleFactor()
        width = LINE_DECORATION_WIDTH * scaleFactor
        return width

    def _GetAttributeTextWidth(self):
        scaleFactor = self._GetScaleFactor()
        width = ATTRIBUTE_TEXT_WIDTH * scaleFactor
        return width

    def _GetAttributeFontsize(self):
        return ATTRIBUTE_TEXT_FONTSIZE * self._GetScaleFactor()

    def _GetAttributesSize(self):
        textWidth = self._GetAttributeTextWidth()
        columnWidth = ATTRIBUTE_ICON_SIZE + ATTRIBUTE_ICON_SEPARATION + textWidth + INTERNAL_MARGIN_H
        columnHeightLeft = self._GetAttributesColumnHeight(self.attributesLeft)
        columnHeightRight = self._GetAttributesColumnHeight(self.attributesRight)
        width = 2 * columnWidth
        height = max(columnHeightLeft, columnHeightRight)
        return (width, height)

    def _GetAttributesColumnHeight(self, attributesColumn):
        height = 0
        for attribute in attributesColumn:
            if height > 0:
                height += ATTRIBUTE_ROWS_SEPARATION
            height += attribute.textHeight

        return height

    def _GetTurretViewSize(self):
        scaleFactor = self._GetScaleFactor()
        width = TURRET_VIEW_WIDTH * scaleFactor
        height = TURRET_VIEW_HEIGHT * scaleFactor
        return (width, height)

    def _GetWeaponsDescriptionFontsize(self):
        return WEAPONS_DESCRIPTION_FONTSIZE * self._GetScaleFactor()

    def _GetWeaponsDescriptionSize(self, text):
        width = WEAPONS_DESCRIPTION_WIDTH * self._GetScaleFactor()
        height = GetTextHeight(strng=text, width=width, fontsize=self._GetWeaponsDescriptionFontsize())
        return (width, height)

    def _GetScaleFactor(self):
        desktopHeight = uicore.desktop.height
        if desktopHeight > BIG_SCREEN_HEIGHT:
            desktopHeight = BIG_SCREEN_HEIGHT
        return SCALE_FACTOR_AT_SMALL_SCREEN_HEIGHT * desktopHeight / SMALL_SCREEN_HEIGHT

    def PlayTurretVideoAndSound(self):
        sm.GetService('audio').SendUIEvent(self.racialAnimationSounds[self.raceID])
        self.turretVideo.Play()
        self.turretVideo.opacity = 1.0
        self.turretVideo.UnmuteAudio()

    def Close(self):
        self.turretVideo.MuteAudio()
        self.turretVideo.opacity = 0.0
        TechnologyView.Close(self)
