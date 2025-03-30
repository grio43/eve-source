#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\enlistmentUtil.py
import appConst
from factionwarfare.client.enrollmentConst import warningByWarningID
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR, FACTION_ID_TO_FLAT_ICON
from localization import GetByLabel
import carbonui.const as uiconst
ANIM_DURATION = 0.75
BG_MAP_OPACITY = 0.3
mottoPathByFactionID = {appConst.factionAmarrEmpire: 'UI/FactionWarfare/Enlistment/MottoAmarr',
 appConst.factionCaldariState: 'UI/FactionWarfare/Enlistment/MottoCaldari',
 appConst.factionGallenteFederation: 'UI/FactionWarfare/Enlistment/MottoGallente',
 appConst.factionMinmatarRepublic: 'UI/FactionWarfare/Enlistment/MottoMinmatar',
 appConst.factionAngelCartel: 'UI/FactionWarfare/Enlistment/MottoAngels',
 appConst.factionGuristasPirates: 'UI/FactionWarfare/Enlistment/MottoGuristas'}

def GetFactionColor(factionID):
    return FACTION_ID_TO_COLOR.get(factionID, None)


_FACTION_ID_TO_FLAT_ICON = {appConst.factionAmarrEmpire: 'res:/UI/Texture/Classes/Enlistment/logos/amarr.png',
 appConst.factionCaldariState: 'res:/UI/Texture/Classes/Enlistment/logos/caldari.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/Enlistment/logos/gallente.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/Enlistment/logos/minmatar.png',
 appConst.factionAngelCartel: 'res:/UI/Texture/Classes/Enlistment/logos/angels.png',
 appConst.factionGuristasPirates: 'res:/UI/Texture/Classes/Enlistment/logos/guristas.png'}

def GetFactionIcon(factionID):
    return _FACTION_ID_TO_FLAT_ICON.get(factionID, '')


def GetFactionIconSmall(factionID):
    return FACTION_ID_TO_FLAT_ICON.get(factionID, '')


INFO_1 = 'INFO_1'
INFO_2 = 'INFO_2'
INFO_3 = 'INFO_3'
INFO_4 = 'INFO_4'
INFO_ICONS = [(INFO_1, 'res:/UI/Texture/Classes/Enlistment/infoIcons/CallToArms.png', 'UI/FactionWarfare/Enlistment/CallToArms'),
 (INFO_2, 'res:/UI/Texture/Classes/Enlistment/infoIcons/Warning.png', 'UI/FactionWarfare/Enlistment/Warnings'),
 (INFO_3, 'res:/UI/Texture/Classes/Enlistment/infoIcons/Benefits.png', 'UI/FactionWarfare/Enlistment/Benefits'),
 (INFO_4, 'res:/UI/Texture/Classes/Enlistment/infoIcons/AtWar.png', 'UI/FactionWarfare/Enlistment/Conflict')]
INFO_BY_FACTION_ID = {appConst.factionAmarrEmpire: {INFO_1: 'UI/FactionWarfare/Enlistment/DetailsAmarrInfo1',
                               INFO_2: 'UI/FactionWarfare/Enlistment/DetailsAmarrInfo2',
                               INFO_3: 'UI/FactionWarfare/Enlistment/DetailsAmarrInfo3',
                               INFO_4: 'UI/FactionWarfare/Enlistment/DetailsAmarrInfo4'},
 appConst.factionCaldariState: {INFO_1: 'UI/FactionWarfare/Enlistment/DetailsCaldariInfo1',
                                INFO_2: 'UI/FactionWarfare/Enlistment/DetailsCaldariInfo2',
                                INFO_3: 'UI/FactionWarfare/Enlistment/DetailsCaldariInfo3',
                                INFO_4: 'UI/FactionWarfare/Enlistment/DetailsCaldariInfo4'},
 appConst.factionGallenteFederation: {INFO_1: 'UI/FactionWarfare/Enlistment/DetailsGallenteInfo1',
                                      INFO_2: 'UI/FactionWarfare/Enlistment/DetailsGallenteInfo2',
                                      INFO_3: 'UI/FactionWarfare/Enlistment/DetailsGallenteInfo3',
                                      INFO_4: 'UI/FactionWarfare/Enlistment/DetailsGallenteInfo4'},
 appConst.factionMinmatarRepublic: {INFO_1: 'UI/FactionWarfare/Enlistment/DetailsMinmatarInfo1',
                                    INFO_2: 'UI/FactionWarfare/Enlistment/DetailsMinmatarInfo2',
                                    INFO_3: 'UI/FactionWarfare/Enlistment/DetailsMinmatarInfo3',
                                    INFO_4: 'UI/FactionWarfare/Enlistment/DetailsMinmatarInfo4'},
 appConst.factionAngelCartel: {INFO_1: 'UI/FactionWarfare/Enlistment/DetailsAngelsInfo1',
                               INFO_2: 'UI/FactionWarfare/Enlistment/DetailsAngelsInfo2',
                               INFO_3: 'UI/FactionWarfare/Enlistment/DetailsAngelsInfo3',
                               INFO_4: 'UI/FactionWarfare/Enlistment/DetailsAngelsInfo4'},
 appConst.factionGuristasPirates: {INFO_1: 'UI/FactionWarfare/Enlistment/DetailsGuristasInfo1',
                                   INFO_2: 'UI/FactionWarfare/Enlistment/DetailsGuristasInfo2',
                                   INFO_3: 'UI/FactionWarfare/Enlistment/DetailsGuristasInfo3',
                                   INFO_4: 'UI/FactionWarfare/Enlistment/DetailsGuristasInfo4'}}

