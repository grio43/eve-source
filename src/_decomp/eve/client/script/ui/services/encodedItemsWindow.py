#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\encodedItemsWindow.py
import uthread2
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import StreamingVideoSprite, Sprite
from carbonui.uiconst import TOALL, CENTER
import blue
from dogma.const import attributeAspectRatioWidth, attributeAspectRatioHeight
from localization import GetByLabel
VIDEO_TYPE = '.webm'
IMAGE_TYPE = '.png'

class EncodedItemsWindow(Window):
    __guid__ = 'form.EncryptedItemsResultWindow'
    default_windowID = 'encodedItemsWindow'
    default_width = 900
    default_height = 480

    def ApplyAttributes(self, attributes):
        self.apectRatio = 1.0
        super(EncodedItemsWindow, self).ApplyAttributes(attributes)
        self.downloadingFile = False
        self.typeID = attributes.typeID
        resourcePath = attributes.url
        self.resourceUrl = resourcePath
        if self.isVideo:
            self.spriteCont = Container(name='spriteCont', parent=self.content, align=TOALL)
            self.sprite = StreamingVideoSprite(parent=self.spriteCont, align=TOALL, videoPath=resourcePath, videoAutoPlay=True)
        else:
            clientDogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
            aspectRatioWidth = clientDogmaStaticSvc.GetTypeAttribute(self.typeID, attributeAspectRatioWidth, 1)
            aspectRatioHeight = clientDogmaStaticSvc.GetTypeAttribute(self.typeID, attributeAspectRatioHeight, 1)
            self.apectRatio = float(aspectRatioWidth) / aspectRatioHeight
            self.spriteCont = Container(name='spriteCont', parent=self.content, align=CENTER)
            texture, _, _ = sm.GetService('photo').GetTextureFromURL(resourcePath)
            self.sprite = Sprite(parent=self.spriteCont, align=TOALL)
            self.sprite.texture = texture
            w, h = self._GetNewWidthAndHeight(self.width, self.height)
            self.width = w
            self.height = h
        self.sprite.GetMenu = self.GetResourceMenu
        self.UpdateSpriteContSize()

    def GetResourceMenu(self):
        m = MenuData()
        if self.isVideo:
            labelPath = GetByLabel('UI/VideoPlayer/DownloadVideo')
        elif self.isImage:
            labelPath = GetByLabel('UI/VideoPlayer/DownloadImage')
        else:
            return m
        m.AddEntry(labelPath, func=lambda : self.DownloadFile())
        return m

    def DownloadFile(self):
        if self.downloadingFile:
            raise UserError('CustomNotify', {'notify': 'UI/VideoPlayer/AlreadyDownloadingFile'})
        self.downloadingFile = True
        uthread2.StartTasklet(self._DownloadFile)

    def _DownloadFile(self):
        failureMsgPath = 'UI/VideoPlayer/FailedToDownloadVideo'
        try:
            if self.isVideo:
                fileName = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/capture/Screenshots/VideoFragment_%s%s' % (self.typeID, VIDEO_TYPE)
                successMsgPath = 'UI/VideoPlayer/VideoDownloaded'
            elif self.isImage:
                fileName = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/capture/Screenshots/ImageFragment_%s%s' % (self.typeID, IMAGE_TYPE)
                successMsgPath = 'UI/VideoPlayer/ImageDownloaded'
            else:
                raise RuntimeError('Video is not of the right format')
            stream = blue.BlueNetworkStream(unicode(self.resourceUrl).encode('utf-8'))
            data = stream.read()
            with open(fileName, 'wb') as outputPath:
                outputPath.write(data)
                eve.Message('CustomNotify', {'notify': GetByLabel(successMsgPath)})
        except StandardError:
            eve.Message('CustomNotify', {'notify': GetByLabel(failureMsgPath)})
            raise
        finally:
            self.downloadingFile = False

    def OnResize_(self, *args):
        self.UpdateSpriteContSize()

    def UpdateSpriteContSize(self):
        if self.isImage:
            lPad, tPad, rPad, bPad = self.GetContentToWindowEdgePadding()
            availWidth = self.width - lPad - rPad
            availHeight = self.height - tPad - bPad
            newWidth, newHeight = self._GetNewWidthAndHeight(availWidth, availHeight)
            self.spriteCont.width = newWidth
            self.spriteCont.height = newHeight

    def _GetNewWidthAndHeight(self, availWidth, availHeight):
        if float(availWidth) / availHeight > self.apectRatio:
            newHeight = availHeight
            newWidth = self.apectRatio * newHeight
        else:
            newWidth = availWidth
            newHeight = newWidth / self.apectRatio
        return (newWidth, newHeight)

    @property
    def isVideo(self):
        return self.resourceUrl.endswith(VIDEO_TYPE)

    @property
    def isImage(self):
        return self.resourceUrl.endswith(IMAGE_TYPE)
