#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetsutil\markers.py
MARKER_COLORS = [(0, 0.721, 0.78, 0.5),
 (0, 0.78, 0.345, 0.5),
 (1, 0.992, 0.019, 0.5),
 (1, 0.4, 0.019, 0.5),
 (0.811, 0.164, 0.203, 0.5),
 (0.56, 0.56, 0.56, 0.5),
 (0.043, 0.286, 0.396, 0.5)]
MARKER_PATTERNS = ['res:/UI/Texture/classes/Exoplanets/Marker/marker_1.png',
 'res:/UI/Texture/classes/Exoplanets/Marker/marker_2.png',
 'res:/UI/Texture/classes/Exoplanets/Marker/marker_3.png',
 'res:/UI/Texture/classes/Exoplanets/Marker/marker_4.png',
 'res:/UI/Texture/classes/Exoplanets/Marker/marker_5.png',
 'res:/UI/Texture/classes/Exoplanets/Marker/marker_6.png',
 'res:/UI/Texture/classes/Exoplanets/Marker/marker_7.png']
MINIMUM_PERIOD = 0.25

def convert_transit_markers_to_classification_object(transit_markers):
    classification_object = {'transits': []}
    for transit in transit_markers:
        transit_info = {'epoch': transit.get_center(),
         'transitMarkers': transit.get_centers()}
        if transit.get_period_length():
            transit_info['period'] = transit.get_period_length()
        classification_object['transits'].append(transit_info)

    return classification_object


def are_markers_similar(marker_one, marker_two):
    marker_two_ranges = marker_two.get_transit_ranges(1.2)
    marker_one_markings = [ center for center in marker_one.get_centers() ]
    marker_one_markings.insert(0, marker_one_markings[0] - marker_one.get_period_length())
    marker_one_markings.append(marker_one_markings[1] + marker_one.get_period_length())
    hits = []
    for minimum_time, maximum_time in marker_two_ranges:
        for marking in marker_one_markings:
            if minimum_time <= marking <= maximum_time:
                hits.append((minimum_time, maximum_time))
                break

    return all((m_range in hits for m_range in marker_two_ranges))
