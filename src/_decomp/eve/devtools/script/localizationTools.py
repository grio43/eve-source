#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\localizationTools.py
import blue
import subprocess
import localization
from localization.const import DATATYPE_FSD

def RebuildFSDLocalizationPickles():
    batchPath = blue.paths.ResolvePath('root:/tools/staticData/build/localization/RebuildAll_nopause.bat')
    return subprocess.Popen([batchPath, '2>&1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def ReloadFSDLocalizationPickle():
    langList = localization._ReadLocalizationMainPickle('root:/autobuild/localizationFSD/EVE/localization_fsd_main.pickle', DATATYPE_FSD)
    readRtr = localization._ReadLocalizationLanguagePickles('root:/autobuild/localizationFSD/EVE/localization_fsd_', langList, DATATYPE_FSD)
    return readRtr
