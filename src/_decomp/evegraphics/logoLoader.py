#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\logoLoader.py
from evegraphics.gateLogoConst import LOGO_BLACK_ICON_PATH

class LogoLoader:
    ALLIANCE = 1
    CORP = 2
    CEO = 3

    def __init__(self, logosToHandle):
        self.logosToHandle = logosToHandle
        self.logoIDs = {}
        self.logoIconPaths = {}

    def HasID(self, checkID):
        return checkID in self.logoIDs.itervalues()

    def Load(self, model, slimItem):
        allianceID = getattr(slimItem, 'allianceID', None)
        corpID = getattr(slimItem, 'corpID', None)
        corpInfo = sm.GetService('corp').GetCorporation(corpID) if corpID is not None else None
        ceoID = getattr(corpInfo, 'ceoID', None)
        self.logoIDs = {}
        self.logoIDs[LogoLoader.ALLIANCE] = allianceID
        self.logoIDs[LogoLoader.CORP] = corpID
        self.logoIDs[LogoLoader.CEO] = ceoID
        self.Update(model)

    def Update(self, model):
        photoSvc = sm.GetService('photo')
        iconSize = 128
        if LogoLoader.ALLIANCE in self.logosToHandle and self.logoIDs.get(LogoLoader.ALLIANCE, None) is not None:
            self.logoIconPaths[LogoLoader.ALLIANCE] = photoSvc.GetAllianceLogo(self.logoIDs[LogoLoader.ALLIANCE], iconSize, callback=True)
        else:
            self.logoIconPaths[LogoLoader.ALLIANCE] = LOGO_BLACK_ICON_PATH
        if LogoLoader.CORP in self.logosToHandle and self.logoIDs.get(LogoLoader.CORP, None) is not None:
            self.logoIconPaths[LogoLoader.CORP] = photoSvc.GetCorporationLogo(self.logoIDs[LogoLoader.CORP], iconSize, callback=True)
        else:
            self.logoIconPaths[LogoLoader.CORP] = LOGO_BLACK_ICON_PATH
        if LogoLoader.CEO in self.logosToHandle and self.logoIDs.get(LogoLoader.CEO, None) is not None:
            path = photoSvc.GetPortrait(self.logoIDs[LogoLoader.CEO], iconSize, callback=True)
            if path is None:
                path = photoSvc.GetPortraitDefaultIcon(iconSize)
            self.logoIconPaths[LogoLoader.CEO] = path
        else:
            self.logoIconPaths[LogoLoader.CEO] = LOGO_BLACK_ICON_PATH
        if model is not None:
            for param in model.externalParameters:
                if param.name == 'AllianceLogoResPath':
                    param.SetValue(self.logoIconPaths[LogoLoader.ALLIANCE])
                if param.name == 'CorpLogoResPath':
                    param.SetValue(self.logoIconPaths[LogoLoader.CORP])
                if param.name == 'CeoPortraitResPath':
                    param.SetValue(self.logoIconPaths[LogoLoader.CEO])
