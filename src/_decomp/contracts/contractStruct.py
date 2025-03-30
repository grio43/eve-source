#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contracts\contractStruct.py


class ContractStruct(object):

    def __init__(self, contractType, isPrivate, assignedToID, minutesExpire, numDays, startStationID, destinationID, price, reward, collateral, title, description, itemList, startStationDivision, requestItemTypeList, forCorp, multiContract):
        self.contractType = contractType
        self.isPrivate = isPrivate
        self.assignedToID = assignedToID
        self.minutesExpire = minutesExpire
        self.numDays = numDays
        self.startStationID = startStationID
        self.destinationID = destinationID
        self.price = price
        self.reward = reward
        self.collateral = collateral
        self.title = title
        self.description = description
        self.itemList = itemList
        self.startStationDivision = startStationDivision
        self.requestItemTypeList = requestItemTypeList
        self.forCorp = forCorp
        self.multiContract = multiContract

    def __str__(self):
        members = dict(filter(lambda (k, v): not k.startswith('__'), self.__dict__.items()))
        return 'ContractStruct: %s' % members

    def __repr__(self):
        return '<%s>' % str(self)
