#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\newFeatures\newFeatureNotify.py
import gametime
import uthread
from carbonui import uiconst
from eve.client.script.ui.shared.newFeatureNotifyWnd import NewFeatureNotifyWnd
from fsdBuiltData.common.newFeaturesFSDLoader import NewFeaturesFSDLoader
from newFeatures.feature import ReleasedFeature
from newFeatures.newFeatureConst import ISNEWUSER_DAYS_THRESHOLD
_features = None

def GetNewFeatures():
    features = [ feature for feature in _GetFeatures() if feature.IsShown() ]
    return sorted(features, key=_GetSortValue)


def _GetSortValue(feature):
    return (feature.GetReleaseDate(), feature.GetID())


def GetAvailableNewFeatures():
    features = [ feature for feature in _GetFeatures() if feature.IsApproriateToShow() ]
    return sorted(features, key=_GetSortValue)


def _GetFeatures():
    global _features
    if _features is None:
        _features = _ConstructFeatures()
    return _features


def _ConstructFeatures():
    return [ ReleasedFeature(featureID, fsdData) for featureID, fsdData in GetFSDData().iteritems() ]


def GetFSDData():
    fsd_loader = NewFeaturesFSDLoader()
    NewFeaturesFSDLoader.ConnectToOnReload(_OnFSDReloaded)
    return fsd_loader.GetData()


def _OnFSDReloaded(*args):
    global _features
    _features = None


def MarkAllAsSeen():
    for feature in _GetFeatures():
        feature.MarkAsSeen()


def MarkAllAsUnseen():
    for feature in _GetFeatures():
        feature.MarkAsUnseen()


def MarkAllAsForceShow():
    for feature in _GetFeatures():
        feature.MarkAsForceShow()


def CheckOpenNewFeatureNotifyWindow():
    newFeatures = GetNewFeatures()
    if not newFeatures:
        return False
    if not session.charid:
        return False
    uthread.new(OpenNewFeaturesWindow, newFeatures)
    return True


def OpenNewFeaturesWindow(newFeatures):
    wnd = NewFeatureNotifyWnd.Open(newFeatures=newFeatures)
    wnd.sr.underlay.SetState(uiconst.UI_HIDDEN)
    wnd.ShowDialog(modal=True, state=uiconst.UI_PICKCHILDREN, closeWhenClicked=True)


def UserIsTooNew():
    userCreateDate = sm.RemoteSvc('userSvc').GetCreateDate()
    daysSinceUserCreated = gametime.GetDaysSinceWallclockTime(userCreateDate)
    isTooNew = daysSinceUserCreated < ISNEWUSER_DAYS_THRESHOLD
    return isTooNew
