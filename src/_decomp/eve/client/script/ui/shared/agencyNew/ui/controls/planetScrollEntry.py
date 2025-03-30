#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\planetScrollEntry.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew.ui.controls.agencyScrollContEntry import AgencyScrollContEntry
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.planet import planetConst
from eve.client.script.ui.view.viewStateConst import ViewState
from localization import GetByLabel
ICON_SIZE = 36

class PlanetScrollEntry(AgencyScrollContEntry):
    default_name = 'PlanetScrollEntry'
    default_height = 40

    def ApplyAttributes(self, attributes):
        self.isPlanetColonizedByMe = False
        super(PlanetScrollEntry, self).ApplyAttributes(attributes)

    def ConstructLayout(self):
        if self.contentPiece.isBlacklisted:
            ErrorFrame(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, opacity=0.3)
        self.ConstructIcon()
        self.ConstructPlanetViewLabelButton()
        self.ConstructLabel()

    def GetHint(self):
        if self.contentPiece.isBlacklisted:
            return GetByLabel('UI/Agency/PlanetaryProduction/planetCannotBeColonized')

    def ConstructIcon(self):
        iconContainer = Container(name='iconContainer', parent=self, align=uiconst.TOLEFT, width=ICON_SIZE, padding=(2, 2, 4, 2))
        self.icon = Sprite(name='planetIcon', bgParent=iconContainer)
        if self.contentPiece.IsColonizedByMe():
            self.isColonizedFrame = Frame(parent=iconContainer, color=eveColor.CRYO_BLUE, display=False)
            Sprite(name='colonyIndicatorSprite', parent=iconContainer, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/agency/iconPlanetaryStructure.png', hint=GetByLabel('UI/Agency/PlanetaryProduction/planetColonizedByMe'), pos=(3, 3, 16, 16))

    def ConstructLabel(self):
        labelContainer = Container(name='labelContainer', parent=self, align=uiconst.TOALL)
        self.label = EveLabelMedium(name='planetNameLabel', parent=labelContainer, align=uiconst.CENTERLEFT, left=4)

    def ConstructPlanetViewLabelButton(self):
        planetViewLabelButtonContainer = ContainerAutoSize(name='planetViewLabelButtonContainer', parent=self, align=uiconst.TORIGHT, left=5)
        planetViewButton = ButtonIcon(name='planetViewButtonIcon', parent=planetViewLabelButtonContainer, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED if self.contentPiece.isBlacklisted else uiconst.UI_NORMAL, width=28, height=28, iconSize=28, texturePath='res:/UI/Texture/WindowIcons/planets.png', hint=GetByLabel('UI/PI/Common/ViewInPlanetMode'), func=lambda : sm.GetService('viewState').ActivateView(ViewState.Planet, planetID=self.contentPiece.itemID))
        Frame(bgParent=planetViewButton, opacity=0.4)
        EveLabelMedium(name='planetTypeName', parent=planetViewLabelButtonContainer, align=uiconst.CENTERRIGHT, left=35, text=GetByLabel(planetConst.PLANETTYPE_NAMES[self.contentPiece.typeID]), opacity=0.8)

    def UpdateIcon(self):
        sm.GetService('photo').GetIconByType(self.icon, self.contentPiece.typeID)

    def OnClick(self, *args):
        if self.contentPiece.isBlacklisted:
            return
        super(PlanetScrollEntry, self).OnClick(*args)