def GetInfoLabelPath(factionID, infoConst):
    infoLabels = INFO_BY_FACTION_ID.get(factionID, None)
    if not infoLabels:
        return ''
    return infoLabels.get(infoConst, None)


_BG_BY_FACTIONID = {appConst.factionAmarrEmpire: 'res:/UI/Texture/Classes/Enlistment/backgrounds/Amarr.png',
 appConst.factionCaldariState: 'res:/UI/Texture/Classes/Enlistment/backgrounds/Caldari.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/Enlistment/backgrounds/Gallente.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/Enlistment/backgrounds/Minmatar.png',
 appConst.factionAngelCartel: 'res:/UI/Texture/Classes/Enlistment/backgrounds/Angels.png',
 appConst.factionGuristasPirates: 'res:/UI/Texture/Classes/Enlistment/backgrounds/Guristas.png'}

def GetBgTexturePath(factionID):
    return _BG_BY_FACTIONID.get(factionID, None)


_MAP_BG_BY_FACTIONID = {appConst.factionAmarrEmpire: 'res:/UI/Texture/Classes/Enlistment/backgrounds/amarrMap.png',
 appConst.factionCaldariState: 'res:/UI/Texture/Classes/Enlistment/backgrounds/caldariMap.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/Enlistment/backgrounds/gallenteMap.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/Enlistment/backgrounds/minmatarMap.png',
 appConst.factionAngelCartel: 'res:/UI/Texture/Classes/Enlistment/backgrounds/angelsMap.png',
 appConst.factionGuristasPirates: 'res:/UI/Texture/Classes/Enlistment/backgrounds/guristasMap.png'}

def GetMapBgTexturePath(factionID):
    return _MAP_BG_BY_FACTIONID.get(factionID, None)


JOB_PROVIDER = 'factional_warfare_enlistment'

def RetireAlliance(*args):
    factionID = sm.GetService('facwar').GetCorpFactionalWarStatus().factionID
    ret = eve.Message('CustomQuestion', {'header': GetByLabel('UI/FactionWarfare/ConfirmRetireHeader'),
     'question': GetByLabel('UI/FactionWarfare/ConfirmRetire', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
    if ret == uiconst.ID_YES:
        sm.GetService('facwar').LeaveFactionAsAlliance(factionID)


def RetireCorp(*args):
    factionID = sm.GetService('facwar').GetCorpFactionalWarStatus().factionID
    ret = eve.Message('CustomQuestion', {'header': GetByLabel('UI/FactionWarfare/ConfirmRetireHeader'),
     'question': GetByLabel('UI/FactionWarfare/ConfirmRetire', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
    if ret == uiconst.ID_YES:
        sm.GetService('facwar').LeaveFactionAsCorporation(factionID)


def Retire(*args):
    if ConfirmCharacterRetire():
        corp = sm.GetService('corp')
        corp.KickOut(session.charid, confirm=False)
        sm.GetService('objectCaching').InvalidateCachedMethodCall('corporationSvc', 'GetEmploymentRecord', session.charid)


def RemoveDirectEnlistment(*args):
    if ConfirmCharacterRetire():
        sm.GetService('fwEnlistmentSvc').RemoveMyDirectEnlistment()


def CancelRetirement(*args):
    factionID = sm.GetService('facwar').GetCorpFactionalWarStatus().factionID
    ret = eve.Message('CustomQuestion', {'header': GetByLabel('UI/FactionWarfare/ConfirmCancelRetirementHeader'),
     'question': GetByLabel('UI/FactionWarfare/ConfirmCancelRetirementHeader', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
    if ret == uiconst.ID_YES:
        if session.allianceid:
            sm.GetService('facwar').WithdrawLeaveFactionAsAlliance(factionID)
        else:
            sm.GetService('facwar').WithdrawLeaveFactionAsCorporation(factionID)


def ConfirmCharacterRetire():
    factionID = session.warfactionid
    ret = eve.Message('CustomQuestion', {'header': GetByLabel('UI/FactionWarfare/ConfirmRetireHeader'),
     'question': GetByLabel('UI/FactionWarfare/ConfirmRetire', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
    return ret == uiconst.ID_YES


def CancelApplication(*args):
    factionID = sm.GetService('facwar').GetCorpFactionalWarStatus().factionID
    msgArgs = {'header': GetByLabel('UI/FactionWarfare/ConfirmCancelApplicationHeader'),
     'question': GetByLabel('UI/FactionWarfare/ConfirmCancelApplicationAlliance', factionName=cfg.eveowners.Get(factionID).name)}
    ret = eve.Message('CustomQuestion', msgArgs, uiconst.YESNO)
    if ret == uiconst.ID_YES:
        if session.allianceid:
            sm.GetService('facwar').WithdrawJoinFactionAsAlliance(factionID)
        else:
            sm.GetService('facwar').WithdrawJoinFactionAsCorporation(factionID)


def GetTextForWarning(warningValue):
    labelPath, _ = warningByWarningID.get(warningValue, ('', ''))
    text = ''
    if labelPath:
        text = GetByLabel(labelPath)
    return text


def GetHintForWarning(warningValue):
    _, hintPath = warningByWarningID.get(warningValue, ('', ''))
    hint = ''
    if hintPath:
        hint = GetByLabel(hintPath)
    return hint
