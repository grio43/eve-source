#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\charactercreator\client\animparams.py
import trinity
import uthread
from carbonui.uicore import uicore
import blue
from animparams_const import *
import log

class AnimParams(object):

    def __init__(self, avatar, charID = None, doll = None, factory = None):
        self.factory = factory
        self.doll = doll
        self.id_to_value_dict = {}
        id_to_name = list(enumerate(CONTROL_PARAM_LIST))
        self.id_to_name_dict = dict(id_to_name)
        ids, names = zip(*id_to_name)
        self.name_to_id_dict = dict(zip(names, ids))
        self.update = True
        self.last_id = max(ids)
        self.avatar = avatar
        self.rebuilding = False
        self.lastNetworkMode = -1
        self.lastPortraitPose = -1
        if charID is None:
            if hasattr(uicore, 'layer'):
                self.charID = uicore.layer.charactercreation.controller.GetInfo().charID
            else:
                self.charID = 0
        else:
            self.charID = charID
        self.characterSvc = sm.GetServiceIfRunning('character')
        gender = avatar.visualModel.geometryResPath.lower()
        for param in ccconst.FACE_POSE_CONTROLPARAMS:
            self.InitParameter(param[0], param[1])

        if 'female' in gender:
            self.InitParameter('ControlParameters|HeadLookTarget', (0.0, 1.5, 0.5))
        else:
            self.InitParameter('ControlParameters|HeadLookTarget', (0.0, 1.6, 0.5))
        self.InitParameter('ControlParameters|PuckerLips', 0.0)
        self.InitParameter('ControlParameters|IsAlive', 1)
        self.InitParameter('ControlParameters|NetworkMode', 1)

    def InitParameter(self, name, value):
        if name not in self.name_to_id_dict:
            self.last_id += 1
            self.name_to_id_dict[name] = self.last_id
            self.id_to_name_dict[self.last_id] = name
        self.id_to_value_dict[self.name_to_id_dict[name]] = value

    def SetControlParameter(self, name, value):
        if name not in self.name_to_id_dict:
            self.last_id += 1
            self.name_to_id_dict[name] = self.last_id
            self.id_to_name_dict[self.last_id] = name
        if value != self.id_to_value_dict.get(self.name_to_id_dict[name]):
            self.id_to_value_dict[self.name_to_id_dict[name]] = value
        self.ProcessControlParameter(self.name_to_id_dict[name])

    def GetControlParameter(self, name):
        if name in self.name_to_id_dict:
            if self.name_to_id_dict[name] not in self.id_to_value_dict:
                self.id_to_value_dict[self.name_to_id_dict[name]] = 0.0
            return self.id_to_value_dict[self.name_to_id_dict[name]]

    def GetControlParameterValue(self, name):
        return self.GetControlParameter(name)

    def SetControlParameterByID(self, id, args):
        self.id_to_value_dict[id] = args
        if id > self.last_id:
            self.last_id = id
        self.ProcessControlParameter(id)

    def GetControlParameterValueByID(self, id):
        if id not in self.id_to_value_dict:
            self.id_to_value_dict[id] = 0.0
        return self.id_to_value_dict[id]

    def GetControlParameterName(self, id):
        for name in self.name_to_id_dict:
            if id == self.name_to_id_dict[name]:
                return name

        return 'Unknown'

    def GetControlParameterID(self, name):
        return self.name_to_id_dict[name]

    def GetAllControlParameters(self):
        return self.name_to_id_dict

    def GetAllEventIDs(self):
        return {}

    def GetAllRequestIDs(self):
        return {}

    def GetRequests(self):
        return []

    def GetAllEventTrackIDs(self):
        return {}

    def ProcessControlParameter(self, id):
        value = self.id_to_value_dict.get(id)
        if value is None:
            return
        if '|NetworkMode' in self.id_to_name_dict[id]:
            log.LogWarn('Setting network mode to %s' % value)
            if value == NETWORKMODE_PORTRAIT and type(self.avatar.animationUpdater) != trinity.Tr2GrannyAnimation:
                self.Rebuild()
            elif value != NETWORKMODE_PORTRAIT and type(self.avatar.animationUpdater) != trinity.Tr2GStateAnimation:
                self.Rebuild()
        if '|PortraitPoseNumber' in self.id_to_name_dict[id]:
            if self.GetControlParameter('ControlParameters|NetworkMode') == 2:
                self.Rebuild()
        if '|OrientChar' in self.id_to_name_dict[id]:
            uthread.new(BaseParamHandler, value, self)
        if '|BrowLeftCurl' in self.id_to_name_dict[id]:
            uthread.new(TwoLayerParamHandler, value, self, 'ControlParameters|BrowLeftCurlDown', 'ControlParameters|BrowLeftCurlUp')
        if '|BrowRightCurl' in self.id_to_name_dict[id]:
            uthread.new(TwoLayerParamHandler, value, self, 'ControlParameters|BrowRightCurlDown', 'ControlParameters|BrowRightCurlUp')
        if '|BrowLeftUpDown' in self.id_to_name_dict[id]:
            uthread.new(TwoLayerParamHandler, value, self, 'ControlParameters|BrowLeftDown', 'ControlParameters|BrowLeftUp')
        if '|BrowRightUpDown' in self.id_to_name_dict[id]:
            uthread.new(TwoLayerParamHandler, value, self, 'ControlParameters|BrowRightDown', 'ControlParameters|BrowRightUp')
        if '|BrowLeftTighten' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|BrowLeftTighten')
        if '|BrowRightTighten' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|BrowRightTighten')
        if '|SquintLeft' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|SquintLeft')
        if '|SquintRight' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|SquintRight')
        if '|FrownLeft' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|FrownLeft')
        if '|FrownRight' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|FrownRight')
        if '|SmileLeft' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|SmileLeft')
        if '|SmileRight' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|SmileRight')
        if '|HeadTilt' in self.id_to_name_dict[id]:
            scaled_value = (value + 1.0) / 2.0
            uthread.new(TwoLayerParamHandler, scaled_value, self, 'ControlParameters|TiltHeadRight', 'ControlParameters|TiltHeadLeft')
        if '|JawSideways' in self.id_to_name_dict[id]:
            uthread.new(TwoLayerParamHandler, value, self, 'ControlParameters|JawRight', 'ControlParameters|JawLeft')
        if '|JawUp' in self.id_to_name_dict[id]:
            inv_value = 1 - 2 * value
            uthread.new(OneLayerParamHandler, inv_value, self, 'ControlParameters|JawDown')
        if '|EyesLookVertical' in self.id_to_name_dict[id]:
            uthread.new(TwoLayerParamHandler, value, self, 'ControlParameters|EyesLookDown', 'ControlParameters|EyesLookUp')
        if '|EyesLookHorizontal' in self.id_to_name_dict[id]:
            uthread.new(TwoLayerParamHandler, value, self, 'ControlParameters|EyesLookRight', 'ControlParameters|EyesLookLeft')
        if '|EyeClose' in self.id_to_name_dict[id]:
            uthread.new(OneLayerParamHandler, value, self, 'ControlParameters|EyesClose')
        if '|HeadLookTarget' in self.id_to_name_dict[id]:
            uthread.new(HeadLookTargetHandler, value, self)
        if '|HeadLookLeftRight' in self.id_to_name_dict[id]:
            uthread.new(HeadLookLeftRightHandler, value, self)
        if '|HeadLookUpDown' in self.id_to_name_dict[id]:
            uthread.new(HeadLookUpDownHandler, value, self)
        if '|CameraDistance' in self.id_to_name_dict[id]:
            uthread.new(CameraDistanceHandler, value, self)
        if '|IsAlive' in self.id_to_name_dict[id]:
            uthread.new(IsAliveHandler, value, self)

    def Rebuild(self):
        self.rebuilding = True
        uthread.new(RebuildAnimationNode, self)


