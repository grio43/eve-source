#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\errors.py
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.sequencing.job.job_pb2 import Failure
from itertoolsext.Enum import Enum

@Enum

class GenericError(object):
    UNKNOWN = 'UNKNOWN'
    TIMEOUT = 'TIMEOUT'


@Enum

class SequencingJobError(object):
    INVALID_DESIGN = 'INVALID_DESIGN'
    INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS'
    INSUFFICIENT_COMPONENT_LICENSES = 'INSUFFICIENT_COMPONENT_LICENSES'
    INSUFFICIENT_SEQUENCE_BINDERS = 'INSUFFICIENT_SEQUENCE_BINDERS'
    INSUFFICIENT_SKILLS_FOR_SHIP_TYPE = 'INSUFFICIENT_SKILLS_FOR_SHIP_TYPE'
    MASS_SEQUENCING_LIMIT_REACHED = 'MASS_SEQUENCING_LIMIT_REACHED'
    MAX_CONCURRENT_SEQUENCING_JOBS_REACHED = 'MAX_CONCURRENT_SEQUENCING_JOBS_REACHED'
    SKIN_NAME_MISSING = 'SKIN_NAME_MISSING'
    INTERNAL_ERROR = 'INTERNAL_ERROR'


STATUS_CODE_TO_INITIATE_SEQUENCING_ERROR = {400: SequencingJobError.INVALID_DESIGN,
 490: SequencingJobError.MAX_CONCURRENT_SEQUENCING_JOBS_REACHED,
 491: SequencingJobError.INSUFFICIENT_COMPONENT_LICENSES,
 492: SequencingJobError.INSUFFICIENT_SEQUENCE_BINDERS,
 493: SequencingJobError.INSUFFICIENT_SKILLS_FOR_SHIP_TYPE,
 494: SequencingJobError.INSUFFICIENT_FUNDS,
 495: SequencingJobError.MASS_SEQUENCING_LIMIT_REACHED,
 500: SequencingJobError.INTERNAL_ERROR}
STATUS_CODE_TO_EXPEDITE_SEQUENCING_ERROR = {403: SequencingJobError.INSUFFICIENT_FUNDS}

def convert_sequencing_error_from_proto(proto_error):
    if proto_error in [Failure.FAILURE_UNSPECIFIED, Failure.FAILURE_INTERNAL_SERVER_ERROR]:
        return GenericError.UNKNOWN
    if proto_error == Failure.FAILURE_MISSING_FUNDS:
        return SequencingJobError.INSUFFICIENT_FUNDS
    if proto_error == Failure.FAILURE_MISSING_RESOURCES:
        return SequencingJobError.INSUFFICIENT_SEQUENCE_BINDERS


def convert_sequencing_error_to_proto(error):
    if error == SequencingJobError.INSUFFICIENT_FUNDS:
        return Failure.FAILURE_MISSING_FUNDS
    if error == SequencingJobError.INSUFFICIENT_SEQUENCE_BINDERS:
        return Failure.FAILURE_MISSING_RESOURCES
    return Failure.FAILURE_UNSPECIFIED


@Enum

class SkinDesignManagementError(object):
    MAX_SAVED_DESIGNS_LIMIT_REACHED = 'MAX_SAVED_DESIGNS_LIMIT_REACHED'
    INVALID_DESIGN = 'INVALID_DESIGN'
    SKIN_NAME_MISSING = 'SKIN_NAME_MISSING'


@Enum

class SkinDesignSharingError(object):
    DESIGN_NOT_FOUND = 'DESIGN_NOT_FOUND'


class NoTimeRemainingException(Exception):
    pass


class ConsumeComponentItemFailed(Exception):
    pass


class ConsumeComponentItemConflict(Exception):
    pass


@Enum

class ListingError(object):
    INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS'
    INVALID_LOCATION = 'INVALID_LOCATION'
    INVALID_LISTING = 'INVALID_LISTING'
    LISTING_NOT_FOUND = 'LISTING_NOT_FOUND'
    INSUFFICIENT_LICENSES = 'INSUFFICIENT_LICENSES'
    FEATURE_FLAG_OFF = 'FEATURE_FLAG_OFF'
    INVALID_VERSION = 'INVALID_VERSION'
    NO_RIGHT_TO_VIEW = 'NO_RIGHT_TO_VIEW'
    UNAUTHORIZED_PURCHASE = 'UNAUTHORIZED_PURCHASE'
    MAX_LISTING_LIMIT_REACHED = 'MAX_LISTING_LIMIT_REACHED'
    UNKNOWN = 'UNKNOWN'


