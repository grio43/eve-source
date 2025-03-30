#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\voting\voting.py
import localization
MAX_CLOSED_VOTES_FETCHED = 20
MAX_OPEN_VOTES = 1000
MAX_VOTE_DURATION = 30
MAX_VOTE_OPTIONS = 50
VOTECASE_STATUS_OPEN = 2
VOTECASE_STATUS_CLOSED = 1
VOTECASE_STATUS_ALL = 0
SANCTIONED_ACTION_STATUS_EXPIRED = 0
SANCTIONED_ACTION_STATUS_IN_EFFECT = 1
SANCTIONED_ACTION_STATUS_NOT_IN_EFFECT = 2
voteCEO = 0
voteWar = 1
voteShares = 2
voteKickMember = 3
voteGeneral = 4
voteItemLockdown = 5
voteItemUnlock = 6
voteTypeStrings = {voteCEO: 'New CEO',
 voteWar: 'Declaration of War',
 voteShares: 'Creation of shares',
 voteKickMember: 'Expel member',
 voteGeneral: 'General vote',
 voteItemLockdown: 'Lockdown Blueprint',
 voteItemUnlock: 'Unlock Blueprint'}

def GetVoteText(vote):
    voteText = vote.voteCaseText
    if vote.voteType == voteShares:
        voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeCreateShares')
    elif vote.voteType == voteWar:
        voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeDeclareWar')
    elif vote.voteType == voteItemLockdown:
        voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeLockBlueprint')
    elif vote.voteType == voteItemUnlock:
        voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeUnlockBlueprint')
    elif vote.voteType == voteKickMember:
        voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeKickMember')
    elif vote.voteType == voteGeneral:
        voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeGeneral')
    return voteText


def GetVoteOptionText(option, vote):
    optionText = option.optionText
    if vote.voteType == voteShares:
        if option.optionID == 0:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CreateShares', shares=option.parameter)
        else:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DoNotCreateShares')
    elif vote.voteType == voteWar:
        if option.optionID == 0:
            victimName = cfg.eveowners.Get(option.parameter).name
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DeclareWarAgainst', Name=victimName)
        else:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontDeclareWar')
    elif vote.voteType == voteItemLockdown:
        if option.optionID == 0:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockdownItem', item=option.parameter1)
        else:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontLockdownItem', item=option.parameter1)
    elif vote.voteType == voteItemUnlock:
        if option.optionID == 0:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/UnlockItem', item=option.parameter1)
        else:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontUnlockItem', item=option.parameter1)
    elif vote.voteType == voteKickMember:
        if option.optionID == 0:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ExpelFromCorporation', char=option.parameter)
        else:
            optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontExpelCorporationMember')
    elif vote.voteType == voteGeneral:
        pass
    return optionText
