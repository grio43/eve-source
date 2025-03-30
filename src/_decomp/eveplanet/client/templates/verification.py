#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveplanet\client\templates\verification.py
from eveplanet.client.templates.templateConst import TemplateDictKeys, PlanetTypes, TemplatePinDataDictKeys, TemplateLinkDataDictKeys, TemplateRouteDataDictKeys

def VerifyTemplate(loadedTemplate):
    try:
        _VerifyTemplate(loadedTemplate)
    except RuntimeError as e:
        raise UserError('PITemplateVerificationFailed')


def _VerifyTemplate(loadedTemplate):
    if not isinstance(loadedTemplate, dict):
        raise RuntimeError('Template not dictionary')
    for key in loadedTemplate.iterkeys():
        if key not in TemplateDictKeys:
            raise RuntimeError('Template contains invalid key')

    _VerifyCmdCenterLv(loadedTemplate)
    _VerifyComment(loadedTemplate)
    _VerifyDiamater(loadedTemplate)
    _VerifyPlanetType(loadedTemplate)
    _VerifyPins(loadedTemplate)
    _VerifyRoutes(loadedTemplate)


def _VerifyCmdCenterLv(loadedTemplate):
    value = loadedTemplate.get(TemplateDictKeys.CmdCenterLV, None)
    if value is None:
        raise RuntimeError('Missing cmd center info')
    if isinstance(value, int):
        return
    raise RuntimeError('Some problem with cmd center value')


def _VerifyComment(loadedTemplate):
    value = loadedTemplate.get(TemplateDictKeys.Comments, None)
    if not isinstance(value, basestring):
        raise RuntimeError('Comment is not a string')


def _VerifyDiamater(loadedTemplate):
    value = loadedTemplate.get(TemplateDictKeys.Diameter, None)
    if not isinstance(value, float):
        raise RuntimeError('Diameter is not a float')


def _VerifyPlanetType(loadedTemplate):
    value = loadedTemplate.get(TemplateDictKeys.PlanetType, None)
    if value not in PlanetTypes:
        raise RuntimeError('Planet type is invalid')


def _VerifyPins(loadedTemplate):
    pinData = loadedTemplate.get(TemplateDictKeys.PinData, None)
    if not isinstance(pinData, list):
        raise RuntimeError('PinData is not a list')
    pinDataDictKeysSet = set(TemplatePinDataDictKeys)
    for eachPinDict in pinData:
        if not isinstance(eachPinDict, dict):
            raise RuntimeError('eachPinDict is not a dict')
        if set(eachPinDict.keys()) != pinDataDictKeysSet:
            raise RuntimeError('eachPinDict mismatch with TemplatePinDataDictKeys')
        v = eachPinDict.get(TemplatePinDataDictKeys.ExtractorHeadCount, None)
        if not isinstance(v, int):
            raise RuntimeError('ExtractorHeadCount is not int')
        v = eachPinDict.get(TemplatePinDataDictKeys.Longi, None)
        if not isinstance(v, float):
            raise RuntimeError('Longi is not float')
        v = eachPinDict.get(TemplatePinDataDictKeys.Lat, None)
        if not isinstance(v, float):
            raise RuntimeError('Lat is not float')
        v = eachPinDict.get(TemplatePinDataDictKeys.PinTypeID, None)
        if not isinstance(v, int):
            raise RuntimeError('PinTypeID is not int')
        v = eachPinDict.get(TemplatePinDataDictKeys.Product, None)
        if v is None:
            pass
        elif not isinstance(v, int):
            raise RuntimeError('PinTypeID is not int')


def _VerifyLinks(loadedTemplate):
    linkData = loadedTemplate.get(TemplateDictKeys.LinkData, None)
    if not linkData:
        return
    if not isinstance(linkData, list):
        raise RuntimeError('linkData is not a list')
    linkDataDictKeysSet = set(TemplateLinkDataDictKeys)
    for eachLinkData in linkData:
        if not isinstance(eachLinkData, dict):
            raise RuntimeError('eachLinkData is not a dict')
        if set(eachLinkData.keys()) != linkDataDictKeysSet:
            raise RuntimeError('eachLinkData mismatch with TemplateLinkDataDictKeys')
        v = eachLinkData.get(TemplateLinkDataDictKeys.Source, None)
        if not isinstance(v, int):
            raise RuntimeError('Source is not int')
        v = eachLinkData.get(TemplateLinkDataDictKeys.Destination, None)
        if not isinstance(v, int):
            raise RuntimeError('Destination is not int')
        v = eachLinkData.get(TemplateLinkDataDictKeys.Level, None)
        if not isinstance(v, int):
            raise RuntimeError('Level is not int')


def _VerifyRoutes(loadedTemplate):
    routeData = loadedTemplate.get(TemplateDictKeys.RouteData, None)
    if not routeData:
        return
    if not isinstance(routeData, list):
        raise RuntimeError('routeData is not a list')
    routeDataDictKeysSet = set(TemplateRouteDataDictKeys)
    for eachRouteData in routeData:
        if not isinstance(eachRouteData, dict):
            raise RuntimeError('eachRouteData is not a dict')
        if set(eachRouteData.keys()) != routeDataDictKeysSet:
            raise RuntimeError('eachRouteData mismatch with TemplateRouteDataDictKeys')
        v = eachRouteData.get(TemplateRouteDataDictKeys.ItemQuantity, None)
        if not isinstance(v, int):
            raise RuntimeError('ItemQuantity is not int')
        v = eachRouteData.get(TemplateRouteDataDictKeys.ItemType, None)
        if not isinstance(v, int):
            raise RuntimeError('ItemType is not int')
        path = eachRouteData.get(TemplateRouteDataDictKeys.Path, None)
        if not isinstance(path, list):
            raise RuntimeError('Path is not list')
        for x in path:
            if not isinstance(x, int):
                raise RuntimeError('Path member is not int')