STATUS_CODE_TO_LISTING_OPERATION_ERROR = {400: ListingError.INVALID_LISTING,
 401: ListingError.INVALID_LISTING,
 403: ListingError.INVALID_LISTING,
 404: ListingError.LISTING_NOT_FOUND,
 409: ListingError.INVALID_VERSION,
 412: ListingError.INSUFFICIENT_LICENSES,
 423: ListingError.NO_RIGHT_TO_VIEW}
STATUS_CODE_TO_LISTING_PURCHASE_OPERATION_ERROR = {400: ListingError.INVALID_LISTING,
 401: ListingError.INVALID_LISTING,
 403: ListingError.INSUFFICIENT_FUNDS,
 404: ListingError.LISTING_NOT_FOUND,
 409: ListingError.INVALID_VERSION,
 412: ListingError.INSUFFICIENT_LICENSES,
 423: ListingError.UNAUTHORIZED_PURCHASE}
DESIGN_ERROR_TEXT_BY_CODE = {SkinDesignManagementError.INVALID_DESIGN: 'UI/Personalization/ShipSkins/SKINR/Studio/DesignErrors/InvalidDesign',
 SkinDesignManagementError.MAX_SAVED_DESIGNS_LIMIT_REACHED: 'UI/Personalization/ShipSkins/SKINR/Studio/DesignErrors/SaveLimitReached',
 SkinDesignManagementError.SKIN_NAME_MISSING: 'UI/Personalization/ShipSkins/SKINR/Studio/DesignErrors/SkinNameMissing'}
SEQUENCING_ERROR_TEXT_BY_CODE = {SequencingJobError.INVALID_DESIGN: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/InvalidDesign',
 SequencingJobError.INSUFFICIENT_FUNDS: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/InsufficientPLEXFunds',
 SequencingJobError.INSUFFICIENT_COMPONENT_LICENSES: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/InsufficientComponentLicenses',
 SequencingJobError.INSUFFICIENT_SEQUENCE_BINDERS: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/InsufficientSequenceBinders',
 SequencingJobError.INSUFFICIENT_SKILLS_FOR_SHIP_TYPE: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/InsufficientSkillsForShipType',
 SequencingJobError.MASS_SEQUENCING_LIMIT_REACHED: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/MaxSequencingLimitReached',
 SequencingJobError.MAX_CONCURRENT_SEQUENCING_JOBS_REACHED: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/MaxConcurrentSequencingJobsReached',
 SequencingJobError.SKIN_NAME_MISSING: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/SkinNameMissing',
 SequencingJobError.INTERNAL_ERROR: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/InternalError',
 GenericError.TIMEOUT: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/InternalError',
 GenericError.UNKNOWN: 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingErrors/InternalError'}

def get_sequencing_error_text(error_code):
    if error_code in SEQUENCING_ERROR_TEXT_BY_CODE:
        return SEQUENCING_ERROR_TEXT_BY_CODE[error_code]
    return SEQUENCING_ERROR_TEXT_BY_CODE[GenericError.UNKNOWN]


SEQUENCE_FAILURE_REASON_TO_ERROR = {0: SequencingJobError.INTERNAL_ERROR,
 1: SequencingJobError.INSUFFICIENT_FUNDS,
 3: SequencingJobError.INSUFFICIENT_SEQUENCE_BINDERS,
 4: SequencingJobError.INTERNAL_ERROR}
LISTING_ERROR_TEXT_BY_CODE = {ListingError.INSUFFICIENT_FUNDS: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InsufficientFunds',
 ListingError.INVALID_LOCATION: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InvalidLocation',
 ListingError.INVALID_LISTING: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InvalidListing',
 ListingError.LISTING_NOT_FOUND: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/ListingNotFound',
 ListingError.INSUFFICIENT_LICENSES: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InternalError',
 ListingError.NO_RIGHT_TO_VIEW: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/NoRightToView',
 ListingError.UNAUTHORIZED_PURCHASE: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/UnauthorizedPurchase',
 ListingError.MAX_LISTING_LIMIT_REACHED: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/MaxListingLimitReached',
 ListingError.FEATURE_FLAG_OFF: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InternalError',
 ListingError.UNKNOWN: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InternalError',
 GenericError.TIMEOUT: 'UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InternalError'}

def get_listing_error_text(error_code):
    if error_code in LISTING_ERROR_TEXT_BY_CODE:
        return LISTING_ERROR_TEXT_BY_CODE[error_code]
    return LISTING_ERROR_TEXT_BY_CODE[ListingError.UNKNOWN]


class GetSkinLicensesFailed(Exception):

    def __init__(self, error_list, opt = ''):
        self._msg = 'Failed to load licenses:\n'
        for license_id, error_msg in error_list:
            self._msg += '%s: %s\n' % (license_id, error_msg)

        Exception.__init__(self, self._msg, opt)

    def __str__(self):
        return self._msg
