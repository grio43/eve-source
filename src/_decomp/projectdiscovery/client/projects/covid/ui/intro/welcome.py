#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\intro\welcome.py
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from localization import GetByLabel
from projectdiscovery.client.projects.covid.sounds import Sounds
WELCOME_LABEL_PATH = 'UI/ProjectDiscovery/Covid/Intro/Welcome'
BEGIN_BUTTON_LABEL_PATH = 'UI/ProjectDiscovery/Covid/Intro/ButtonBegin'

class Welcome(Container):

    def ApplyAttributes(self, attributes):
        super(Welcome, self).ApplyAttributes(attributes)
        go_to_doctor_presentation = attributes.get('go_to_doctor_presentation')
        Label(name='welcome_label', parent=self, align=uiconst.CENTERTOP, top=130, fontsize=24, text=GetByLabel(WELCOME_LABEL_PATH))
        Sprite(name='project_discovery_image', parent=self, align=uiconst.CENTERTOP, width=474, height=237, top=229, texturePath='res:/UI/Texture/classes/ProjectDiscovery/covid/intro/project_discovery.png')
        Button(parent=self, align=uiconst.CENTERTOP, top=536, label=GetByLabel(BEGIN_BUTTON_LABEL_PATH), func=lambda *args: go_to_doctor_presentation())
        sm.GetService('audio').SendUIEvent(Sounds.WELCOME_START)

    def fade_in(self):
        animations.FadeIn(self)
