#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\cosmeticsManager.py
import logging
import blue
import evegraphics.effects as gfx
import evegraphics.utils as gfxutils
import evetypes
import trinity
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader, PatternProjectionType
from cosmetics.common.ships.skins.static_data.pattern_blend_mode import PatternBlendMode
from cosmetics.common.ships.skins.static_data.slot_name import SlotID, PATTERN_SLOT_IDS
from trinity import EveSOFDataAreaType
from cosmeticsConst import AREA_MAPS, BLEND_MODE, DARKHULL_TEXTURE_MAP, PATTERN_INDEX_MAP
logger = logging.getLogger(__name__)
RESOURCE_NAME_BY_INDEX = {0: 'PatternMask1Map',
 1: 'PatternMask2Map'}
INDEX_BY_SLOT_ID = {SlotID.PATTERN: 0,
 SlotID.SECONDARY_PATTERN: 1}

class CosmeticsManager:

    def __init__(self):
        self.sofService = sm.GetService('sofService')
        self.model = None
        self.faction_id = None
        self.pattern = None
        self.targetMaterials = [1.0,
         1.0,
         1.0,
         1.0]
        self.hull_name = 'gc3_t1'
        self.mat1 = str()
        self.mat2 = str()
        self.mat3 = str()
        self.mat4 = str()
        self.pmat1 = str()
        self.pmat2 = str()
        self.selected_materials = dict()
        self.projection_texture = ''
        self.projection_texture_secondary = ''

    @property
    def sofDB(self):
        return self.sofService.spaceObjectFactory.GetSofDB()

    def apply_design(self, skin_design):
        if not skin_design:
            return
        for slot_id, component_instance in skin_design.slot_layout.slots.items():
            self.apply_component(slot_id, component_instance)

        self.UpdatePatternProjectionParametersFromSkinState(skin_design, self.model)
        blend_mode = skin_design.slot_layout.pattern_blend_mode
        if blend_mode is not None:
            CosmeticsManager.SetBlendMode(self.model, blendMode=blend_mode)

    def apply_component(self, slot_id, component_instance):
        if not component_instance:
            self.selected_materials.pop(slot_id, None)
            path = ''
        else:
            component_data = component_instance.get_component_data()
            path = component_data.resource_file_path if component_data else None
        if slot_id in PATTERN_SLOT_IDS:
            self.SetProjectionTexture(path, slot_id)
            if component_instance:
                component_instance.ellipsoid_center = self.model.shapeEllipsoidCenter
                component_instance.ellipsoid_radii = self.model.shapeEllipsoidRadius
                CosmeticsManager.ConfigurePatternBorderSettings(self.model, component_instance.projection_type_u, component_instance.projection_type_v, slot_id)
                self.ApplyScaling(slot_id, component_instance.scaling)
                self.ApplyTranslation(slot_id, component_instance.position)
                self.ApplyRotation(slot_id, component_instance.rotation)
                self.SetMirroredState(slot_id, component_instance.mirrored)
        elif slot_id == SlotID.SECONDARY_PATTERN_MATERIAL:
            self.SetMaterialOnArea(path, slot_id)
        else:
            self.SetMaterialOnArea(path, slot_id)

    def get_all_pattern_texture_names(self):
        pass

    def get_pattern_texture_name(self):
        pass

    def SetModel(self, model):
        self.model = model
        dna_parts = model.dna.split(':')
        self.hull_name = dna_parts[0]
        self.faction = dna_parts[1]
        self.race = dna_parts[2]
        factionID = evetypes.GetFactionID(self.typeID)
        self.SetFaction(factionID)
        hull = [ hull for hull in self.sofDB.hull if hull.name == self.hull_name ][0]
        darkhullAreas = [ area for area in hull.opaqueAreas if area.areaType == EveSOFDataAreaType.Darkhull ]
        if len(darkhullAreas) < 1:
            return
        darkuhull_indices = [ area.index for area in darkhullAreas ]
        darkhull_effects = [ area.effect for area in self.model.mesh.opaqueAreas if area.index in darkuhull_indices ]
        for fx in darkhull_effects:
            areaMap = AREA_MAPS[self.faction_id]
            targetIndex = areaMap[SlotID.TECH_AREA]
            texturePath = DARKHULL_TEXTURE_MAP[targetIndex]
            fxResource = [ res for res in fx.resources if res.name == 'MaterialMap' ][0]
            fxResource.resourcePath = texturePath

    def SetTypeID(self, type_id):
        self.typeID = type_id

    def SetFaction(self, factionID):
        self.faction_id = factionID

    def ApplyTranslation(self, slot_id, pos):
        if not self.model:
            return
        self._get_custom_mask(slot_id).position = pos

    def ApplyRotation(self, slot_id, rot):
        if not self.model:
            return
        self._get_custom_mask(slot_id).rotation = rot

    def _get_custom_mask(self, slot_id):
        mask_index = INDEX_BY_SLOT_ID[slot_id]
        return self.model.customMasks[mask_index]

    def ApplyScaling(self, slot_id, scaling):
        if not self.model:
            return
        self._get_custom_mask(slot_id).scaling = scaling

    def SetTargetMaterialArea(self, slot_id, area_id, is_active):
        if not self.model:
            return
        self.targetMaterials = list(self.targetMaterials)
        remapped_slot_id = AREA_MAPS[self.faction_id][area_id]
        self.targetMaterials[remapped_slot_id - 1] = float(is_active)
        mask = self.model.customMasks[INDEX_BY_SLOT_ID[slot_id]]
        mask.targetMaterials = self.targetMaterials

    def SetProjectionTexture(self, texturePath, slot_id = SlotID.PATTERN):
        attributeName = 'PatternMask1Map'
        if slot_id == SlotID.PATTERN:
            self.projection_texture = texturePath
        elif slot_id == SlotID.SECONDARY_PATTERN:
            attributeName = 'PatternMask2Map'
            self.projection_texture_secondary = texturePath
        for area in self.model.mesh.opaqueAreas:
            for each in area.effect.resources:
                if each.name == attributeName:
                    each.resourcePath = texturePath

    @staticmethod
    def SetBlendMode(model, blendMode = PatternBlendMode.OVERLAY):
        if not model:
            return
        effects = [ area.effect for area in model.mesh.opaqueAreas ]
        for each in effects:
            gfx.SetEffectOption(each, 'BLEND_MODE', BLEND_MODE[blendMode])

    def SetMirroredState(self, slot_id, is_mirrored):
        if self.model:
            self._get_custom_mask(slot_id).isMirrored = is_mirrored

    def GetDefaultMaterialForSlot(self, slot_id):
        factionData = [ faction for faction in self.sofDB.faction if faction.name == self.faction ][0].areaTypes.Primary
        try:
            targetSlot = AREA_MAPS[self.faction_id][slot_id]
        except KeyError:
            return

        if targetSlot == 1:
            return factionData.material1
        if targetSlot == 2:
            return factionData.material2
        if targetSlot == 3:
            return factionData.material3
        if targetSlot == 4:
            return factionData.material4

    @staticmethod
    def GetDefaultMaterialForSlotStatic(slot_id, factionName, factionID):
        sofDB = sm.GetService('sofService').spaceObjectFactory.GetSofDB()
        if sofDB is None:
            return
        factionData = [ faction for faction in sofDB.faction if faction.name == factionName ][0].areaTypes.Primary
        targetSlot = AREA_MAPS[factionID][slot_id]
        if targetSlot == 1:
            return factionData.material1
        if targetSlot == 2:
            return factionData.material2
        if targetSlot == 3:
            return factionData.material3
        if targetSlot == 4:
            return factionData.material4

    def SetMaterialOnDarkhull(self, material, hull):
        darkhullAreas = [ area for area in hull.opaqueAreas if area.areaType == EveSOFDataAreaType.Darkhull ]
        if len(darkhullAreas) < 1:
            return
        prefix = ''
        indices = ['1',
         '2',
         '3',
         '4']
        for idx in indices:
            index_string = prefix + 'Mtl' + idx
            diffuseName = index_string + 'DiffuseColor'
            dustDiffuseName = index_string + 'DustDiffuseColor'
            fresnelName = index_string + 'FresnelColor'
            glossName = index_string + 'Gloss'
            darkuhull_indices = [ area.index for area in darkhullAreas ]
            darkhull_effects = [ area.effect for area in self.model.mesh.opaqueAreas if area.index in darkuhull_indices ]
            for fx in darkhull_effects:
                gfx.SetParameterValue(fx, diffuseName, material.parameters[0].value)
                gfx.SetParameterValue(fx, dustDiffuseName, material.parameters[1].value)
                gfx.SetParameterValue(fx, fresnelName, material.parameters[2].value)
                gfx.SetParameterValue(fx, glossName, material.parameters[3].value)

    def SetMaterialOnArea(self, resPath, slot_id):
        if not resPath:
            material_name = self.GetDefaultMaterialForSlot(slot_id)
            if material_name is None:
                return
            material_path = 'res:/dx9/model/SpaceObjectFactory/materials/' + material_name + '.red'
        else:
            material_path = resPath
        material = blue.resMan.LoadObject(material_path)
        self.selected_materials[slot_id] = resPath
        dna = self.model.dna
        hullName = dna.split(':')[0]
        hull = [ hull for hull in self.sofDB.hull if hull.name == hullName ][0]
        allowedShaders = ['quad/quaddetailv5.fx',
         'quad/quadv5.fx',
         'quad/skinned_quadheatv5.fx',
         'skinned_quaddetailv5.fx']
        if slot_id == SlotID.PATTERN_MATERIAL or slot_id == SlotID.SECONDARY_PATTERN_MATERIAL:
            primaryAreas = [ area for area in hull.opaqueAreas ]
            decalAreas = [ area for area in hull.decalAreas ]
            for each in decalAreas:
                primaryAreas.append(each)

        else:
            primaryAreas = [ area for area in hull.opaqueAreas if area.areaType == EveSOFDataAreaType.Primary or area.areaType == EveSOFDataAreaType.SimplePrimary or area.areaType == EveSOFDataAreaType.Reactor or area.areaType == EveSOFDataAreaType.Ornament or 'area_hull' in area.name and area.shader in allowedShaders ]
        prefix = ''
        index_sting = str()
        if self.faction_id in AREA_MAPS.keys():
            index_string = str(AREA_MAPS[self.faction_id][slot_id])
        else:
            index_string = str(AREA_MAPS[500003])
            print 'area map missing for faction_id'
            print self.faction_id
        if slot_id is SlotID.PATTERN_MATERIAL:
            prefix = 'P'
            index_string = '1'
        if slot_id is SlotID.SECONDARY_PATTERN_MATERIAL:
            prefix = 'P'
            index_string = '2'
        index_string = prefix + 'Mtl' + index_string
        diffuseName = index_string + 'DiffuseColor'
        dustDiffuseName = index_string + 'DustDiffuseColor'
        fresnelName = index_string + 'FresnelColor'
        glossName = index_string + 'Gloss'
        indices = [ area.index for area in primaryAreas ]
        effects = [ area.effect for area in self.model.mesh.opaqueAreas if area.index in indices ]
        for fx in effects:
            gfx.SetParameterValue(fx, diffuseName, material.parameters[0].value)
            gfx.SetParameterValue(fx, dustDiffuseName, material.parameters[1].value)
            gfx.SetParameterValue(fx, fresnelName, material.parameters[2].value)
            gfx.SetParameterValue(fx, glossName, material.parameters[3].value)

        if slot_id is SlotID.TECH_AREA:
            self.SetMaterialOnDarkhull(material, hull)

    @staticmethod
    def GetSlotComponentFromSkinState(skin_state, slotIndex):
        slots, slot = (None, None)
        if hasattr(skin_state, 'skin_data'):
            if skin_state.skin_data is not None and hasattr(skin_state.skin_data, 'slot_layout'):
                if skin_state.skin_data.slot_layout is not None and hasattr(skin_state.skin_data.slot_layout, 'slots'):
                    slots = skin_state.skin_data.slot_layout.slots
        if skin_state is not None and hasattr(skin_state, 'slot_layout'):
            if skin_state.slot_layout is not None and hasattr(skin_state.slot_layout, 'slots'):
                slots = skin_state.slot_layout.slots
        if slots is not None:
            slot = slots.get(slotIndex)
        return slot

    @staticmethod
    def CreateSOFDNAfromSkinState(skinState, typeID):
        baseDNA = gfxutils.BuildSOFDNAFromTypeID(typeID)
        try:
            primaryMaterial = CosmeticsManager.GetSlotComponentFromSkinState(skinState, SlotID.PRIMARY_NANOCOATING)
            secondaryMaterial = CosmeticsManager.GetSlotComponentFromSkinState(skinState, SlotID.SECONDARY_NANOCOATING)
            tertiaryMaterial = CosmeticsManager.GetSlotComponentFromSkinState(skinState, SlotID.TERTIARY_NANOCOATING)
            techMaterial = CosmeticsManager.GetSlotComponentFromSkinState(skinState, SlotID.TECH_AREA)
            patternComponent = CosmeticsManager.GetSlotComponentFromSkinState(skinState, SlotID.PATTERN)
            patternMaterial = CosmeticsManager.GetSlotComponentFromSkinState(skinState, SlotID.PATTERN_MATERIAL)
            secondaryPatternComponent = CosmeticsManager.GetSlotComponentFromSkinState(skinState, SlotID.SECONDARY_PATTERN)
            secondaryPatternMaterial = CosmeticsManager.GetSlotComponentFromSkinState(skinState, SlotID.SECONDARY_PATTERN_MATERIAL)
            dna_parts = baseDNA.split(':')
            faction = dna_parts[1]
            materialString = ':material?'
            materialSlots = [SlotID.PRIMARY_NANOCOATING,
             SlotID.SECONDARY_NANOCOATING,
             SlotID.TERTIARY_NANOCOATING,
             SlotID.TECH_AREA]
            materialComponents = [primaryMaterial,
             secondaryMaterial,
             tertiaryMaterial,
             techMaterial]
            materials = ['',
             '',
             '',
             '']
            for materialIndex in range(4):
                component = materialComponents[materialIndex]
                componentID = None
                if component is not None:
                    if hasattr(component, 'component_id'):
                        componentID = component.component_id
                if componentID is None:
                    defaultFactionID = evetypes.GetFactionID(typeID)
                    materialSOFName = CosmeticsManager.GetDefaultMaterialForSlotStatic(materialSlots[materialIndex], faction, defaultFactionID)
                else:
                    component_data = ComponentsDataLoader.get_component_data(componentID)
                    filePath = component_data.resource_file_path
                    material = trinity.Load(filePath)
                    materialSOFName = material.name
                defaultFactionID = evetypes.GetFactionID(typeID)
                materialMappedIndex = AREA_MAPS[defaultFactionID][materialSlots[materialIndex]]
                materials[materialMappedIndex - 1] = materialSOFName

            for each in materials:
                materialString += each + ';'

            if None not in materials:
                baseDNA += materialString[:-1]
            if patternComponent is not None:
                componentID = None
                if patternComponent is not None:
                    if hasattr(patternComponent, 'component_id'):
                        componentID = patternComponent.component_id
                if componentID is not None:
                    patternString = ':pattern?'
                    filePath = 'res:/dx9/model/SpaceObjectFactory/patterns/cosm_blank_projection.red'
                    pattern = trinity.Load(filePath)
                    patternName = pattern.name
                    patternString += patternName
                    materialComponentID = None
                    if patternMaterial is not None:
                        if hasattr(patternMaterial, 'component_id'):
                            materialComponentID = patternMaterial.component_id
                    if materialComponentID is not None:
                        component_data = ComponentsDataLoader.get_component_data(materialComponentID)
                        filePath = component_data.resource_file_path
                        patternMaterial = trinity.Load(filePath)
                        patternMaterialName = patternMaterial.name
                        patternString += ';' + patternMaterialName
                    secondaryMaterialComponentID = None
                    if secondaryPatternMaterial is not None:
                        if hasattr(secondaryPatternMaterial, 'component_id'):
                            secondaryMaterialComponentID = secondaryPatternMaterial.component_id
                    if secondaryMaterialComponentID is not None:
                        component_data = ComponentsDataLoader.get_component_data(secondaryMaterialComponentID)
                        filePath = component_data.resource_file_path
                        secondaryPatternMaterial = trinity.Load(filePath)
                        secondaryPatternMaterialName = secondaryPatternMaterial.name
                        patternString += ';' + secondaryPatternMaterialName
                    baseDNA += patternString
        except Exception as exc:
            logger.exception('Failed to create DNA from SKIN state: %s', exc)

        return baseDNA

    @staticmethod
    def ClearPatternProjections(model):
        for area in model.mesh.opaqueAreas:
            for each in area.effect.resources:
                if each.name == 'PatternMask1Map' or each.name == 'PatternMask2Map':
                    each.resourcePath = 'res:/texture/Global/black.dds'

    @staticmethod
    def UpdatePatternProjectionParametersFromSkinState(skin_state, model, typeID = None):
        try:
            CosmeticsManager.ClearPatternProjections(model)
            if hasattr(skin_state, 'ship_type_id'):
                typeID = skin_state.ship_type_id
            for slot_id in PATTERN_SLOT_IDS:
                CosmeticsManager._apply_pattern_projection_parameters(slot_id, skin_state, model, typeID)

            sofDB = sm.GetService('sofService').spaceObjectFactory.GetSofDB()
            hull_name = model.dna.split(':')[0]
            hull = [ hull for hull in sofDB.hull if hull.name == hull_name ][0]
            darkhullAreas = [ area for area in hull.opaqueAreas if area.areaType == EveSOFDataAreaType.Darkhull ]
            if len(darkhullAreas) < 1:
                return
            darkuhull_indices = [ area.index for area in darkhullAreas ]
            darkhull_effects = [ area.effect for area in model.mesh.opaqueAreas if area.index in darkuhull_indices ]
            if typeID:
                for fx in darkhull_effects:
                    faction_id = evetypes.GetFactionID(typeID)
                    areaMap = AREA_MAPS[faction_id]
                    targetIndex = areaMap[SlotID.TECH_AREA]
                    texturePath = DARKHULL_TEXTURE_MAP[targetIndex]
                    fxResource = [ res for res in fx.resources if res.name == 'MaterialMap' ][0]
                    fxResource.resourcePath = texturePath

        except Exception as exc:
            logger.exception('Failed to create DNA from SKIN state: %s', exc)

    @staticmethod
    def _apply_pattern_projection_parameters(slot_id, skin_state, model, typeID):
        custom_mask_index = INDEX_BY_SLOT_ID[slot_id]
        component_instance = CosmeticsManager.GetSlotComponentFromSkinState(skin_state, slot_id)
        try:
            if component_instance is not None:
                patternMask = model.customMasks[custom_mask_index]
                patternMask.position = component_instance.position
                patternMask.rotation = component_instance.rotation
                patternMask.scaling = component_instance.scaling
                selectedSlots = (float(component_instance.projection_area1),
                 float(component_instance.projection_area2),
                 float(component_instance.projection_area3),
                 float(component_instance.projection_area4))
                materialSlots = [SlotID.PRIMARY_NANOCOATING,
                 SlotID.SECONDARY_NANOCOATING,
                 SlotID.TERTIARY_NANOCOATING,
                 SlotID.TECH_AREA]
                if typeID is not None:
                    slots = [1.0,
                     1.0,
                     1.0,
                     1.0]
                    for index in range(4):
                        defaultFactionID = evetypes.GetFactionID(typeID)
                        materialMappedIndex = AREA_MAPS[defaultFactionID][materialSlots[index]]
                        slots[materialMappedIndex - 1] = selectedSlots[index]

                    selectedSlots = tuple(slots)
                patternMask.targetMaterials = selectedSlots
                patternMask.isMirrored = component_instance.mirrored
                patternComponentID = component_instance.component_id
                component_data = ComponentsDataLoader.get_component_data(patternComponentID)
                CosmeticsManager.ConfigurePatternBorderSettings(model, component_instance.projection_type_u, component_instance.projection_type_v, slot_id)
                texturePath = component_data.resource_file_path
                for area in model.mesh.opaqueAreas:
                    for each in area.effect.resources:
                        if each.name == RESOURCE_NAME_BY_INDEX[custom_mask_index]:
                            each.resourcePath = texturePath

        except Exception as exc:
            logger.exception('Failed to apply projection parameters: %s', exc)

    @staticmethod
    def ConfigurePatternBorderSettings(model, projection_type_u, projection_type_v, slot_id):
        projection_type_to_address = {PatternProjectionType.CLAMP: 4,
         PatternProjectionType.REPEAT: 1,
         PatternProjectionType.BORDER: 3}
        pattern_index = PATTERN_INDEX_MAP[slot_id]
        targetTextureName = 'PatternMask' + str(pattern_index) + 'MapSampler'
        for area in model.mesh.opaqueAreas:
            populateParameters = False
            for i, each in enumerate(area.effect.samplerOverrides):
                if len(each) < 3:
                    continue
                if each[0] == targetTextureName:
                    mutableObj = list(each)
                    mutableObj[1] = projection_type_to_address.get(projection_type_u, 4)
                    mutableObj[2] = projection_type_to_address.get(projection_type_v, 4)
                    area.effect.samplerOverrides[i] = tuple(mutableObj)
                    populateParameters = True

            if populateParameters:
                area.effect.PopulateParameters()
