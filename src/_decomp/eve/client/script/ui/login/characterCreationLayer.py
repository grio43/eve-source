#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\characterCreationLayer.py
import telemetry
from carbonui.control.layer import LayerCore
from eve.client.script.ui.login.characterCreationContainer import CharacterCreationContainer
from eve.client.script.ui.login.feature_flag import is_new_character_creation_enabled

class CharacterCreationLayer(LayerCore):
    __update_on_reload__ = 1

    def ApplyAttributes(self, attributes):
        super(CharacterCreationLayer, self).ApplyAttributes(attributes)
        self.controller = None

    @telemetry.ZONE_METHOD
    def OnOpenView(self, **kwargs):
        sm.GetService('sceneManager').CreateCharacterBackdropUIRoot()
        if is_new_character_creation_enabled():
            from eve.client.script.ui.login.characterCreationContainer_new import CharacterCreationContainer_new
            self.controller = CharacterCreationContainer_new(name='ccContainer', parent=self)
        else:
            self.controller = CharacterCreationContainer(name='ccContainer', parent=self)
        self.controller.OnOpenView()

    @telemetry.ZONE_METHOD
    def OnCloseView(self):
        self.controller.OnCloseView()
