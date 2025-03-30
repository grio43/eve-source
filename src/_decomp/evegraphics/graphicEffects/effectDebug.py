#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\graphicEffects\effectDebug.py
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from collections import OrderedDict
import blue
import telemetry
import trinity
import locks

class EffectNotSetUpError(ValueError):
    pass


DEBUG_PARAMETER_KEY = 'debugParameter'
DEBUG_CHOICES_KEY = 'debugChoices'
DEBUG_TOGGLE_KEY = 'debugToggle'
DEBUG_OFF_VALUE_KEY = 'debugOffValue'
DEBUG_DESCRIPTIVE_NAME = 'descriptiveName'
DEBUG_SETTINGS = {'V5_DEBUG': {DEBUG_DESCRIPTIVE_NAME: 'V5',
              DEBUG_PARAMETER_KEY: 'V5DebugType',
              DEBUG_TOGGLE_KEY: ['OFF', 'ON'],
              DEBUG_OFF_VALUE_KEY: -1,
              DEBUG_CHOICES_KEY: OrderedDict([('None', -1),
                                  ('Mesh: UV Set 0', 51),
                                  ('Mesh: UV Set 1', 52),
                                  ('Mesh: Vertex Color', 53),
                                  ('Mesh: Normal World', 55),
                                  ('Texture: Albedo', 0),
                                  ('Texture: Transparency', 1),
                                  ('Texture: Glow', 2),
                                  ('Texture: Normal in tangent space', 3),
                                  ('Texture: Roughness', 4),
                                  ('Texture: Dirt', 5),
                                  ('Texture: Paint mask', 6),
                                  ('Texture: Ambient occlusion', 7),
                                  ('Texture: Material selection', 8),
                                  ('Texture: Weights of material 1', 9),
                                  ('Texture: Weights of material 2', 10),
                                  ('Texture: Weights of material 3', 11),
                                  ('Texture: Weights of material 4', 12),
                                  ('Texture: Paint mask texture', 13),
                                  ('Texture: Dirt detail texture', 14),
                                  ('Material: Diffuse', 15),
                                  ('Material: Glow', 16),
                                  ('Material: Fresnel', 17),
                                  ('Material: Gloss Factor', 18),
                                  ('Material: Paint map influence', 19),
                                  ('Material: Heat booster gain influence', 20),
                                  ('Material: Heat shimmer speed', 21),
                                  ('Material: Heat shimmer size', 22),
                                  ('Material: Heat Shimmer Strength', 23),
                                  ('Material: Dirt Albedo Color', 24),
                                  ('Material: Translucency', 25),
                                  ('Area: Heat area', 35),
                                  ('Area: Wreck area', 36),
                                  ('Area: Transparency area', 37),
                                  ('Area: Oil area', 38),
                                  ('Lighting: Normal in world space', 26),
                                  ('Lighting: Shadow', 27),
                                  ('Lighting: Reflectance in world space', 28),
                                  ('Lighting: Specular Dot', 43),
                                  ('Lighting: SSAO', 59),
                                  ('Lighting: SSAO + AO', 60),
                                  ('Detail: Detail Map 1', 73),
                                  ('Detail: Detail Map 1 alpha', 74),
                                  ('Detail: Detail Map 2', 75),
                                  ('Detail: Detail Map 2 alpha', 76),
                                  ('Detail: Detail Map 3', 77),
                                  ('Detail: Detail Map 3 alpha', 78),
                                  ('Detail: Normal Offset', 56),
                                  ('Detail: All strength', 57),
                                  ('Detail: Single Detail Strength', 58),
                                  ('Base: Precalc Albedo', 29),
                                  ('Base: Precalc Fresnel', 30),
                                  ('Base: Precalc Roughness', 31),
                                  ('Base: Fresnel (Schlick)', 46),
                                  ('Base: Visibility (Schlick-Smith Optimized)', 48),
                                  ('Base: Normal distribution (GGX)', 47),
                                  ('Base: Specular', 49),
                                  ('Base: Diffuse', 69),
                                  ('Base: Normal Map Occlusion', 54),
                                  ('Base: Sun Light', 45),
                                  ('Base: BRDF (COD-BO 2)', 50),
                                  ('Base: Nebula Light', 44),
                                  ('Base: Light from transparency', 82),
                                  ('Base: Material color', 39),
                                  ('Dirt: Precalc Albedo', 32),
                                  ('Dirt: Precalc Fresnel', 33),
                                  ('Dirt: Precalc Roughness', 34),
                                  ('Dirt: Fresnel (Schlick)', 63),
                                  ('Dirt: Visibility (Schlick-Smith Optimized)', 64),
                                  ('Dirt: Normal distribution (GGX)', 65),
                                  ('Dirt: Specular', 66),
                                  ('Dirt: Diffuse', 70),
                                  ('Dirt: Normal Map Occlusion', 67),
                                  ('Dirt: Sun Light', 62),
                                  ('Dirt: BRDF (COD-BO 2)', 68),
                                  ('Dirt: Nebula Light', 61),
                                  ('Dirt: Material color', 40),
                                  ('Final: Base + Dirt Material color', 41),
                                  ('Final: Glow color', 71),
                                  ('Final: Wreck color', 72),
                                  ('Final: Heat color', 79),
                                  ('Final: Transparency color', 80),
                                  ('Final: Oil color', 81),
                                  ('Final: Final material color', 42)])}}

