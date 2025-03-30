#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\loadingWheel.py
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel

class CharacterCreationLoadingWheel(LoadingWheel):
    default_texturePath = 'res:/UI/Texture/CharacterCreation/ccLoadingWheel.png'

    def ApplyAttributes(self, attributes):
        LoadingWheel.ApplyAttributes(self, attributes)
