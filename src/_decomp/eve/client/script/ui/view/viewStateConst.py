#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\viewStateConst.py


class ViewState:
    Login = 'login'
    CharacterSelector = 'charsel'
    Space = 'inflight'
    Station = 'station'
    Hangar = 'hangar'
    StarMap = 'starmap'
    DockPanel = 'dockpanelview'
    SystemMap = 'systemmap'
    Planet = 'planet'
    ShipTree = 'shiptree'
    CharacterCreation = 'charactercreation'
    VirtualGoodsStore = 'virtual_goods_store'
    Structure = 'structure'
    StarMapNew = 'starmap_new'
    SystemMapNew = 'systemmap_new'
    SkillPlan = 'skill_plan'
    SkillTree = 'skill_tree'
    CareerPortal = 'career_portal'
    PaintTool = 'paint_tool'
    ShipSKINR = 'ship_skinr'


class ViewOverlay:
    Target = 'target'
    SidePanels = 'sidePanels'
    ShipUI = 'shipui'


def is_entering_character_selection(new_state):
    return new_state == ViewState.CharacterSelector


def is_entering_space(new_state):
    return new_state == ViewState.Space


def is_entering_game(old_state, new_state):
    return old_state in (ViewState.CharacterSelector, ViewState.CharacterCreation) and new_state in (ViewState.Space, ViewState.Station, ViewState.Hangar)
