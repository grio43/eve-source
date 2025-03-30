#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\ccpDevNews.py
from baseFormatter import BaseNotificationFormatter

class CCPDevNewsFormatter(BaseNotificationFormatter):

    def __init__(self, subjectLabel = None, bodyLabel = None, subtextLabel = None):
        super(CCPDevNewsFormatter, self).__init__()
        self.subjectLabel = subjectLabel
        self.bodyLabel = bodyLabel
        self.subtextLabel = subtextLabel

    def Format(self, notification):
        notification.subject = notification.data.get('title', None)
        notification.body = notification.data.get('text', None)
        return notification
