#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\CosmeticsLoader.py
from evegraphics.gateLogoConst import LOGO_BLACK_ICON_PATH
import logging
logger = logging.getLogger(__name__)

class CosmeticsLoader:
    CORP = 1
    ALLIANCE = 2

    def __init__(self, cosmeticsToHandle):
        self.cosmeticsToHandle = cosmeticsToHandle
        self.cosmeticIDs = {}
        self.logoIconPaths = {}

    def HasID(self, checkID):
        return checkID in self.cosmeticIDs.itervalues()

    def Load(self, model, slimItem):
        allianceID = getattr(slimItem, 'allianceID', None)
        corpID = getattr(slimItem, 'corpID', None)
        self.cosmeticIDs = {}
        self.cosmeticIDs[CosmeticsLoader.ALLIANCE] = allianceID
        self.cosmeticIDs[CosmeticsLoader.CORP] = corpID
        if hasattr(slimItem, 'cosmeticsItems'):
            cosmetics = slimItem.cosmeticsItems
        else:
            cosmetics = []
        self.Update(model, cosmeticItems=cosmetics)

    def Update(self, model, cosmeticItems):
        if sm.GetService('cosmeticsSvc').are_ship_emblems_disabled():
            cosmeticItems = []
        if cosmeticItems is None:
            return
        photoSvc = sm.GetService('photo')
        iconSize = 512
        if CosmeticsLoader.ALLIANCE in cosmeticItems and self.cosmeticIDs.get(CosmeticsLoader.ALLIANCE, None) is not None:
            self.logoIconPaths[CosmeticsLoader.ALLIANCE] = photoSvc.GetAllianceLogo(self.cosmeticIDs[CosmeticsLoader.ALLIANCE], iconSize, callback=True)
        else:
            self.logoIconPaths[CosmeticsLoader.ALLIANCE] = LOGO_BLACK_ICON_PATH
        if CosmeticsLoader.CORP in cosmeticItems and self.cosmeticIDs.get(CosmeticsLoader.CORP, None) is not None:
            self.logoIconPaths[CosmeticsLoader.CORP] = photoSvc.GetCorporationLogo(self.cosmeticIDs[CosmeticsLoader.CORP], iconSize, callback=True)
        else:
            self.logoIconPaths[CosmeticsLoader.CORP] = LOGO_BLACK_ICON_PATH
        if model is not None:
            for param in model.externalParameters:
                if param.name == 'AllianceLogoResPath':
                    param.SetValue(self.logoIconPaths[CosmeticsLoader.ALLIANCE])
                if param.name == 'CorpLogoResPath':
                    param.SetValue(self.logoIconPaths[CosmeticsLoader.CORP])

    def SetCosmeticsOnShip(self, shipModel, enabledCosmetics):
        if sm.GetService('cosmeticsSvc').are_ship_emblems_disabled():
            enabledCosmetics = []
        photoSvc = sm.GetService('photo')
        iconSize = 512
        logoIconPaths = {}
        if CosmeticsLoader.ALLIANCE in enabledCosmetics:
            logoIconPaths[CosmeticsLoader.ALLIANCE] = photoSvc.GetAllianceLogo(session.allianceid, iconSize, callback=True)
        else:
            logoIconPaths[CosmeticsLoader.ALLIANCE] = LOGO_BLACK_ICON_PATH
        if CosmeticsLoader.CORP in enabledCosmetics:
            logoIconPaths[CosmeticsLoader.CORP] = photoSvc.GetCorporationLogo(session.corpid, iconSize, callback=True)
        else:
            logoIconPaths[CosmeticsLoader.CORP] = LOGO_BLACK_ICON_PATH
        if shipModel is not None:
            for param in shipModel.externalParameters:
                if param.name == 'AllianceLogoResPath':
                    param.SetValue(logoIconPaths[CosmeticsLoader.ALLIANCE])
                if param.name == 'CorpLogoResPath':
                    param.SetValue(logoIconPaths[CosmeticsLoader.CORP])
