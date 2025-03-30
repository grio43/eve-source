#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\navigation_systemmap.py
import evecamera
import trinity
import blue
import geo2
import carbonui.const as uiconst
import log
from carbonui.control.layer import LayerCore
from carbonui.uicore import uicore
from eve.client.script.ui.shared.maps import maputils
from eve.client.script.ui.shared.maps.mapcommon import SYSTEMMAP_SCALE

class SystemMapLayer(LayerCore):
    __update_on_reload__ = 0
    default_align = uiconst.TOALL
    default_cursor = uiconst.UICURSOR_DRAGGABLE
    activeManipAxis = None
    _isPicked = False

    def SetInterest(self, itemID, interpolate = True):
        solarsystem = sm.GetService('systemmap').GetCurrentSolarSystem()
        if solarsystem is None:
            log.LogTrace('No solar system (SystemmapNav::SetInterest)')
            return
        endPos = None
        for tf in solarsystem.children:
            tfName = getattr(tf, 'name', None)
            if tfName is None:
                continue
            if tfName.startswith('systemParent_'):
                for stf in tf.children:
                    stfName = getattr(stf, 'name', None)
                    if stfName is None:
                        continue
                    try:
                        prefix, stfItemID = stfName.split('_')
                        if prefix == 'scanResult':
                            stfItemID = ('result', stfItemID)
                        else:
                            stfItemID = int(stfItemID)
                    except:
                        continue

                    if stfItemID == itemID:
                        endPos = stf.worldTransform[3][:3]
                        break

                if endPos:
                    break
            elif tfName.startswith('bm_') and isinstance(itemID, tuple) and itemID[0] == 'bookmark':
                tfItemID = int(tfName.split('_')[1])
                if tfItemID == itemID[1]:
                    endPos = tf.worldTransform[3][:3]
                    break
            elif tfName.endswith(str(itemID)):
                endPos = tf.worldTransform[3][:3]
                break

        if endPos is None and itemID == eve.session.shipid:
            endPos = maputils.GetMyPos()
            endPos.Scale(SYSTEMMAP_SCALE)
            endPos = (endPos.x, endPos.y, endPos.z)
        self.FocusOnTrinityPoint(endPos, interpolate=interpolate)

    def FocusOnPoint(self, endPos):
        scaledEndPos = geo2.Vec3Scale(endPos, SYSTEMMAP_SCALE)
        self.FocusOnTrinityPoint(scaledEndPos)

    def FocusOnTrinityPoint(self, triVector, interpolate = True):
        if triVector and interpolate:
            now = blue.os.GetSimTime()
            cameraParent = self.GetCameraParent()
            if cameraParent.translationCurve:
                startPos = cameraParent.translationCurve.GetVectorAt(now)
                startPos = (startPos.x, startPos.y, startPos.z)
            else:
                startPos = cameraParent.translation
            vc = trinity.Tr2CurveVector3()
            vc.AddKey(0.0, startPos)
            vc.AddKey(0.5, triVector)
            cameraParent.translationCurve = trinity.Tr2TranslationAdapter()
            cameraParent.translationCurve.curve = vc
            cameraParent.useCurves = 1
        elif triVector:
            cameraParent = self.GetCameraParent()
            cameraParent.translationCurve = None
            cameraParent.translation = triVector

    def GetCameraParent(self):
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
        return camera.GetCameraParent()

    def OnMouseMove(self, *args):
        self.sr.hint = ''
        lib = uicore.uilib
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
        dx = lib.dx
        dy = lib.dy
        if not self._isPicked:
            return
        if lib.leftbtn and not lib.rightbtn:
            fov = camera.fieldOfView
            camera.OrbitParent(-dx * fov * 0.1, dy * fov * 0.1)
            sm.GetService('systemmap').SortBubbles()
        elif lib.rightbtn and not lib.leftbtn:
            cameraParent = self.GetCameraParent()
            if cameraParent.translationCurve:
                pos = cameraParent.translationCurve.GetVectorAt(blue.os.GetSimTime())
                cameraParent.translationCurve = None
                cameraParent.translation = (pos.x, pos.y, pos.z)
            scalefactor = camera.translationFromParent * (camera.fieldOfView * 0.001)
            offset = (dx * scalefactor, -dy * scalefactor, 0.0)
            offset = geo2.QuaternionTransformVector(camera.rotationAroundParent, offset)
            cameraParent.translation = geo2.Vec3Subtract(cameraParent.translation, offset)
        elif lib.leftbtn and lib.rightbtn:
            modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
            camera.Dolly(modifier * -(dy * 0.01) * abs(camera.translationFromParent))
            camera.translationFromParent = camera.CheckTranslationFromParent(camera.translationFromParent)

    def OnMouseEnter(self, *args):
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN

    def OnMouseDown(self, button):
        systemmap = sm.GetService('systemmap')
        self._isPicked = True
        self.SetOrder(0)
        systemmap.CollapseBubbles()
        systemmap.SortBubbles()

    def OnMouseUp(self, button):
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if not (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            self._isPicked = False
        if button == 1:
            self.SetOrder(-1)
            return
        self.SetOrder(-1)
        sm.GetService('systemmap').SortBubbles()
        sm.GetService('ui').ForceCursorUpdate()

    def OnMouseWheel(self, *args):
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        self.ZoomBy(modifier * uicore.uilib.dz)
        return 1

    def ZoomBy(self, amount):
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
        camera.Dolly(amount * 0.001 * abs(camera.translationFromParent))
        camera.translationFromParent = camera.CheckTranslationFromParent(camera.translationFromParent)

    def _OnClose(self):
        pass
