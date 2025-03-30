#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\materialselection\viewmodel.py


class MaterialSelectionViewModel(object):

    def __init__(self, model):
        self.sofMaterials = model.sofMaterials
        self.currentMat = ['None',
         'None',
         'None',
         'None']
        self.currentPatternMat = ['None', 'None']
