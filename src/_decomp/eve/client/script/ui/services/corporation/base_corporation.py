#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corporation\base_corporation.py
from caching import Memoize
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING
from collections import defaultdict, namedtuple
import utillib
from carbon.common.script.util.format import FmtDate
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.services.corporation.bco_alliance import CorpAllianceO
from eve.client.script.ui.services.corporation.bco_applications import ApplicationsO
from eve.client.script.ui.services.corporation.bco_corporations import CorporationsO
from eve.client.script.ui.services.corporation.bco_members import CorporationMembersO
from eve.client.script.ui.services.corporation.bco_recruitment import CorporationRecruitmentO
from eve.client.script.ui.services.corporation.bco_shares import SharesO
from eve.client.script.ui.services.corporation.bco_titles import TitlesO
from eve.common.lib import appConst
from eve.common.script.net import eveMoniker
from eve.common.script.sys import eveCfg, idCheckers
from carbon.common.script.sys.row import Row
from crimewatch.corp_aggression.settings import AggressionSettings
from eve.client.script.ui.shared.neocom.corporation.corp_ui_applications import ApplyToCorpWnd, MyCorpApplicationWnd
from eve.client.script.ui.shared.neocom.corporation.corp_ui_bulletins import EditCorpBulletin, BulletinEntry
from eve.client.script.ui.shared.neocom.corporation.recruitment.corpRecruitmentAdWindow import CorpRecruitmentAdStandaloneWindow
from evecorporation.roles import CORP_ROLE_GROUPS_ATTRS, get_corporation_role_groups, get_role_description, get_role_name, iter_roles, check_is_role_director, is_corporation_role_director
from eve.common.script.sys.rowset import IndexRowset
from eve.client.script.ui.util import uix
import blue
import uthread
import carbonui.const as uiconst
import localization
import eve.common.lib.appConst as const
from carbonui.uicore import uicore
from eveexceptions import UserError
from expiringdict import ExpiringDict
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from localization import GetByLabel
from localization.formatters import FormatGenericList
FSD_COMMUNICATIONS_OFFICER_ROLE_ID = 60217
MAX_NUM_BULLETINS = 10
Role = namedtuple('Role', ['roleID',
 'roleName',
 'shortDescription',
 'description'])
FUNCTIONAL_OBJECT_TYPE_MAP = {'alliance': CorpAllianceO,
 'applications': ApplicationsO,
 'corporations': CorporationsO,
 'members': CorporationMembersO,
 'recruitment': CorporationRecruitmentO,
 'shares': SharesO,
 'titles': TitlesO}

