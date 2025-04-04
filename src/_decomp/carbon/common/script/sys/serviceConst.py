#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\serviceConst.py
SERVICE_STOPPED = 1
SERVICE_START_PENDING = 2
SERVICE_STOP_PENDING = 3
SERVICE_RUNNING = 4
SERVICE_CONTINUE_PENDING = 5
SERVICE_PAUSE_PENDING = 6
SERVICE_PAUSED = 7
SERVICE_FAILED = 8
SERVICE_STARTING_DEPENDENCIES = 9
SERVICE_CONTROL_STOP = 1
SERVICE_CONTROL_PAUSE = 2
SERVICE_CONTROL_CONTINUE = 3
SERVICE_CONTROL_INTERROGATE = 4
SERVICE_CONTROL_SHUTDOWN = 5
ROLE_CL = 549755813888L
ROLE_CR = 1099511627776L
ROLE_CM = 2199023255552L
ROLE_BSDADMIN = 35184372088832L
ROLE_EXT_GM1 = 70368744177664L
ROLE_EXT_GM2 = 140737488355328L
ROLE_EXT_GM3 = 281474976710656L
ROLE_EXT_GM4 = 562949953421312L
ROLE_SECURITY = 1125899906842624L
ROLE_PROGRAMMER = 2251799813685248L
ROLE_QA = 4503599627370496L
ROLE_GMH = 9007199254740992L
ROLE_GMS = 274877906944L
ROLE_GML = 18014398509481984L
ROLE_CONTENT = 36028797018963968L
ROLE_ADMIN = 72057594037927936L
ROLE_VIPLOGIN = 144115188075855872L
ROLE_ROLEADMIN = 288230376151711744L
ROLE_NEWBIE = 576460752303423488L
ROLE_SERVICE = 1152921504606846976L
ROLE_PLAYER = 2305843009213693952L
ROLE_LOGIN = 4611686018427387904L
ROLE_DBA = 16384L
ROLE_REMOTESERVICE = 131072L
ROLE_TRANSLATION = 524288L
ROLE_CHTINVISIBLE = 1048576L
ROLE_CHTADMINISTRATOR = 2097152L
ROLE_TRANSLATIONADMIN = 134217728L
ROLE_ACCOUNTMANAGEMENT = 536870912L
ROLE_IGB = 2147483648L
ROLE_TRANSLATIONEDITOR = 4294967296L
ROLE_TRANSLATIONTESTER = 34359738368L
ROLE_BANNING = 2L
ROLE_VMSADMIN = 4L
ROLE_MARKETH = 8L
ROLE_CSMADMIN = 16L
ROLE_CSMDELEGATE = 32L
ROLE_PINKCHAT = 64L
ROLE_VGSADMIN = 128L
ROLE_PETITIONEE = 256L
ROLE_CDKEYS = 512L
ROLE_VGSMANAGER = 1024L
ROLE_CENTURION = 2048L
ROLE_WORLDMOD = 4096L
ROLE_LEGIONEER = 262144L
ROLE_HEALSELF = 4194304L
ROLE_HEALOTHERS = 8388608L
ROLE_NEWSREPORTER = 16777216L
ROLE_SPAWN = 8589934592L
ROLE_BATTLESERVER = 17179869184L
ROLE_TOURNAMENT = 68719476736L
ROLE_TRANSFER = 137438953472L
ROLE_EXT_GM4_PLUS = ROLE_EXT_GM4 | ROLE_GML | ROLE_GMH
ROLE_EXT_GM3_PLUS = ROLE_EXT_GM3 | ROLE_EXT_GM4_PLUS
ROLE_EXT_GM2_PLUS = ROLE_EXT_GM2 | ROLE_EXT_GM3_PLUS
ROLE_EXT_GM1_PLUS = ROLE_EXT_GM1 | ROLE_EXT_GM2_PLUS
ROLE_ANY = 18446744073709551615L & ~(ROLE_IGB | ROLE_EXT_GM1_PLUS | ROLE_EXT_GM2_PLUS | ROLE_EXT_GM3_PLUS)
ROLEMASK_ELEVATEDPLAYER = ROLE_ANY & ~(ROLE_LOGIN | ROLE_PLAYER | ROLE_NEWBIE | ROLE_VIPLOGIN | ROLE_NEWSREPORTER | ROLE_CSMDELEGATE)
ROLEMASK_VIEW = ROLE_ADMIN | ROLE_CONTENT | ROLE_GML | ROLE_GMH | ROLE_QA | ROLE_EXT_GM1_PLUS
PRE_NONE = 0
PRE_AUTH = 1
PRE_HASCHAR = 2
PRE_HASSHIP = 4
PRE_INSTATION = 8
PRE_INFLIGHT = 16