class EffectDebugger(object):

    def __init__(self, root, scene):
        self.root = blue.BluePythonWeakRef(root)
        self.applicableParentsAndEffects = {}
        self.nonApplicableParentsAndEffects = {}
        self.ready = False
        self.scene = blue.BluePythonWeakRef(scene)
        self.cachedValues = {}
        self.enabled = {o:False for o in DEBUG_SETTINGS.iterkeys()}
        self.shown = {o:True for o in DEBUG_SETTINGS.iterkeys()}
        self.Update()

    def __del__(self):
        for option in DEBUG_SETTINGS.iterkeys():
            self.ApplyDebugByValue(option, DEBUG_SETTINGS[option][DEBUG_OFF_VALUE_KEY], updateCache=False)

    @telemetry.ZONE_METHOD
    def FindEffects(self):
        allObjects = blue.FindAllReferences(self.root.object)
        if self.scene.object is None:
            return []
        d = []
        for obj, path in allObjects.iteritems():
            if not isinstance(obj, trinity.Tr2Effect):
                continue
            for parent, _, __ in path:
                if parent is self.scene.object or parent in self.scene.object.objects:
                    continue
                d.append((obj, parent))

        return d

    @telemetry.ZONE_METHOD
    def Update(self, applyValues = False):
        self.ready = False
        self.applicableParentsAndEffects = {debugSetting:[] for debugSetting in DEBUG_SETTINGS.iterkeys()}
        self.nonApplicableParentsAndEffects = {debugSetting:[] for debugSetting in DEBUG_SETTINGS.iterkeys()}
        options = [ debugSetting for debugSetting in DEBUG_SETTINGS.iterkeys() ]
        effects = self.FindEffects()
        for effect, parent in effects:
            try:
                optionsApplicable, optionsNotApplicable = self._IsEffectApplicable(effect, options)
            except EffectNotSetUpError:
                return

            effectRef = blue.BluePythonWeakRef(effect)
            for option in optionsApplicable:
                self.applicableParentsAndEffects[option].append((effectRef, blue.BluePythonWeakRef(parent)))

            for option in optionsNotApplicable:
                self.nonApplicableParentsAndEffects[option].append((effectRef, blue.BluePythonWeakRef(parent)))

        self.ready = True
        if applyValues:
            self.ReApplyDebugValues()

    @staticmethod
    def _IsEffectApplicable(effect, options):
        if effect is None or effect is None or effect.effectResource is None:
            return ([], [])
        applicableOptions = []
        unapplicableOptions = options[:]
        try:
            descriptions = effect.effectResource.GetPermutationDescription()
        except ValueError:
            return ([], [])

        for desc in descriptions:
            if desc['name'] in options:
                applicableOptions.append(desc['name'])
                unapplicableOptions.remove(desc['name'])

        return (applicableOptions, unapplicableOptions)

    @telemetry.ZONE_METHOD
    def GetDebugOptions(self):
        if not self.ready:
            self.Initialize()
        d = {option:DEBUG_SETTINGS[option][DEBUG_CHOICES_KEY] for option in self.applicableParentsAndEffects.keys()}
        return d

    def GetDescriptiveName(self, debugOption):
        return DEBUG_SETTINGS[debugOption][DEBUG_DESCRIPTIVE_NAME]

    @telemetry.ZONE_METHOD
    def ApplyDebugByValue(self, debugOption, value, updateCache = True, checkToggle = True):
        enabled = value != DEBUG_SETTINGS[debugOption][DEBUG_OFF_VALUE_KEY]
        self.SetShaderOption(debugOption, enabled, checkToggle)
        self._SetDebugValue(debugOption, value, updateCache)
        self.ToggleVisibilityForParents()

    def _SetDebugValue(self, debugOption, debugValue, updateCache = True):
        debugParameter = DEBUG_SETTINGS[debugOption][DEBUG_PARAMETER_KEY]
        if updateCache:
            self.cachedValues[debugOption] = debugValue
        for effect, _ in self.applicableParentsAndEffects.get(debugOption, []):
            self._SetEffectValue(effect, debugParameter, debugValue)

    def _SetEffectValue(self, effectWeakRef, parameterName, value):
        effect = effectWeakRef.object
        if effect:
            effect.RebuildCachedData()
            effect.PopulateParameters()
            parameter = effect.parameters.FindByName(parameterName)
            if parameter is None:
                return
            parameter.value = value

    def GetDebugValue(self, debugOption):
        if not self.enabled[debugOption]:
            return DEBUG_SETTINGS[debugOption][DEBUG_OFF_VALUE_KEY]
        debugParameter = DEBUG_SETTINGS[debugOption][DEBUG_PARAMETER_KEY]
        cachedValue = self.cachedValues.get(debugOption)
        if cachedValue is not None:
            return cachedValue
        effectsWithToggle = self.applicableParentsAndEffects.get(debugOption, [])
        if not effectsWithToggle or len(effectsWithToggle[0]) == 0:
            return DEBUG_SETTINGS[debugOption][DEBUG_OFF_VALUE_KEY]
        firstEffect = effectsWithToggle[0][0]
        if not firstEffect:
            return DEBUG_SETTINGS[debugOption][DEBUG_OFF_VALUE_KEY]
        parameter = firstEffect.object.parameters.FindByName(debugParameter)
        if parameter is None:
            return DEBUG_SETTINGS[debugOption][DEBUG_OFF_VALUE_KEY]
        return parameter.value

    def IsEnabled(self, option):
        return self.enabled[option]

    def Enable(self, option):
        if self.enabled[option]:
            return
        self.ApplyDebugByValue(option, self.cachedValues.get(option, DEBUG_SETTINGS[option][DEBUG_OFF_VALUE_KEY]))

    def Disable(self, option):
        if not self.enabled[option]:
            return
        self.ApplyDebugByValue(option, DEBUG_SETTINGS[option][DEBUG_OFF_VALUE_KEY], updateCache=False)

    def IsShown(self, option):
        return self.shown[option]

    def Show(self, option):
        self.shown[option] = True
        self.ToggleVisibilityForParents()

    def Hide(self, option):
        self.shown[option] = False
        self.ToggleVisibilityForParents()

    def ReApplyDebugValues(self):
        for option, enabled in self.enabled.iteritems():
            if enabled:
                self.ApplyDebugByValue(option, self.cachedValues.get(option, DEBUG_SETTINGS[option][DEBUG_OFF_VALUE_KEY]), checkToggle=False)

    def SetShaderOption(self, optionName, toggle, checkToggle = True):
        if checkToggle and self.enabled[optionName] == toggle:
            return
        self._SetOptions(optionName, toggle)
        self.enabled[optionName] = toggle

    @telemetry.ZONE_METHOD
    def _SetOptions(self, optionName, toggle):
        for currentIndex, (effect, _) in enumerate(self.applicableParentsAndEffects.get(optionName, [])):
            self._SetEffectOption(effect, optionName, toggle)

    def _SetEffectOption(self, ewr, optionName, toggle):
        key = DEBUG_SETTINGS[optionName][DEBUG_TOGGLE_KEY][toggle]
        effect = ewr.object
        index = -1
        for i, o in enumerate(getattr(effect, 'options', [])):
            if o[0] == optionName:
                index = i
                break

        if index != -1:
            if not toggle:
                effect.options.removeAt(index)
            else:
                effect.options[index] = (optionName, key)
        elif toggle:
            effect.options.append((optionName, key))
        effect.RebuildCachedData()
        effect.PopulateParameters()

    def ToggleVisibilityForParents(self):
        anyEffectEnabled = any(self.enabled.values())
        for option, enabled in self.enabled.iteritems():
            for _, parent in self.nonApplicableParentsAndEffects.get(option, []):
                if parent and parent.object and hasattr(parent.object, 'display'):
                    parent.object.display = not anyEffectEnabled

        for option, enabled in self.enabled.iteritems():
            for _, parent in self.applicableParentsAndEffects.get(option, []):
                if parent and parent.object and hasattr(parent.object, 'display'):
                    parent.object.display = self.shown[option] and (enabled or not anyEffectEnabled)

        if self.scene.object:
            postprocess = self.scene.object.postprocess
            if postprocess and postprocess.bloom is not None:
                postprocess.bloom.display = not anyEffectEnabled

    def CleanUp(self):
        for debugOption in DEBUG_SETTINGS.iterkeys():
            self.shown[debugOption] = True
            self.Disable(debugOption)

        self.applicableParentsAndEffects.clear()
        self.nonApplicableParentsAndEffects.clear()