class Corporation(Service):
    __guid__ = 'svc.corp'
    __notifyevents__ = ['DoSessionChanging',
     'OnSessionChanged',
     'OnSessionReset',
     'OnCorporationChanged',
     'OnCorporationMemberChanged',
     'OnCorporationApplicationChanged',
     'OnCorporationRecruitmentAdChanged',
     'OnShareChange',
     'OnTitleChanged',
     'OnAllianceApplicationChanged',
     'OnCorporationWelcomeMailChanged']
    __servicename__ = 'corp'
    __displayname__ = 'Corporation Client Service'
    __dependencies__ = ['sessionMgr']
    __functionalobjects__ = ['corporations',
     'members',
     'applications',
     'shares',
     'alliance',
     'titles',
     'recruitment']

    def __init__(self):
        Service.__init__(self)
        self.__roles = None
        self.__roleGroupings = None
        self.__roleGroupingsForTitles = None
        self.__divisionalRoles = None
        self.__hierarchicalRoles = None
        self.__locationalRoles = const.locationalCorpRoles
        self.__recruitmentAdTypes = None
        self.__recruitmentAdGroups = None
        self.resigning = False
        self.aggressionSettingsByCorpID = ExpiringDict(100000, 600)

    def GetDependencies(self):
        return self.__dependencies__

    def GetObjectNames(self):
        return self.__functionalobjects__

    def Run(self, memStream = None):
        self.LogInfo('Starting Corporation')
        self.state = SERVICE_START_PENDING
        sm.FavourMe(self.OnSessionChanged)
        sm.FavourMe(self.OnCorporationMemberChanged)
        self.__corpRegistry = None
        self.__corpRegistryCorpID = None
        self.__corpStationManager = None
        self.__corpStationManagerStationID = None
        for objectName in self.__functionalobjects__:
            dataObject = None
            dataObjectType = FUNCTIONAL_OBJECT_TYPE_MAP.get(objectName, None)
            if dataObjectType is not None:
                dataObject = dataObjectType(self)
            if dataObject is None:
                raise RuntimeError('FunctionalObject not found %s' % objectName)
            setattr(self, objectName, dataObject)

        for objectName in self.__functionalobjects__:
            object = getattr(self, objectName)
            object.DoObjectWeakRefConnections()

        self.state = SERVICE_RUNNING
        import __builtin__
        if hasattr(__builtin__, 'eve') and eve.session.corpid:
            uthread.new(self.members.PrimeCorpInformation)
        self.bulletins = None
        self.bulletinsTimestamp = 0

    def Stop(self, memStream = None):
        self.__corpRegistry = None
        self.__corpRegistryCorpID = None
        self.__corpStationManager = None
        self.__corpStationManagerStationID = None

    def RefreshMoniker(self):
        if self.__corpRegistry is not None:
            self.__corpRegistry.UnBind()

    def GetCorpRegistry(self):
        if self.__corpRegistry is None:
            self.__corpRegistry = eveMoniker.GetCorpRegistry()
            self.__corpRegistryCorpID = eve.session.corpid
            self.__corpRegistry.Bind()
        if self.__corpRegistryCorpID != eve.session.corpid:
            if self.__corpRegistry is not None:
                self.__corpRegistry.Unbind()
            self.__corpRegistry = eveMoniker.GetCorpRegistry()
            self.__corpRegistry.Bind()
            self.__corpRegistryCorpID = eve.session.corpid
        return self.__corpRegistry

    def GetCorpStationManager(self):
        if not eve.session.stationid:
            if self.__corpStationManager is not None:
                self.__corpStationManager.Unbind()
            raise RuntimeError('InvalidCallee due to state')
        else:
            if self.__corpStationManager is None:
                self.__corpStationManager = eveMoniker.GetCorpStationManager()
                self.__corpStationManagerStationID = eve.session.stationid
            if self.__corpStationManagerStationID != eve.session.stationid:
                if self.__corpStationManager is not None:
                    self.__corpStationManager.Unbind()
                self.__corpStationManager = eveMoniker.GetCorpStationManager()
                self.__corpStationManagerStationID = eve.session.stationid
        return self.__corpStationManager

    def SetAccountKey(self, accountKey):
        self.sessionMgr.PerformSessionChange('corp.setaccountkey', self.members.SetAccountKey, accountKey, violateSafetyTimer=True)

    def GetCorpAccountName(self, acctID):
        if acctID is None:
            return
        return self.GetDivisionNames()[acctID - 1000 + 8]

    def GetMyCorpAccountName(self):
        return eve.session.corpAccountKey and self.GetCorpAccountName(eve.session.corpAccountKey)

    def CallDelegates(self, functionName, *args):
        for objectName in self.__functionalobjects__:
            object = getattr(self, objectName)
            function = getattr(object, functionName, None)
            if function is not None:
                function(*args)

    def DoSessionChanging(self, isRemote, session, change):
        if 'stationid' in change:
            oldID, newID = change['stationid']
            if self.__corpStationManager is not None:
                self.__corpStationManager = None
                self.__corpStationManagerStationID = None
        if 'corpid' in change:
            self.__hierarchicalRoles = None
            self.__divisionalRoles = None
            self.__roleGroupings = None
            self.__roleGroupingsForTitles = None
        self.CallDelegates('DoSessionChanging', isRemote, session, change)

    def OnSessionChanged(self, isRemote, session, change):
        self.CallDelegates('OnSessionChanged', isRemote, session, change)
        if 'corpid' in change:
            self.bulletins = None
            self.bulletinsTimestamp = 0

    def OnSessionReset(self):
        self.Stop()

    def GetCorporation(self, corpid = None, new = 0):
        return self.corporations.GetCorporation(corpid, new)

    def GetCorporations(self, corporations, new = 0):
        return self.corporations.GetCorporations(corporations, new)

    def GetCostForCreatingACorporation(self):
        return self.corporations.GetCostForCreatingACorporation()

    def ResetCacheForMyCorp(self):
        self.corporations.Reset()

    def UpdateCorporationAbilities(self):
        return self.corporations.UpdateCorporationAbilities()

    def UpdateLogo(self, shape1, shape2, shape3, color1, color2, color3, typeface):
        return self.corporations.UpdateLogo(shape1, shape2, shape3, color1, color2, color3, typeface)

    def UpdateCorporation(self, description, url, iskTaxRate, isRecruiting, loyaltyPointTaxRate):
        return self.corporations.UpdateCorporation(description, url, iskTaxRate, isRecruiting, loyaltyPointTaxRate)

    def GetSuggestedTickerNames(self, corporationName):
        return self.corporations.GetSuggestedTickerNames(corporationName)

    def AddCorporation(self, corporationName, tickerName, description, url = '', iskTaxRate = 0.0, shape1 = None, shape2 = None, shape3 = None, color1 = None, color2 = None, color3 = None, typeface = None, applicationsEnabled = 1, friendlyFireEnabled = False, loyaltyPointTaxRate = 0.0):
        return self.corporations.AddCorporation(corporationName, tickerName, description, url, iskTaxRate, shape1, shape2, shape3, color1, color2, color3, typeface, applicationsEnabled, friendlyFireEnabled, loyaltyPointTaxRate)

    def OnCorporationChanged(self, corpID, change):
        self.corporations.OnCorporationChanged(corpID, change)

    def GetDivisionNames(self):
        names = self.corporations.GetDivisionNames()
        return names

    @Memoize
    def GetHangarDivisionNameFromFlagID(self, flagID):
        divisionID = const.corpDivisionsByFlag.get(flagID, None)
        if divisionID is None:
            return
        return self.GetDivisionNames()[divisionID + 1]

    def GetAggressionSettings(self, corpID):
        if corpID in self.aggressionSettingsByCorpID:
            return self.aggressionSettingsByCorpID[corpID]
        aggressionSettings = sm.RemoteSvc('corpmgr').GetAggressionSettings(corpID)
        self.aggressionSettingsByCorpID[corpID] = aggressionSettings
        return aggressionSettings

    def GetAggressionSettingsForCorps(self, corpIDs):
        retAggressionSettings = {}
        toFetch = set()
        for eachCorpID in corpIDs:
            if eachCorpID in self.aggressionSettingsByCorpID:
                retAggressionSettings[eachCorpID] = self.aggressionSettingsByCorpID[eachCorpID]
            else:
                toFetch.add(eachCorpID)

        if toFetch:
            newAggressionSettingsByCorpID = sm.RemoteSvc('corpmgr').GetAggressionSettingsForCorps(toFetch)
            for eachCorpID, eachAggressionSettings in newAggressionSettingsByCorpID.iteritems():
                self.aggressionSettingsByCorpID[eachCorpID] = eachAggressionSettings
                retAggressionSettings[eachCorpID] = eachAggressionSettings

        return retAggressionSettings

    def GetCorpFriendlyFireStatus(self, aggressionSettings):
        now = blue.os.GetWallclockTime()
        isLegal = aggressionSettings.IsFriendlyFireLegalAtTime(now)
        changeAtTime = aggressionSettings.GetNextPendingChangeTime(now)
        if changeAtTime:
            time = FmtDate(changeAtTime, 'ns')
            isTomorrow = FmtDate(changeAtTime, 'xn') != FmtDate(now, 'xn')
            if isLegal:
                if isTomorrow:
                    return localization.GetByLabel('UI/Corporations/FriendlyFire/LegalWithChangeTimeTomorrow', time=time)
                return localization.GetByLabel('UI/Corporations/FriendlyFire/LegalWithChangeTime', time=time)
            elif isTomorrow:
                return localization.GetByLabel('UI/Corporations/FriendlyFire/IllegalWithChangeTimeTomorrow', time=time)
            else:
                return localization.GetByLabel('UI/Corporations/FriendlyFire/IllegalWithChangeTime', time=time)
        else:
            if isLegal:
                return localization.GetByLabel('UI/Corporations/FriendlyFire/Legal')
            return localization.GetByLabel('UI/Corporations/FriendlyFire/Illegal')

    def GetSuggestedAllianceShortNames(self, allianceName):
        return self.alliance.GetSuggestedAllianceShortNames(allianceName)

    def CreateAlliance(self, allianceName, shortName, description, url):
        return self.alliance.CreateAlliance(allianceName, shortName, description, url)

    def ApplyToJoinAlliance(self, allianceID, applicationText):
        self.LogNotice('Calling server ApplyToJoinAlliance(', allianceID, applicationText, ') for corp', session.corpid)
        return self.GetCorpRegistry().ApplyToJoinAlliance(allianceID, applicationText)

    def CheckCanApplyToJoinAlliance(self, allianceID = None):
        if session.allianceid is not None:
            self.LogInfo('CheckCanApplyToJoinAlliance - corp', session.corpid, 'is already in an alliance')
            return False
        if not session.corprole & const.corpRoleDirector:
            raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NotDirector')})
        if session.charid != sm.GetService('corp').GetCorporation().ceoID:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/AccessRestrictions/OnlyForActiveCEO')})
        if allianceID and allianceID in self.GetAllianceApplications():
            raise UserError('CantApplyTwiceToAlliance')
        for war in sm.GetService('war').GetWars(session.corpid).itervalues():
            if war.declaredByID == session.corpid:
                if war.timeFinished is not None and blue.os.GetWallclockTime() > war.timeFinished:
                    continue
                raise UserError('CanNotJoinAllianceWhileAgressor')
            if war.mutual:
                raise UserError('CanNotJoinAllianceWithActiveMututalWars')
            if war.againstID != session.corpid:
                if allianceID is not None and war.againstID != allianceID:
                    raise UserError('CanNotJoinAllianceWhileAlliedWithOthers')

        return True

    def GetAllianceApplications(self):
        return self.alliance.GetAllianceApplications()

    def DeleteAllianceApplication(self, allianceID):
        return self.alliance.DeleteAllianceApplication(allianceID)

    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        if corpID == eve.session.corpid:
            self.alliance.OnAllianceApplicationChanged(allianceID, corpID, change)

    def GetMemberIDs(self):
        return self.members.GetMemberIDs()

    def GetMembers(self):
        return self.members.GetMembers()

    def GetMembersPaged(self, page):
        return self.members.GetMembersPaged(page)

    def GetMembersByIds(self, memberIDs):
        return self.members.GetMembersByIds(memberIDs)

    def GetMember(self, charID):
        return self.members.GetMember(charID)

    def ClearMemberCache(self, charID):
        self.members.GetMember.clear_memoized(self.members, charID)

    def GetMembersAsEveOwners(self):
        return self.members.GetMembersAsEveOwners()

    def UpdateMember(self, charIDToUpdate, title = None, divisionID = None, squadronID = None, roles = None, grantableRoles = None, rolesAtHQ = None, grantableRolesAtHQ = None, rolesAtBase = None, grantableRolesAtBase = None, rolesAtOther = None, grantableRolesAtOther = None, baseID = None, titleMask = None, blockRoles = None):
        return self.members.UpdateMember(charIDToUpdate, title, divisionID, squadronID, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther, baseID, titleMask, blockRoles)

    def UpdateMembers(self, rows):
        return self.members.UpdateMembers(rows)

    def OnCorporationMemberChanged(self, corporationID, memberID, change):
        self.members.OnCorporationMemberChanged(corporationID, memberID, change)

    def UserIsCEO(self):
        return self.GetCorporation().ceoID == eve.session.charid

    def UserIsActiveCEO(self):
        if eve.session.corprole & const.corpRoleDirector:
            if self.UserIsCEO():
                return 1
        return 0

    def MemberCanCreateCorporation(self):
        return self.members.MemberCanCreateCorporation()

    def GetMyGrantableRoles(self):
        return self.members.GetMyGrantableRoles()

    def CanLeaveCurrentCorporation(self):
        return self.GetCorpRegistry().CanLeaveCurrentCorporation()

    def CanKickOut(self, charID):
        if eve.session.charid != charID and not is_corporation_role_director(eve.session.corprole):
            return 0
        return self.GetCorpRegistry().CanBeKickedOut(charID)

    def KickOut(self, charID, confirm = True):
        if not self.CanKickOut(charID):
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/BaseCorporationUI/CannotKickMember')})
        if not self.ConfirmMemberKickIfActiveWar():
            return
        if not self.ConfirmKickMembers([charID], confirm):
            return
        if charID == eve.session.charid:
            self.sessionMgr.PerformSessionChange('corp.kickself', self.GetCorpRegistry().KickOutMember, charID)
        else:
            return self.GetCorpRegistry().KickOutMember(charID)

    def ConfirmMemberKickIfActiveWar(self):
        activeWars = self.GetActiveCorporationWars()
        if not activeWars:
            return True
        return eve.Message('CorpMemberKickActiveWarConfirm', {'noOfWars': len(activeWars)}, uiconst.YESNO) == uiconst.ID_YES

    def GetActiveCorporationWars(self):
        activeWars = []
        warEntityID = session.allianceid or session.corpid
        for war in sm.GetService('war').GetWars(warEntityID).itervalues():
            if war.mutual:
                continue
            if war.timeFinished is not None:
                continue
            activeWars.append(war)

        return activeWars

    def ConfirmKickMembers(self, charIds, confirm):
        if self.resigning:
            return False
        try:
            self.resigning = True
            if not confirm:
                return True
            if len(charIds) == 1:
                charId = charIds[0]
                if charId == eve.session.charid:
                    if eve.Message('ConfirmQuitCorporation', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
                        return True
                elif eve.Message('ConfirmKickCorpMember', {'member': charId}, uiconst.OKCANCEL) == uiconst.ID_OK:
                    return True
            else:
                charactersString = FormatGenericList((cfg.eveowners.Get(characterId).name for characterId in charIds))
                if eve.Message('ConfirmKickCorpMembers', {'members': charactersString}, uiconst.OKCANCEL) == uiconst.ID_OK:
                    return True
            return False
        except:
            return False
        finally:
            self.resigning = False

    def KickOutMultipleMembers(self, characterIds, confirm = True):
        if session.charid in characterIds:
            raise UserError('CorpCantKickSelfInMultiKick')
        check_is_role_director(session.corprole)
        if not self.ConfirmMemberKickIfActiveWar():
            return
        if not self.ConfirmKickMembers(characterIds, confirm):
            return
        results = self.GetCorpRegistry().KickOutMembers(characterIds)
        kickedCharactersString = FormatGenericList((cfg.eveowners.Get(characterId).name for characterId in results['kicked']))
        if len(results['notKicked']):
            notKickedCharactersString = FormatGenericList((cfg.eveowners.Get(characterId).name for characterId in results['notKicked']))
            notKickedCharactersMessage = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorpKickedMultipleMembersFailed', notKickedMembers=notKickedCharactersString)
        else:
            notKickedCharactersMessage = ''
        eve.Message('CorpKickedMultipleMembersResult', {'kickedMembers': kickedCharactersString,
         'notKickedMessage': notKickedCharactersMessage})

    def GetPendingAutoKicks(self):
        return self.GetCorpRegistry().GetPendingAutoKicks()

    def RemoveAllRoles(self, silent = False):
        if not silent and eve.Message('ConfirmRemoveAllRoles', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        self.UpdateMember(eve.session.charid, None, None, None, 0, 0, 0, 0, 0, 0, 0, 0, None, 0, 1)

    def GetMemberIDsWithMoreThanAvgShares(self):
        return self.GetCorpRegistry().GetMemberIDsWithMoreThanAvgShares()

    def GetMemberIDsByQuery(self, query, includeImplied, searchTitles):
        return self.GetCorpRegistry().GetMemberIDsByQuery(query, includeImplied, searchTitles)

    def ExecuteActions(self, targetIDs, actions):
        return self.members.ExecuteActions(targetIDs, actions)

    def UserBlocksRoles(self):
        return self.members.MemberBlocksRoles()

    def GetTitles(self):
        return self.titles.GetTitles()

    def UpdateTitle(self, titleID, titleName, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther):
        self.titles.UpdateTitle(titleID, titleName, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther)

    def UpdateTitles(self, titles):
        self.titles.UpdateTitles(titles)

    def DeleteTitle(self, titleID):
        self.titles.DeleteTitle(titleID)

    def OnTitleChanged(self, corpID, titleID, change):
        self.titles.OnTitleChanged(corpID, titleID, change)

    def GetSharesByShareholder(self, corpShares = 0):
        return self.shares.GetSharesByShareholder(corpShares)

    def GetShareholders(self):
        return self.shares.GetShareholders()

    def MoveCompanyShares(self, corporationID, toShareholderID, numberOfShares):
        return self.shares.MoveCompanyShares(corporationID, toShareholderID, numberOfShares)

    def MovePrivateShares(self, corporationID, toShareholderID, numberOfShares):
        return self.shares.MovePrivateShares(corporationID, toShareholderID, numberOfShares)

    def OnShareChange(self, shareholderID, corporationID, change):
        self.shares.OnShareChange(shareholderID, corporationID, change)

    @staticmethod
    def DeclareWarAgainst(againstID, warHQ = None):
        return eveMoniker.GetCorpRegistry().DeclareWarAgainst(againstID, warHQ)

    def GetRecentKills(self, num, offset):
        return self.GetCorpRegistry().GetRecentKills(num, offset)

    def GetRecentLosses(self, num, offset):
        return self.GetCorpRegistry().GetRecentLosses(num, offset)

    def OnCorporationApplicationChanged(self, corpID, applicantID, applicationID, newApplication):
        self.applications.OnCorporationApplicationChanged(corpID, applicantID, applicationID, newApplication)

    def GetApplications(self, characterID = -1, forceUpdate = False):
        return self.applications.GetApplications(characterID, forceUpdate)

    def GetApplicationsWithStatus(self, status):
        return self.applications.GetApplicationsWithStatus(status)

    def GetOldApplicationsWithStatus(self, status):
        return self.applications.GetOldApplicationsWithStatus(status)

    def GetMyApplications(self, corporationID = -1, forceUpdate = False):
        return self.applications.GetMyApplications(corporationID, forceUpdate)

    def GetMyApplicationsWithStatus(self, status):
        return self.applications.GetMyApplicationsWithStatus(status)

    def GetMyOpenInvitations(self):
        if not session.corpid:
            return []
        return self.applications.GetMyApplicationsWithStatus([appConst.crpApplicationInvitedByCorporation, appConst.crpApplicationAcceptedByCorporation])

    def GetMyOldApplicationsWithStatus(self, status):
        return self.applications.GetMyOldApplicationsWithStatus(status)

    def InsertApplication(self, corporationID, applicationText):
        return self.applications.InsertApplication(corporationID, applicationText)

    def UpdateApplicationOffer(self, applicationID, characterID, corporationID, applicationText, status, customMessage = '', applicationDateTime = None):
        return self.applications.UpdateApplicationOffer(applicationID, characterID, corporationID, applicationText, status, customMessage, applicationDateTime)

    def GetActiveApplication(self, corpid):
        applications = self.GetMyApplications(corpid)
        for application in applications:
            if application.status in const.crpApplicationActiveStatuses:
                return application

    def ApplyForMembership(self, corpid):
        if eve.session.corpid == corpid:
            raise UserError('CanNotJoinCorpAlreadyAMember', {'corpName': cfg.eveowners.Get(eve.session.corpid).name})
        if self.UserIsCEO():
            raise UserError('CeoCanNotJoinACorp', {'CEOsCorporation': cfg.eveowners.Get(eve.session.corpid).name,
             'otherCorporation': cfg.eveowners.Get(corpid).name})
        application = self.GetActiveApplication(corpid)
        if application is not None:
            wnd = MyCorpApplicationWnd.Open(corpid=application.corporationID, application=application, status=application.status)
            if wnd.ShowModal() == 1:
                retval = wnd.result
            else:
                retval = None
            if retval is not None:
                sm.GetService('corp').UpdateApplicationOffer(application.applicationID, application.characterID, application.corporationID, application.applicationText, retval)
            return
        corporation = self.GetCorporation(corpid)
        wnd = ApplyToCorpWnd.Open(corpid=corpid, corporation=corporation)
        if wnd.ShowModal() == 1:
            retval = wnd.result
        else:
            retval = None
        if retval is not None:
            try:
                return self.InsertApplication(corpid, retval)
            except UserError as e:
                raise

    def CheckApplication(self, retval):
        if retval.has_key('appltext'):
            applicationText = retval['appltext']
            if len(applicationText) > 1000:
                return localization.GetByLabel('UI/Corporations/BaseCorporationUI/ApplicationTextTooLong', length=len(applicationText))
        return ''

    def GetCorpWelcomeMail(self):
        return self.applications.GetCorpWelcomeMail()

    def SetCorpWelcomeMail(self, welcomeMail):
        self.GetCorpRegistry().SetCorpWelcomeMail(welcomeMail)

    def OnCorporationWelcomeMailChanged(self, characterID, changeDate):
        self.applications.SetCorpWelcomeMail(None)

    def OnCorporationRecruitmentAdChanged(self):
        self.recruitment.OnCorporationRecruitmentAdChanged()

    def CreateRecruitmentAd(self, days, typeMask, langMask, description = None, recruiters = (), title = None, hourMask1 = 0, hourMask2 = 0, minSP = 0, otherMask = 0):
        return sm.ProxySvc('corpRecProxy').CreateRecruitmentAd(days, typeMask, langMask, description, recruiters, title, hourMask1, minSP, otherMask)

    def UpdateRecruitmentAd(self, adID, typeMask, langMask, description = None, recruiters = (), title = None, addedDays = 0, hourMask1 = 0, minSP = 0, otherMask = 0):
        return sm.ProxySvc('corpRecProxy').UpdateRecruitmentAd(adID, typeMask, langMask, description, recruiters, title, addedDays, hourMask1, minSP=minSP, otherMask=otherMask)

    def DeleteRecruitmentAd(self, adID):
        return sm.ProxySvc('corpRecProxy').DeleteRecruitmentAd(adID)

    def GetRecruitmentAdsForCorporation(self):
        return self.recruitment.GetRecruitmentAdsForCorporation()

    def GetRecruitmentAdsForCorpID(self, corpID):
        return sm.ProxySvc('corpRecProxy').GetRecruitmentAdsByCorpID(corpID)

    def GetRecruiters(self, adID):
        return sm.ProxySvc('corpRecProxy').GetRecruiters(adID)

    def GetRecruitmentAdsByCriteria(self, typeMask, langMask, excludeAlliances, excludeFriendlyFire, spRestriction, minMembers, maxMembers, maxISKTaxRate, maxLPTaxRate, searchTimeMask, otherMask):
        return sm.ProxySvc('corpRecProxy').SearchCorpAds(typeMask, langMask, excludeAlliances, excludeFriendlyFire, spRestriction, minMembers, maxMembers, maxISKTaxRate, maxLPTaxRate, searchTimeMask, otherMask)

    def GetAdFromCorpAndAdID(self, corpID, adID):
        return sm.ProxySvc('corpRecProxy').GetRecruitmentAd(corpID, adID)

    def GetDivisionalRoles(self):
        if self.__divisionalRoles is None:
            roles = self.GetHierarchicalRoles()
            divisions = roles.divisions
            self.__divisionalRoles = []
            for divisionNumber, division in divisions.iteritems():
                for roleID in division.roles.itervalues():
                    self.__divisionalRoles.append(roleID)

        return self.__divisionalRoles

    def GetHierarchicalRoles(self):
        if self.__hierarchicalRoles is None:
            divisionNames = self.GetDivisionNames()
            divisions = {}
            digits = ('1', '2', '3', '4', '5', '6', '7')
            for roleID, role in iter_roles():
                lastCharacter = role.roleName[-1:]
                if lastCharacter in digits:
                    divisionID = int(lastCharacter)
                    if divisionID not in divisions:
                        divisions[divisionID] = Row(['name', 'roles'], [divisionNames[divisionID], {}])
                    divisions[divisionID].roles[role.roleName[:-1]] = roleID

            self.__hierarchicalRoles = Row(['divisions'], [divisions])
        return self.__hierarchicalRoles

    def GetRoleGroupings(self, forTitles = 0):
        roleGroups = get_corporation_role_groups()
        divisionNames = self.GetDivisionNames()
        header = None
        if roleGroups:
            header = ['roleGroupID'] + CORP_ROLE_GROUPS_ATTRS + ['columns']
        lines = []
        for groupID, roleGroup in roleGroups.iteritems():
            line = [groupID]
            for columnName in header:
                if columnName == 'columns' or columnName == 'roleGroupID':
                    continue
                s = getattr(roleGroup, columnName)
                line.append(s)

            columns = []
            if roleGroup.isDivisional:
                rolesByDivisions = {}
                isAccount = False
                for roleID, role in iter_roles():
                    if roleID & roleGroup.roleMask == roleID:
                        divisionID = self.get_division_id(role)
                        if divisionID not in rolesByDivisions:
                            rolesByDivisions[divisionID] = []
                        desc = self.get_division_role_description(role)
                        if role.roleName.startswith('roleAccount'):
                            isAccount = True
                            desc = ''
                        localizedRoleName = get_role_name(roleID, role)
                        localizedRoleDescription = get_role_description(roleID, role)
                        _role = Role(roleID, role.roleName, localizedRoleName, localizedRoleDescription)
                        rolesByDivisions[divisionID].append([role.roleName, [desc, _role]])

                for divisionID in rolesByDivisions.keys():
                    subcolumns = []
                    rolesByDivision = rolesByDivisions[divisionID]
                    rolesByDivision.sort(lambda a, b: -(a[1][0].upper() < b[1][0].upper()))
                    for roleName, descAndRole in rolesByDivision:
                        subcolumns.append(descAndRole)

                    add = [0, 7][isAccount]
                    name = divisionNames.get(divisionID + add, None)
                    columns.append([name, subcolumns])

            else:
                for roleID, role in sorted(iter_roles(), key=lambda r: get_role_name(r[0], r[1]).upper()):
                    if forTitles and roleID == const.corpRoleDirector:
                        continue
                    if roleID & roleGroup.roleMask == roleID:
                        localizedRoleName = get_role_name(roleID, role)
                        localizedRoleDescription = get_role_description(roleID, role)
                        _role = Role(roleID, role.roleName, localizedRoleName, localizedRoleDescription)
                        columns.append([localizedRoleName, [['', _role]]])

            line.append(columns)
            lines.append(line)

        if forTitles:
            self.__roleGroupingsForTitles = IndexRowset(header, lines, 'roleGroupID')
            return self.__roleGroupingsForTitles
        else:
            self.__roleGroupings = IndexRowset(header, lines, 'roleGroupID')
            return self.__roleGroupings

    def get_division_id(self, role):
        return int(role.roleName[-1:])

    def get_division_role_description(self, role):
        if -1 != role.roleName.find('CanTake'):
            return localization.GetByLabel('UI/Corporations/BaseCorporationUI/Take')
        if -1 != role.roleName.find('CanQuery'):
            return localization.GetByLabel('UI/Corporations/BaseCorporationUI/Query')
        return ''

    def GetLocationalRoles(self):
        return self.__locationalRoles

    def PayoutDividend(self, payShareholders, payoutAmount):
        return self.GetCorpRegistry().PayoutDividend(payShareholders, payoutAmount)

    def UpdateDivisionNames(self, divisions1, divisions2, divisions3, divisions4, divisions5, divisions6, divisions7, walletDivision1, walletDivision2, walletDivision3, walletDivision4, walletDivision5, walletDivision6, walletDivision7):
        res = self.GetCorpRegistry().UpdateDivisionNames(divisions1, divisions2, divisions3, divisions4, divisions5, divisions6, divisions7, walletDivision1, walletDivision2, walletDivision3, walletDivision4, walletDivision5, walletDivision6, walletDivision7)
        self.__hierarchicalRoles = None
        self.__roleGroupings = None
        self.__roleGroupingsForTitles = None
        return res

    def __ResignFromCEO(self, newCeoID = None):
        if newCeoID is None and eve.session.allianceid is not None and len(self.members.GetMembers()) < 2:
            raise UserError('CanNotDestroyCorpInAlliance')
        return self.GetCorpRegistry().ResignFromCEO(newCeoID)

    def ResignFromCEO(self):
        if eveCfg.InSpace():
            eve.Message('CrpCanNotChangeCorpInSpace')
            return
        if not self.UserIsCEO():
            eve.Message('OnlyCEOCanResign')
            return
        memberCount = len(self.GetMembers())
        if memberCount <= 1:
            if eve.Message('CrpDestroyCorpWarning', {}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
                return
        else:
            potentialCEOs = len(self.members.GetNumberOfPotentialCEOs())
            if potentialCEOs > 0:
                if eve.Message('AskResignAsCEO', {'memberCount': potentialCEOs}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
                    return
            elif eve.Message('CrpDestroyNonEmptyCorpWarning', {}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
                return
        res = self.sessionMgr.PerformSessionChange('corp.resignceo', self.__ResignFromCEO)
        if res is None:
            return
        owners = []
        for charID in res:
            if charID not in owners:
                owners.append(charID)

        if len(owners):
            cfg.eveowners.Prime(owners)
        tmplist = []
        for charID in res:
            owner = cfg.eveowners.Get(charID)
            tmplist.append((owner.name, charID, owner.typeID))

        newCEO = uix.ListWnd(tmplist, 'character', localization.GetByLabel('UI/Corporations/BaseCorporationUI/SelectReplacementCEO'), localization.GetByLabel('UI/Corporations/BaseCorporationUI/SelectReplacementCEOText'), 1)
        if newCEO:
            newCeoID = newCEO[1]
            eve.session.ResetSessionChangeTimer('Retrying with selected alternate CEO')
            self.sessionMgr.PerformSessionChange('corp.resignceo', self.__ResignFromCEO, newCeoID)

    def GetInfoWindowDataForChar(self, charID, acceptBlank = 0):
        data = self.GetCorpRegistry().GetInfoWindowDataForChar(charID)
        if not acceptBlank:
            if data.title1 is not None and len(data.title1) == 0:
                data.title1 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=1)
            if data.title2 is not None and len(data.title2) == 0:
                data.title2 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=2)
            if data.title3 is not None and len(data.title3) == 0:
                data.title3 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=3)
            if data.title4 is not None and len(data.title4) == 0:
                data.title4 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=4)
            if data.title5 is not None and len(data.title5) == 0:
                data.title5 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=5)
            if data.title6 is not None and len(data.title6) == 0:
                data.title6 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=6)
            if data.title7 is not None and len(data.title7) == 0:
                data.title7 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=7)
            if data.title8 is not None and len(data.title8) == 0:
                data.title8 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=8)
            if data.title9 is not None and len(data.title9) == 0:
                data.title9 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=9)
            if data.title10 is not None and len(data.title10) == 0:
                data.title10 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=10)
            if data.title11 is not None and len(data.title11) == 0:
                data.title11 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=11)
            if data.title12 is not None and len(data.title12) == 0:
                data.title12 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=12)
            if data.title13 is not None and len(data.title13) == 0:
                data.title13 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=13)
            if data.title14 is not None and len(data.title14) == 0:
                data.title14 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=14)
            if data.title15 is not None and len(data.title15) == 0:
                data.title15 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=15)
            if data.title16 is not None and len(data.title16) == 0:
                data.title16 = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=16)
        return data

    def GetMemberTrackingInfo(self):
        if eve.session.corprole & const.corpRoleDirector:
            return self.GetCorpRegistry().GetMemberTrackingInfo()
        else:
            return self.GetCorpRegistry().GetMemberTrackingInfoSimple()

    def GetBulletins(self, isAlliance = False):
        if isAlliance:
            bulletins = sm.GetService('alliance').GetAllianceBulletins()
        else:
            bulletins = self.GetCorpBulletins()
        bulletinsList = []
        for dbrow in bulletins:
            b = utillib.KeyVal(dbrow)
            sortKey = (b.sortOrder, -b.editDateTime)
            bulletinsList.append((sortKey, b))

        bulletinsList = SortListOfTuples(bulletinsList)
        return bulletinsList

    def GetCorpBulletins(self):
        if self.bulletins is None or self.bulletinsTimestamp < blue.os.GetWallclockTime():
            self.bulletins = self.GetCorpRegistry().GetBulletins()
            self.bulletinsTimestamp = blue.os.GetWallclockTime() + 15 * const.MIN
        return self.bulletins

    def GetBulletinEntries(self, isAlliance = False):
        bulletins = self.GetBulletins(isAlliance)
        canEditCorp = const.corpRoleChatManager & session.corprole == const.corpRoleChatManager
        isContentControlled = IsContentComplianceControlSystemActive(sm.GetService('machoNet'))
        se = []
        for bulletin in bulletins:
            postedBy = localization.GetByLabel('UI/Corporations/BaseCorporationUI/BulletinPostedBy', charID=bulletin.editCharacterID, infoLinkData=('showinfo', cfg.eveowners.Get(bulletin.editCharacterID).typeID, bulletin.editCharacterID), postTime=bulletin.editDateTime)
            text = '<fontsize=18><b>%s</b></fontsize><br>%s' % (bulletin.title, bulletin.body)
            editLinks = ''
            if canEditCorp and not isContentControlled:
                editTag = '<a href="localsvc:method=EditBulletin&id=%s">' % bulletin.bulletinID
                delTag = '<a href="localsvc:method=DeleteBulletin&id=%s">' % bulletin.bulletinID
                editLinks = localization.GetByLabel('UI/Corporations/BaseCorporationUI/BulletinEditLinks', startEditTag=editTag, endEditTag='</a>', startDelTag=delTag, endDelTag='</a>')
            se.append(GetFromClass(BulletinEntry, {'text': text,
             'postedBy': postedBy + editLinks}))

        return se

    def GetBulletin(self, bulletinID):

        def FindBulletin(id, bulletins):
            bulletin = None
            for b in bulletins:
                if b.bulletinID == id:
                    bulletin = b
                    break

            return bulletin

        bulletin = None
        if bulletinID is not None:
            ownerID = session.corpid
            bulletins = self.GetBulletins()
            bulletin = FindBulletin(bulletinID, bulletins)
            if bulletin is None and session.allianceid:
                bulletins = self.GetBulletins(isAlliance=True)
                bulletin = FindBulletin(bulletinID, bulletins)
                ownerID = session.allianceid
            if bulletin is None:
                raise UserError('CorpBulletinNotFound')
        return bulletin

    def EditBulletin(self, id, isAlliance = False):
        if not const.corpRoleChatManager & eve.session.corprole == const.corpRoleChatManager:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/BaseCorporationUI/DoNotHaveRole', roleName=localization.GetByMessageID(FSD_COMMUNICATIONS_OFFICER_ROLE_ID))})
        bulletin = self.GetBulletin(id)
        if bulletin and bulletin.ownerID == session.allianceid:
            isAlliance = True
        EditCorpBulletin.CloseIfOpen()
        EditCorpBulletin.Open(isAlliance=isAlliance, bulletin=bulletin)

    def DeleteBulletin(self, id):
        if not const.corpRoleChatManager & eve.session.corprole == const.corpRoleChatManager:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/BaseCorporationUI/DoNotHaveRole', roleName=localization.GetByMessageID(FSD_COMMUNICATIONS_OFFICER_ROLE_ID))})
        if uicore.Message('ConfirmDeleteBulletin', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        bulletin = self.GetBulletin(id)
        if bulletin.ownerID == session.allianceid:
            sm.GetService('alliance').GetMoniker().DeleteBulletin(id)
        else:
            self.GetCorpRegistry().DeleteBulletin(id)
        self.RefreshBulletins()

    def AddBulletin(self, title, body, isAlliance):
        if len(self.GetBulletins(isAlliance)) >= MAX_NUM_BULLETINS:
            eve.Message('CorpTooManyBulletins')
            return
        if isAlliance:
            sm.GetService('alliance').GetMoniker().AddBulletin(title, body)
        else:
            self.GetCorpRegistry().AddBulletin(title, body)
        self.RefreshBulletins()

    def UpdateBulletin(self, bulletinID, title, body, isAlliance, editDateTime = None):
        try:
            if isAlliance:
                sm.GetService('alliance').GetMoniker().AddBulletin(title, body, bulletinID=bulletinID, editDateTime=editDateTime)
            else:
                self.GetCorpRegistry().AddBulletin(title, body, bulletinID=bulletinID, editDateTime=editDateTime)
        except UserError as e:
            eve.Message(e.msg, e.dict)

        self.RefreshBulletins()

    def UpdateBulletinOrder(self, newOrder):
        self.GetCorpRegistry().UpdateBulletinOrder(newOrder)
        self.bulletinsTimestamp = 0

    def RefreshBulletins(self):
        self.bulletins = None
        sm.GetService('alliance').bulletins = None
        sm.GetService('corpui').ResetWindow(1)

    def GetContactList(self):
        if idCheckers.IsNPC(session.corpid):
            return {}
        return self.GetCorpRegistry().GetCorporateContacts()

    def AddCorporateContact(self, contactID, relationshipID):
        self.GetCorpRegistry().AddCorporateContact(contactID, relationshipID)

    def EditCorporateContact(self, contactID, relationshipID):
        self.GetCorpRegistry().EditCorporateContact(contactID, relationshipID)

    def RemoveCorporateContacts(self, contactIDs):
        self.GetCorpRegistry().RemoveCorporateContacts(contactIDs)

    def EditContactsRelationshipID(self, contactIDs, relationshipID):
        self.GetCorpRegistry().EditContactsRelationshipID(contactIDs, relationshipID)

    def GetLabels(self):
        return self.GetCorpRegistry().GetLabels()

    def CreateLabel(self, name, color = 0):
        return self.GetCorpRegistry().CreateLabel(name, color)

    def DeleteLabel(self, labelID):
        self.GetCorpRegistry().DeleteLabel(labelID)

    def EditLabel(self, labelID, name = None, color = None):
        self.GetCorpRegistry().EditLabel(labelID, name, color)

    def AssignLabels(self, contactIDs, labelMask):
        self.GetCorpRegistry().AssignLabels(contactIDs, labelMask)

    def RemoveLabels(self, contactIDs, labelMask):
        self.GetCorpRegistry().RemoveLabels(contactIDs, labelMask)

    def GetAllyBaseCost(self):
        try:
            lastRefreshTime = self.allyBaseCost[1]
            if lastRefreshTime + 1 * const.MIN < blue.os.GetWallclockTime():
                self.RefreshAllyBaseCost()
        except AttributeError:
            self.RefreshAllyBaseCost()

        return self.allyBaseCost[0]

    def RefreshAllyBaseCost(self):
        self.allyBaseCost = (self.GetCorpRegistry().CharGetAllyBaseCost(), blue.os.GetWallclockTime())

    def LogCorpRecruitmentEvent(self, columnNames, *args):
        if not sm.GetService('machoNet').GetGlobalConfig().get('disableCorpRecruitmentLogging', 0):
            uthread.new(self.DoLogCorpRecruitmentEvent, columnNames, *args)

    def DoLogCorpRecruitmentEvent(self, columnNames, *args):
        try:
            sm.ProxySvc('eventLog').LogClientEvent('corpRecruitment', columnNames, *args)
        except UserError:
            pass

    def OpenCorpAdInNewWindow(self, corpID, adID, *args):
        corpAd = self.GetAdFromCorpAndAdID(corpID, adID)
        if not corpAd:
            return
        ads = [(None, corpAd)]
        dataList = self.GetRecruitementEntryDataList(ads, None, None, None, {})
        wnd = CorpRecruitmentAdStandaloneWindow.GetIfOpen(windowID='corAd_%s' % adID)
        if wnd and not wnd.destroyed:
            wnd.Maximize()
        else:
            CorpRecruitmentAdStandaloneWindow(windowID='corAd_%s' % adID, data=dataList[0])

    def GetRecruitementEntryDataList(self, ads, wantMask, wantLanguageMask, otherMask, expandedAd, *args):
        dataList = []
        allIDsToPrime = set()
        allCorpIDs = set()
        warSvc = sm.GetService('war')
        corpWarsByCorpID = defaultdict(set)
        warEntitiesToPrime = {advert.corporationID for _, advert in ads}
        warEntitiesToPrime.update({advert.allianceID for _, advert in ads})
        warEntitiesToPrime = filter(None, warEntitiesToPrime)
        warSvc.PrimeWarsForOwners(warEntitiesToPrime)
        for grade, advert in ads:
            allIDsToPrime.add(advert.corporationID)
            allCorpIDs.add(advert.corporationID)
            regWars = warSvc.GetWars(advert.corporationID).values()
            if advert.allianceID:
                regWars.extend(warSvc.GetWars(advert.allianceID).values())
            facWars = []
            warFactionID = sm.StartService('facwar').GetCorporationWarFactionID(advert.corporationID)
            if warFactionID:
                facWars = sm.GetService('facwar').GetFactionWars(advert.corporationID).values()
            for wars in (regWars, facWars):
                for war in wars:
                    for corpAtWar in (war.declaredByID, war.againstID):
                        if corpAtWar not in (advert.corporationID, advert.allianceID, warFactionID):
                            corpWarsByCorpID[advert.corporationID].add(corpAtWar)

                    allIDsToPrime.add(war.declaredByID)
                    allIDsToPrime.add(war.againstID)

            if advert.allianceID:
                allIDsToPrime.add(advert.allianceID)

        cfg.eveowners.Prime(allIDsToPrime)
        corpService = sm.GetService('corp')
        aggressionSettingsByCorpID = corpService.GetAggressionSettingsForCorps(allCorpIDs)
        for grade, advert in ads:
            atWarWith = corpWarsByCorpID.get(advert.corporationID, set())
            aggressionSettings = aggressionSettingsByCorpID.get(advert.corporationID, AggressionSettings.CreateDefaultForCorp(advert.corporationID))
            friendlyFire = corpService.GetCorpFriendlyFireStatus(aggressionSettings)
            data = self.GetRecruitmenEntryData(advert, wantMask, wantLanguageMask, otherMask, expandedAd, atWarWith.copy(), grade, friendlyFire)
            dataList.append(data)

        return dataList

    def GetRecruitmenEntryData(self, advert, wantMask, wantLanguageMask, otherMask, expandedAd, atWarWith, grade, friendlyFireStatus, *args):
        data = utillib.KeyVal()
        data.advert = advert
        data.createDateTime = advert.createDateTime
        data.corporationID = advert.corporationID
        data.allianceID = advert.allianceID
        data.channelID = advert.channelID
        data.corpView = False
        data.grade = grade
        data.minSP = advert.minSP
        data.memberCount = advert.memberCount
        data.searchMask = wantMask
        data.otherMask = otherMask
        data.searchLangMask = wantLanguageMask
        data.expandedView = expandedAd.get(data.corpView, None) == advert.adID
        data.standaloneMode = False
        data.adTitle = advert.title
        data.timeZoneMask1 = advert.hourMask1
        data.warOpponents = atWarWith
        if data.expandedView:
            data.recruiters = self.GetRecruiters(advert.adID)
        data.friendlyFireStatus = friendlyFireStatus
        return data

    def InviteToJoinCorp(self, charID):
        if eve.Message('ConfirmSendInviteToJoinCorp', {'charID': charID}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        self.GetCorpRegistry().InsertInvitation(charID)

    def GetStructureReinforceDefault(self):
        return self.GetCorpRegistry().GetStructureReinforceDefault()

    def SetStructureReinforceDefault(self, reinforceHour):
        self.GetCorpRegistry().SetStructureReinforceDefault(reinforceHour)
        uicore.Message('CustomNotify', {'notify': GetByLabel('UI/StructureBrowser/DefaultReinforcementSuccessfullyUpdated')})
