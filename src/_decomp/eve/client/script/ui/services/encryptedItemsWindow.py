#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\encryptedItemsWindow.py
from carbonui.control.window import Window
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.uiconst import TOALL

class EncryptedItemsResultWindow(Window):
    __guid__ = 'form.EncryptedItemsResultWindow'
    default_width = 900
    default_height = 480

    def ApplyAttributes(self, attributes):
        super(EncryptedItemsResultWindow, self).ApplyAttributes(attributes)
        video_path = attributes.url
        StreamingVideoSprite(parent=self.sr.main, align=TOALL, videoPath=video_path, videoAutoPlay=True)
