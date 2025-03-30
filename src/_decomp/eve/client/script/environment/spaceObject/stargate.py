#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\stargate.py
import eve.common.lib.appConst as const
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import evegraphics.gateLogoConst as lconst
import eve.client.script.ui.control.eveIcon as eveIcon
import logging
logger = logging.getLogger(__name__)

class StargateBannerModel(object):

    def __init__(self, destAllianceID, originAllianceID, targetSystemWarningIcon, logoList):
        self.destAllianceID = destAllianceID
        self.originAllianceID = originAllianceID
        self.targetSystemWarningIcon = targetSystemWarningIcon
        self.logoList = logoList


class Stargate(SpaceObject):

    def __init__(self):
        SpaceObject.__init__(self)
        self.lastActivationTime = 0
        self.activeStateDuration = 15 * const.SEC
        self.isDeactivationThreadRunning = False
        self.isActive = False
        self.deactivationCurve = None
        self.activationCurve = None
        self.lightningTransform = None
        self.arrivalCurve = None
        self.departureCurve = None
        self.bannerModel = None

    def _SetupStargateBanners(self):
        slimItem = self.typeData.get('slimItem')
        if slimItem is None:
            return
        self.bannerModel = StargateBannerModel(destAllianceID=slimItem.destinationSystemOwnerID, originAllianceID=slimItem.originSystemOwnerID, targetSystemWarningIcon=slimItem.destinationSystemWarningIcon, logoList=slimItem.destinationSystemStatusIcons or [])
        self.SetupStargateBanners(self.bannerModel)

    def SetupStargateBanners(self, bannerModel):
        model = self.GetModel()
        if model is None:
            return

        def _IsPlayerAlliance(allianceID):
            return allianceID >= lconst.MIN_PLAYER_ALLIANCE_ID

        photoSvc = sm.GetService('photo')
        iconSize = 128
        for param in model.externalParameters:
            if param.name == 'TargetSystemAllianceLogoResPath':
                targetAllianceLogoPath = lconst.LOGO_BLACK_ICON_PATH
                if bannerModel.destAllianceID:
                    if _IsPlayerAlliance(bannerModel.destAllianceID):
                        targetAllianceLogoPath = photoSvc.GetAllianceLogo(bannerModel.destAllianceID, iconSize, callback=True)
                    else:
                        targetAllianceLogoPath = eveIcon.LogoIcon.GetFactionIconTexturePath(bannerModel.destAllianceID, isSmall=False)
                param.SetValue(targetAllianceLogoPath)
            elif param.name == 'CurrentSystemAllianceLogoResPath':
                currentAllianceLogoPath = lconst.LOGO_BLACK_ICON_PATH
                if bannerModel.originAllianceID:
                    if _IsPlayerAlliance(bannerModel.originAllianceID):
                        currentAllianceLogoPath = photoSvc.GetAllianceLogo(bannerModel.originAllianceID, iconSize, callback=True)
                    else:
                        currentAllianceLogoPath = eveIcon.LogoIcon.GetFactionIconTexturePath(bannerModel.originAllianceID, isSmall=False)
                param.SetValue(currentAllianceLogoPath)
            elif param.name == 'TargetSystemVerticalBannerResPath':
                value = lconst.LOGO_BLACK_ICON_PATH
                if bannerModel.destAllianceID in lconst.FACTION_BANNERS:
                    value = lconst.FACTION_BANNER_DIR + lconst.FACTION_BANNERS[bannerModel.destAllianceID]
                param.SetValue(value)
            elif param.name == 'CurrentSystemVerticalBannerResPath':
                value = lconst.LOGO_BLACK_ICON_PATH
                if bannerModel.originAllianceID in lconst.FACTION_BANNERS:
                    value = lconst.FACTION_BANNER_DIR + lconst.FACTION_BANNERS[bannerModel.originAllianceID]
            elif param.name == 'TargetSystemStatusResPath':
                value = lconst.LOGO_BLACK_ICON_PATH
                if bannerModel.targetSystemWarningIcon:
                    value = lconst.SYSTEM_STATUS_DIR + bannerModel.targetSystemWarningIcon
                param.SetValue(value)
            elif param.name[:-8] == 'TargetSystemInfo':
                index = int(param.name[-8:-7])
                logo_path = lconst.LOGO_BLACK_ICON_PATH
                logoList = bannerModel.logoList
                if index < len(logoList) and logoList[index] and logoList[index] > -1:
                    logo_path = lconst.SYSTEM_STATUS_DIR + lconst.SYSTEM_STATUS_ICONS[logoList[index]]
                param.SetValue(logo_path)

    def OnAllianceLogoReady(self, allianceID, _size):
        if allianceID and (self.bannerModel.originAllianceID == allianceID or self.bannerModel.destAllianceID == allianceID):
            self._SetupStargateBanners()

    def OnSlimItemUpdated(self, slimItem):
        self.typeData['slimItem'] = slimItem
        self._SetupStargateBanners()
        self.SetControllerVariablesFromSlimItem(slimItem)

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True):
        SpaceObject.LoadModel(self, fileName, loadedModel, notify, addToScene)
        self._SetupStargateBanners()
        self.SetStaticRotation()
        sm.ScatterEvent('OnStargateModelLoaded', self)

    def Assemble(self):
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
