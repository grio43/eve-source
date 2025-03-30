#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\abyssal_content_constants.py
from inventorycommon.const import typeCausticToxinWeather1
from inventorycommon.const import typeCausticToxinWeather2
from inventorycommon.const import typeCausticToxinWeather3
from inventorycommon.const import typeDarknessWeather1
from inventorycommon.const import typeDarknessWeather2
from inventorycommon.const import typeDarknessWeather3
from inventorycommon.const import typeElectricStormWeather1
from inventorycommon.const import typeElectricStormWeather2
from inventorycommon.const import typeElectricStormWeather3
from inventorycommon.const import typeInfernalWeather1
from inventorycommon.const import typeInfernalWeather2
from inventorycommon.const import typeInfernalWeather3
from inventorycommon.const import typeLensFlareA30
from inventorycommon.const import typeLensFlareA31
from inventorycommon.const import typeLensFlareA32
from inventorycommon.const import typeLensFlareA33
from inventorycommon.const import typeLensFlareA34
from inventorycommon.const import typeLensFlareA35
from inventorycommon.const import typeLensFlareA36
from inventorycommon.const import typeXenonGasWeather1
from inventorycommon.const import typeXenonGasWeather2
from inventorycommon.const import typeXenonGasWeather3
TIER_CHOICES = [('Tier 0', 0),
 ('Tier 1', 1),
 ('Tier 2', 2),
 ('Tier 3', 3),
 ('Tier 4', 4),
 ('Tier 5', 5),
 ('Tier 6', 6)]
NEBULA_CHOICES = [('Random', None),
 ('01A: 22041', 22041),
 ('02A: 22042', 22042),
 ('02B: 22043', 22043),
 ('02C: 22044', 22044),
 ('03A: 22045', 22045),
 ('03B: 22046', 22046),
 ('03C: 22047', 22047),
 ('04A: 22048', 22048),
 ('04B: 22207', 22207),
 ('04C: 22208', 22208),
 ('05A: 22209', 22209),
 ('05A: 22210', 22210),
 ('05A: 22211', 22211),
 ('06A: 22212', 22212),
 ('06A: 22213', 22213),
 ('06A: 22214', 22214)]
DUNGEON_ID_CHOICES = [('Random', None),
 ('Asteroid: 5810 Canyon', 5810),
 ('Asteroid: 6047 The Fall', 6047),
 ('Asteroid: 6200 Rise', 6200),
 ('Asteroid: 6201 Obelix', 6201),
 ('Asteroid: 6202 The Belt', 6202),
 ('Pillar: 6048 Forest Opening', 6048),
 ('Pillar: 6049 The Hill', 6049),
 ('Pillar: 6050 Strike Down', 6050),
 ('Pillar: 6051 Shattered Oak', 6051),
 ('Pillar: 6052 Fallen Forest', 6052),
 ('Crystal: 6203 Crystal 1', 6203),
 ('Crystal: 6204 Crystal 2', 6204),
 ('Crystal: 6205 Crystal 3', 6205),
 ('Crystal: 6206 Crystal 4', 6206),
 ('Crystal: 6207 Crystal 5', 6207)]
LENS_FLARE_TYPE_IDS = [('Random by weather', None),
 ('A30: black: %s ' % typeLensFlareA30, typeLensFlareA30),
 ('A31: blue: %s ' % typeLensFlareA31, typeLensFlareA31),
 ('A32: orange: %s ' % typeLensFlareA32, typeLensFlareA32),
 ('A33: pink: %s ' % typeLensFlareA33, typeLensFlareA33),
 ('A34: purple: %s ' % typeLensFlareA34, typeLensFlareA34),
 ('A35: white: %s ' % typeLensFlareA35, typeLensFlareA35),
 ('A36: yellow: %s ' % typeLensFlareA36, typeLensFlareA36)]
WEATHER_EFFECT_CHOICES = [('Random', None),
 ('Electric Storm Weather 1: %s' % typeElectricStormWeather1, typeElectricStormWeather1),
 ('Electric Storm Weather 2: %s' % typeElectricStormWeather2, typeElectricStormWeather2),
 ('Electric Storm Weather 3: %s' % typeElectricStormWeather3, typeElectricStormWeather3),
 ('Caustic Toxin Weather 1: %s' % typeCausticToxinWeather1, typeCausticToxinWeather1),
 ('Caustic Toxin Weather 2: %s' % typeCausticToxinWeather2, typeCausticToxinWeather2),
 ('Caustic Toxin Weather 3: %s' % typeCausticToxinWeather3, typeCausticToxinWeather3),
 ('Infernal Weather 1: %s' % typeInfernalWeather1, typeInfernalWeather1),
 ('Infernal Weather 2: %s' % typeInfernalWeather2, typeInfernalWeather2),
 ('Infernal Weather 3: %s' % typeInfernalWeather3, typeInfernalWeather3),
 ('Xenon Gas Weather 1: %s' % typeXenonGasWeather1, typeXenonGasWeather1),
 ('Xenon Gas Weather 2: %s' % typeXenonGasWeather2, typeXenonGasWeather2),
 ('Xenon Gas Weather 3: %s' % typeXenonGasWeather3, typeXenonGasWeather3),
 ('Darkness Weather 1: %s' % typeDarknessWeather1, typeDarknessWeather1),
 ('Darkness Weather 2: %s' % typeDarknessWeather2, typeDarknessWeather2),
 ('Darkness Weather 3: %s' % typeDarknessWeather3, typeDarknessWeather3)]
NPC_SPAWN_TABLE_IDS = [('Random', None),
 ('EM Drone Swarm [78]', 78),
 ('Therm Drone Swarm [79]', 79),
 ('Kin Drone Swarm [80]', 80),
 ('Exp Drone Swarm [81]', 81),
 ('Drone Boss [83]', 83),
 ('Damaged Drifter Fleet [84]', 84),
 ('Triglavian Gang [86]', 86),
 ('Damaged Triglavian Battleships [87]', 87),
 ('Omni Drone Swarm [88]', 88),
 ('Triglavian Drone Fleet [89]', 89),
 ('Seeker and Drifter swarm [90]', 90),
 ('Drone Battlecruisers [91]', 91),
 ('Damaged Drifter BS and Seekers [92]', 92),
 ('Sleeper Swarm [93]', 93),
 ('Malfunctioning Sleeper BS [94]', 94),
 ('Seeker and Sleeper Frig Swarm [95]', 95),
 ('Sleeper and Drifter Cruisers [96]', 96),
 ('Triglavians and Rogue Drones [97]', 97),
 ("Sansha's nation [366]", 366),
 ('Triglavian Battlecruisers [369]', 369),
 ('Rodiva / Kiki Fleet [370]', 370),
 ('CONCORD Fleet [371]', 371),
 ('Rodiva and Rogue Drones [372]', 372),
 ('Angel Cartel Expedition [375]', 375)]
