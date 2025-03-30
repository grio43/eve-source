#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\eveeffectroot2.py
from evegraphics.validation.commonUtilities import Validate

@Validate('EveEffectRoot2')
def EveEffectRoot2BoundingSphere(context, root):
    if root.boundingSphereRadius is None:
        context.Error(root, 'Bounding Sphere Radius is None ')
    elif root.boundingSphereRadius <= 0.0:
        context.Error(root, 'Bounding Sphere Radius is 0.0 or less.')
