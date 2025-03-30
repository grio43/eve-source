#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\entitlements\corporation\structure\qaconst.py
FORCE_STRUCTURE_ISSUE_LICENSE_ERRORS = False
FORCE_STRUCTURE_GET_LICENSE_ERRORS = False
FORCE_STRUCTURE_GET_LICENSE_RANDOM_ERRORS = False
FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_ERRORS = False
FORCE_STRUCTURE_GET_COSMETIC_STATE_ERRORS = False
FORCE_STRUCTURE_REVOKE_LICENSE_ERRORS = False
FORCE_STRUCTURE_ISSUE_LICENSE_DELAY = 0
FORCE_STRUCTURE_GET_LICENSE_DELAY = 0
FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_DELAY = 0
FORCE_STRUCTURE_GET_COSMETIC_STATE_DELAY = 0
FORCE_STRUCTURE_REVOKE_LICENSE_DELAY = 0

def flush_cache():
    sm.GetService('cosmeticsLicenseSvc').flush_paintwork_cache()


def set_force_structure_issue_license_errors(enabled):
    global FORCE_STRUCTURE_ISSUE_LICENSE_ERRORS
    flush_cache()
    FORCE_STRUCTURE_ISSUE_LICENSE_ERRORS = enabled


def set_force_structure_get_license_errors(enabled):
    global FORCE_STRUCTURE_GET_LICENSE_ERRORS
    flush_cache()
    FORCE_STRUCTURE_GET_LICENSE_ERRORS = enabled


def set_force_structure_get_license_random_errors(enabled):
    global FORCE_STRUCTURE_GET_LICENSE_RANDOM_ERRORS
    flush_cache()
    FORCE_STRUCTURE_GET_LICENSE_RANDOM_ERRORS = enabled


def set_force_structure_get_license_catalogue_errors(enabled):
    global FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_ERRORS
    flush_cache()
    FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_ERRORS = enabled


def set_force_structure_get_cosmetic_state_errors(enabled):
    global FORCE_STRUCTURE_GET_COSMETIC_STATE_ERRORS
    flush_cache()
    FORCE_STRUCTURE_GET_COSMETIC_STATE_ERRORS = enabled


def set_force_structure_revoke_license_errors(enabled):
    global FORCE_STRUCTURE_REVOKE_LICENSE_ERRORS
    flush_cache()
    FORCE_STRUCTURE_REVOKE_LICENSE_ERRORS = enabled


def set_force_structure_issue_license_delay(seconds):
    global FORCE_STRUCTURE_ISSUE_LICENSE_DELAY
    flush_cache()
    FORCE_STRUCTURE_ISSUE_LICENSE_DELAY = seconds


def set_force_structure_get_license_delay(seconds):
    global FORCE_STRUCTURE_GET_LICENSE_DELAY
    flush_cache()
    FORCE_STRUCTURE_GET_LICENSE_DELAY = seconds


def set_force_structure_get_license_catalogue_delay(seconds):
    global FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_DELAY
    flush_cache()
    FORCE_STRUCTURE_GET_LICENSE_CATALOGUE_DELAY = seconds


def set_force_structure_get_cosmetic_state_delay(seconds):
    global FORCE_STRUCTURE_GET_COSMETIC_STATE_DELAY
    flush_cache()
    FORCE_STRUCTURE_GET_COSMETIC_STATE_DELAY = seconds


def set_force_structure_revoke_license_delay(seconds):
    global FORCE_STRUCTURE_REVOKE_LICENSE_DELAY
    flush_cache()
    FORCE_STRUCTURE_REVOKE_LICENSE_DELAY = seconds
