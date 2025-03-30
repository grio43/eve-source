#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\baseFormatter.py


class BaseNotificationFormatter(object):

    def __init__(self, subjectLabel = None, bodyLabel = None, subtextLabel = None):
        self.subjectLabel = subjectLabel
        self.bodyLabel = bodyLabel
        self.subtextLabel = subtextLabel

    def Format(self, notification):
        pass

    @staticmethod
    def MakeSampleData(variant = 0):
        return {}

    @staticmethod
    def GetSampleSender():
        return 98000001

    def GetLocalizationImpl(self, localizationInject):
        if localizationInject is None:
            import localization
            localizationInject = localization
        return localizationInject
