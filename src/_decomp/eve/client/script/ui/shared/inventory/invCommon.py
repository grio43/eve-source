#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\invCommon.py
CONTAINERGROUPS = (const.groupCargoContainer,
 const.groupSecureCargoContainer,
 const.groupAuditLogSecureContainer,
 const.groupFreightContainer)

def SortData(data):
    data.sort(key=lambda x: x.GetLabel().lower())
