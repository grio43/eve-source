#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\globalConfig\getFunctions.py
from globalConfig import const
import ccpProfile

@ccpProfile.TimedFunction('GetGlobalConfigValue')
def GetGlobalConfigValue(machoNet, configName, defaultValue):
    return machoNet.GetGlobalConfig().get(configName, defaultValue)


def GetGlobalConfigBooleanValue(machoNet, configName, defaultValue):
    value = GetGlobalConfigValue(machoNet, configName, defaultValue)
    try:
        return bool(int(value))
    except ValueError:
        return defaultValue


def GetGlobalConfigIntValue(machoNet, configName, defaultValue, fallbackValue = None):
    value = GetGlobalConfigValue(machoNet, configName, defaultValue)
    try:
        return int(value)
    except ValueError:
        if fallbackValue is None:
            return defaultValue
        return fallbackValue


def GetGlobalConfigFloatValue(machoNet, configName, defaultValue, fallbackValue = None):
    value = GetGlobalConfigValue(machoNet, configName, defaultValue)
    try:
        return float(value)
    except ValueError:
        if fallbackValue is None:
            return defaultValue
        return fallbackValue


def GetMaxShipsToFit(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.BULK_FIT_SHIPS_CONFIG, const.BULK_FIT_SHIPS_DEFAULT)


def GetMaxShipsToContract(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.BULK_CONTRACT_SHIPS_CONFIG, const.BULK_CONTRACT_SHIPS_DEFAULT)


def AreCommunityFittingsEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.SHOW_COMMUNITY_FITTINGS_CONFIG, const.SHOW_COMMUNITY_FITTINGS_DEFAULT)


def ShouldShowFittingWarnings(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.SHOW_FITTING_WARNING_CONFIG, const.SHOW_FITTING_WARNING_DEFAULT)


def ShouldShowBugreportButton(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.BUGREPORT_SHOWBUTTON_CONFIG, const.BUGREPORT_SHOWBUTTON_DEFAULT)


def GetESIBaseUrl(machoNet):
    return GetGlobalConfigValue(machoNet, const.ESI_BASE_URL_CONFIG, const.ESI_BASE_URL_DEFAULT)


def GetESIDatasource(machoNet):
    return GetGlobalConfigValue(machoNet, const.ESI_DATASOURCE_CONFIG, const.ESI_DATASOURCE_DEFAULT)


def GetESIKillmailVersion(machoNet):
    return GetGlobalConfigValue(machoNet, const.ESI_KILLMAIL_VERSION_CONFIG, const.ESI_KILLMAIL_VERSION_DEFAULT)


def GetESIFleetVersion(machoNet):
    return GetGlobalConfigValue(machoNet, const.ESI_FLEET_VERSION_CONFIG, const.ESI_FLEET_VERSION_DEFAULT)


def GetMaxConnectionIdleTime(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.MAX_CONNECTION_IDLE_TIME_SECONDS_CONFIG, const.MAX_CONNECTION_IDLE_TIME_SECONDS_DEFAULT, fallbackValue=0)


def GetBugReportServer(machoNet, defaultBugreportServer):
    return GetGlobalConfigValue(machoNet, const.BUGREPORT_SERVER_CONFIG, defaultBugreportServer)


def GetOverviewMousemovementTimeout(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.OVERVIEW_MOUSEMOVEMENT_TIMEOUT_CONFIG, const.OVERVIEW_MOUSEMOVEMENT_TIMEOUT_DEFAULT)


def GetMaxChatChannelIdleTime(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.MAX_CHAT_CHANNEL_IDLE_TIME_SECONDS_CONFIG, const.MAX_CHAT_CHANNEL_IDLE_TIME_SECONDS_DEFAULT, fallbackValue=0)


def GetUpdateChannelCountIntervalSeconds(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.UPDATE_CHANNEL_COUNT_INTERVAL_SECONDS_CONFIG, const.UPDATE_CHANNEL_COUNT_INTERVAL_SECONDS_DEFAULT, fallbackValue=0)


def AllowCharacterLogoff(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.ALLOW_CHARACTER_LOGOFF_CONFIG, True)


def IsPlayerBountyHidden(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.HIDE_PLAYER_BOUNTIES_CONFIG, const.HIDE_PLAYER_BOUNTIES_DEFAULT)


def IsCsatVisible(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.IS_CSAT_VISIBLE_CONFIG, const.IS_CSAT_VISIBLE_DEFAULT)


def ArePointerLinksActive(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.POINTER_LINKS_ACTIVE_CONFIG, const.POINTER_LINKS_ACTIVE_DEFAULT)


def CheckPlayerBountyEnabled(machoNet):
    if IsPlayerBountyHidden(machoNet):
        raise RuntimeError('Player bounties are not enabled on this server')


def GetImageServerURL(machoNet):
    return GetGlobalConfigValue(machoNet, const.IMAGE_SERVER_URL_CONFIG, const.IMAGE_SERVER_URL_DEFAULT)


