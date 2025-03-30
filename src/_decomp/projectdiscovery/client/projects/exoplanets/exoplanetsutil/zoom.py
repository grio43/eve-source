#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetsutil\zoom.py


def get_zoom_animation_duration(start_zoom, end_zoom, max_duration = 1.0):
    end_zoom_distance = end_zoom[1] - end_zoom[0]
    start_zoom_distance = start_zoom[1] - start_zoom[0]
    gap_distance = max(end_zoom_distance, start_zoom_distance) - min(end_zoom_distance, start_zoom_distance)
    ratio = gap_distance / max(end_zoom_distance, start_zoom_distance)
    return max_duration * ratio
