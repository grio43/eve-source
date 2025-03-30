#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\seasons.py
from carbon.common.script.util.format import FmtAmt
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
from localization import GetByLabel, GetByMessageID

class SeasonalChallengeCompletedFormatter(BaseNotificationFormatter):

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel='Notifications/SeasonalChallengeCompletedSubject', subtextLabel='Notifications/SeasonalChallengeCompletedSubtext')

    def Format(self, notification):
        data = notification.data
        points_awarded = data.get('points_awarded')
        message_text = data.get('message_text', None)
        if message_text is None:
            notification.subject = GetByLabel(self.subjectLabel, points_awarded=points_awarded)
            notification.subtext = GetByLabel(self.subtextLabel)
        else:
            notification.subject = GetByLabel(self.subjectLabel, points_awarded=points_awarded)
            progress_text = data.get('progress_text')
            max_progress = data.get('max_progress')
            challenge_name = GetByMessageID(message_text)
            achievement_text = '%s %s' % (FmtAmt(max_progress), GetByMessageID(progress_text))
            body_text = '%s<br/>%s' % (challenge_name, achievement_text)
            notification.subtext = challenge_name
            notification.body = body_text
