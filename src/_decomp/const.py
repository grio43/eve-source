#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\const.py
SERVICE_CHARID = -1
defaultResourceCacheDx8 = 32
defaultResourceCacheDx9 = 256
maxNodeID = 1000000000
systemEventTypeServerPageRefresh = 2000000201
noteTypeGeneral = 30001
noteTypeUser = 30002
noteTypeCharacter = 30003
noteTypeStructure = 30004
usernameAlreadyTaken = -11
userConnectTypeClient = 201
userConnectTypeServerPages = 202
userConnectTypeJessica = 203
userTypeTester = 2
userTypeVolunteer = 9
userTypeCustomerSupport = 11
userTypeEvent = 12
userTypeCCP = 13
userTypeVolunteerPlayerAccount = 16
userTypePBC = 20
userTypeETC = 21
userTypeTrial = 23
userTypePromotion = 25
userTypeMammon = 30
userTypeMedia = 31
userTypeCDKey = 33
userTypeIA = 34
userTypeCCPPlayerAccount = 6
userTypeCSSPlayerAccount = 7
userStatusActive = 1
userStatusDeleted = 2
userStatusDisabled = 3
userStatusExpired = 4
userStatusBanned = 5
userStatusPending = 6
userStatusSWIFTConfirmPending = 7
userStatusTrash = 8
userStatusPyByCashPending = 9
userStatusGameTimeCardPending = 10
userStatusCDKeyLessPending = 11
userStatusPermanentBan = 12
userStatusPendingBan = 13
userStatusTrialPendingActivation = 14
BAN_STATES = (userStatusBanned, userStatusPendingBan, userStatusPermanentBan)
countryChina = 37
timeZoneGMT = 13
timeZoneCCT = 21
zmetricCounter_MachoChar = 30010
zmetricCounter_MachoUser = 30011
doomheimStationID = 6000001
eveUniverseLocationID = 1
genderFemale = 0
genderMale = 1
DBTYPE_BOOL = 11
DBTYPE_I1 = 16
DBTYPE_UI1 = 17
DBTYPE_I2 = 2
DBTYPE_UI2 = 18
DBTYPE_I4 = 3
DBTYPE_UI4 = 19
DBTYPE_R4 = 4
DBTYPE_I8 = 20
DBTYPE_UI8 = 21
DBTYPE_R5 = 5
DBTYPE_CY = 6
DBTYPE_FILETIME = 64
DBTYPE_DBTIMESTAMP = 135
DBTYPE_STR = 129
DBTYPE_WSTR = 130
DBTYPE_BYTES = 508
DBTYPE_EMPTY = 0
SQL_SYSTEM_TYPE_ID_IMAGE = 34
SQL_SYSTEM_TYPE_ID_TEXT = 35
SQL_SYSTEM_TYPE_ID_UNIQUEIDENTIFIER = 36
SQL_SYSTEM_TYPE_ID_DATETIME2 = 42
SQL_SYSTEM_TYPE_ID_TINYINT = 48
SQL_SYSTEM_TYPE_ID_SMALLINT = 52
SQL_SYSTEM_TYPE_ID_INT = 56
SQL_SYSTEM_TYPE_ID_SMALLDATETIME = 58
SQL_SYSTEM_TYPE_ID_REAL = 59
SQL_SYSTEM_TYPE_ID_MONEY = 60
SQL_SYSTEM_TYPE_ID_DATETIME = 61
SQL_SYSTEM_TYPE_ID_FLOAT = 62
SQL_SYSTEM_TYPE_ID_SQL_VARIANT = 98
SQL_SYSTEM_TYPE_ID_NTEXT = 99
SQL_SYSTEM_TYPE_ID_BIT = 104
SQL_SYSTEM_TYPE_ID_DECIMAL = 106
SQL_SYSTEM_TYPE_ID_NUMERIC = 108
SQL_SYSTEM_TYPE_ID_SMALLMONEY = 122
SQL_SYSTEM_TYPE_ID_BIGINT = 127
SQL_SYSTEM_TYPE_ID_VARBINARY = 165
SQL_SYSTEM_TYPE_ID_VARCHAR = 167
SQL_SYSTEM_TYPE_ID_BINARY = 173
SQL_SYSTEM_TYPE_ID_CHAR = 175
SQL_SYSTEM_TYPE_ID_TIMESTAMP = 189
SQL_SYSTEM_TYPE_ID_NVARCHAR = 231
SQL_SYSTEM_TYPE_ID_NCHAR = 239
SQL_SYSTEM_TYPE_ID_XML = 241
SQL_SYSTEM_TYPE_IDS_STRINGS = (SQL_SYSTEM_TYPE_ID_CHAR,
 SQL_SYSTEM_TYPE_ID_NCHAR,
 SQL_SYSTEM_TYPE_ID_VARCHAR,
 SQL_SYSTEM_TYPE_ID_NVARCHAR,
 SQL_SYSTEM_TYPE_ID_TEXT,
 SQL_SYSTEM_TYPE_ID_NTEXT)
