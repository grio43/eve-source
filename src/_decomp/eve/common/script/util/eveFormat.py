#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\eveFormat.py
import math
import sys
import evetypes
import localization
import log
from carbon.common.script.util.format import FmtAmt
from eve.common.lib import appConst as const
from eve.common.script.mgt import appLogConst as logConst
from eveprefs import boot
from npcs.npccorporations import get_corporation_faction_id
from security.client.securityColor import get_security_status_color
CURRENCY_FORMAT_TRANSLATIONS = {(const.creditsAURUM, 0): 'UI/Util/FmtAurNoDecimal',
 (const.creditsAURUM, 1): 'UI/Util/FmtAur',
 (const.creditsISK, 0): 'UI/Util/FmtIskNoDecimal',
 (const.creditsISK, 1): 'UI/Util/FmtIsk'}

def FmtLP(lp):
    amount = FmtAmt(lp, showFraction=False)
    return localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=amount)


def FmtISK(isk, showFractionsAlways = 1):
    return FmtCurrency(isk, showFractionsAlways, const.creditsISK)


def FmtAUR(aur, showFractionsAlways = 0):
    return FmtCurrency(aur, showFractionsAlways, const.creditsAURUM)


def FmtISKAndRound(isk, showFractionsAlways = 1):
    return FmtISK(RoundISK(isk), showFractionsAlways)


def RoundISK(isk):
    if isk < 10:
        return round(isk, 2)
    elif isk < 100:
        return round(isk, 1)
    elif isk < 1000:
        return round(isk, 0)
    elif isk < 10000:
        return round(isk, -1)
    elif isk < 100000:
        return round(isk, -2)
    elif isk < 1000000:
        return round(isk, -3)
    elif isk < 10000000:
        return round(isk, -4)
    elif isk < 100000000:
        return round(isk, -5)
    else:
        return round(isk, -6)


def FmtCurrency(amount, showFractionsAlways = 1, currency = None):
    if currency is None:
        key = (const.creditsISK, showFractionsAlways)
    else:
        key = (currency, showFractionsAlways)
    fmtPath = CURRENCY_FORMAT_TRANSLATIONS[key]
    if not showFractionsAlways:
        amount = int(round(amount))
    return localization.GetByLabel(fmtPath, amount=amount)


