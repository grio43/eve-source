#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\search.py
import eveui
import utillib
from nodegraph.common.nodedata import get_node_type
from nodegraph.common.atomdata import get_atom_data
from nodegraph.common.util import get_operator_function
from .parameter_field import ParameterField
from .list_item import NodeGraphListItem, ListItem

class NodeGraphSearch(eveui.Container):

    def __init__(self, select_node_graph, **kwargs):
        super(NodeGraphSearch, self).__init__(**kwargs)
        self._select_node_graph = select_node_graph
        self._reconstruct()

    def _reconstruct(self):
        self.Flush()
        eveui.EveLabelLarge(parent=self, align=eveui.Align.to_top, text='Find Usage', padBottom=12)
        node_graph_parameter = utillib.KeyVal(parameterKey='Node Graph', parameterType='nodeGraphIdType', description='', defaultValue=None, isRequired=False)
        self._node_graph_parameter = ParameterField(parent=self, align=eveui.Align.to_top, parameter=node_graph_parameter, value=search_values.get('node_graph_id', None), on_change=self._node_graph_changed)
        node_type_parameter = utillib.KeyVal(parameterKey='Node Type', parameterType='nodeTypeIdType', description='', defaultValue=None, isRequired=False)
        self._node_type_parameter = ParameterField(parent=self, align=eveui.Align.to_top, parameter=node_type_parameter, value=search_values.get('node_type_id', None), on_change=self._node_type_changed)
        atom_type_parameter = utillib.KeyVal(parameterKey='Atom Type', parameterType='atomIdType', description='', defaultValue=None, isRequired=False)
        self._atom_type_parameter = ParameterField(parent=self, align=eveui.Align.to_top, parameter=atom_type_parameter, value=search_values.get('atom_id', None), on_change=self._atom_type_changed)
        self._condition_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top)
        self._construct_condition()
        self._search_container = eveui.Container(parent=self, align=eveui.Align.to_all)
        self._construct_search_result()

    def _construct_condition(self):
        self._condition_container.Flush()
        if search_values.get('node_type_id', None) is None and search_values.get('atom_id', None) is None:
            return
        container = eveui.ContainerAutoSize(parent=self._condition_container, align=eveui.Align.to_top)
        self._parameter_condition = ParameterCondition(parent=container)

    def _construct_search_result(self):
        self._search_container.Flush()
        if search_values.get('node_type_id', None) is None and search_values.get('atom_id', None) is None:
            return
        eveui.Button(parent=self._search_container, align=eveui.Align.to_top, label='Find Usage', func=self._search, padTop=24)
        eveui.Button(parent=self._search_container, align=eveui.Align.to_top, label='Copy Results', func=self._copy_results, padTop=24)
        eveui.EveLabelMedium(parent=self._search_container, align=eveui.Align.to_top, text=u'Number of node graphs: {}'.format(len(search_result.keys())), padTop=12)
        self._search_result_container = eveui.ScrollContainer(parent=self._search_container, align=eveui.Align.to_all, padTop=12)
        for node_graph_id, node_ids in search_result.iteritems():
            NodeGraphListItem(parent=self._search_result_container, node_graph_id=node_graph_id, on_click=self._select_node_graph)

    def _node_graph_changed(self, parameter_id, value):
        search_values['node_graph_id'] = value
        self._reconstruct()

    def _node_type_changed(self, parameter_id, value):
        search_values['node_type_id'] = value
        if value:
            search_values['atom_id'] = None
        self._conditions = []
        search_result.clear()
        self._reconstruct()

    def _atom_type_changed(self, parameter_id, value):
        search_values['atom_id'] = value
        if value:
            search_values['node_type_id'] = None
        self._conditions = []
        search_result.clear()
        self._reconstruct()

    def _search(self, *args, **kwargs):
        from nodegraph.tools import find_usage
        self._searching = True
        self.Disable()
        search_result.clear()
        loading = eveui.DottedProgress(parent=self._search_container, align=eveui.Align.center, dot_size=10)
        search_parameters = {'node_type_id': search_values['node_type_id'],
         'atom_id': search_values['atom_id'],
         'node_graph_id': search_values['node_graph_id'],
         'condition': self._parameter_condition.get_compare_function()}
        search_result.update(find_usage(**search_parameters))
        loading.Close()
        self._searching = False
        self._construct_search_result()
        self.Enable()

    def _copy_results(self, *args, **kwargs):
        import blue
        blue.pyos.SetClipboardData(str(search_result))


class ParameterCondition(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_padTop = 12

    def __init__(self, **kwargs):
        super(ParameterCondition, self).__init__(**kwargs)
        self._parameters = {}
        node_type_id = search_values.get('node_type_id', None)
        if node_type_id:
            node_type = get_node_type(node_type_id)
            for parameter in node_type.parameters.inputs:
                self._parameters[parameter.parameterKey] = parameter

        atom_id = search_values.get('atom_id', None)
        if atom_id:
            atom_type = get_atom_data(atom_id)
            for parameter in atom_type.parameters.inputs:
                self._parameters[parameter.parameterKey] = parameter

        if not self._parameters:
            return
        options = [('None', None)]
        options.extend([ (parameter, parameter) for parameter in self._parameters.iterkeys() ])
        eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text='Parameter Key')
        eveui.Combo(parent=self, align=eveui.Align.to_top, options=options, callback=self._handle_parameter)
        operator_type_parameter = utillib.KeyVal(parameterKey='Operator', parameterType='operatorType', description='', defaultValue=None, isRequired=False)
        ParameterField(parent=self, align=eveui.Align.to_top, parameter=operator_type_parameter, value=search_values['parameter_condition']['operator'], on_change=self._operator_type_changed)
        self._parameter_value_field = None

    def _handle_parameter(self, combo, key, value):
        search_values['parameter_condition']['key'] = value
        search_values['parameter_condition']['value'] = None
        if self._parameter_value_field:
            self._parameter_value_field.Close()
        if value:
            self._parameter_value_field = ParameterField(parent=self, align=eveui.Align.to_top, parameter=self._parameters[value], value=None, on_change=self._handle_parameter_value)

    def _handle_parameter_value(self, parameter_id, value):
        search_values['parameter_condition']['value'] = value

    def _operator_type_changed(self, parameter_id, value):
        search_values['parameter_condition']['operator'] = value

    def get_compare_function(self):
        from nodegraph.tools import get_parameter_value
        if search_values['parameter_condition']['key']:
            operator_function = get_operator_function(search_values['parameter_condition']['operator'])
            return lambda node: operator_function(get_parameter_value(node, search_values['parameter_condition']['key']), search_values['parameter_condition']['value'])


search_values = {'atom_id': None,
 'node_type_id': None,
 'parameter_condition': {'key': None,
                         'operator': 'equalTo',
                         'value': None},
 'node_graph_id': None}
search_result = {}
