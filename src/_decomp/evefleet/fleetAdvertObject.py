#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\fleetAdvertObject.py
import evefleet
import mathext
from brennivin.itertoolsext import Bundle
MAX_ALLOWED_ENTITIES = 1000

class BaseFleetAdvertObject(object):
    name = 'BaseFleetAdvertObject'

    def __init__(self, **kwargs):
        self._fleetName = ''
        self._description = ''
        self.inviteScope = evefleet.INVITE_CLOSED
        self._activityValue = None
        self.useAdvanceOptions = False
        self._newPlayerFriendly = False
        self.advancedOptions = self.GetDefaultAdvancedOptions()
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def get(self, key, defaultValue = None):
        return getattr(self, key, defaultValue)

    def Get(self, key, defaultValue = None):
        return self.get(key, defaultValue)

    def __repr__(self):
        return '<%s %s>' % (self.name, self.GetData())

    def GetDefaultAdvancedOptions(self):
        advancedOptionsBundle = Bundle()
        advancedOptionsBundle.public_minStanding = None
        advancedOptionsBundle.public_minSecurity = None
        advancedOptionsBundle.public_allowedEntities = set()
        advancedOptionsBundle.public_disallowedEntities = set()
        advancedOptionsBundle.membergroups_minStanding = None
        advancedOptionsBundle.membergroups_minSecurity = None
        advancedOptionsBundle.membergroups_allowedEntities = set()
        advancedOptionsBundle.membergroups_disallowedEntities = set()
        advancedOptionsBundle.joinNeedsApproval = False
        advancedOptionsBundle.hideInfo = False
        advancedOptionsBundle.updateOnBossChange = True
        advancedOptionsBundle.advertJoinLimit = None
        return advancedOptionsBundle

    def GetData(self, fullAdvancedOptions = True):
        ret = {}
        for k, v in self.__dict__.iteritems():
            if k == 'advancedOptions':
                continue
            if k.startswith('_'):
                newKey = k.replace('_', '', 1)
                ret[newKey] = getattr(self, newKey, None)
                continue
            ret[k] = v

        if fullAdvancedOptions:
            ret.update(self.advancedOptions)
        else:
            ret.update(self.GetLimitedAdvancedOptionsData())
        return ret

    def GetAllAdvancedOptionsData(self):
        return self.advancedOptions

    def GetLimitedAdvancedOptionsData(self):
        advanced = self.advancedOptions.copy()
        advanced.pop('public_allowedEntities', None)
        advanced.pop('public_disallowedEntities', None)
        advanced.pop('membergroups_allowedEntities', None)
        advanced.pop('membergroups_disallowedEntities', None)
        return advanced

    @property
    def fleetName(self):
        return self._fleetName

    @fleetName.setter
    def fleetName(self, fleetName):
        self._fleetName = fleetName[:evefleet.FLEETNAME_MAXLENGTH]

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, desc):
        self._description = desc[:evefleet.FLEETDESC_MAXLENGTH]

    @property
    def public_minStanding(self):
        return self.advancedOptions.public_minStanding

    @public_minStanding.setter
    def public_minStanding(self, standingValue):
        self.advancedOptions.public_minStanding = self._GetFormattedValue(standingValue)

    @property
    def public_minSecurity(self):
        return self.advancedOptions.public_minSecurity

    @public_minSecurity.setter
    def public_minSecurity(self, value):
        self.advancedOptions.public_minSecurity = self._GetFormattedValue(value)

    @property
    def public_allowedEntities(self):
        return self.advancedOptions.public_allowedEntities

    @public_allowedEntities.setter
    def public_allowedEntities(self, allowedEntities):
        if allowedEntities and len(allowedEntities) > MAX_ALLOWED_ENTITIES:
            allowedEntities = set(list(allowedEntities)[:MAX_ALLOWED_ENTITIES])
        self.advancedOptions.public_allowedEntities = allowedEntities

    @property
    def public_disallowedEntities(self):
        return self.advancedOptions.public_disallowedEntities

    @public_disallowedEntities.setter
    def public_disallowedEntities(self, disallowedEntities):
        if disallowedEntities and len(disallowedEntities) > MAX_ALLOWED_ENTITIES:
            disallowedEntities = set(list(disallowedEntities)[:MAX_ALLOWED_ENTITIES])
        self.advancedOptions.public_disallowedEntities = disallowedEntities

    @property
    def membergroups_minStanding(self):
        return self.advancedOptions.membergroups_minStanding

    @membergroups_minStanding.setter
    def membergroups_minStanding(self, standingValue):
        self.advancedOptions.membergroups_minStanding = self._GetFormattedValue(standingValue)

    @property
    def membergroups_minSecurity(self):
        return self.advancedOptions.membergroups_minSecurity

    @membergroups_minSecurity.setter
    def membergroups_minSecurity(self, value):
        self.advancedOptions.membergroups_minSecurity = self._GetFormattedValue(value)

    @property
    def membergroups_allowedEntities(self):
        return self.advancedOptions.membergroups_allowedEntities

    @membergroups_allowedEntities.setter
    def membergroups_allowedEntities(self, allowedEntities):
        if allowedEntities and len(allowedEntities) > MAX_ALLOWED_ENTITIES:
            allowedEntities = set(list(allowedEntities)[:MAX_ALLOWED_ENTITIES])
        self.advancedOptions.membergroups_allowedEntities = allowedEntities

    @property
    def membergroups_disallowedEntities(self):
        return self.advancedOptions.membergroups_disallowedEntities

    @membergroups_disallowedEntities.setter
    def membergroups_disallowedEntities(self, disallowedEntities):
        if disallowedEntities and len(disallowedEntities) > MAX_ALLOWED_ENTITIES:
            disallowedEntities = set(list(disallowedEntities)[:MAX_ALLOWED_ENTITIES])
        self.advancedOptions.membergroups_disallowedEntities = disallowedEntities

    @property
    def advertJoinLimit(self):
        return self.advancedOptions.advertJoinLimit

    @advertJoinLimit.setter
    def advertJoinLimit(self, limit):
        if limit is not None:
            limit = mathext.clamp(limit, 1, evefleet.MAX_MEMBERS_IN_FLEET)
        self.advancedOptions.advertJoinLimit = limit

    @property
    def activityValue(self):
        return self._activityValue

    @activityValue.setter
    def activityValue(self, value):
        if value in evefleet.fleetActivityNames:
            self._activityValue = value
        else:
            self._activityValue = None

    @property
    def joinNeedsApproval(self):
        return self.advancedOptions.joinNeedsApproval

    @joinNeedsApproval.setter
    def joinNeedsApproval(self, needsApproval):
        self.advancedOptions.joinNeedsApproval = needsApproval

    @property
    def hideInfo(self):
        return self.advancedOptions.hideInfo

    @hideInfo.setter
    def hideInfo(self, doHide):
        self.advancedOptions.hideInfo = doHide

    @property
    def newPlayerFriendly(self):
        return self._newPlayerFriendly

    @newPlayerFriendly.setter
    def newPlayerFriendly(self, isNewPlayerFriendly):
        self._newPlayerFriendly = isNewPlayerFriendly

    @property
    def updateOnBossChange(self):
        return self.advancedOptions.updateOnBossChange

    @updateOnBossChange.setter
    def updateOnBossChange(self, doUpdate):
        self.advancedOptions.updateOnBossChange = doUpdate

    def _GetFormattedValue(self, value):
        return value

    def ResetAdvancedOptions(self):
        self.advancedOptions = self.GetDefaultAdvancedOptions()

    def ResetInviteScope(self):
        self.inviteScope = evefleet.INVITE_CLOSED

    def AddToInviteScopeMask(self, value):
        self.inviteScope += value

    def GetNumAllowedEntities(self):
        return len(self.advancedOptions.public_allowedEntities) + len(self.advancedOptions.membergroups_allowedEntities)

    def IsOpenToMemberEntities(self):
        return self.IsAdvertOpenToCorp() or self.IsAdvertOpenToAlliance() or self.IsAdvertOpenToMilitia()

    def IsOpenToPublicThroughStandings(self):
        return self.IsAdvertOpenToPublic() and self.public_minStanding is not None

    def IsAdvertOpenToCorp(self):
        return evefleet.IsOpenToCorpFromMask(self.inviteScope)

    def IsAdvertOpenToAlliance(self):
        return evefleet.IsOpenToAllianceFromMask(self.inviteScope)

    def IsAdvertOpenToMilitia(self):
        return evefleet.IsOpenToMilitiaFromMask(self.inviteScope)

    def IsAdvertOpenToPublic(self):
        return evefleet.IsOpenToPublicFromMask(self.inviteScope)

    def IsAdvertOpenToAllPublic(self):
        return evefleet.IsOpenToAllPublicFromMask(self.inviteScope)

    def IsUsingAdvancedOptions(self):
        if self.inviteScope != evefleet.INVITE_PUBLIC_OPEN:
            return True
        return self.AreAdvancedOptionsDefault()

    def AreAdvancedOptionsDefault(self):
        return self.advancedOptions != self.GetDefaultAdvancedOptions()


class FleetAdvertCreationObject(BaseFleetAdvertObject):
    name = 'FleetAdvertCreationObject'

    def GetCopy(self):
        return FleetAdvertCreationObject(**self.GetData())


class FleetAdvertObject(BaseFleetAdvertObject):
    name = 'FleetAdvertObject'

    def __init__(self, **kwargs):
        self.fleetID = None
        self.leader = None
        self.solarSystemID = None
        self.numMembers = None
        self.advertTime = None
        self.dateCreated = None
        BaseFleetAdvertObject.__init__(self, **kwargs)

    def _GetFormattedValue(self, value):
        if value is None:
            return
        return float(value)

    def GetCopy(self):
        return FleetAdvertObject(**self.GetData())
