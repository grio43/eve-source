#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireTechnologyViews\shipsViewData.py
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
import log
AMARR_SHIP_DATA = {1: {'color_code': (0, 0, 1, 1),
     'description': 'Amarr battleship',
     'tooltip_top': 186,
     'tooltip_left': -1},
 2: {'color_code': (0, 1, 0, 1),
     'description': 'Amarr frigate',
     'tooltip_top': 449,
     'tooltip_left': -106},
 3: {'color_code': (1, 1, 1, 1),
     'description': 'Amarr industrial',
     'tooltip_top': 445,
     'tooltip_left': 159},
 4: {'color_code': (1, 0, 1, 1),
     'description': 'Amarr ewar',
     'tooltip_top': 160,
     'tooltip_left': 775},
 5: {'color_code': (1, 0, 0, 1),
     'description': 'Amarr corvette',
     'tooltip_top': 427,
     'tooltip_left': 609}}
CALDARI_SHIP_DATA = {1: {'color_code': (0, 0, 1, 1),
     'description': 'Caldari battleship',
     'tooltip_top': 190,
     'tooltip_left': 213},
 2: {'color_code': (0, 1, 0, 1),
     'description': 'Caldari frigate',
     'tooltip_top': 250,
     'tooltip_left': -136},
 3: {'color_code': (1, 1, 1, 1),
     'description': 'Caldari industrial',
     'tooltip_top': 443,
     'tooltip_left': -3},
 4: {'color_code': (1, 0, 1, 1),
     'description': 'Caldari ewar',
     'tooltip_top': 167,
     'tooltip_left': 380},
 5: {'color_code': (1, 0, 0, 1),
     'description': 'Caldari corvette',
     'tooltip_top': 349,
     'tooltip_left': 244}}
GALLENTE_SHIP_DATA = {1: {'color_code': (0, 0, 1, 1),
     'description': 'Gallente battleship',
     'tooltip_top': 6,
     'tooltip_left': -143},
 2: {'color_code': (0, 1, 0, 1),
     'description': 'Gallente frigate',
     'tooltip_top': 247,
     'tooltip_left': 58},
 3: {'color_code': (1, 1, 1, 1),
     'description': 'Gallente industrial',
     'tooltip_top': 364,
     'tooltip_left': 97},
 4: {'color_code': (1, 0, 1, 1),
     'description': 'Gallente ewar',
     'tooltip_top': 46,
     'tooltip_left': 660},
 5: {'color_code': (1, 0, 0, 1),
     'description': 'Gallente corvette',
     'tooltip_top': 415,
     'tooltip_left': 800}}
MINMATAR_SHIP_DATA = {1: {'color_code': (0, 0, 1, 1),
     'description': 'Minmatar battleship',
     'tooltip_top': 127,
     'tooltip_left': -51},
 2: {'color_code': (0, 1, 0, 1),
     'description': 'Minmatar frigate',
     'tooltip_top': 326,
     'tooltip_left': -173},
 3: {'color_code': (1, 1, 1, 1),
     'description': 'Minmatar industrial',
     'tooltip_top': 387,
     'tooltip_left': -120},
 4: {'color_code': (1, 0, 1, 1),
     'description': 'Minmatar ewar',
     'tooltip_top': 174,
     'tooltip_left': 605},
 5: {'color_code': (1, 0, 0, 1),
     'description': 'Minmatar corvette',
     'tooltip_top': 280,
     'tooltip_left': 622}}
SHIP_DATA = {raceAmarr: AMARR_SHIP_DATA,
 raceCaldari: CALDARI_SHIP_DATA,
 raceGallente: GALLENTE_SHIP_DATA,
 raceMinmatar: MINMATAR_SHIP_DATA}

class ShipData(object):

    def __init__(self, technology, raceID):
        self.ship_data = {}
        self.build_ship_data(technology, raceID)

    def build_ship_data(self, technology, raceID):
        for order, tech_example in technology.GetTechExamples():
            try:
                base_data = SHIP_DATA[raceID][order]
                icon = tech_example.GetIcon(raceID)
                title = tech_example.GetTitle(raceID)
                subtitle = tech_example.GetSubtitle(raceID)
                self.ship_data[order] = {'color_code': base_data['color_code'],
                 'tooltip_top': base_data['tooltip_top'],
                 'tooltip_left': base_data['tooltip_left'],
                 'icon': icon,
                 'title': title,
                 'subtitle': subtitle}
            except KeyError:
                log.LogWarn('Ship data not available for ship example with id %d' % order)

    def get_ship_data(self):
        return self.ship_data
