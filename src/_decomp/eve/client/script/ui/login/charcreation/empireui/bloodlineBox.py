#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireui\bloodlineBox.py
from carbon.common.lib.const import genderFemale
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
import charactercreator.client.scalingUtils as ccScalingUtils
from eve.client.script.ui.login.charcreation.empireui.bloodlineConst import BloodlineResType, GetImage, GetVideo
from eve.client.script.ui.login.charcreation.empireui.bloodlineConst import PLATFORM_VERTICAL_OFFSET, PLATFORM_PATH
from eve.client.script.ui.login.charcreation.empireui.bloodlineConst import GetPlatformHorizontalOffset
from trinity import TR2_SBM_BLEND, TR2_SFX_COPY
from uthread2 import StartTasklet
RESOURCE_WIDTH = 105
VIDEO_HEIGHT = 325
IMAGE_HEIGHT = 321
PLATFORM_WIDTH = 150
PLATFORM_HEIGHT = 30
PLATFORM_OPACITY = 1.0

class BloodlineBox(Container):

    def ApplyAttributes(self, attributes):
        self.bloodlineID = attributes.Get('bloodlineID', None)
        self.gender = attributes.Get('gender', None)
        self.isSelected = attributes.Get('isSelected', None)
        self.isHovered = False
        self.onSelection = attributes.Get('onSelection', None)
        self.onHover = attributes.Get('onHover', None)
        self.onDehover = attributes.Get('onDehover', None)
        self.useVideos = attributes.Get('useVideos', True)
        showSelectedOnLoad = attributes.Get('showSelectedOnLoad', True)
        self.resAlign = attributes.Get('resAlign', uiconst.TOLEFT_NOPUSH)
        Container.ApplyAttributes(self, attributes)
        StartTasklet(self.LoadContent, showSelectedOnLoad)

    def LoadContent(self, showSelectedOnLoad):
        self.resources = {}
        for type in [BloodlineResType.SELECTED, BloodlineResType.NOT_SELECTED]:
            self.resources[type] = self.ConstructResource(type)

        self.ConstructPlatform()
        if showSelectedOnLoad:
            self.ShowSelected()
        else:
            self.ShowNotSelected()

    def ConstructResource(self, type):
        if self.useVideos:
            return self.ConstructVideo(type)
        return self.ConstructImage(type)

    def ConstructVideo(self, type):
        scale = ccScalingUtils.GetScaleFactor()
        path = GetVideo(type, self.bloodlineID, self.gender)
        video = StreamingVideoSprite(parent=self, name='bloodlineVideo', videoPath=path, videoLoop=True, align=self.resAlign, width=RESOURCE_WIDTH * scale, height=VIDEO_HEIGHT * scale, state=uiconst.UI_DISABLED, spriteEffect=TR2_SFX_COPY, blendMode=TR2_SBM_BLEND, disableAudio=True, muteAudio=True, videoAutoPlay=True, opacity=0.0)
        return video

    def ConstructImage(self, type):
        scale = ccScalingUtils.GetScaleFactor()
        path = GetImage(type, self.bloodlineID, self.gender)
        image = Sprite(parent=self, name='bloodlineSprite', texturePath=path, align=self.resAlign, width=RESOURCE_WIDTH * scale, height=IMAGE_HEIGHT * scale, state=uiconst.UI_DISABLED, opacity=0.0)
        return image

    def ConstructPlatform(self):
        scale = ccScalingUtils.GetScaleFactor()
        width = PLATFORM_WIDTH * scale
        height = PLATFORM_HEIGHT * scale
        containerVerticalOffset = -height / 2
        top = containerVerticalOffset + PLATFORM_VERTICAL_OFFSET * scale
        widthOffset = (width - RESOURCE_WIDTH) / 2
        containerHorizontalOffset = widthOffset if self.gender == genderFemale else -widthOffset
        left = containerHorizontalOffset + GetPlatformHorizontalOffset(self.bloodlineID, self.gender) * scale
        platformContainer = Container(parent=self, name='platformContainer', align=self.resAlign, width=width, height=height, state=uiconst.UI_DISABLED)
        Sprite(parent=platformContainer, name='platformSprite', texturePath=PLATFORM_PATH, align=uiconst.CENTERBOTTOM, width=width, height=height, state=uiconst.UI_DISABLED, opacity=PLATFORM_OPACITY, top=top, left=left)

    def SwitchType(self, typeToShow):
        for type, res in self.resources.iteritems():
            newOpacity = 1.0 if type == typeToShow else 0.0
            res.opacity = newOpacity

    def ShowSelected(self):
        self.SwitchType(BloodlineResType.SELECTED)

    def ShowNotSelected(self):
        self.SwitchType(BloodlineResType.NOT_SELECTED)

    def ShowHover(self):
        self.SwitchType(BloodlineResType.SELECTED)

    def ShowDehover(self):
        self.SwitchType(BloodlineResType.NOT_SELECTED)

    def OnMouseEnter(self, *args):
        self.isHovered = True
        if not self.isSelected:
            if self.onHover:
                self.onHover(self.bloodlineID, self.gender)

    def OnMouseExit(self, *args):
        self.isHovered = False
        if not self.isSelected:
            if self.onDehover:
                self.onDehover(self.bloodlineID, self.gender)

    def OnClick(self, *args):
        if not self.isSelected and self.onSelection:
            self.onSelection(self.bloodlineID, self.gender)

    def Select(self):
        if not self.isSelected:
            self.isSelected = True
            self.ShowSelected()

    def Deselect(self):
        if self.isSelected:
            self.isSelected = False
            self.ShowNotSelected()
