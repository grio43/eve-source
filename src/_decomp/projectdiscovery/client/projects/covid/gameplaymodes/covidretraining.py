#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\covidretraining.py
from projectdiscovery.client.projects.covid.gameplaymodes.covidtransition import CovidTransition

class OfferRetraining(CovidTransition):
    LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Intro/'
    TRANSITION_SKIP_BUTTON_LABEL_PATH = LABELS_FOLDER + 'RetrainingButtonSkip'
    TRANSITION_CONTINUE_BUTTON_LABEL_PATH = LABELS_FOLDER + 'RetrainingButtonContinue'
    TRANSITION_TEXT_LABEL_PATH = LABELS_FOLDER + 'RetrainingText'
