#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveplanet\client\templates\templateConst.py
from itertoolsext.Enum import Enum

@Enum

class PlanetTypes:
    TEMPERATE = 11
    GAS_GIANT = 13
    ICE = 12
    LAVA = 2015
    OCEAN = 2014
    PLASMA = 2063
    BARREN = 2016
    THUNDERSTORM = 2017


@Enum

class ExtractionTypes:
    Microorganisms = 2073
    Carbon_Compounds = 2288
    Planktic_Colonies = 2286
    Non_CS_Crystals = 2306
    Ionic_Solutions = 2309
    Autotrophs = 2305
    Reactive_Gas = 2311
    Noble_Gas = 2310
    Suspended_Plasma = 2308
    Noble_Metals = 2270
    Complex_Organisms = 2287
    Base_Metals = 2267
    Felsic_Magma = 2307
    Heavy_Metals = 2272
    Aqueous_Liquids = 2268


@Enum

class ProcessedTypes:
    Plasmoids = 2389
    Electrolytes = 2390
    Oxidizing_Compound = 2392
    Bacteria = 2393
    Proteins = 2395
    Biofuels = 2396
    Industrial_Fibers = 2397
    Reactive_Metals = 2398
    Precious_Metals = 2399
    Toxic_Metals = 2400
    Chiral_Structures = 2401
    Water = 3645
    Oxygen = 3683
    Biomass = 3779
    Silicon = 9828


@Enum

class RefinedTypes:
    Enriched_Uranium = 44
    Supertensile_Plastics = 2312
    Oxides = 2317
    Test_Cultures = 2319
    Polyaramids = 2321
    Microfiber_Shielding = 2327
    Water_Cooled_CPU = 2328
    Biocells = 2329
    Nanites = 2463
    Mechanical_Parts = 3689
    Synthetic_Oil = 3691
    Fertilizer = 3693
    Polytextiles = 3695
    Silicate_Glass = 3697
    Livestock = 3725
    Viral_Agent = 3775
    Construction_Blocks = 3828
    Rocket_Fuel = 9830
    Coolant = 9832
    Consumer_Electronics = 9836
    Superconductors = 9838
    Transmitter = 9840
    Miniature_Electronics = 9842
    Genetically_Enhanced_Livestock = 15317


@Enum

class SpecializedTypes:
    Condensates = 2344
    Camera_Drones = 2345
    Synthetic_Synapses = 2346
    Gel_Matrix_Biopaste = 2348
    Supercomputers = 2349
    Smartfab_Units = 2351
    Nuclear_Reactors = 2352
    Neocoms = 2354
    Biotech_Research_Reports = 2358
    Industrial_Explosives = 2360
    Hermetic_Membranes = 2361
    Hazmat_Detection_Systems = 2366
    Cryoprotectant_Solution = 2367
    Guidance_Systems = 9834
    Planetary_Vehicles = 9846
    Robotics = 9848
    Transcranial_Microcontrollers = 12836
    Ukomi_Superconductors = 17136
    Data_Chips = 17392
    High_Tech_Transmitters = 17898
    Vaccines = 28974


@Enum

class AdvancedTypes:
    Broadcast_Node = 2867
    Integrity_Response_Drones = 2868
    Nano_Factory = 2869
    Organic_Mortar_Applicators = 2870
    Recursive_Computing_Module = 2871
    Self_Harmonizing_Power_Core = 2872
    Sterile_Conduits = 2875
    Wetware_Mainframe = 2876


@Enum

class TemplateDictKeys:
    PinData = 'P'
    LinkData = 'L'
    RouteData = 'R'
    PlanetType = 'Pln'
    Diameter = 'Diam'
    Comments = 'Cmt'
    CmdCenterLV = 'CmdCtrLv'


@Enum

class TemplatePinDataDictKeys:
    PinTypeID = 'T'
    Lat = 'La'
    Longi = 'Lo'
    Product = 'S'
    ExtractorHeadCount = 'H'


@Enum

class TemplateRouteDataDictKeys:
    Path = 'P'
    ItemType = 'T'
    ItemQuantity = 'Q'


@Enum

class TemplateLinkDataDictKeys:
    Source = 'S'
    Destination = 'D'
    Level = 'Lv'


EXTRACT_PRODUCTS = set(ExtractionTypes.itervalues())
PRODUCTION_PRODUCTS = set(ProcessedTypes.itervalues()).union(set(RefinedTypes.itervalues())).union(set(SpecializedTypes.itervalues())).union(set(AdvancedTypes.itervalues()))
