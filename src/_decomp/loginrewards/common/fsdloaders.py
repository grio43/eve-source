#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\common\fsdloaders.py
from fsdBuiltData.common.base import BuiltDataLoader

class CampaignDoesNotExistError(RuntimeError):
    pass


try:
    import seasonalCampaignsLoginRewardsLoader
except ImportError:
    seasonalCampaignsLoginRewardsLoader = None

class SeasonalCampaignsBuiltDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/seasonalCampaignsLoginRewards.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/seasonalCampaignsLoginRewards.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/seasonalCampaignsLoginRewards.fsdbinary'
    __loader__ = seasonalCampaignsLoginRewardsLoader


class SeasonalCampaignsStaticData(object):

    @staticmethod
    def _get_data():
        loader = SeasonalCampaignsBuiltDataLoader()
        data = loader.GetData()
        return data

    def get_campaign(self, campaign_id):
        data = self._get_data()
        if campaign_id not in data:
            raise CampaignDoesNotExistError('Trying to load a campaign (%s) that does not exist.' % campaign_id)
        return data[campaign_id]

    def get_campaigns(self):
        return self._get_data()


try:
    import loginCampaignsLoginRewardsLoader
except ImportError:
    loginCampaignsLoginRewardsLoader = None

class LoginCampaignsBuiltDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/loginCampaignsLoginRewards.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/loginCampaignsLoginRewards.fsdbinary'
    __loader__ = loginCampaignsLoginRewardsLoader


class LoginCampaignsStaticData(object):

    @staticmethod
    def _get_data():
        loader = LoginCampaignsBuiltDataLoader()
        data = loader.GetData()
        return data

    def get_campaign(self, campaign_id):
        data = self._get_data()
        if campaign_id not in data:
            raise CampaignDoesNotExistError('Trying to load a campaign (%s) that does not exist.' % campaign_id)
        return data[campaign_id]

    def get_campaigns(self):
        return self._get_data()


try:
    import currencyBucketsLoader
except ImportError:
    currencyBucketsLoader = None

class CurrencyBucketsBuiltDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/currencyBuckets.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/currencyBuckets.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/currencyBuckets.fsdbinary'
    __loader__ = currencyBucketsLoader


class CurrencyBucketsStaticData(object):

    @staticmethod
    def _get_data():
        loader = CurrencyBucketsBuiltDataLoader()
        data = loader.GetData()
        return data

    def get_bucket(self, bucket_id):
        data = self._get_data()
        return data[bucket_id]
