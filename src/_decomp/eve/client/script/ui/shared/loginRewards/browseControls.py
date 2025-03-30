#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\browseControls.py
import math
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from carbonui.uianimations import animations
from eve.client.script.ui.eveColor import WHITE
from localization import GetByLabel

class BrowseControls(ContainerAutoSize):
    default_align = uiconst.TOLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.browseFunc = attributes.browseFunc
        self.resetFunc = attributes.resetFunc
        ButtonIcon(name='backBtn', parent=self, align=uiconst.TOLEFT, iconSize=11, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', func=self.browseFunc, args=-1, rotation=-math.pi / 2.0, iconAlign=uiconst.CENTER)
        ResetLabel(parent=self, align=uiconst.TOLEFT, func=self.resetFunc, text=GetByLabel('UI/LoginRewards/DefaultViewText'))
        ButtonIcon(name='fwdtBtn', parent=self, align=uiconst.TOLEFT, iconSize=11, texturePath='res:/UI/Texture/classes/Neocom/arrowDown.png', func=self.browseFunc, args=1, rotation=math.pi / 2.0, iconAlign=uiconst.CENTER)


class ResetLabel(Container):
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.75

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = attributes.text
        resetLabel = EveLabelMediumBold(parent=self, align=uiconst.CENTER, text=text, color=WHITE)
        self.width = resetLabel.width + 10
        self.func = attributes.func
        self.hint = GetByLabel('UI/LoginRewards/DefaultViewHintText')

    def OnClick(self, *args):
        self.func()

    def OnMouseEnter(self, *args):
        animations.FadeTo(self, self.opacity, 1.2, duration=0.1)

    def OnMouseExit(self, *args):
        animations.FadeTo(self, self.opacity, 0.75, duration=0.2)
