#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\whitelist.py
from homestation.error import RemoteChangeNotExpectedError
from homestation.types import StationData, StationCandidateData
from homestation.validation import ChangeHomeStationValidationError, SelfDestructCloneValidationError
whitelist = {ChangeHomeStationValidationError,
 RemoteChangeNotExpectedError,
 SelfDestructCloneValidationError,
 StationCandidateData,
 StationData}
