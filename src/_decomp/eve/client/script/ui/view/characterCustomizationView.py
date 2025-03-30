#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\characterCustomizationView.py
from eve.client.script.ui.login.characterCreationLayer import CharacterCreationLayer
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.parklife.sceneManagerConsts import SCENE_TYPE_CHARACTER_CREATION
import localization
from carbonui.uicore import uicore

class CharacterCustomizationView(View):
    __guid__ = 'viewstate.CharacterCustomizationView'
    __notifyevents__ = ['OnShowUI']
    __dependencies__ = []
    __layerClass__ = CharacterCreationLayer
    __suppressedOverlays__ = {'sidePanels'}
    __dependencies__ = View.__dependencies__[:]
    __dependencies__.extend(['gameui', 'loginCampaignService'])

    def __init__(self):
        View.__init__(self)

    def LoadView(self, charID = None, gender = None, raceID = None, dollState = None, bloodlineID = None, **kwargs):
        View.LoadView(self)
        self.LogInfo('Opening character creator with arguments', kwargs)
        factory = sm.GetService('character').factory
        factory.compressTextures = False
        factory.allowTextureCache = False
        factory.clothSimulationActive = False
        sm.GetService('sceneManager').SetSceneType(SCENE_TYPE_CHARACTER_CREATION)
        self.layer.controller.SetCharDetails(charID, gender, raceID, bloodlineID, dollState=dollState)
        if gender is not None:
            uicore.layer.main.display = False

    def UnloadView(self):
        View.UnloadView(self)
        uicore.layer.main.display = True

    def GetProgressText(self, **kwargs):
        if kwargs.get('charID', None) is not None:
            text = localization.GetByLabel('UI/CharacterCustomization/EnteringCharacterCustomization')
        else:
            text = localization.GetByLabel('UI/CharacterCreation/EnteringCharacterCreation')
        return text

    def OnShowUI(self):
        uicore.layer.main.display = False
