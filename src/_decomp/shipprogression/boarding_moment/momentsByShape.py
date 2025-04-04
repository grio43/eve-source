#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\momentsByShape.py
from shipprogression.boarding_moment.ui import const as moment_ui_const
from shipprogression.boarding_moment.const import MomentSteps, ShipShape, ShipSize
MOMENTS_BY_SHAPE = {(ShipShape.BOX, ShipSize.SMALL): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_s/Tease01_BoxShip_S.red',
                                    'step': MomentSteps.TEASE_1,
                                    'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_s/Boosters01_BoxShip_S.red',
                                    'locator': 'locator_booster_1',
                                    'step': MomentSteps.BOOSTERS_1},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_s/Reveal01_BoxShip_S.red',
                                    'step': MomentSteps.REVEAL_1,
                                    'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_s/Climax01_BoxShip_S.red',
                                    'step': MomentSteps.CLIMAX_1,
                                    'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.BOX, ShipSize.MEDIUM): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_ml/tease01_BoxShip_ml.red',
                                     'step': MomentSteps.TEASE_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_ml/boosters01_BoxShip_ml.red',
                                     'locator': 'locator_booster_1',
                                     'step': MomentSteps.BOOSTERS_1},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_ml/reveal01_BoxShip_ml.red',
                                     'step': MomentSteps.REVEAL_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_ml/reveal02_BoxShip_ml.red',
                                     'step': MomentSteps.REVEAL_2},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_ml/climax01_BoxShip_ml.red',
                                     'step': MomentSteps.CLIMAX_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.BOX, ShipSize.LARGE): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_xl/tease01_BoxShip_xl.red',
                                    'step': MomentSteps.TEASE_1,
                                    'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_xl/tease02_BoxShip_xl.red',
                                    'step': MomentSteps.TEASE_2},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_xl/boosters01_BoxShip_xl.red',
                                    'locator': 'locator_booster_1',
                                    'step': MomentSteps.BOOSTERS_1},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_xl/reveal01_BoxShip_xl.red',
                                    'step': MomentSteps.REVEAL_1,
                                    'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_xl/reveal02_BoxShip_xl.red',
                                    'locator': 'locator_xl_1a',
                                    'step': MomentSteps.REVEAL_2},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_xl/reveal03_BoxShip_xl.red',
                                    'step': MomentSteps.REVEAL_3},
                                   {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/box_xl/climax01_BoxShip_xl.red',
                                    'step': MomentSteps.CLIMAX_1,
                                    'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.LONG, ShipSize.SMALL): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_s/tease01_LongShip_s.red',
                                     'step': MomentSteps.TEASE_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_s/boosters01_LongShip_s.red',
                                     'locator': 'locator_booster_1',
                                     'step': MomentSteps.BOOSTERS_1},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_s/reveal01_LongShip_s.red',
                                     'step': MomentSteps.REVEAL_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_s/climax01_LongShip_s.red',
                                     'step': MomentSteps.CLIMAX_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.LONG, ShipSize.MEDIUM): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_ml/tease01_LongShip_ml.red',
                                      'step': MomentSteps.TEASE_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_ml/boosters01_LongShip_ml.red',
                                      'locator': 'locator_booster_1',
                                      'step': MomentSteps.BOOSTERS_1},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_ml/reveal01_LongShip_ml.red',
                                      'step': MomentSteps.REVEAL_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_ml/reveal02_LongShip_ml.red',
                                      'step': MomentSteps.REVEAL_2},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_ml/climax01_LongShip_ml.red',
                                      'step': MomentSteps.CLIMAX_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.LONG, ShipSize.LARGE): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_xl/tease01_LongShip_xl.red',
                                     'step': MomentSteps.TEASE_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_xl/tease02_LongShip_xl.red',
                                     'step': MomentSteps.TEASE_2},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_xl/boosters01_LongShip_xl.red',
                                     'locator': 'locator_booster_1',
                                     'step': MomentSteps.BOOSTERS_1},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_xl/reveal01_LongShip_xl.red',
                                     'step': MomentSteps.REVEAL_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_xl/reveal02_LongShip_xl.red',
                                     'locator': 'locator_xl_1a',
                                     'step': MomentSteps.REVEAL_2},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_xl/reveal03_LongShip_xl.red',
                                     'step': MomentSteps.REVEAL_3},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/long_xl/climax01_LongShip_xl.red',
                                     'step': MomentSteps.CLIMAX_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.WIDE, ShipSize.SMALL): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_s/tease01_WideShip_s.red',
                                     'step': MomentSteps.TEASE_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_s/boosters01_WideShip_s.red',
                                     'locator': 'locator_booster_1',
                                     'step': MomentSteps.BOOSTERS_1},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_s/reveal01_WideShip_s.red',
                                     'step': MomentSteps.REVEAL_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_s/climax01_WideShip_s.red',
                                     'step': MomentSteps.CLIMAX_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.WIDE, ShipSize.MEDIUM): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_ml/tease01_WideShip_ml.red',
                                      'step': MomentSteps.TEASE_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_ml/boosters01_WideShip_ml.red',
                                      'locator': 'locator_booster_1',
                                      'step': MomentSteps.BOOSTERS_1},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_ml/reveal01_WideShip_ml.red',
                                      'step': MomentSteps.REVEAL_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_ml/reveal02_WideShip_ml.red',
                                      'step': MomentSteps.REVEAL_2},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_ml/climax01_WideShip_ml.red',
                                      'step': MomentSteps.CLIMAX_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.WIDE, ShipSize.LARGE): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_xl/tease01_WideShip_xl.red',
                                     'step': MomentSteps.TEASE_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_xl/tease02_WideShip_xl.red',
                                     'step': MomentSteps.TEASE_2},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_xl/boosters01_WideShip_xl.red',
                                     'locator': 'locator_booster_1',
                                     'step': MomentSteps.BOOSTERS_1},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_xl/reveal01_WideShip_xl.red',
                                     'step': MomentSteps.REVEAL_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_xl/reveal02_WideShip_xl.red',
                                     'locator': 'locator_xl_1a',
                                     'step': MomentSteps.REVEAL_2},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_xl/reveal03_WideShip_xl.red',
                                     'step': MomentSteps.REVEAL_3},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/wide_xl/climax01_WideShip_xl.red',
                                     'step': MomentSteps.CLIMAX_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.TALL, ShipSize.SMALL): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_s/tease01_TallShip_s.red',
                                     'step': MomentSteps.TEASE_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_s/boosters01_TallShip_s.red',
                                     'locator': 'locator_booster_1',
                                     'step': MomentSteps.BOOSTERS_1},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_s/reveal01_TallShip_s.red',
                                     'step': MomentSteps.REVEAL_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_s/climax01_TallShip_s.red',
                                     'step': MomentSteps.CLIMAX_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.TALL, ShipSize.MEDIUM): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_ml/tease01_TallShip_ml.red',
                                      'step': MomentSteps.TEASE_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_ml/boosters01_TallShip_ml.red',
                                      'locator': 'locator_booster_1',
                                      'step': MomentSteps.BOOSTERS_1},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_ml/reveal01_TallShip_ml.red',
                                      'step': MomentSteps.REVEAL_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_ml/reveal02_TallShip_ml.red',
                                      'step': MomentSteps.REVEAL_2},
                                     {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_ml/climax01_TallShip_ml.red',
                                      'step': MomentSteps.CLIMAX_1,
                                      'ui_moments': moment_ui_const.UI_MOMENT_TITLE}],
 (ShipShape.TALL, ShipSize.LARGE): [{'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_xl/tease01_TallShip_xl.red',
                                     'step': MomentSteps.TEASE_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TRAITS},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_xl/tease02_TallShip_xl.red',
                                     'step': MomentSteps.TEASE_2},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_xl/boosters01_TallShip_xl.red',
                                     'locator': 'locator_booster_1',
                                     'step': MomentSteps.BOOSTERS_1},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_xl/reveal01_TallShip_xl.red',
                                     'step': MomentSteps.REVEAL_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_DESIGNER},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_xl/reveal02_TallShip_xl.red',
                                     'locator': 'locator_xl_1a',
                                     'step': MomentSteps.REVEAL_2},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_xl/reveal03_TallShip_xl.red',
                                     'step': MomentSteps.REVEAL_3},
                                    {'camera': 'res:/dx9/scene/cameras/firstBoardingCinematic/tall_xl/climax01_TallShip_xl.red',
                                     'step': MomentSteps.CLIMAX_1,
                                     'ui_moments': moment_ui_const.UI_MOMENT_TITLE}]}
