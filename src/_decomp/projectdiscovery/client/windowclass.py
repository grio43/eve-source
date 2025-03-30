#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\windowclass.py
from projectdiscovery.client.projects.covid.windows.covidwindow import CovidWindow
from projectdiscovery.client.projects.exoplanets.windows.exoplanetswindow import ExoPlanetsWindow
from projectdiscovery.common.const import ACTIVE_PROJECT_ID, COVID_PROJECT_ID, EXOPLANETS_PROJECT_ID
WINDOW_BY_PROJECT = {COVID_PROJECT_ID: CovidWindow,
 EXOPLANETS_PROJECT_ID: ExoPlanetsWindow}

def get_project_discovery_window_class():
    return WINDOW_BY_PROJECT[ACTIVE_PROJECT_ID]
