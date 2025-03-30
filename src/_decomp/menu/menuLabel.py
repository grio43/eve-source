#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menu\menuLabel.py
from localization import GetByLabel, GetByMessageID

class MenuLabel(tuple):

    def __new__(cls, text, kw = None):
        if kw is None:
            kw = {}
        return tuple.__new__(cls, (text, kw))

    def GetText(self):
        if isinstance(self.labelPath, int):
            return GetByMessageID(self.labelPath, **self.labelKeywords)
        return GetByLabel(self.labelPath, **self.labelKeywords)

    @property
    def labelPath(self):
        return self[0]

    @property
    def labelKeywords(self):
        return self[1]
