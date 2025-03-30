#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\wwiseSoundBanks.py
import wwiseSoundBanksLoader
from fsdBuiltData.common.base import BuiltDataLoader

class WwiseSoundBanks(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/wwiseSoundBanks.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/wwiseSoundBanks.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/wwiseSoundBanks.fsdbinary'
    __loader__ = wwiseSoundBanksLoader

    def __init__(self):
        super(WwiseSoundBanks, self).__init__()
        self.wwiseSoundBanksDict = self.TransformToDict()

    def TransformToDict(self):
        soundbankDict = {}
        soundbanks = self.GetData()
        for soundbankName, soundbankData in soundbanks.iteritems():
            soundbankDict[soundbankName] = {'EssentialMedia': soundbankData.EssentialMedia,
             'EssentialSoundBank': soundbankData.EssentialSoundBank,
             'wwiseID': soundbankData.wwiseID}

        return soundbankDict
