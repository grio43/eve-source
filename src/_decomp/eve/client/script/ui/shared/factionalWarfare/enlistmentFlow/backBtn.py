#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\backBtn.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite

class BackBtnBase(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.enlistmentController = attributes.enlistmentController
        super(BackBtnBase, self).ApplyAttributes(attributes)
        self.PrepareUI()

    def PrepareUI(self):
        self.iconCont = Container(name='iconCont', parent=self, align=uiconst.TOALL)
        self.backIcon = Sprite(name='backIcon', parent=self.iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 40, 40), texturePath='res:/UI/Texture/Classes/Enlistment/backArrow.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0)
        self.bgSprite = Sprite(name='bgSprite', parent=self.iconCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/Classes/Enlistment/circle/darkCircle.png', state=uiconst.UI_DISABLED, opacity=1.0, pos=(0,
         0,
         2 * self.width,
         2 * self.width))
        self.mouseOverFrame = Sprite(name='mouseOverFrame', parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/Classes/Enlistment/hoverCircle.png', state=uiconst.UI_DISABLED, opacity=1.0, padding=-4)

    def OnMouseEnter(self, *args):
        self.mouseOverFrame.opacity = 1.5

    def OnMouseExit(self, *args):
        self.mouseOverFrame.opacity = 1.0

    def OnClick(self, *args):
        pass

    def ChangeFrameDisplay(self, show = True):
        if show:
            self.mouseOverFrame.opacity = 1.5
        else:
            self.mouseOverFrame.opacity = 1.0


class BackBtnFaction(BackBtnBase):

    def OnMouseEnter(self, *args):
        self.enlistmentController.on_back_mouse_enter()
        super(BackBtnFaction, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        self.enlistmentController.on_back_mouse_exit()
        super(BackBtnFaction, self).OnMouseExit(*args)

    def OnClick(self, *args):
        func = self.enlistmentController.on_node_clicked(None)


class BackBtnFront(BackBtnBase):

    def OnClick(self, *args):
        self.enlistmentController.ResetSelectedHoveredFactionID()
        self.enlistmentController.SetFrontPageSelected()
        self.enlistmentController.trigger_page_update(animate=True)
