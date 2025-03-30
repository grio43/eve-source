#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\colonyTemplate.py
import json
from collections import defaultdict
from eve.client.script.ui.shared.planet import planetConst
from eve.client.script.ui.shared.planet.planetConst import TYPEIDS_PROCESSORS_HIGHTECH, TYPEIDS_COMMAND_CENTER
from eveplanet.client.templates.templateConst import TemplateDictKeys, TemplatePinDataDictKeys, EXTRACT_PRODUCTS, PRODUCTION_PRODUCTS
from eveplanet.client.templates.verification import VerifyTemplate

class ColonyTemplate(object):

    def __init__(self, rawTemplate, filename):
        self.extractTypes = set()
        self.extractSourceCount = defaultdict(int)
        self.productTypes = set()
        self.productSourceCount = defaultdict(int)
        self.originalPlanetType = planetConst.PLANET_TYPES[0]
        self.commandCenterLV = 0
        self.radiusOfPlanet = 0
        self.description = u''
        self.favourited = False
        self.rawTemplate = u''
        self.loadedTemplate = {}
        self.restricted = False
        self.haveCmdCtr = False
        self.filename = u''
        loadedTemplate = json.loads(rawTemplate)
        VerifyTemplate(loadedTemplate)
        self.rawTemplate = rawTemplate
        self.loadedTemplate = loadedTemplate
        self.originalPlanetType = self.loadedTemplate[TemplateDictKeys.PlanetType]
        self.commandCenterLV = self.loadedTemplate[TemplateDictKeys.CmdCenterLV]
        self.radiusOfPlanet = self.loadedTemplate[TemplateDictKeys.Diameter] / 2
        for pin in self.loadedTemplate[TemplateDictKeys.PinData]:
            productTypeID = pin[TemplatePinDataDictKeys.Product]
            if productTypeID in EXTRACT_PRODUCTS:
                self.extractTypes.add(productTypeID)
                self.extractSourceCount[productTypeID] += 1
            if productTypeID in PRODUCTION_PRODUCTS:
                self.productTypes.add(productTypeID)
                self.productSourceCount[productTypeID] += 1
            if pin[TemplatePinDataDictKeys.PinTypeID] in TYPEIDS_PROCESSORS_HIGHTECH:
                self.restricted = True
            if pin[TemplatePinDataDictKeys.PinTypeID] in TYPEIDS_COMMAND_CENTER:
                self.haveCmdCtr = True

        self.description = self.loadedTemplate[TemplateDictKeys.Comments]
        self.favourited = False
        self.filename = filename