def FmtStandingTransaction(transaction):
    subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectStandingChange')
    body = ''
    try:
        if transaction.eventTypeID == logConst.eventStandingDecay:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectDecay')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageDecay')
        elif transaction.eventTypeID == logConst.eventStandingDerivedModificationPositive:
            cfg.eveowners.Prime([transaction.fromID])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectDerivedModificatonPositive')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageDerivedModificatonPositive', name=cfg.eveowners.Get(transaction.fromID).name)
        elif transaction.eventTypeID == logConst.eventStandingDerivedModificationNegative:
            cfg.eveowners.Prime([transaction.fromID])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectDerivedModificatonNegitive')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageDerivedModificatonNegitive', name=cfg.eveowners.Get(transaction.fromID).name)
        elif transaction.eventTypeID == logConst.eventStandingCombatAggression:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAgression')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAgression', locationID=transaction.int_2, ownerName=cfg.eveowners.Get(transaction.int_1).name, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingCombatAssistance:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAssistence')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAssistence', locationID=transaction.int_2, name=cfg.eveowners.Get(transaction.int_1).name, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingCombatShipKill:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatShipKill')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatShipKill', locationID=transaction.int_2, name=cfg.eveowners.Get(transaction.int_1).name, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingPropertyDamage:
            cfg.eveowners.Prime([transaction.int_1])
            cfg.evelocations.Prime([transaction.int_2])
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectPropertyDamage')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messagePropertyDamage', locationID=transaction.int_2, name=cfg.eveowners.Get(transaction.int_1).name, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingCombatPodKill:
            n1 = cfg.eveowners.Get(transaction.int_1).name if transaction.int_1 else '???'
            n2 = cfg.evelocations.Get(transaction.int_2).name if transaction.int_2 else '???'
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatPodKill')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatPodKill', locationName=n2, name=n1)
        elif transaction.eventTypeID == logConst.eventStandingSlashSet:
            n = cfg.eveowners.Get(transaction.int_1).name if transaction.int_1 else '???'
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectSetBySlashCmd')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageSetBySlashCmd', message=transaction.msg, name=n)
        elif transaction.eventTypeID == logConst.eventStandingReset:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectSetBySlashCmd')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageResetBySlashCmd')
        elif transaction.eventTypeID == logConst.eventStandingPlayerSet:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectPlayerSet')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messagePlayerSet', message=transaction.msg)
        elif transaction.eventTypeID == logConst.eventStandingPlayerCorpSet:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCorporationSet')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCorporationSet', message=transaction.msg, name=cfg.eveowners.Get(transaction.int_1).name)
        elif transaction.eventTypeID in (logConst.eventStandingAgentMissionCompleted,
         logConst.eventStandingAgentMissionDeclined,
         logConst.eventStandingAgentMissionFailed,
         logConst.eventStandingAgentMissionOfferExpired):
            if transaction.int_1 is not None:
                missionName = localization.GetByMessageID(transaction.int_1)
            else:
                missionName = transaction.msg
            if transaction.eventTypeID == logConst.eventStandingAgentMissionCompleted:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionComplete', message=missionName)
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionComplete', message=missionName)
            elif transaction.eventTypeID == logConst.eventStandingAgentMissionDeclined:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionDeclined', message=missionName)
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionDecline', message=missionName)
            elif transaction.eventTypeID == logConst.eventStandingAgentMissionFailed:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionFailed', message=missionName)
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionFailed', message=missionName)
            elif transaction.eventTypeID == logConst.eventStandingAgentMissionOfferExpired:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionExpired', message=missionName)
                if missionName:
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionExpiredNoMsg')
                else:
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionExpiredMsg', message=missionName)
        elif transaction.eventTypeID == logConst.eventStandingAgentMissionBonus:
            import binascii
            import cPickle
            stuff = cPickle.loads(binascii.a2b_hex(transaction.msg))
            if transaction.modification >= 0.0:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionBonus', message=stuff.get('header', '???'))
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionBonus', message=stuff.get('body', '???'))
            else:
                subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectMissionPenalty', message=stuff.get('header', '???'))
                body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageMissionPenalty', message=stuff.get('body', '???'))
        elif transaction.eventTypeID == logConst.eventStandingPirateKillSecurityStatus:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectLawEnforcmentGain')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageLawEnforcmentGain', name=cfg.eveowners.Get(transaction.int_1).name)
        elif transaction.eventTypeID == logConst.eventStandingPromotionFactionIncrease:
            rankNumber = transaction.int_1
            corpID = transaction.int_2
            factionID = get_corporation_faction_id(corpID)
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectFacwarPromotion')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageFacwarPromotion', corpName=cfg.eveowners.Get(corpID).name, rankName=sm.GetService('facwar').GetRankLabel(factionID, rankNumber)[0])
        elif transaction.eventTypeID == logConst.eventStandingCombatShipKillOwnFaction:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatShipKill')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatSkipKillOwnFaction', factionName=cfg.eveowners.Get(transaction.int_1).name, locationID=transaction.int_2, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingCombatPodKillOwnFaction:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatPodKill')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatPodKillOwnFaction', factionName=cfg.eveowners.Get(transaction.int_1).name, locationID=transaction.int_2)
        elif transaction.eventTypeID == logConst.eventStandingCombatAggressionOwnFaction:
            factionID = transaction.int_1
            locationID = transaction.int_2
            typeID = transaction.int_3
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAgression')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAgressionOwnFaction', factionName=cfg.eveowners.Get(factionID).name, locationID=locationID, typeID=typeID)
        elif transaction.eventTypeID == logConst.eventStandingCombatAssistanceOwnFaction:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAssistence')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAssistanceOwnFaction', factionName=cfg.eveowners.Get(transaction.int_1).name, locationID=transaction.int_2, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingPropertyDamageOwnFaction:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectPropertyDamage')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatProprtyDamageOwnFaction', factionName=cfg.eveowners.Get(transaction.int_1).name, locationID=transaction.int_2, typeID=transaction.int_3)
        elif transaction.eventTypeID == logConst.eventStandingTacticalSiteDefended:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectFacwarSiteDefened')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageFacwarSiteDefened', enemyFactionName=cfg.eveowners.Get(transaction.int_2).name, factionName=cfg.eveowners.Get(transaction.int_1).name)
        elif transaction.eventTypeID == logConst.eventStandingTacticalSiteConquered:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectFacwarSiteConquered')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageFacwarSiteConquered', enemyFactionName=cfg.eveowners.Get(transaction.int_2).name, factionName=cfg.eveowners.Get(transaction.int_1).name)
        elif transaction.eventTypeID == logConst.eventStandingRecommendationLetterUsed:
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectRecomendationLetterUsed')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageRecomendationLetterUsed')
        elif transaction.eventTypeID == logConst.eventStandingTutorialAgentInitial:
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageGraduation')
        elif transaction.eventTypeID == logConst.eventStandingContrabandTrafficking:
            factionID = transaction.int_1
            locationID = transaction.int_2
            if factionID:
                factionName = cfg.eveowners.Get(factionID).name
            else:
                factionName = localization.GetByLabel('UI/Generic/FormatStandingTransactions/labelSomeone')
            if locationID:
                locationName = cfg.evelocations.Get(locationID).name
            else:
                locationName = localization.GetByLabel('UI/Generic/FormatStandingTransactions/labelSomewhere')
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectContraband')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageContraband', factionName=factionName, systemName=locationName)
        elif transaction.eventTypeID in (logConst.eventStandingGroupRewardCorporation, logConst.eventStandingGroupRewardFaction):
            subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectGroupReward')
            body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageGroupReward')
    except:
        log.LogException()
        sys.exc_clear()

    return (subject, body)