def RebuildAnimationNode(animparams):
    network_mode = animparams.GetControlParameter('ControlParameters|NetworkMode')
    if network_mode == NETWORKMODE_PORTRAIT:
        RebuildAnimationNodePortrait(animparams)
    else:
        RebuildAnimationNodeNonPortrait(animparams)


def RebuildAnimationNodePortrait(animparams):
    if 'female' in animparams.avatar.visualModel.geometryResPath.lower():
        gender_name = 'Female'
    else:
        gender_name = 'Male'
    posenum = animparams.GetControlParameter('ControlParameters|PortraitPoseNumber') + 1
    animation = SetupAnimationNode()
    pose_res_list = BuildPortraitPoses(animation, gender_name, posenum)
    trinity.WaitForResourceLoads()
    PlayBaseAnimation(animation)
    PlaySecondaryPoseAnimations(animation, pose_res_list)
    animparams.avatar.animationUpdater = animation
    CreateGrannyBoneOffsets(animparams)
    animation.animationEnabled = True
    animparams.rebuilding = False
    param_dict = animparams.GetAllControlParameters()
    InitalizeControlParameters(animparams, param_dict)
    CheckAndSetPosingState(animparams)


def RebuildAnimationNodeNonPortrait(animparams):
    if animparams.avatar.visualModel is None:
        animparams.rebuilding = False
        return
    if 'female' in animparams.avatar.visualModel.geometryResPath.lower():
        gender_name = 'Female'
    else:
        gender_name = 'Male'
    animation = SetupGStateNode()
    LoadNonPortraitAnimations(animation, gender_name)
    animparams.avatar.animationUpdater = animation
    animation.animationEnabled = True
    animparams.rebuilding = False
    CheckAndSetSculptingState(animparams)