SQL_SYSTEM_TYPE_IDS_DATES = (SQL_SYSTEM_TYPE_ID_SMALLDATETIME, SQL_SYSTEM_TYPE_ID_DATETIME, SQL_SYSTEM_TYPE_ID_DATETIME2)
SQL_SYSTEM_TYPE_IDS_FLOATS = (SQL_SYSTEM_TYPE_ID_FLOAT, SQL_SYSTEM_TYPE_ID_REAL)
SQL_BIT_TRUE_VALUES = ('1',
 'on',
 True,
 'True')
bsdBranchMain = 1
bsdBranchStaging = 2
bsdBranchLive = 3
cacheSystemIntervals = 2000109999
cacheSystemSettings = 2000100001
cacheSystemSchemas = 2000100003
cacheSystemTables = 2000100004
cacheSystemEventTypes = 2000100013
cacheUserEventTypes = 2000209999
cacheUserColumns = 2000209998
cacheUserRegions = 2000209997
cacheUserTimeZones = 2000209996
cacheUserCountries = 2000209995
cacheUserTypes = 2000209994
cacheUserStatuses = 2000209993
cacheUserRoles = 2000209992
cacheUserConnectTypes = 2000209991
cacheUserOperatingSystems = 2000209990
cacheUserExternalTypes = 2000209989
cacheUserTags = 2000209988
cacheMlsLanguages = 2000409999
cacheClusterServices = 2000909999
cacheClusterMachines = 2000909998
cacheClusterProxies = 2000909997
cacheBillingBuddyInviteStatuses = 2001209999
cacheBillingBuddyInviteRewardTypes = 2001209998
cacheInventoryFlags = 2001300012
cacheClientBrowserSiteFlags = 2003009999
cacheMetricGroups = 2003209999
cacheMetricCounters = 2003209998
cacheMetricColumns = 2003209997
cacheStaticUsers = 2000000001
cacheUsersDataset = 2000000002
cacheCharactersDataset = 2000000003
cacheInventoryNames = 2000000004
CLUSTERSINGLETON_MOD = 8
USERNODE_MOD = 32
tableUserUsers = 2000200001
tableLocalizationMessages = 2002300003
tableLocalizationMessageTexts = 2002300004
BLUE_TICK = 1L
HNSEC = BLUE_TICK
uSEC = 10L
MSEC = 10000L
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L
DAY = HOUR * 24L
WEEK = DAY * 7L
TP_YEAR = 0
TP_MONTH = 1
TP_DAY_OF_WEEK = 2
TP_DAY = 3
TP_HOUR = 4
TP_MIN = 5
TP_SEC = 6
TP_MILLISEC = 7
SUNDAY = 0
MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
MONTH28 = WEEK * 4L
MONTH30 = DAY * 30L
YEAR365 = DAY * 365L
YEAR360 = MONTH30 * 12L
ONE_TICK = 16 * MSEC
CHANNEL_PREFER_SENDER = 1
CHANNEL_PREFER_RECEIVER = -1
CHANNEL_PREFER_NOTHING = 0
GAMEWORLD_INIT_DATA = {'Gravity': (0.0, -9.80665, 0.0),
 'WorldSize': 10000.0}
CM_FLAG_INVISIBLE = 1
CM_FLAG_SEE_INVISIBLE = 2
CM_FLAG_UPDATES_MOVEMENT = 4
PG_FLAG_WITH_VIS_OBSERVE = 1
PG_FLAG_WITH_VIS_OBSERVED = 2
PG_FLAG_MOVEMENT_UPDATE_CHECK = 4
WWISE_BANK_PREFIXES = {}
WWISE_ONESHOT_SOUND = 1
WWISE_LOOPING_SOUND = 2
WWISE_PLACED_SOUND = 3
WWISE_ATMOS_SOUND = 4
WWISE_SOUND_TYPE_LABELS = {WWISE_ONESHOT_SOUND: 'One Shot',
 WWISE_LOOPING_SOUND: 'Looping',
 WWISE_PLACED_SOUND: 'Placed',
 WWISE_ATMOS_SOUND: 'Atmos'}
WWISE_BANK_POSTFIXES = {WWISE_ONESHOT_SOUND: 'oneshot',
 WWISE_LOOPING_SOUND: 'sustain',
 WWISE_PLACED_SOUND: 'placed_sounds',
 WWISE_ATMOS_SOUND: 'atmoses'}
