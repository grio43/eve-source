#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\sharedtextureviewer.py
import carbonui.const as uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
import trinity
from carbonui.control.window import Window
from eve.client.script.ui.control.eveLabel import EveLabelSmall

class SharedTextureViewer(Window):

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        w, h = (450, 230)
        self.SetMinSize([w, h])
        self.SetHeight(h)
        self.SetCaption('Shared Texture Viewer')
        margin = 4
        innermain = Container(left=margin, top=margin, parent=self.sr.main)
        bottomframe = Container(align=uiconst.TOBOTTOM, parent=innermain, height=16, left=margin, top=margin)
        self.textureCont = Container(align=uiconst.TOALL, parent=innermain, pos=(margin,
         margin,
         margin,
         margin))
        Frame(parent=self.textureCont, color=(1.0, 1.0, 1.0, 0.2), idx=0)
        self.texture = Sprite(parent=self.textureCont, width=1, height=1, align=uiconst.CENTER, state=uiconst.UI_DISABLED, spriteEffect=trinity.TR2_SFX_NOALPHA)
        self.textureRes = trinity.TriTextureRes()
        EveLabelSmall(parent=bottomframe, align=uiconst.TOLEFT, text='Texture Handle (decimals)')
        SingleLineEditText(parent=bottomframe, align=uiconst.TOALL, OnChange=self._OnHandleChanged)

    def OpenTexture(self, handle):
        self.textureRes = trinity.OpenSharedTexture(handle)
        self.texture.texture.atlasTexture = trinity.Tr2AtlasTexture()
        self.texture.texture.atlasTexture.textureRes = self.textureRes
        self._UpdateSpriteSize()

    def OnResizeUpdate(self, *args):
        if self and not self.destroyed:
            self._UpdateSpriteSize()

    def _OnHandleChanged(self, handle):
        self.OpenTexture(long(handle))

    def _UpdateSpriteSize(self):
        x, y, contWidth, contHeight = self.textureCont.GetAbsolute()
        dimWidth = max(self.textureRes.width, 1)
        dimHeight = max(self.textureRes.height, 1)
        contFactor = float(contWidth) / float(contHeight)
        vidResFactor = float(dimWidth) / float(dimHeight)
        if vidResFactor > contFactor:
            widthFactor = float(contWidth) / float(dimWidth)
            dimWidth *= widthFactor
            dimHeight *= widthFactor
        elif vidResFactor < contFactor:
            heightFactor = float(contHeight) / float(dimHeight)
            dimWidth *= heightFactor
            dimHeight *= heightFactor
        else:
            dimWidth = contWidth
            dimHeight = contHeight
        self.texture.width = int(dimWidth)
        self.texture.height = int(dimHeight)
