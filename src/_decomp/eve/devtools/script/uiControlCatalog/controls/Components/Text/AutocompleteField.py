#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Text\AutocompleteField.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.devtools.script.uiControlCatalog.sample import Sample

class _FieldSample(Sample):

    def construct_sample(self, parent):
        container = ContainerAutoSize(parent=parent, align=uiconst.TOPLEFT, width=500)
        self.sample_code(container)


class Sample1(_FieldSample):
    name = 'Category/group/type'

    def sample_code(self, parent):
        import eveui
        eveui.ItemField(parent=parent, align=uiconst.TOTOP, placeholder='Find category/group/type', show_suggestions_on_focus=True)
        eveui.ItemTypeField(parent=parent, align=uiconst.TOTOP, padTop=16, placeholder='Find Type only', show_suggestions_on_focus=True)


class Sample2(_FieldSample):
    name = 'Location'

    def sample_code(self, parent):
        import eveui
        eveui.LocationField(parent=parent, align=uiconst.TOTOP, placeholder='Find any location type', show_suggestions_on_focus=True)
        eveui.SolarSystemField(parent=parent, align=uiconst.TOTOP, padTop=16, placeholder='Find Solar System', show_suggestions_on_focus=True)


class Sample3(_FieldSample):
    name = 'NPC Faction/Corp'

    def sample_code(self, parent):
        import eveui
        eveui.NpcCorporationFactionField(parent=parent, align=uiconst.TOTOP, placeholder='Find NPC Corp or Faction', show_suggestions_on_focus=True)
        eveui.NpcCorporationField(parent=parent, align=uiconst.TOTOP, padTop=16, placeholder='Find NPC Corp', show_suggestions_on_focus=True)
        eveui.FactionField(parent=parent, align=uiconst.TOTOP, padTop=16, placeholder='Find NPC Faction', show_suggestions_on_focus=True)


class Sample4(_FieldSample):
    name = 'Agent'

    def sample_code(self, parent):
        import eveui
        eveui.AgentField(parent=parent, align=uiconst.TOTOP, placeholder='Find Agent', show_suggestions_on_focus=True)


class Sample5(Sample):
    name = 'Multiple providers'

    def sample_code(self, parent):
        import eveui
        eveui.autocomplete.AutocompleteField(parent=parent, align=uiconst.TOTOP, width=260, placeholder='Find anything', provider=[eveui.autocomplete.ItemTypeProvider(),
         eveui.autocomplete.ItemGroupProvider(),
         eveui.autocomplete.ItemCategoryProvider(),
         eveui.autocomplete.SolarSystemProvider()])


class Sample6(Sample):
    name = 'Custom provider'

    def sample_code(self, parent):
        import eveui
        data = [('A Good Start', '78_64_13'),
         ('A Tiny Palm Tree', '101_64_7'),
         ('Battleship 3D', '78_64_8'),
         ('Crystal Schimitars +1', '78_64_2'),
         ('Dirty Fedora', '79_64_13'),
         ('Grandma', '78_64_4'),
         ('Hunky Capsuleer', '100_64_8'),
         ('Jade Dragon', '78_64_11'),
         ("Lil' Timmy", '101_64_12'),
         ('Space Sushi', '78_64_1')]

        def fetch_suggestions(query, previous_suggestions):
            for i, (name, _) in enumerate(data):
                match, score, _ = eveui.autocomplete.fuzzy_match(query, name)
                if match:
                    yield (score, CustomSuggestion(i))

        class CustomSuggestion(eveui.autocomplete.Suggestion):
            __slots__ = ('data_index',)
            key_attributes = __slots__

            def __init__(self, data_index):
                self.data_index = data_index

            @property
            def text(self):
                return data[self.data_index][0]

            def render_icon(self, size):
                texture = 'res:/UI/Texture/Icons/{}.png'.format(data[self.data_index][1])
                return Sprite(width=size, height=size, texturePath=texture)

        eveui.autocomplete.AutocompleteField(parent=parent, align=uiconst.TOPLEFT, width=260, placeholder='Search', provider=fetch_suggestions)
