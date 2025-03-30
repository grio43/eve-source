#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\labelOverride.py
import logging
import os
import blue
import eveLocalization
import fsd
import localizationcache
from localization import const as locconst
from localization.parser import _Tokenize
APP_DATA_DIR = fsd.AbsJoin(blue.sysinfo.GetUserApplicationDataDirectory(), 'CCP', 'EVE')
APP_DATA_FILE = fsd.AbsJoin(APP_DATA_DIR, 'labelOverride.txt')
logger = logging.getLogger(__name__)

def Coerce(key):
    return str(key).lower()


def SetConfigValue(value):
    if not os.path.exists(APP_DATA_DIR):
        os.makedirs(APP_DATA_DIR)
    with open(APP_DATA_FILE, 'w+') as f:
        f.write(value)


def GetConfigValue():
    if os.path.exists(APP_DATA_FILE):
        with open(APP_DATA_FILE, 'r') as f:
            value = f.read()
        return value == 'true'
    return False


def EnableLabelOverride():
    SetConfigValue('true')
    logger.info('Localization label live reload is now enabled')


def DisableLabelOverride():
    SetConfigValue('false')
    logger.info('Localization label live reload is now disabled')


def GetByLabelFromSource(labelNameAndPath, languageID = None, **kwargs):
    path, labelName = GetPathAndLabel(labelNameAndPath)
    groupMessages = localizationcache.LoadGroup(path)
    for messageID, message in groupMessages.iteritems():
        messageLabel = message.get('label', None)
        if labelName == messageLabel:
            return ParseMessage(message['baseText']['text'], **kwargs)

    logger.warning('Unable to find message for {} with override function, falling back to binaries'.format(labelNameAndPath))


def InitializeLocalizationCache():
    if not InitializeLocalizationCache.called:
        InitializeLocalizationCache.called = True
        storage = localizationcache.Storage(Coerce)
        storage.initializeFileIndex()


InitializeLocalizationCache.called = False

def GetPathAndLabel(labelNameAndPath):
    if labelNameAndPath[0] == '/':
        labelNameAndPath = labelNameAndPath[1:]
    labelList = labelNameAndPath.split('/')
    labelPath = labelList[:-1]
    labelName = labelList[-1]
    path = labelPath if labelList[0] == 'Carbon' else ['EVE'] + labelPath
    path = '/'.join(path).lower()
    return (path, labelName)


def ParseMessage(messageText, **kwargs):
    if not isinstance(messageText, unicode):
        messageText = messageText.decode('utf8')
    tags = _Tokenize(messageText)
    return eveLocalization.Parse(messageText, locconst.LOCALE_SHORT_ENGLISH, tags, **kwargs)
