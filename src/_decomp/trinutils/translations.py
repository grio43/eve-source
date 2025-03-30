#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinutils\translations.py
import trinity

def GetTranslationValue(obj):
    try:
        return obj.translationCurve.value
    except AttributeError:
        return (0.0, 0.0, 0.0)


def SetTranslationValue(obj, pos):
    if hasattr(obj, 'translationCurve') and obj.translationCurve is None:
        obj.translationCurve = trinity.Tr2TranslationAdapter()
    obj.translationCurve.value = pos
