#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\ui\const.py
from projectdiscovery.common.const import ACTIVE_PROJECT_ID, COVID_PROJECT_ID, EXOPLANETS_PROJECT_ID
AGENCY_LABELS_FOLDER = 'UI/Agency/ProjectDiscovery/'
TITLE_BY_PROJECT_ID = {COVID_PROJECT_ID: AGENCY_LABELS_FOLDER + 'Covid/Covid',
 EXOPLANETS_PROJECT_ID: AGENCY_LABELS_FOLDER + 'Exoplanets/Exoplanets'}
DESCRIPTION_BY_PROJECT_ID = {COVID_PROJECT_ID: AGENCY_LABELS_FOLDER + 'Covid/Description',
 EXOPLANETS_PROJECT_ID: AGENCY_LABELS_FOLDER + 'Exoplanets/Description'}
RESOURCES_FOLDER = 'res:/UI/Texture/classes/agency/ActivityImages/'
IMAGE_BY_PROJECT_ID = {COVID_PROJECT_ID: RESOURCES_FOLDER + 'projectDiscovery_Covid.png',
 EXOPLANETS_PROJECT_ID: RESOURCES_FOLDER + 'projectDiscovery.png'}

def get_agency_title():
    if ACTIVE_PROJECT_ID in TITLE_BY_PROJECT_ID:
        return TITLE_BY_PROJECT_ID[ACTIVE_PROJECT_ID]
    return TITLE_BY_PROJECT_ID[0]


def get_agency_description():
    if ACTIVE_PROJECT_ID in DESCRIPTION_BY_PROJECT_ID:
        return DESCRIPTION_BY_PROJECT_ID[ACTIVE_PROJECT_ID]
    return DESCRIPTION_BY_PROJECT_ID[0]


def get_agency_image():
    if ACTIVE_PROJECT_ID in IMAGE_BY_PROJECT_ID:
        return IMAGE_BY_PROJECT_ID[ACTIVE_PROJECT_ID]
    return IMAGE_BY_PROJECT_ID[0]
