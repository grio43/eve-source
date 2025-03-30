#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\characterSelectorView.py
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.login.charSelection.characterSelection import CharacterSelection

class CharacterSelectorView(View):
    __guid__ = 'viewstate.CharacterSelectorView'
    __notifyevents__ = []
    __dependencies__ = ['menu', 'loginCampaignService']
    __layerClass__ = CharacterSelection
    __progressText__ = 'UI_CHARSEL_ENTERINGCHARSEL'

    def LoadView(self, **kwargs):
        View.LoadView(self, **kwargs)

    def UnloadView(self):
        View.UnloadView(self)
