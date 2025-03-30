#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\static_data\hull_type_projections.py
import blue
import evetypes
import fsdBuiltData
red_file_path = 'res:/dx9/model/SpaceObjectFactory/patterns/cosm_blank_projection.red'
_projections_by_hull_name = None

def get_projections_by_hull_type_name():
    global _projections_by_hull_name
    if _projections_by_hull_name is None:
        data = blue.resMan.LoadObject(red_file_path)
        _projections_by_hull_name = {p.name:p for p in data.projections}
    return _projections_by_hull_name


def get_default_scaling(hull_name):
    return get_projections_by_hull_type_name()[hull_name].transformLayer1.scaling[0]


def get_default_scaling_for_type(type_id):
    graphic_id = evetypes.GetGraphicID(type_id)
    hull_name = fsdBuiltData.common.graphicIDs.GetSofHullName(graphic_id)
    return get_default_scaling(hull_name)
