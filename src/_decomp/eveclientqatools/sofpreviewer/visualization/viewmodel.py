#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\visualization\viewmodel.py


class RightViewModel(object):

    def __init__(self, model):
        self.currentResPathInsert = None
        self.currentDirtLevel = None
        self.sofVariants = model.sofVariants
        self.currentVariant = 'None'
