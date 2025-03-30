#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\paperdoll\common\blend_shape.py
BODY_BLENDSHAPE_ZONES = ('Abs', 'Chest', 'Legs', 'Shoulders', 'Pelvis', 'Feet', 'Neck')
HEAD_BLENDSHAPE_ZONES = ('CheeksMiddle', 'CheeksUpper', 'Chin', 'Ears', 'Eyes', 'EyesInner', 'EyesOuter', 'InnerBrow', 'Jaw', 'JawCheek', 'LowerLip', 'MouthCorner', 'Nose', 'NoseBone', 'NoseTip', 'Nostrils', 'OuterBrow', 'UpperLip')
ALL_BLENDSHAPE_ZONES = BODY_BLENDSHAPE_ZONES + HEAD_BLENDSHAPE_ZONES

class SpecialHandleShapeData(object):

    def __init__(self, field, positive):
        self.field = field
        self.positive = positive


SPECIAL_HANDLE_SHAPES = {'thin': SpecialHandleShapeData(field='weightUpDown', positive=True),
 'fat': SpecialHandleShapeData(field='weightLeftRight', positive=True),
 'muscular': SpecialHandleShapeData(field='weightForwardBack', positive=True)}
