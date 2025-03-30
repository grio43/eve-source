#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Combo.py
from carbonui import Density, uiconst
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.control.combo import Combo
        Combo(parent=parent, align=uiconst.TOPLEFT, options=[('Option A', 1), ('Option B', 2, 'This is option B'), ('Option C', 3)])


class Sample2(Sample):
    name = 'Compact'

    def sample_code(self, parent):
        from carbonui.control.combo import Combo
        Combo(parent=parent, align=uiconst.TOPLEFT, options=[('Option A', 1), ('Option B', 2, 'This is option B'), ('Option C', 3)], density=Density.COMPACT)


class Sample3(Sample):
    name = 'With Icons'

    def sample_code(self, parent):
        from carbonui.control.combo import Combo
        Combo(parent=parent, align=uiconst.TOPLEFT, options=[('Option A', 1, None, 'res:/UI/Texture/classes/infoPanels/daily_opportunities.png'), ('Option B', 2, None, 'res:/UI/Texture/classes/infoPanels/LocationInfo.png'), ('Option C', 3, None, 'res:/UI/Texture/classes/infoPanels/Missions.png')])


class Sample4(Sample):
    name = 'Icon only'

    def sample_code(self, parent):
        from carbonui.control.combo import Combo
        Combo(parent=parent, align=uiconst.TOPLEFT, iconOnly=True, options=[('Option A', 1, None, 'res:/UI/Texture/classes/infoPanels/daily_opportunities.png'), ('Option B', 2, None, 'res:/UI/Texture/classes/infoPanels/LocationInfo.png'), ('Option C', 3, None, 'res:/UI/Texture/classes/infoPanels/Missions.png')])


class Sample5(Sample):
    name = 'Allow None'
    description = "The combo's selection can optionally be cleared."

    def sample_code(self, parent):
        from carbonui.control.combo import Combo
        Combo(parent=parent, align=uiconst.TOPLEFT, hasClearButton=True, nothingSelectedText='No selection', options=[('Option A', 1), ('Option B', 2), ('Option C', 3)])
