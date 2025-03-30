#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\loginView.py
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.login.loginII import Login

class LoginView(View):
    __guid__ = 'viewstate.LoginView'
    __notifyevents__ = []
    __dependencies__ = []
    __layerClass__ = Login
    __progressText__ = None

    def __init__(self):
        View.__init__(self)

    def UnloadView(self):
        View.UnloadView(self)
