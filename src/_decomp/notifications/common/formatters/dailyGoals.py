#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\dailyGoals.py
import uuid
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class DailyGoalCompleted(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = GetByLabel('UI/DailyGoals/Notifications/DailyGoalCompletedHeader')
        notification.subtext = GetByLabel('UI/DailyGoals/Notifications/DailyGoalCompletedBody', goalName=notification.data['goalName'])

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'goalName': 'AIR Daily Goal',
         'goalID': uuid.uuid4()}


class MilestoneCompleted(BaseNotificationFormatter):

    def Format(self, notification):
        if notification.data['isOmega']:
            notification.subject = GetByLabel('Notifications/DailyGoals/RewardTrack/OmegaMilestoneRewardTitle')
            notification.subtext = GetByLabel('Notifications/DailyGoals/RewardTrack/OmegaMilestoneRewardDescription')
        else:
            notification.subject = GetByLabel('Notifications/DailyGoals/RewardTrack/AlphaMilestoneRewardTitle')
            notification.subtext = GetByLabel('Notifications/DailyGoals/RewardTrack/AlphaMilestoneRewardDescription')

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'isOmega': False}


class RewardTrackCompleted(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = GetByLabel('Notifications/DailyGoals/RewardTrack/AllMilestonesCompletedTitle')
        notification.subtext = GetByLabel('Notifications/DailyGoals/RewardTrack/AllMilestonesCompletedDescription')