INFOSERVICE_OFFLINE = -2
INFOTYPE_OFFLINE = -1
maxInt = 2147483647
maxBigint = 9223372036854775807L
responseUnknown = 'Unknown'
FLOAT_TOLERANCE = 0.001
AVATAR_HEIGHT = 1.8
AVATAR_RADIUS = 0.35
paperDollGender = 1
paperDollDNA = 2
ADDRESS_TYPE_NODE = 1
ADDRESS_TYPE_CLIENT = 2
ADDRESS_TYPE_BROADCAST = 4
ADDRESS_TYPE_ANY = 8
TYPEID_NONE = -1
paperdollStateNoRecustomization = 0
paperdollStateResculpting = 1
paperdollStateNoExistingCustomization = 2
paperdollStateFullRecustomizing = 3
paperdollStateForceRecustomize = 4
paperdollStateNames = {paperdollStateNoRecustomization: 'No re-customization',
 paperdollStateResculpting: 'Re-sculpting',
 paperdollStateNoExistingCustomization: 'No existing data',
 paperdollStateFullRecustomizing: 'Full bloodline, gender, sculpting',
 paperdollStateForceRecustomize: 'Force re-customization'}
facialPortraitOnError = -2
facialPortraitInProgress = -1
facialPortraitNotRendered = 0
facialPortraitRendered = 1
localizedLanguageEnglishUS = 1033
localizedLanguageChinese = 1051
FEMALE = 0
MALE = 1
UE_DATETIME = 14
UE_DATE = 15
UE_TIME = 16
UE_TIMESHRT = 17
UE_MSGARGS = 22
UE_LOC = 101
UE_MESSAGEID = 102
UE_LIST = 103
SIZE_FIELD_SHORT = (150,)
SIZE_FIELD_MEDIUM = (250,)
SIZE_FIELD_LONG = (350,)
ATTACK_TYPE_BAD_SCOPE = 252
ATTACK_TYPE_BAD_TOKEN = 253
ixItemID = 0
ixTypeID = 1
ixOwnerID = 2
ixLocationID = 3
ixFlag = 4
ixQuantity = 5
REDEEM_ADDED_BY_CONTEXT_ESP = 1
REDEEM_ADDED_BY_CONTEXT_WEB_PURCHASE = 2
REDEEM_ADDED_BY_CONTEXT_MASS_TOKEN = 3
RETURNED_TO_REDEEM_ITEMS = 4
REDEEM_ADDED_BY_CONTEXT_PLEX = 5
REDEEM_ADDED_BY_CONTEXT_STORE_PURCHASE = 7
REDEEM_ADDED_BY_CONTEXT_SEASON_REWARD = 8
REDEEM_ADDED_BY_CONTEXT_INCEPTION_NPE = 9
REDEEM_ADDED_BY_CONTEXT_PROJECT_DISCOVERY = 10
REDEEM_ADDED_BY_CONTEXT_LOGIN_REWARD = 11
REDEEM_ADDED_BY_CONTEXT_DB_SCRIPT = 13
REDEEM_ADDED_BY_CONTEXT_PROVING_GROUND_REWARDS = 14
REDEEM_ADDED_BY_CONTEXT_BOT_REPORT_LOYALTY_PROGRAM = 15
REDEEM_ADDED_BY_CONTEXT_SURVEY_REWARD = 16
REDEEM_ADDED_BY_CONTEXT_BNNPE_TO_AIR_NPE = 17
REDEEM_CONTEXT_BY_ID = {REDEEM_ADDED_BY_CONTEXT_ESP: 'Added from ESP',
 REDEEM_ADDED_BY_CONTEXT_WEB_PURCHASE: 'Added from Web',
 REDEEM_ADDED_BY_CONTEXT_MASS_TOKEN: 'Redeemed from Mass Token',
 RETURNED_TO_REDEEM_ITEMS: 'Returned to Redeem Items',
 REDEEM_ADDED_BY_CONTEXT_PLEX: 'Plex',
 REDEEM_ADDED_BY_CONTEXT_STORE_PURCHASE: 'Store Purchase',
 REDEEM_ADDED_BY_CONTEXT_SEASON_REWARD: 'Season Reward',
 REDEEM_ADDED_BY_CONTEXT_INCEPTION_NPE: 'Tutorial Reward',
 REDEEM_ADDED_BY_CONTEXT_PROJECT_DISCOVERY: 'Project Discovery',
 REDEEM_ADDED_BY_CONTEXT_LOGIN_REWARD: 'Awarded to the user for logging in',
 REDEEM_ADDED_BY_CONTEXT_DB_SCRIPT: 'Added by means of a DB script',
 REDEEM_ADDED_BY_CONTEXT_PROVING_GROUND_REWARDS: 'Proving Ground Rewards',
 REDEEM_ADDED_BY_CONTEXT_BOT_REPORT_LOYALTY_PROGRAM: 'Bot Report Loyalty Program Reward',
 REDEEM_ADDED_BY_CONTEXT_SURVEY_REWARD: 'Survey Participation Reward',
 REDEEM_ADDED_BY_CONTEXT_BNNPE_TO_AIR_NPE: 'Compensation for BNNPE termination on AIR NPE deployment (new tutorial)'}
SECONDS_IN_MILLISECOND = 0.001
try:
    import blue
except ImportError:
    pass

if 'blue' in globals() and hasattr(blue, 'pyos'):
    import session
