#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\graphics\paperDollClient.py
import telemetry
import eve.common.script.paperDoll.paperDollConfiguration as pdCfg
import eve.client.script.paperDoll.paperDollImpl as pdImp
import evegraphics.settings as gfxsettings
from charactercreator.const import TEXTURE_RESOLUTIONS
from carbon.client.script.graphics.paperDollClient import PaperDollClient

class EvePaperDollClient(PaperDollClient):
    __guid__ = 'svc.evePaperDollClient'
    __replaceservice__ = 'paperDollClient'
    __notifyevents__ = PaperDollClient.__notifyevents__ + ['OnGraphicSettingsChanged']
    __dependencies__ = PaperDollClient.__dependencies__ + ['character', 'device']

    def Run(self, *etc):
        PaperDollClient.Run(self, *etc)
        kicker = self.dollFactory

    def _AppPerformanceOptions(self):
        pdCfg.PerformanceOptions.EnableEveOptimizations()

    @telemetry.ZONE_METHOD
    def GetDollDNA(self, scene, entity, dollGender, dollDnaInfo, bloodlineID):
        return self.character.GetDNAFromDBRowsForEntity(entity.entityID, dollDnaInfo, dollGender, bloodlineID)

    def GetInitialTextureResolution(self):
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        return TEXTURE_RESOLUTIONS[textureQuality]

    @telemetry.ZONE_METHOD
    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.GFX_CHAR_TEXTURE_QUALITY in changes:
            textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
            resolution = TEXTURE_RESOLUTIONS[textureQuality]
            for character in self.paperDollManager:
                character.doll.SetTextureSize(resolution)
                character.doll.buildDataManager.SetAllAsDirty()
                character.Update()