def GetImageServerMissingImageRetryDelay(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.IMAGE_SERVER_MISSING_IMAGE_RETRY_DELAY_IN_SECONDS_CONFIG, const.IMAGE_SERVER_MISSING_IMAGE_RETRY_DELAY_IN_SECONDS_DEFAULT)


def IsSkillPurchaseEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.SKILL_PURCHASE_ENABLED_CONFIG, const.SKILL_PURCHASE_ENABLED_DEFAULT)


def IsBannedWordsEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.BANNED_WORDS_ENABLED_CONFIG, const.BANNED_WORDS_ENABLED_DEFAULT)


def IsBannedWordsSearchEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.BANNED_WORDS_SEARCH_ENABLED_CONFIG, const.BANNED_WORDS_SEARCH_ENABLED_DEFAULT)


def GetBannedWordsBannedCharacterFromID(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.BANNED_WORDS_BANNED_CHARACTER_FROM_ID, const.BANNED_WORDS_BANNED_CHARACTER_FROM_ID_DEFAULT)


def BillboardTakeoverEnabled(machoNet):
    return bool(int(GetGlobalConfigValue(machoNet, const.BILLBOARD_TAKEOVER_CONFIG, const.BILLBOARD_TAKEOVER_DEFAULT)))


def GetRookieLoginCampaignAutoEnrollmentID(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.ROOKIE_LOGIN_CAMPAIGN_AUTO_ENROLL_ID_CONFIG, 0)


def GetHoursBetweenAddictionWarnings(machoNet):
    return GetGlobalConfigFloatValue(machoNet, const.HOURS_BETWEEN_ADDICTION_WARNINGS_CONFIG, const.HOURS_BETWEEN_ADDICTION_WARNINGS_DEFAULT)


def GetInventoryBadgingEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.INVENTORY_BADGING_ENABLED_CONFIG, const.INVENTORY_BADGING_ENABLED_DEFAULT)


def CanCloakedShipsBeKicked(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.ALLOW_KICKING_CLOAKED_SHIPS_CONFIG, const.ALLOW_KICKING_CLOAKED_SHIPS_DEFAULT)


def IsContentComplianceControlSystemActive(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.CONTENT_COMPLIANCE_CONTROL_SYSTEM_CONFIG, const.CONTENT_COMPLIANCE_CONTROL_SYSTEM_DEFAULT)


def GetEjabberdAddress(machoNet):
    service_address = GetGlobalConfigValue(machoNet=machoNet, configName=const.EJABBERD_CLIENT_ADDRESS_CONFIG, defaultValue=const.EJABBERD_CLIENT_ADDRESS_DEFAULT)
    return service_address


def GetLoginCampaignIDs(machoNet):
    return {'rookie': GetGlobalConfigIntValue(machoNet, const.DAILY_LOGIN_ROOKIE_CAMPAIGN_ID, 0),
     'alpha': GetGlobalConfigIntValue(machoNet, const.DAILY_LOGIN_ALPHA_CAMPAIGN_ID, 0),
     'omega': GetGlobalConfigIntValue(machoNet, const.DAILY_LOGIN_OMEGA_CAMPAIGN_ID, 0)}


def GetMinUserIdForRookieAutoEnrollment(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.AUTO_ENROLL_INTO_ROOKIE_DLI_WHEN_USERID_IS_ABOVE, 0) or None


def AreSurveysAllowed(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.USER_SURVEYS_ALLOWED_CONFIG, const.USER_SURVEYS_ALLOWED_DEFAULT)


def ShouldShowProjectDiscoveryTaskIds(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.SHOW_PROJECT_DISCOVERY_TASK_IDS_CONFIG, const.SHOW_PROJECT_DISCOVERY_TASK_IDS_DEFAULT)


def GetProjectDiscoveryMaxDailySubmissionsAge7DaysOrLess(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.PROJECT_DISCOVERY_MAX_DAILY_SUBMISSIONS_AGE_7_OR_LESS, const.PROJECT_DISCOVERY_MAX_DAILY_SUBMISSIONS_AGE_7_OR_LESS_DEFAULT)


def GetProjectDiscoveryMaxDailySubmissionsAge14DaysOrLess(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.PROJECT_DISCOVERY_MAX_DAILY_SUBMISSIONS_AGE_14_OR_LESS, const.PROJECT_DISCOVERY_MAX_DAILY_SUBMISSIONS_AGE_14_OR_LESS_DEFAULT)


def GetProjectDiscoveryMaxDailySubmissionsAge30DaysOrLess(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.PROJECT_DISCOVERY_MAX_DAILY_SUBMISSIONS_AGE_30_OR_LESS, const.PROJECT_DISCOVERY_MAX_DAILY_SUBMISSIONS_AGE_30_OR_LESS_DEFAULT)


def GetProjectDiscoveryMaxDailySubmissionsAgeOver30Days(machoNet):
    return GetGlobalConfigIntValue(machoNet, const.PROJECT_DISCOVERY_MAX_DAILY_SUBMISSIONS_AGE_OVER_30, const.PROJECT_DISCOVERY_MAX_DAILY_SUBMISSIONS_AGE_OVER_30_DEFAULT)