def LoadNonPortraitAnimations(animation, gender_name):
    pose_base_path = 'res:\\Animation\\CharacterCreatorV2\\GState\\CharacterCreator_Gstate_%s_Master.gsf' % gender_name
    animation.gStateResPath = pose_base_path
    log.LogNotice('Resetting gStateResPath')
    trinity.WaitForResourceLoads()
    while not animation.IsFullyLoaded():
        blue.synchro.Yield()

    animation.InstantiateCharacter()


def CheckAndSetSculptingState(animparams):
    if hasattr(uicore, 'layer') and hasattr(uicore.layer, 'charactercreation') and getattr(uicore.layer.charactercreation, 'isopen', 0):
        if uicore.layer.state is not None and uicore.layer.state == 0:
            if getattr(uicore.layer.charactercreation.controller, 'stepID', 0) in [ccconst.BLOODLINESTEP,
             ccconst.CUSTOMIZATIONSTEP,
             ccconst.PORTRAITSTEP,
             ccconst.DOLLSTEP]:
                if animparams.characterSvc:
                    animparams.characterSvc.StartPosing(animparams.charID)


def PortraitSetupFaceAnimLayer(animation, face_pose_res_path):
    animation.AddAnimationLayer('face', 1.0)
    face_clip = animation.GetSecondaryAnimationName(face_pose_res_path, 0)
    for bone in FACE_POSE_BONELIST:
        animation.AddAnimationLayerBone('face', bone)

    animation.PlayLayerAnimation('face', face_clip, True, 0, 0, 1.0, False)


def PortraitSetupBodyAnimLayer(animation, body_pose_res_path):
    animation.AddAnimationLayer('body', 1.0)
    body_clip = animation.GetSecondaryAnimationName(body_pose_res_path, 0)
    animation.AddAnimationLayerAllBones('body')
    for bone in FACE_POSE_BONELIST:
        animation.RemoveAnimationLayerBone('body', bone)

    animation.PlayLayerAnimation('body', body_clip, True, 0, 0, 1.0, False)


def CheckAndSetPosingState(animparams):
    if animparams.characterSvc and hasattr(uicore, 'layer'):
        if animparams.characterSvc.sculpting is not None:
            animparams.characterSvc.sculpting.Stop()
        animparams.characterSvc.StartPosing(animparams.charID)


def InitalizeControlParameters(animparams, param_dict):
    for name in param_dict:
        if '|NetworkMode' not in name and '|PortraitPoseNumber' not in name:
            animparams.ProcessControlParameter(param_dict[name])


def PlayBaseAnimation(animation):
    baseclip = animation.grannyRes.GetAnimationName(0)
    animation.PlayAnimationEx(baseclip, 0, 0, 0.0)


def SetupAnimationNode():
    animation = trinity.Tr2GrannyAnimation()
    animation.animationEnabled = False
    return animation


def SetupGStateNode():
    animation = trinity.Tr2GStateAnimation()
    animation.animationEnabled = False
    return animation


def GetParamsPerAvatar(avatar, charID = None, doll = None, factory = None):
    avatar_id = id(avatar)
    if avatar_id not in PARAMS_PER_AVATAR:
        PARAMS_PER_AVATAR[avatar_id] = AnimParams(avatar, charID, doll, factory)
    return PARAMS_PER_AVATAR[avatar_id]


def AddPose(animation, pose_res_list, res_path, param_name, default_value, default_weight = 1.0, bone_list = []):
    animation.AddSecondaryResPath(res_path)
    pose_res_list.append((res_path,
     param_name,
     default_value,
     default_weight,
     bone_list))


def AddIdle(animation, pose_res_list, res_path):
    animation.AddSecondaryResPath(res_path)
    pose_res_list.append((res_path,
     'idle',
     None,
     1.0,
     IDLE_POSE_BONELIST))


