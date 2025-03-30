#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\marketutil\__init__.py
import collections
from skilllimits import GetSkillLimits
BestByOrder = collections.namedtuple('BestByOrder', ['price',
 'volRemaining',
 'typeID',
 'stationID'])

def ConvertTuplesToBestByOrders(bestOrdersByType):
    return {typeID:BestByOrder(*order) for typeID, order in bestOrdersByType.iteritems()}


OrderAllData = collections.namedtuple('OrderAllData', ['id',
 'issuer',
 'isIssuerCharacter',
 'isIssuerNpcCorp',
 'typeID',
 'price',
 'volRemaining',
 'volEntered',
 'minVolume',
 'range',
 'bid',
 'issueDate',
 'duration',
 'stationID',
 'structureID',
 'regionID',
 'solarSystemID',
 'accountID',
 'corporationID',
 'corporationWalletKeyID',
 'escrow',
 'state'])
