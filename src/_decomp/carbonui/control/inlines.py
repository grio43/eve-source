#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\inlines.py
_inline_type_to_deco_class = None

def get_inline_deco_class(inline_type):
    global _inline_type_to_deco_class
    if _inline_type_to_deco_class is None:
        _initialize_inline_type_to_deco_class_map()
    try:
        return _inline_type_to_deco_class[inline_type]
    except KeyError:
        return


def _initialize_inline_type_to_deco_class_map():
    global _inline_type_to_deco_class
    import carbonui.control.editPlainText
    import carbonui.control.edit_components
    _inline_type_to_deco_class = {'EditTextlineCore': carbonui.control.editPlainText.SE_EditTextlineCore,
     'border': carbonui.control.edit_components.BorderUnderlay,
     'div': carbonui.control.edit_components.DivOverlay,
     'hr': carbonui.control.edit_components.hr,
     'img': carbonui.control.edit_components.ImgListentry,
     'table': carbonui.control.edit_components.VirtualTable}
