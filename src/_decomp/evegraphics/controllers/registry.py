#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\controllers\registry.py
import trinity
from eveaudio.const import ActingParty, ModuleState, ModuleType, WarpState
from eveaudio.const import STOP_SHIP_CTRL_VARIABLE
FLOAT = 0
INTEGER = 1
BOOLEAN = 2
ENUM = 3

class VariableDescription(object):

    def __init__(self, name, varType, description, defaultValue = 0.0, enumValues = ''):
        self.name = name
        self.type = varType
        self.description = description
        self.enumValues = enumValues
        self.defaultValue = defaultValue

    def CreateVariable(self):
        var = trinity.Tr2ControllerFloatVariable()
        var.name = self.name
        var.variableType = self.type
        var.enumValues = self.enumValues
        var.defaultValue = self.defaultValue
        var.value = self.defaultValue
        return var


class EventDescription(object):

    def __init__(self, name, description):
        self.name = name
        self.description = description


VARIABLES = [VariableDescription('InSiegeMode', BOOLEAN, 'If the ship is in siege mode or not. Set by a client effect.'),
 VariableDescription('IsWarping', BOOLEAN, 'If the ship is warping (a.k.a. full speed of warp). Applies to ships. Set by client code.'),
 VariableDescription('IsHighlighted', BOOLEAN, 'If the asteroid is highlighted (for some dungeons). Set by client code.'),
 VariableDescription('IsBuilt', BOOLEAN, 'If a deployable structure is build or is being built. Set by client code.', 1.0),
 VariableDescription('BuildDuration', FLOAT, 'Total build duration in seconds for a deployable structure if it is being build or teared down (is set to 0 when the structure is fully built or teared down). Set by client code.'),
 VariableDescription('BuildElapsedTime', FLOAT, 'Time in seconds since a deployable structure started being built/teared down when IsBuild variable was set. Set by client code.'),
 VariableDescription('IsDeployableActive', BOOLEAN, 'If a deployable object is active. Set by client code.'),
 VariableDescription('IsDissolving', BOOLEAN, 'Is the object being dissolved. Set by client code.'),
 VariableDescription('ShipStance', ENUM, 'Tech3 ship stance. Set by client code.', 2.0, 'Defence=1, Speed=2, Sniper=3'),
 VariableDescription('SecurityState', ENUM, 'Container security state. Set by client code.', enumValues='Secure=0, BeingHacked=1, Hacked=2'),
 VariableDescription('IsOnline', BOOLEAN, 'Is the object active/online. Applies to claim markers and monuments? Set by client code.'),
 VariableDescription('DirtLevel', FLOAT, 'Amount of dirt on the space object (0 to 1). Set by trinity.'),
 VariableDescription('ActivationStrength', FLOAT, 'Space object activation strength. Set by trinity.'),
 VariableDescription('ShieldDamage', FLOAT, 'Space object shield damage. Set by trinity.'),
 VariableDescription('ArmorDamage', FLOAT, 'Space object armor damage. Set by trinity.'),
 VariableDescription('HullDamage', FLOAT, 'Space object hull damage. Set by trinity.'),
 VariableDescription('ClipSphereFactor', FLOAT, 'Space object clip sphere factor. Set by trinity.'),
 VariableDescription('TurretState', ENUM, 'Current Turret state. Only usable by turretsets that have EveStretch3 as their firing effect. Set by trinity', enumValues='invalid=0, deactive=1, idle=2, targeting=3, firing=4, reloading=5'),
 VariableDescription('ShipBoosterIntensity', FLOAT, 'The booster intensity of a ship. Set by Trinity.'),
 VariableDescription(WarpState.__name__, ENUM, 'The given ships warping state. Needed for engine audio.', enumValues=WarpState.EnumValues()),
 VariableDescription(ModuleState.__name__, ENUM, 'The state a ships propulsion module is in. Needed for engine audio.', enumValues=ModuleState.EnumValues()),
 VariableDescription(ModuleType.__name__, ENUM, 'The type of propulsion module being used on a ship. Needed for engine audio.', enumValues=ModuleType.EnumValues()),
 VariableDescription(STOP_SHIP_CTRL_VARIABLE, BOOLEAN, 'Whether the player has sent the stop ship command. Keep in mind, this is never set to False in code and needs to be handled in a controller if you use it. Needed for engine audio.', defaultValue=0),
 VariableDescription(ActingParty.__name__, ENUM, "The acting party of a ship. For instance, if the controller is on the player's ship then it is first party. Otherwise it is a third party. Needed for engine audio.", enumValues=ActingParty.EnumValues())]
EVENTS = [EventDescription('Arrival', 'Triggered when a ship arrives at a gate'), EventDescription('Departure', 'Triggered when a ship departs from a gate')]
