#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\npcStandingChangedNotificationFormatter.py
from eve.common.script.util.standingUtil import RoundStandingChange
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import localization

class NPCStandingChangedNotificationFormatter(BaseNotificationFormatter):

    def __init__(self):
        super(NPCStandingChangedNotificationFormatter, self).__init__()

    def Format(self, notification):
        first_standing_change = notification.data[0]
        first_raw_change = first_standing_change[2]
        real_standing_change = RoundStandingChange(first_raw_change * 10.0)
        if real_standing_change > 0:
            subjectLabel = 'Tooltips/Standings/StandingsIncreaseSubject'
            subtextLabel = 'Tooltips/Standings/StandingsIncreaseSubtext'
        else:
            subjectLabel = 'Tooltips/Standings/StandingsDecreaseSubject'
            subtextLabel = 'Tooltips/Standings/StandingDecreaseSubtext'
        notification.subject = localization.GetByLabel(subjectLabel)
        notification.subtext = localization.GetByLabel(subtextLabel, ownerID=notification.senderID, amount=real_standing_change, numOthers=len(notification.data) - 1)
        return notification