def BuildPortraitPoses(animation, gender_name, posenum):
    animation.SetAdditiveBlendMode(True)
    pose_res_list = []
    base_pose_res_path = 'res:/Animation/PortraitCreator/%s/CharacterCreation/Portrait_Pose_Base%d.gr2' % (gender_name, posenum)
    animation.resPath = base_pose_res_path
    animation.SetLayerControlParam('', 0.5)
    idle_pose_res_path = 'res:/Animation/PortraitCreator/Female/CharacterCreation/Portrait_Idle_Additive_FullBody.gr2'
    AddIdle(animation, pose_res_list, idle_pose_res_path)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowLeftCurlDown.gr2', 'ControlParameters|BrowLeftCurlDown', 0.0, 1.0, FACE_POSE_BROW_LEFT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowLeftCurlUp.gr2', 'ControlParameters|BrowLeftCurlUp', 0.0, 1.0, FACE_POSE_BROW_LEFT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowLeftDown.gr2', 'ControlParameters|BrowLeftDown', 0.0, 1.0, FACE_POSE_BROW_LEFT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowLeftUp.gr2', 'ControlParameters|BrowLeftUp', 0.0, 1.0, FACE_POSE_BROW_LEFT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowLeftTighten.gr2', 'ControlParameters|BrowLeftTighten', 0.0, 1.0, FACE_POSE_BROW_LEFT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowRightCurlDown.gr2', 'ControlParameters|BrowRightCurlDown', 0.0, 1.0, FACE_POSE_BROW_RIGHT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowRightCurlUp.gr2', 'ControlParameters|BrowRightCurlUp', 0.0, 1.0, FACE_POSE_BROW_RIGHT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowRightDown.gr2', 'ControlParameters|BrowRightDown', 0.0, 1.0, FACE_POSE_BROW_RIGHT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowRightUp.gr2', 'ControlParameters|BrowRightUp', 0.0, 1.0, FACE_POSE_BROW_RIGHT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_BrowRightTighten.gr2', 'ControlParameters|BrowRightTighten', 0.0, 1.0, FACE_POSE_BROW_RIGHT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_EyesClose.gr2', 'ControlParameters|EyesClose', 0.0, 1.0, FACE_POSE_EYE_CLOSED_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_EyesLookDown.gr2', 'ControlParameters|EyesLookDown', 0.0, 1.0, FACE_POSE_EYE_LOOK_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_EyesLookLeft.gr2', 'ControlParameters|EyesLookLeft', 0.0, 1.0, FACE_POSE_EYE_LOOK_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_EyesLookRight.gr2', 'ControlParameters|EyesLookRight', 0.0, 1.0, FACE_POSE_EYE_LOOK_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_EyesLookUp.gr2', 'ControlParameters|EyesLookUp', 0.0, 1.0, FACE_POSE_EYE_LOOK_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_FrownLeft.gr2', 'ControlParameters|FrownLeft', 0.0, 1.0, FACE_POSE_FROWN_LEFT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_FrownRight.gr2', 'ControlParameters|FrownRight', 0.0, 1.0, FACE_POSE_FROWN_RIGHT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_JawDown.gr2', 'ControlParameters|JawDown', 0.0, 1.0, FACE_POSE_JAW_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_JawLeft.gr2', 'ControlParameters|JawLeft', 0.0, 1.0, FACE_POSE_JAW_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_JawRight.gr2', 'ControlParameters|JawRight', 0.0, 1.0, FACE_POSE_JAW_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_JawUp.gr2', 'ControlParameters|JawUp', 0.0, 1.0, FACE_POSE_JAW_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_SmileLeft.gr2', 'ControlParameters|SmileLeft', 0.0, 1.0, FACE_POSE_SMILE_LEFT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_SmileRight.gr2', 'ControlParameters|SmileRight', 0.0, 1.0, FACE_POSE_SMILE_RIGHT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_SquintLeft.gr2', 'ControlParameters|SquintLeft', 0.0, 1.0, FACE_POSE_SQUINT_LEFT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_SquintRight.gr2', 'ControlParameters|SquintRight', 0.0, 1.0, FACE_POSE_SQUINT_RIGHT_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_TiltHeadLeft.gr2', 'ControlParameters|TiltHeadLeft', 0.0, 1.0, FACE_POSE_TILTHEAD_BONELIST)
    AddPose(animation, pose_res_list, 'res:\\Animation\\PortraitCreator\\Female\\Common\\Util_TiltHeadRight.gr2', 'ControlParameters|TiltHeadRight', 0.0, 1.0, FACE_POSE_TILTHEAD_BONELIST)
    return pose_res_list


