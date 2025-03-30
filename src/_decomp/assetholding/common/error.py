#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\assetholding\common\error.py


class AssetHoldingError(RuntimeError):

    def __init__(self, request, status_code):
        super(AssetHoldingError, self).__init__(self)
        self.message = '{request} returning with status code {status_code}'.format(request=request, status_code=status_code)

    def __str__(self):
        return self.message