def FmtSystemSecStatus(raw, getColor = 0):
    sec = round(raw, 1)
    if sec == -0.0:
        sec = 0.0
    if getColor == 0:
        return sec
    else:
        return (sec, get_security_status_color(sec))


def GetName(ownerID):
    try:
        if ownerID == -1:
            return '(none)'
        if ownerID < 0:
            return evetypes.GetName(-ownerID)
        return cfg.eveowners.Get(ownerID).name
    except:
        sys.exc_clear()
        return localization.uiutil.PrepareLocalizationSafeString('id:%s (no name)' % ownerID)


def GetLocation(locationID):
    try:
        if boot.role == 'server' or eve.session.regionid < const.mapWormholeRegionMin:
            return cfg.evelocations.Get(locationID).name
        if locationID >= const.mapWormholeRegionMin and locationID <= const.mapWormholeRegionMax:
            return localization.GetByLabel('UI/Generic/FormatLocations/unchartedRegion')
        if locationID >= const.mapWormholeConstellationMin and locationID <= const.mapWormholeConstellationMax:
            return localization.GetByLabel('UI/Generic/FormatLocations/unchartedConstellation')
        if locationID >= const.mapWormholeSystemMin and locationID <= const.mapWormholeSystemMax:
            return localization.GetByLabel('UI/Generic/FormatLocations/unchartedSystem')
    except:
        sys.exc_clear()
        return localization.GetByLabel('UI/Generic/FormatLocations/errorUnknowenLocation', id=locationID)


