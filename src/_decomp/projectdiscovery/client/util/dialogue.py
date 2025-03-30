#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\util\dialogue.py
import carbonui.const as uiconst
import localization
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold
from projectdiscovery.client.const import Events as projectDiscoveryEvents
from projectdiscovery.client import const
from projectdiscovery.client.ui.agents import get_agent
TEXT_HEADER_HEIGHT = 20
HEADER_CONTAINER_HEIGHT = 25
BOTTOM_CONTAINER_HEIGHT = 40
MIN_MESSAGE_TEXT_HEIGHT = 220

class Dialogue(Container):
    default_bgColor = (0, 0, 0, 1)

    def ApplyAttributes(self, attributes):
        super(Dialogue, self).ApplyAttributes(attributes)
        self.label = attributes.get('label')
        self.message_header_text = attributes.get('messageHeaderText')
        self.message_text = attributes.get('messageText')
        self.button_label = attributes.get('buttonLabel')
        self.toHide = attributes.get('toHide')
        self.isTutorial = attributes.get('isTutorial')
        self._close_event = attributes.get('onCloseEvent', projectDiscoveryEvents.EnableUI)
        self.agent = get_agent()
        if self.isTutorial:
            sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoadStop)
        if self.toHide:
            self.toHide.opacity = 0.5
        self.construct_layout()

    def construct_layout(self):
        Frame(name='main_frame', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/SampleBack.png', cornerSize=20, padLeft=-8, padTop=-8, padRight=-8, padBottom=-8, color=(1.0, 1.0, 1.0, 0.5))
        header_container = Container(name='headerContainer', parent=self, height=HEADER_CONTAINER_HEIGHT, align=uiconst.TOTOP)
        eveLabel.Label(name='headerLabel', parent=header_container, align=uiconst.CENTERLEFT, left=10, text=self.label)
        main_container = Container(name='mainContainer', parent=self, align=uiconst.TOTOP)
        agent_container = Container(name='agentContainer', parent=main_container, align=uiconst.TOPLEFT, height=170, width=150, left=10, top=5)
        Sprite(name='agentImage', parent=agent_container, align=uiconst.TOTOP, height=150, width=150, texturePath=self.agent.image)
        eveLabel.Label(name='agentName', parent=agent_container, align=uiconst.TOTOP, text=localization.GetByLabel(self.agent.name), top=5)
        text_container = Container(name='textContainer', parent=main_container, align=uiconst.TORIGHT, width=270, left=10)
        text_header_container = Container(name='textHeaderContainer', parent=text_container, align=uiconst.TOTOP, height=TEXT_HEADER_HEIGHT)
        EveLabelLargeBold(parent=text_header_container, align=uiconst.CENTERLEFT, text=self.message_header_text)
        text_message_container = Container(name='text_message_container', parent=text_container, align=uiconst.TOTOP)
        main_message = eveLabel.Label(parent=text_message_container, align=uiconst.TOTOP, text=self.message_text, top=5)
        bottom_container = Container(name='bottomContainer', parent=self, height=BOTTOM_CONTAINER_HEIGHT, align=uiconst.TOBOTTOM)
        self.close_button = Button(name='close_button', parent=bottom_container, fontsize=14, fixedwidth=125, fixedheight=22, label=self.button_label, align=uiconst.BOTTOMRIGHT, top=10, left=10, func=lambda x: self.close())
        if self.isTutorial:
            self.skip_button = Button(name='skipButton', parent=bottom_container, fontsize=14, fixedwidth=125, fixedheight=22, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SkipTutorial'), align=uiconst.CENTERBOTTOM, top=10, left=10, func=lambda x: self.skip_tutorial())
        message_height = max(MIN_MESSAGE_TEXT_HEIGHT, main_message.height)
        text_message_container.height = message_height
        self.height = message_height + TEXT_HEADER_HEIGHT + HEADER_CONTAINER_HEIGHT + BOTTOM_CONTAINER_HEIGHT
        main_container.height = message_height + TEXT_HEADER_HEIGHT

    def close(self):
        if self.isTutorial:
            sm.ScatterEvent(projectDiscoveryEvents.StartTutorial)
        if self.toHide:
            self.toHide.opacity = 1
        sm.ScatterEvent(self._close_event)
        self.Close()

    def skip_tutorial(self):
        if self.toHide:
            self.toHide.opacity = 1
        sm.ScatterEvent(projectDiscoveryEvents.ProjectDiscoveryStarted, False)
        self.Close()


class ResumeTutorialDialogue(Container):
    default_bgColor = (0, 0, 0, 1)

    def ApplyAttributes(self, attributes):
        super(ResumeTutorialDialogue, self).ApplyAttributes(attributes)
        self.label = attributes.get('label')
        self.toHide = attributes.get('toHide')
        self.isTutorial = attributes.get('isTutorial')
        self._close_event = attributes.get('onCloseEvent', projectDiscoveryEvents.EnableUI)
        self.agent = get_agent()
        if self.toHide:
            self.toHide.opacity = 0.5
        self.construct_layout()

    def construct_layout(self):
        Frame(name='main_frame', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/SampleBack.png', cornerSize=20, padLeft=-8, padTop=-8, padRight=-8, padBottom=-8, color=(1.0, 1.0, 1.0, 0.5))
        header_container = Container(name='headerContainer', parent=self, height=HEADER_CONTAINER_HEIGHT, align=uiconst.TOTOP)
        eveLabel.Label(name='headerLabel', parent=header_container, align=uiconst.CENTERLEFT, left=10, text=self.label)
        main_container = Container(name='mainContainer', parent=self, align=uiconst.TOTOP)
        agent_container = Container(name='agentContainer', parent=main_container, align=uiconst.TOPLEFT, height=170, width=150, left=10, top=5)
        Sprite(name='agentImage', parent=agent_container, align=uiconst.TOTOP, height=150, width=150, texturePath=self.agent.image)
        eveLabel.Label(name='agentName', parent=agent_container, align=uiconst.TOTOP, text=localization.GetByLabel(self.agent.name), top=5)
        text_container = Container(name='textContainer', parent=main_container, align=uiconst.TORIGHT, width=270, left=10)
        text_header_container = Container(name='textHeaderContainer', parent=text_container, align=uiconst.TOTOP, height=TEXT_HEADER_HEIGHT)
        EveLabelLargeBold(parent=text_header_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/TutorialReturnHeader'))
        text_message_container = Container(name='text_message_container', parent=text_container, align=uiconst.TOTOP)
        main_message = eveLabel.Label(parent=text_message_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/TutorialReturnMessage'), top=5)
        bottom_container = Container(name='bottomContainer', parent=self, height=BOTTOM_CONTAINER_HEIGHT, align=uiconst.TOBOTTOM)
        self.close_button = Button(name='close_button', parent=bottom_container, fontsize=14, fixedwidth=125, fixedheight=22, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ContinueButtonLabel'), align=uiconst.BOTTOMRIGHT, top=10, left=10, func=lambda x: self.close())
        if self.isTutorial:
            self.skip_button = Button(name='skipButton', parent=bottom_container, fontsize=14, fixedwidth=125, fixedheight=22, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SkipTutorial'), align=uiconst.CENTERBOTTOM, top=10, left=0, func=lambda x: self.skip_tutorial())
            self.reset_button = Button(name='resetButton', parent=bottom_container, fontsize=14, fixedwidth=125, fixedheight=22, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/RestartTutorialButtonLabel'), align=uiconst.BOTTOMLEFT, top=10, left=10, func=lambda x: self.reset_tutorial())
        message_height = max(MIN_MESSAGE_TEXT_HEIGHT, main_message.height)
        text_message_container.height = message_height
        self.height = message_height + TEXT_HEADER_HEIGHT + HEADER_CONTAINER_HEIGHT + BOTTOM_CONTAINER_HEIGHT
        main_container.height = message_height + TEXT_HEADER_HEIGHT

    def close(self):
        if self.isTutorial:
            sm.ScatterEvent(projectDiscoveryEvents.StartTutorial)
        if self.toHide:
            self.toHide.opacity = 1
        sm.ScatterEvent(self._close_event)
        self.Close()

    def skip_tutorial(self):
        if self.toHide:
            self.toHide.opacity = 1
        sm.ScatterEvent(projectDiscoveryEvents.ProjectDiscoveryStarted, False)
        self.Close()

    def reset_tutorial(self):
        if self.toHide:
            self.toHide.opacity = 1
        sm.ScatterEvent(projectDiscoveryEvents.ResetTutorial)
        self.Close()