def PlaySecondaryPoseAnimations(animation, pose_res_list):
    for pose_res_path, pose_layer_name, default_value, default_weight, bone_list in pose_res_list:
        pose_anim_name = animation.GetSecondaryAnimationName(pose_res_path, 0)
        animation.AddAnimationLayer(pose_layer_name, default_weight)
        if not bone_list:
            animation.AddAnimationLayerAllBones(pose_layer_name)
            animation.RemoveAnimationLayerBone(pose_layer_name, 'Plane')
        else:
            for bone_name in bone_list:
                animation.AddAnimationLayerBone(pose_layer_name, bone_name)

        if default_value is None:
            animation.PlayLayerAnimation(pose_layer_name, pose_anim_name, True, 0, 0, 1.0, False)
        else:
            animation.SetLayerControlParam(pose_layer_name, default_value)
            animation.PlayLayerAnimation(pose_layer_name, pose_anim_name, True, 0, 0, 0.0, False)


def OneLayerParamHandler(value, animparams, param):
    while animparams.rebuilding:
        blue.synchro.Yield()

    animparams.avatar.animationUpdater.SetLayerControlParam(param, clamp(value, 0.99, 0.0))


def BaseParamHandler(value, animparams):
    while animparams.rebuilding:
        blue.synchro.Yield()

    animparams.avatar.animationUpdater.SetLayerControlParam('', clamp(value, 0.99, 0.0))


def TwoLayerParamHandler(value, animparams, lowParam, highParam):
    while animparams.rebuilding:
        blue.synchro.Yield()

    if value < 0.5:
        scaled_val = clamp(1 - value * 2, 0.99, 0.0)
        animparams.avatar.animationUpdater.SetLayerControlParam(lowParam, scaled_val)
        animparams.avatar.animationUpdater.SetLayerControlParam(highParam, 0.0)
    else:
        scaled_val = clamp(value * 2 - 1, 0.99, 0.0)
        animparams.avatar.animationUpdater.SetLayerControlParam(lowParam, 0.0)
        animparams.avatar.animationUpdater.SetLayerControlParam(highParam, scaled_val)


def SetGstateParameter(name, value, animparams):
    for parameter in animparams.avatar.animationUpdater.parameters:
        if parameter.name == name and parameter.nodename == 'Controls':
            parameter.value = value


def HeadLookUpDownHandler(value, animparams):
    while animparams.rebuilding:
        blue.synchro.Yield()

    network_mode = animparams.GetControlParameter('ControlParameters|NetworkMode')
    if network_mode == NETWORKMODE_PORTRAIT:
        return
    if type(animparams.avatar.animationUpdater) == trinity.Tr2GStateAnimation:
        SetGstateParameter('HeadPitch', value, animparams)


def HeadLookLeftRightHandler(value, animparams):
    while animparams.rebuilding:
        blue.synchro.Yield()

    network_mode = animparams.GetControlParameter('ControlParameters|NetworkMode')
    if network_mode == NETWORKMODE_PORTRAIT:
        return
    if type(animparams.avatar.animationUpdater) == trinity.Tr2GStateAnimation:
        SetGstateParameter('HeadYaw', value, animparams)


def CameraDistanceHandler(value, animparams):
    while animparams.rebuilding:
        blue.synchro.Yield()

    network_mode = animparams.GetControlParameter('ControlParameters|NetworkMode')
    if network_mode == NETWORKMODE_PORTRAIT:
        return
    if type(animparams.avatar.animationUpdater) == trinity.Tr2GStateAnimation:
        SetGstateParameter('CloseupToggle', value, animparams)


def HeadLookTargetHandler(value, animparams):
    while animparams.rebuilding:
        blue.synchro.Yield()

    if type(value) is tuple:
        animparams.avatar.animationUpdater.AimBone('Head', value[0], value[1], value[2], 0.0, 0.0, 1.0)


def IsAliveHandler(value, animparams):
    while animparams.rebuilding:
        blue.synchro.Yield()

    if value:
        animparams.avatar.animationUpdater.SetLayerWeight('idle', 1.0)
    else:
        animparams.avatar.animationUpdater.SetLayerWeight('idle', 0.0)


def CreateGrannyBoneOffsets(animparams):
    if animparams.doll:
        animparams.factory.CreateAnimationOffsets(animparams.avatar, animparams.doll)
        return
    if animparams.characterSvc:
        for character in animparams.characterSvc.characters:
            default_factory = sm.GetService('paperDollClient').dollFactory
            av = animparams.characterSvc.characters[character].avatar
            fac = getattr(animparams.characterSvc.characters[character], 'factory', default_factory)
            doll = animparams.characterSvc.characters[character].doll
            if av is animparams.avatar:
                fac.CreateAnimationOffsets(av, doll)


def clamp(value, max_value, min_value):
    return max(min(value, max_value), min_value)
