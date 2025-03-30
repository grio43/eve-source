#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\fitting.py
import itertools
from nodegraph.client.util import get_item_name
from nodegraph.common.util import get_object_predicate, get_operator_function
from .base import Condition

class FittingWindowAttributeExpanded(Condition):
    atom_id = 297

    def __init__(self, menu_name = None, **kwargs):
        super(FittingWindowAttributeExpanded, self).__init__(**kwargs)
        self.menu_name = menu_name

    def validate(self, **kwargs):
        try:
            from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
            fitting_window = FittingWindow.GetIfOpen()
            return fitting_window.rightPanel.IsPanelExpanded(self.menu_name)
        except:
            return False

    @classmethod
    def get_subtitle(cls, menu_name = None, **kwargs):
        return u'{}'.format(menu_name)


class ItemFitted(Condition):
    atom_id = 33

    def __init__(self, item_id = None, type_id = None, group_id = None, quantity = None, operator = None, **kwargs):
        super(Condition, self).__init__(**kwargs)
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.quantity = self.get_atom_parameter_value('quantity', quantity)
        self.operator = self.get_atom_parameter_value('operator', operator)

    def validate(self, **kwargs):
        fitted_modules, fitted_charges = get_fitted_items()
        if not fitted_modules and not fitted_charges:
            return False
        if self.type_id:
            predicate = get_object_predicate('typeID', self.type_id)
        elif self.group_id:
            predicate = get_object_predicate('groupID', self.group_id)
        elif self.item_id:
            predicate = get_object_predicate('itemID', self.item_id)
        else:
            return False
        amount = 0
        operator_func = get_operator_function(self.operator)
        for item in itertools.chain(fitted_modules, fitted_charges):
            if predicate(item):
                amount += item.stacksize

        return operator_func(amount, self.quantity)

    @classmethod
    def get_subtitle(cls, type_id = None, group_id = None, quantity = None, operator = None, **kwargs):
        name = get_item_name(type_id=type_id, group_id=group_id)
        return u'{} {} - {}'.format(cls.get_atom_parameter_value('operator', operator), cls.get_atom_parameter_value('quantity', quantity), name)


def get_fitted_items():
    from eve.client.script.ui.inflight.shipHud import ActiveShipController
    ship_controller = ActiveShipController()
    return (ship_controller.GetModules(), ship_controller.GetCharges())
