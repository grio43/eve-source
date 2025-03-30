#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\qa_tools.py
from functools import partial
from carbon.common.script.sys.service import ROLE_QA
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData

def is_qa():
    return bool(session.role & ROLE_QA)


def get_objective_chain_context_menu(objective_chain, include_blackboard = False):
    result = MenuData()
    if not is_qa() or not objective_chain:
        return result
    if objective_chain.node_graph:
        result.AddEntry('Open Objective Chain Node Graph', func=lambda : _open_active_node_graph(objective_chain.node_graph.instance_id))
    result.AddEntry('Open Objective Chain in FSD Editor', func=lambda : _open_objective_chain(objective_chain.content_id))

    def toggle_objective(objective_id):
        objective = objective_chain.objectives.get(objective_id)
        if objective and objective.is_active:
            objective_chain.stop_objective(objective_id)
        else:
            objective_chain.start_objective(objective_id)

    objectives = []
    for objective_id, objective_info in objective_chain.objectives_info.iteritems():
        objective = objective_chain.objectives.get(objective_id)
        objectives.append(MenuEntryData(objective_id, func=partial(toggle_objective, objective_id), subMenuData=get_objective_context_menu(objective, False)))

    result.AddEntry('Objectives', subMenuData=objectives)
    if include_blackboard:
        result.entrylist.append(key_value_entry('Blackboard Values', objective_chain.context.values, objective_chain.context))
    return result


def get_objective_context_menu(objective, group = True):
    result = MenuData()
    if not is_qa() or not objective:
        return result

    def toggle_completed(objective):
        objective.completed = not objective.completed

    def toggle_active(objective):
        if objective.is_active:
            objective.stop()
        else:
            objective.start()

    def toggle_hidden(objective):
        objective.hidden = not objective._hidden

    result.AddEntry('Completed: {}'.format(objective.completed), func=partial(toggle_completed, objective))
    result.AddEntry('Active: {}'.format(objective.is_active), func=partial(toggle_active, objective))
    result.AddEntry('Hidden: {} ({})'.format(objective.hidden, objective._hidden), func=partial(toggle_hidden, objective))
    result.entrylist.append(key_value_entry('Objective Values', objective._objective_values))
    tasks = []
    for task in objective._tasks.itervalues():
        tasks.append(MenuEntryData(task.task_id, subMenuData=get_objective_task_context_menu(task, False)))

    result.AddEntry('Tasks', subMenuData=tasks)
    if group:
        data = MenuData()
        data.AddEntry('QA', subMenuData=result)
        return data
    else:
        return result


def get_objective_task_context_menu(task, group = True):
    result = MenuData()
    if not is_qa():
        return result

    def toggle_completed(task):
        task.completed = not task.completed

    def toggle_active(task):
        if task.is_active:
            task.stop()
        else:
            task.start()

    result.AddEntry('Completed: {}'.format(task.completed), func=partial(toggle_completed, task))
    result.AddEntry('Active: {}'.format(task.is_active), func=partial(toggle_active, task))
    result.AddEntry('Hidden: {}'.format(task.hidden))
    result.AddSeparator()
    result.entrylist.extend(key_value_entry('Values', task.get_values())._subMenuData)
    if group:
        data = MenuData()
        data.AddEntry('QA', subMenuData=result)
        return data
    else:
        return result


def key_value_entry(key, value, context = None, path = None):
    from utillib import KeyVal
    import eveui
    if path is None:
        path = ''
    elif path:
        path = '{}.{}'.format(path, key)
    else:
        path = key

    def _copy_value(value):
        if context and path and eveui.Key.shift.is_down:
            edit_context_value(context, path)
            return
        import json
        import blue
        if isinstance(value, dict):
            try:
                clipboard_data = json.dumps(value, indent=2, sort_keys=True)
            except:
                clipboard_data = unicode(dict(value))

        else:
            clipboard_data = unicode(value)
        blue.pyos.SetClipboardData(clipboard_data)

    if isinstance(value, KeyVal):
        value = value.__dict__
    if isinstance(value, dict):
        sub_menu = []
        for value_key, value_value in value.iteritems():
            sub_menu.append(key_value_entry(value_key, value_value, context, path))

        return MenuEntryData(key, func=partial(_copy_value, value), subMenuData=sub_menu)
    elif isinstance(value, list):
        sub_menu = []
        for index, value_value in enumerate(value):
            sub_menu.append(key_value_entry(index, value_value, context, path))

        return MenuEntryData(u'{} ({})'.format(key, len(value)), func=partial(_copy_value, value), subMenuData=sub_menu)
    else:
        try:
            label = u'{}: {}'.format(key, value)
        except AttributeError:
            label = u'{}: __object__'.format(key)

        return MenuEntryData(label, func=partial(_copy_value, value))


def edit_context_value(context, path):
    from eve.client.script.ui.util import uix
    import carbonui.const as uiconst
    from ast import literal_eval
    from objectives.common.objective_context import get_object_value_by_path, set_object_value_by_path
    current_value = get_object_value_by_path(context.values, path)
    format = [{'type': 'text',
      'text': path}, {'type': 'text',
      'text': current_value}, {'type': 'textedit',
      'key': 'new_value',
      'setvalue': unicode(current_value),
      'label': '_hide',
      'setfocus': 1,
      'height': 150}]
    retval = uix.HybridWnd(format, caption='Edit Context Value', windowID='edit_context_value', modal=1, buttons=uiconst.OKCANCEL, minW=300, minH=50)
    if not retval:
        return
    try:
        new_value = literal_eval(retval['new_value'])
    except:
        new_value = retval['new_value']

    path_list = path.split('.')
    key = path_list[0]
    if len(path_list) > 1:
        path = '.'.join(path_list[1:])
        key_value = set_object_value_by_path(context.get_value(key), path, new_value)
        context.update_value(key, key_value)
    else:
        context.update_value(key, new_value)


def _open_objective_chain(content_id):
    import webbrowser
    webbrowser.open_new('http://localhost:8000/objectives/objective_chains/{}/'.format(content_id))


def _open_active_node_graph(node_graph_instance_id):
    from nodegraph.client.ui.window import NodeGraphEditorWindow
    NodeGraphEditorWindow.Open(node_graph_id=node_graph_instance_id)
