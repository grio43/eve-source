#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\client\jump_checks.py
import carbonui.const as uiconst
from eveuniverse.security import securityClassLowSec, securityClassHighSec

def check_cancel_stargate_jump(stargateID, to_solar_system_id, exclude_checks = None):
    exclude_checks = exclude_checks or []
    for key, should_cancel_jump in _stargate_jump_checks.iteritems():
        if key not in exclude_checks and should_cancel_jump(stargateID, to_solar_system_id):
            return True

    return False


def add_stargate_jump_check(key, callback):
    _stargate_jump_checks[key] = callback


def remove_stargate_jump_check(key):
    _stargate_jump_checks.pop(key, None)


def check_illicit_goods(stargateID, to_solar_system_id):
    faction_service = sm.GetService('faction')
    from_faction_id = faction_service.GetFactionOfSolarSystem(session.solarsystemid)
    to_faction_id = faction_service.GetFactionOfSolarSystem(to_solar_system_id)
    if to_faction_id and from_faction_id != to_faction_id:
        stuff = sm.GetService('menu').GetIllegality(session.shipid, solarSystemID=to_solar_system_id)
        faction_name = cfg.eveowners.Get(to_faction_id).name
        if stuff and eve.Message('ConfirmJumpWithIllicitGoods', {'faction': faction_name,
         'stuff': stuff}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return True
    return False


def check_sec_status(stargateID, to_solar_system_id):
    security_service = sm.GetService('securitySvc')
    to_sec_class = security_service.get_modified_security_class(to_solar_system_id)
    from_sec_class = security_service.get_modified_security_class(session.solarsystemid)
    if to_sec_class <= securityClassLowSec:
        security_level = security_service.get_modified_security_level(to_solar_system_id)
        if from_sec_class >= securityClassHighSec and eve.Message('ConfirmJumpToUnsafeSS', {'ss': security_level}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return True
    elif from_sec_class <= securityClassLowSec and sm.GetService('crimewatchSvc').IsCriminal(session.charid):
        if eve.Message('JumpCriminalConfirm', {}, uiconst.YESNO) != uiconst.ID_YES:
            return True
    return False


def check_triglavian(stargateID, to_solar_system_id):
    if to_solar_system_id not in sm.GetService('map').GetTriglavianMinorVictorySystems():
        return False
    if settings.user.suppress.Get('suppress.ConfirmJumpToTriglavianSS', None):
        return False
    user_input = eve.Message('ConfirmJumpToTriglavianSS', params={'customicon': 'res:/ui/Texture/WindowIcons/triglavians.png'}, buttons=uiconst.OKCANCEL, suppress=uiconst.ID_OK)
    if user_input != uiconst.ID_OK:
        settings.user.suppress.Set('suppress.ConfirmJumpToTriglavianSS', None)
    return user_input != uiconst.ID_OK


def check_edencom(stargateID, to_solar_system_id):
    if to_solar_system_id not in sm.GetService('map').GetEdencomAvoidanceSystems():
        return False
    if settings.user.suppress.Get('suppress.ConfirmJumpToEdencomSS', None):
        return False
    user_input = eve.Message('ConfirmJumpToEdencomSS', buttons=uiconst.OKCANCEL, suppress=uiconst.ID_OK)
    if user_input != uiconst.ID_OK:
        settings.user.suppress.Set('suppress.ConfirmJumpToEdencomSS', None)
    return user_input != uiconst.ID_OK


def check_insurgency(stargateID, to_solar_system_id):
    ballpark = sm.GetService('michelle').GetBallpark()
    gateSlimItem = ballpark.slimItems.get(stargateID)
    destinationCorruptionStageAndMaximum = getattr(gateSlimItem, 'destinationCorruptionStageAndMaximum')
    if destinationCorruptionStageAndMaximum is not None:
        currentCorruptionStage, maximumCorruptionStage = destinationCorruptionStageAndMaximum
        if currentCorruptionStage and currentCorruptionStage == maximumCorruptionStage:
            if eve.Message('ConfirmJumpToMaxCorruption', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                return True
    destinationSuppressionStageAndMaximum = getattr(gateSlimItem, 'destinationSuppressionStageAndMaximum')
    if destinationSuppressionStageAndMaximum is not None:
        currentSuppressionStage, maximumSuppresionStage = destinationSuppressionStageAndMaximum
        if currentSuppressionStage and currentSuppressionStage == maximumSuppresionStage:
            if eve.Message('ConfirmJumpToMaxSuppression', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                return True
    return False


_stargate_jump_checks = {'illicit_goods': check_illicit_goods,
 'sec_status': check_sec_status,
 'triglavian': check_triglavian,
 'edencom': check_edencom,
 'insurgency': check_insurgency}
