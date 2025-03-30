#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\frontPageCont.py
from carbonui import TextCustom, TextAlign
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import carbonui.const as uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.toggleButtonGroupCircular import ToggleButtonGroupCircular
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentConst import SELECTED_EMPIRE, SELECTED_PIRATES, BG_TEXTURE_PATH_BY_SIDE
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.insurgencySideSelector import InsurgencySideSelector
from localization import GetByLabel

class EnlistmentFrontPageCont(Container):
    default_name = 'EnlistmentFrontPageCont'

    def ApplyAttributes(self, attributes):
        super(EnlistmentFrontPageCont, self).ApplyAttributes(attributes)
        self.enlistmentController = attributes.enlistmentController
        text = GetByLabel('UI/FactionWarfare/Enlistment/ChooseYourSide')
        TextCustom(parent=self, fontsize=20, text=text, align=uiconst.CENTER)
        self.AddBanners()

    def AddBanners(self):
        grid = LayoutGrid(parent=self, align=uiconst.CENTER, columns=2)
        InsurgencySideSelector(parent=grid, insurgencySideID=SELECTED_EMPIRE, enlistmentController=self.enlistmentController, left=0)
        InsurgencySideSelector(parent=grid, insurgencySideID=SELECTED_PIRATES, enlistmentController=self.enlistmentController, left=300)
