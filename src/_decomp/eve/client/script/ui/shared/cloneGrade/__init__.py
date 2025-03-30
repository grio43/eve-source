#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\__init__.py
from launchdarkly.client.featureflag import create_boolean_flag_check
ORIGIN_CHARACTERSHEET = 'charactersheet'
ORIGIN_INDUSTRY = 'industryWnd'
ORIGIN_INVENTORY = 'inventory'
ORIGIN_SHIPTREE = 'shipTree'
ORIGIN_MARKET = 'RegionalMarket'
ORIGIN_BUYONMARKET = 'marketbuyaction'
ORIGIN_SHOWINFO = 'showinfo'
ORIGIN_LAPSENOTIFYWINDOW = 'lapseNotifyWindow'
ORIGIN_SKILLQUEUETIMELINE = 'skillQueueTimeline'
ORIGIN_TRAININGSPEEDICON = 'trainingSpeedIcon'
ORIGIN_SKILLREQUIREMENTSTOOLTIP = 'skillRequirementsTooltip'
ORIGIN_SKILLPLANBUTTON = 'skillPlanButton'
ORIGIN_CHARACTERSELECTION = 'characterSelection'
ORIGIN_AGENTS = 'agents'
ORIGIN_SEASONALREWARDS = 'seasonalRewards'
REASON_DEFAULT = 'default'
ORIGIN_SKILLPLAN = 'skillPlan'
ORIGIN_SHIPRESTRICTIONS = 'shipRestrictions'
ORIGIN_SHIP_SKINR = 'shipSKINR'
ORIGIN_SKILLREQ_PANEL = 'skillRequirementPanel'
ORIGIN_OPPORTUNITIES = 'opportunitiesWindow'
ORGIN_AGENCY_MERCDEN = 'agencyMercDen'
ORGIN_MY_MERCDENS = 'myMercenaryDens'
use_new_omega_window = create_boolean_flag_check(launchdarkly_key='new-omega-upgrade-window-enabled', fallback_value=True)

def open_omega_upgrade_window(origin = None, reason = None):
    if use_new_omega_window():
        from .cloneStateWindow import open_upgrade_window
        open_upgrade_window(origin=origin, reason=reason)
    else:
        from .cloneUpgradeWindow import CloneUpgradeWindow
        CloneUpgradeWindow.Open(origin=origin, reason=reason)


def open_omega_state_window():
    if use_new_omega_window():
        from .cloneStateWindow import open_omega_state_window
        open_omega_state_window()
    else:
        from .cloneUpgradeWindow import CloneUpgradeWindow
        CloneUpgradeWindow.ShowFanfare()


def open_alpha_state_window():
    if use_new_omega_window():
        from .cloneStateWindow import open_alpha_state_window
        open_alpha_state_window()
    else:
        from .lapseNotifyWindow import LapseNotifyWindow
        wnd = LapseNotifyWindow.Open()
        wnd.ShowModal()