def FmtPlanetAttributeKeyVal(key, val):
    text = val
    label = None
    typeID = None
    if key == 'temperature':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeTemperature')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatTempatureKelvin', value=str(int(val)))
    elif key == 'orbitRadius':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeOrbitRadius')
        numAU = val / const.AU
        if numAU > 0.1:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalRadiusInAU', value=numAU)
        else:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalRadiusInKM', value=FmtAmt(int(val)))
    elif key == 'eccentricity':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeEccentricity')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatEccentricity', value=val)
    elif key == 'massDust':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeMassDust')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatMassInKG', value='%.1e' % val)
    elif key == 'massGas':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeMassGas')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatMassInKG', value='%.1e' % val)
    elif key == 'density':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeDensity')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatDensity', value=val)
    elif key == 'orbitPeriod':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeOrbitPeriod')
        numDays = val / 864000
        if numDays > 1.0:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalPeriodInt', value=int(numDays))
        else:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalPeriodFloat', value=numDays)
    elif key in ('age',):
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeAge')
        value = int(val / 31536000 / 1000000) * 1000000
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatAge', value=value)
    elif key == 'radius':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeRadius')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatOrbitalRadiusInKM', value=FmtAmt(int(val / 1000)))
    elif key == 'surfaceGravity':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeSurfaceGravity')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatSurfaceGravity', value=val)
    elif key == 'escapeVelocity':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeEscapeVelocity')
        text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatEscapeVelocity', value=val / 1000)
    elif key == 'pressure':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributePressure')
        if val < 1000:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatSurfacePresureVeryLow')
        else:
            text = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/formatSurfacePresure', value=val / 100000)
    elif key == 'reagentType':
        label = localization.GetByLabel('UI/Sovereignty/ReagentType')
        text = evetypes.GetName(val)
        typeID = val
    elif key == 'reagentAmountPerMinute':
        label = localization.GetByLabel('UI/Sovereignty/HarvestingAmount')
        text = localization.GetByLabel('UI/Sovereignty/AmountPerMinute', value=val)
    elif key == 'fragmented':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeFragmented')
    elif key == 'life':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeLife')
    elif key == 'locked':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeLocked')
    elif key == 'luminosity':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeLuminosity')
        text = localization.formatters.FormatNumeric(text)
    elif key == 'mass':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeMass')
    elif key == 'rotatopmRate':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeRotatopmRate')
    elif key == 'spectralClass':
        label = localization.GetByLabel('UI/Generic/FormatPlanetAttributes/attributeSpectralClass')
    elif key == 'power':
        label = localization.GetByLabel('UI/Sovereignty/Power')
        text = localization.GetByLabel('UI/Sovereignty/PowerFmt', power=val)
    elif key == 'workforce':
        label = localization.GetByLabel('UI/Sovereignty/Workforce')
        text = localization.GetByLabel('UI/Sovereignty/WorkforceFmt', workforce=val)
    return (label, text, typeID)


def FmtDist2(dist, maxDecimals = 2):
    if dist < 0.0:
        dist = abs(dist)
        maxDecimals = None
    if dist < 10000.0:
        dist = int(dist)
        maxDecimals = None
        fmtUrl = '/Carbon/UI/Common/FormatDistance/fmtDistInMeters'
    elif dist < 10000000000.0:
        dist = float(dist) / 1000.0
        fmtUrl = '/Carbon/UI/Common/FormatDistance/fmtDistInKiloMeters'
    else:
        dist = round(dist / const.AU, maxDecimals)
        fmtUrl = '/Carbon/UI/Common/FormatDistance/fmtDistInAU'
    if maxDecimals == 0:
        maxDecimals = None
        dist = int(dist)
    distStr = localization.formatters.FormatNumeric(dist, useGrouping=False, decimalPlaces=maxDecimals)
    return localization.GetByLabel(fmtUrl, distance=distStr)


def FmtISKEng(isk, showFractionsAlways = True):
    return FmtCurrencyEng(isk, showFractionsAlways, const.creditsISK)


def FmtAUREng(aur, showFractionsAlways = False):
    return FmtCurrencyEng(aur, showFractionsAlways, const.creditsAURUM)


def FmtCurrencyEng(amount, showFractionsAlways = True, currency = None):
    CURRENCIES = {const.creditsAURUM: 'AUR',
     const.creditsISK: 'ISK'}
    if amount is None:
        amount = 0
    currency_label = CURRENCIES.get(currency, '')
    if showFractionsAlways or abs(math.fmod(amount, 1.0)) > 0.0:
        return u'{:,.2f} {}'.format(float(amount), currency_label)
    else:
        return u'{:,.0f} {}'.format(amount, currency_label)


def GetAveragePrice(item):
    if item.singleton == const.singletonBlueprintCopy:
        return
    try:
        import inventorycommon.typeHelpers
        return inventorycommon.typeHelpers.GetAveragePrice(item.typeID)
    except KeyError:
        return
