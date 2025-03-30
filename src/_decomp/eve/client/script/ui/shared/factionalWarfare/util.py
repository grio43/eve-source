#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\util.py


def OpenEnlistmentFlowIfUnseen():
    if session.warfactionid is None and settings.user.ui.Get('autoOpenEnlistmentWindow', True):
        settings.user.ui.Set('autoOpenEnlistmentWindow', False)
        sm.GetService('cmd').OpenFwEnlistment()
    elif session.warfactionid is not None and settings.user.ui.Get('autoOpenEnlistmentWindow', True):
        settings.user.ui.Set('autoOpenEnlistmentWindow', False)
