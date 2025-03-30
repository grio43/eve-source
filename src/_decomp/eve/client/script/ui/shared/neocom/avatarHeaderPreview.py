#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\avatarHeaderPreview.py
import logging
from carbonui.util.color import Color
from eve.client.script.ui.shared.preview import PreviewContainer, CharacterSceneContext, PreviewSceneContainer, PreviewNavigation
from eve.common.lib import appConst as const
import blue
import carbonui.const as uiconst
import charactercreator.const as ccConst
import trinity
import uthread
stdlog = logging.getLogger(__name__)

class AvatarHeaderPreview(PreviewContainer):
    __notifyevents__ = ['OnUIColorsChanged', 'OnGraphicSettingsChanged', 'OnSetDevice']

    def __init__(self, **kwargs):
        self.previewCharThread = None
        super(AvatarHeaderPreview, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        PreviewContainer.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        dna = sm.RemoteSvc('paperDollServer').GetPaperDollData(session.charid)
        if not self.previewCharThread:
            self.previewCharThread = uthread.new(self.PreviewCharacter, session.charid, dna=dna)

    def PreviewCharacter(self, charID, dna = None, apparel = None, background = None):
        if self.destroyed:
            self.previewCharThread = None
            return
        context = AvatarHeaderPreviewContext(charID, dna=dna, apparel=apparel)
        self.LoadScene(context)
        self.previewCharThread = None

    def LoadScene(self, context, force = False):
        while self.sceneContainer.viewport.width == 1 or self.sceneContainer.viewport.height == 1:
            blue.synchro.Yield()

        PreviewContainer.LoadScene(self, context, force)
        if not self.destroyed:
            self.UpdateLights()

    def UpdateLights(self):
        lights = self.sceneContainer.scene.lights
        color = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHTGLOW)
        lights[0].color = Color(*color).SetSaturation(0.05).GetRGBA()
        lights[2].color = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHTGLOW)
        lights[3].color = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHTGLOW)

    def _OnResize(self, *args, **kw):
        if not self.previewCharThread:
            self.UpdateViewPort()

    def OnUIColorsChanged(self):
        self.UpdateLights()

    def OnSetDevice(self):
        if hasattr(self, 'sceneContainer') and self.sceneContainer is not None and hasattr(self.sceneContainer, 'renderJob') and self.sceneContainer.renderJob is not None:
            self.sceneContainer.renderJob.RebuildPostprocess()
        if not self.previewCharThread:
            self.UpdateViewPort()

    def DisableRender(self):
        if not self.previewCharThread:
            self.sceneContainer.renderJob.Disable()

    def EnableRender(self):
        if not self.previewCharThread:
            self.sceneContainer.renderJob.Enable()

    def ConstructSceneContainer(self):
        self.sceneContainer = AvatarHeaderSceneContainer(parent=self, align=uiconst.TOALL)

    def _Cleanup(self):
        try:
            self.sceneContainer = None
            self.ConstructSceneContainer()
            self.sceneContainer.Startup()
            self.navigation = None
            self.navigation = PreviewNavigation(parent=self)
            self.navigation.Startup(self.sceneContainer)
            if self.previewCharThread:
                self.previewCharThread.kill()
                self.previewCharThread = None
        except TaskletExit:
            pass

        super(AvatarHeaderPreview, self)._Cleanup()


class AvatarHeaderSceneContainer(PreviewSceneContainer):

    def UpdateViewPort(self, *args):
        self.camera.fov = self.viewport.height / 4000.0
        PreviewSceneContainer.UpdateViewPort(self, *args)


class AvatarHeaderPreviewContext(CharacterSceneContext):

    def SetupCamera(self, sceneContainer):
        CharacterSceneContext.SetupCamera(self, sceneContainer)
        cam = sceneContainer.camera
        cam.verticalOffset = -1.0
        if self.character.doll.gender == 'female':
            cam.SetEyePosition((-0.24811527132987976, 1.4142124235630034, 5.934291362762451))
            cam.SetAtPosition((0.011998310685157776, 1.8277159810066221, -0.020278582349419594))
        else:
            cam.SetEyePosition((-0.3404092073440552, 1.5400760936737061, 7.255154972076416))
            cam.SetAtPosition((-0.01654062792658806, 1.9754442143440247, -0.01789170503616333))

    def PrepareCharacterAnimation(self, avatar, gender):

        def _Prepare():
            trinity.WaitForResourceLoads()
            while not animation.IsFullyLoaded():
                blue.synchro.Yield()

            animation.InstantiateCharacter()
            avatar.animationUpdater = animation

        animation = trinity.Tr2GStateAnimation()
        genderStr = 'Female' if gender == ccConst.GENDERID_FEMALE else 'Male'
        animation.gStateResPath = str('res:/Animation/CharacterCreatorV2/Gstate/%s_CharacterSheet.gsf' % genderStr)
        uthread.new(_Prepare)

    def GetSceneFile(self, charInfo):
        if charInfo.raceID == const.raceAmarr:
            return 'res:/Graphics/Interior/characterSheet/CharacterSheetAmarr.red'
        elif charInfo.raceID == const.raceCaldari:
            return 'res:/Graphics/Interior/characterSheet/CharacterSheetCaldari.red'
        elif charInfo.raceID == const.raceGallente:
            return 'res:/Graphics/Interior/characterSheet/CharacterSheetGallente.red'
        elif charInfo.raceID == const.raceMinmatar:
            return 'res:/Graphics/Interior/characterSheet/CharacterSheetMinmatar.red'
        else:
            return super(AvatarHeaderPreviewContext, self).GetSceneFile(charInfo)

    def GetBackground(self):
        return None