def ShouldUseProjectDiscoveryNewDrawingTool(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.SHOW_PROJECT_DISCOVERY_NEW_DRAWING_TOOL_CONFIG, const.SHOW_PROJECT_DISCOVERY_NEW_DRAWING_TOOL_DEFAULT)


def GetMonolithHoneycombEventsEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.MONOLITH_HONEYCOMB_EVENTS_ENABLED_CONFIG, const.MONOLITH_HONEYCOMB_EVENTS_ENABLED_DEFAULT)


def GetMonolithHoneycombDataset(machoNet):
    return GetGlobalConfigValue(machoNet, const.MONOLITH_HONEYCOMB_DATASET_CONFIG, const.MONOLITH_HONEYCOMB_DATASET_DEFAULT)


def GetMonolithHoneycombPublicKey(machoNet):
    return GetGlobalConfigValue(machoNet, const.MONOLITH_HONEYCOMB_PUBLIC_KEY_CONFIG, const.MONOLITH_HONEYCOMB_PUBLIC_KEY_DEFAULT)


def GetDynamicBountySystemEmergencyOffline(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.DYNAMIC_BOUNTY_SYSTEM_EMERGENCY_OFFLINE_CONFIG, const.DYNAMIC_BOUNTY_SYSTEM_EMERGENCY_OFFLINE_DEFAULT)


def GetESSFeatureFlaggedOffline(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.ESS_FEATURE_FLAG_DISABLED_CONFIG, const.ESS_FEATURE_FLAG_DISABLED_DEFAULT)


def GetESSReserveBankFeatureFlaggedOffline(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.ESS_RESERVE_BANK_DISABLED_CONFIG, const.ESS_RESERVE_BANK_DISABLED_DEFAULT)


def GetMammonMockingEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.FAKE_MAMMON_ENABLED_CONFIG, const.FAKE_MAMMON_ENABLED_DEFAULT)


def GetFakeFastCheckoutEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.FAKE_FAST_CHECKOUT_ENABLED_CONFIG, const.FAKE_FAST_CHECKOUT_ENABLED_DEFAULT)


def GetFakeFastCheckoutResponse(machoNet):
    return GetGlobalConfigValue(machoNet, const.FAKE_FAST_CHECKOUT_RESPONSE_CONFIG, const.FAKE_FAST_CHECKOUT_RESPONSE_DEFAULT)


def GetFakeFastCheckoutPlexOffers(machoNet):
    return GetGlobalConfigValue(machoNet, const.FAKE_FAST_CHECKOUT_PLEX_OFFERS_CONFIG, const.FAKE_FAST_CHECKOUT_PLEX_OFFERS_DEFAULT)


def GetFakeVgsEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.FAKE_VGS_ENABLED_CONFIG, const.FAKE_VGS_ENABLED_DEFAULT)


def GetFakeChinaFunnelEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.FAKE_CHINA_FUNNEL_ENABLED_CONFIG, const.FAKE_CHINA_FUNNEL_ENABLED_DEFAULT)


def GetFakeBuyPlexOfferUrl(machoNet):
    return GetGlobalConfigValue(machoNet, const.FAKE_BUY_PLEX_OFFER_URL_CONFIG, const.FAKE_BUY_PLEX_OFFER_URL_DEFAULT)


def GetUseShellExecuteToBuyPlexOffer(machoNet):
    return GetGlobalConfigValue(machoNet, const.USE_SHELL_EXECUTE_TO_BUY_PLEX_OFFER_CONFIG, const.USE_SHELL_EXECUTE_TO_BUY_PLEX_OFFER_DEFAULT)


def GetPreloadRookieSystems(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.PRELOAD_ROOKIE_SYSTEMS, const.PRELOAD_ROOKIE_SYSTEMS_DEFAULT)


def GetAirNpeEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.AIR_NPE_ENABLED, const.AIR_NPE_ENABLED_DEFAULT)


def GetVoidSpaceAutoCleanupEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.VOID_SPACE_AUTO_CLEANUP_ENABLED_CONFIG, const.VOID_SPACE_AUTO_CLEANUP_ENABLED_DEFAULT)


def GetConversationLine3dPortraitEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.CONVERSATION_LINE_3D_PORTRAIT_ENABLED_CONFIG, const.CONVERSATION_LINE_3D_PORTRAIT_ENABLED_DEFAULT)


def IsMaterialCompressionEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.MATERIAL_COMPRESSION_ENABLED_CONFIG, const.MATERIAL_COMPRESSION_ENABLED_DEFAULT)


def GetNewMissionGiverEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.NEW_MISSION_GIVER_ENABLED_CONFIG, const.NEW_MISSION_GIVER_ENABLED_DEFAULT)


def IsPercentageHullDamageEnabled(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.PERCENTAGE_HULL_DAMAGE_ENABLED_CONFIG, const.PERCENTAGE_HULL_DAMAGE_ENABLED_DEFAULT)


def UseNewApplyDamage(machoNet):
    return GetGlobalConfigBooleanValue(machoNet, const.USE_NEW_APPLY_DAMAGE_CONFIG, const.USE_NEW_APPLY_DAMAGE_DEFAULT)
