#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\state_icon.py
import threadutils
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
import localization
from expertSystems.client import texture
from expertSystems.client.service import ExpertSystemService

class StateIcon(Sprite):
    __notifyevents__ = ['OnExpertSystemsUpdated_Local']
    default_state = uiconst.UI_NORMAL
    default_texturePath = texture.badge_64
    default_width = 64
    default_height = 64

    def __init__(self, **kwargs):
        self.base_opacity = 1.0
        super(StateIcon, self).__init__(**kwargs)
        self.display = False
        self.update()
        ServiceManager.Instance().RegisterNotify(self)

    @threadutils.threaded
    def update(self):
        my_expert_systems = ExpertSystemService.instance().GetMyExpertSystems()
        self.display = bool(my_expert_systems)

    def OnMouseEnter(self, *args):
        self.FadeIn()

    def OnMouseExit(self, *args):
        self.FadeOut()

    def FadeIn(self):
        animations.FadeTo(self, self.opacity, 1.5 * self.base_opacity, duration=0.3)

    def FadeOut(self):
        animations.FadeTo(self, self.opacity, self.base_opacity, duration=0.3)

    def OnClick(self, *args):
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        CharacterSheetWindow.OpenExpertSystems()

    def LoadTooltipPanel(self, panel, *args):
        panel.LoadGeneric1ColumnTemplate()
        panel.AddSpriteLabel(texturePath=texture.logo_simple_32, label=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/ExpertSystems/ExpertSystems'), bold=True, iconOffset=0)
        panel.AddLabelMedium(text=localization.GetByLabel('UI/ExpertSystem/ExpertSystemActive'), wrapWidth=300)

    def OnExpertSystemsUpdated_Local(self):
        self.update()
