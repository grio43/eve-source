#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\effects\effectconverter.py
import contextlib
import yaml
import dogma.const as dgmconst

def get_domain_idx_from_value(expressionValue):
    if expressionValue == 'Ship':
        return 'shipID'
    if expressionValue == 'Target':
        return 'targetID'
    if expressionValue == 'Char':
        return 'charID'
    if expressionValue == 'Self':
        return 'itemID'
    if expressionValue == 'Other':
        return 'otherID'
    raise RuntimeError('Could not decipher %s' % expressionValue)


EXPRESSIONS = set()

class ModifierExpression(object):

    def __init__(self, row, modifier_type, attributes, generator):
        self.__modifier_type__ = modifier_type
        self._generator = generator
        self._row = row
        self._yaml_expression = {}
        self._get_modified_info()
        self._attributes = attributes
        self.update_funcs_by_attribute = {'domain': self._update_domain,
         'skillTypeID': self._update_skill_type_id,
         'groupID': self._update_group_id}

    def _get_modified_info(self):
        self._modified_info = self._generator.get_db_expression_as_yaml_expression(self._row.arg1)

    def get_expression(self):
        self._update_expression()
        return self._yaml_expression

    def _update_expression(self):
        self._update_func()
        self._update_operator()
        self._update_modified_attribute()
        self._update_modifying_attribute()
        for attribute in self._attributes:
            self.update_funcs_by_attribute[attribute]()

    def _update_func(self):
        self._yaml_expression['func'] = self.__modifier_type__

    def _update_modifying_attribute(self):
        self._yaml_expression['modifyingAttributeID'] = self._generator.get_db_expression_as_yaml_expression(self._row.arg2)['attribute']

    def _update_modified_attribute(self):
        self._yaml_expression['modifiedAttributeID'] = self._modified_info['attribute']

    def _update_domain(self):
        self._yaml_expression['domain'] = self._modified_info['domain']

    def _update_operator(self):
        self._yaml_expression['operator'] = self._get_operator()

    def _get_operator(self):
        try:
            op = getattr(dgmconst, 'dgmAss%s' % self._modified_info['operator'])
        except:
            op = int(self._modified_info['operator'])

        return op

    def _update_skill_type_id(self):
        self._yaml_expression['skillTypeID'] = self._modified_info['skillTypeID']

    def _update_group_id(self):
        self._yaml_expression['groupID'] = self._modified_info['groupID']


class YamlExpressionGenerator:

    def __init__(self, get_expression_row):
        self._get_expression_row = get_expression_row

    def get_db_expression_as_yaml_expression(self, expression_id):
        global EXPRESSIONS
        EXPRESSIONS.add(expression_id)
        expression_row = self._get_expression_row(expression_id)
        operandID = expression_row.operandID
        try:
            expression = self.get_expression_by_operand_id(expression_row)
        except KeyError:
            if operandID == dgmconst.operandCOMBINE:
                return self.get_db_expression_as_yaml_expression(expression_row.arg1) + self.get_db_expression_as_yaml_expression(expression_row.arg2)
            if operandID == dgmconst.operandDEFENVIDX:
                return {'domain': get_domain_idx_from_value(expression_row.expressionValue)}
            if operandID == dgmconst.operandDEFATTRIBUTE:
                return {'attribute': expression_row.expressionAttributeID}
            if operandID == dgmconst.operandDEFASSOCIATION:
                return {'operator': expression_row.expressionValue}
            if operandID == dgmconst.operandDEFTYPEID:
                return {'skillTypeID': expression_row.expressionTypeID}
            if operandID == dgmconst.operandDEFGROUP:
                group_id = expression_row.expressionGroupID
                if group_id is None:
                    raise InvalidExpression()
                return {'groupID': group_id}
            if operandID == dgmconst.operandGETTYPE:
                raise InvalidExpression()
            else:
                yaml_expression = {}
                for arg in (expression_row.arg1, expression_row.arg2):
                    if arg is not None:
                        yaml_expression.update(self.get_db_expression_as_yaml_expression(arg))

                return yaml_expression
        else:
            return [expression.get_expression()]

    def get_expression_by_operand_id(self, expression_row):
        operand_id = expression_row.operandID
        modifier_name, attributes = MODIFIER_INFO_BY_OPERAND[operand_id]
        return ModifierExpression(expression_row, modifier_name, attributes, self)


def get_db_expression_as_yaml_expression(expression_id):
    return YamlExpressionGenerator(get_expression_row_from_db).get_db_expression_as_yaml_expression(expression_id)


class InvalidExpression(Exception):
    pass


MODIFIER_INFO_BY_OPERAND = {dgmconst.operandALRSM: ('LocationRequiredSkillModifier', ('domain', 'skillTypeID')),
 dgmconst.operandAORSM: ('OwnerRequiredSkillModifier', ('domain', 'skillTypeID')),
 dgmconst.operandAIM: ('ItemModifier', ('domain',)),
 dgmconst.operandALGM: ('LocationGroupModifier', ('domain', 'groupID')),
 dgmconst.operandALM: ('LocationModifier', ('domain',))}
EXPRESSIONS_BY_ID = None

def get_expression_row_from_db(expression_id):
    global EXPRESSIONS_BY_ID
    if EXPRESSIONS_BY_ID is None:
        with db_connection() as connection:
            expressions = connection.execute('select * from dogma.expressions').fetchall()
            EXPRESSIONS_BY_ID = {r.expressionID:r for r in expressions}
    return EXPRESSIONS_BY_ID[expression_id]


@contextlib.contextmanager
def db_connection():
    import pyodbc
    sqlConnection = pyodbc.connect('DRIVER={SQL Server};SERVER=sqldev1is;DATABASE=local_eve_audunn;Trusted_Connection=yes')
    sqlConnection.autocommit = True
    cursor = sqlConnection.cursor()
    try:
        yield cursor
    finally:
        sqlConnection.close()


def get_data_for_conversion(path = None):
    modifier_info_by_effect = {}
    effect_ids = [4,
     901,
     263,
     9,
     10,
     4491,
     4492,
     3855,
     17,
     18,
     6165,
     4689,
     26,
     2971,
     4489,
     34,
     27,
     6692,
     4773,
     38,
     5163,
     1199,
     4656,
     3380,
     649,
     569,
     4490,
     650,
     1086,
     4928,
     67,
     2757,
     6753,
     4936,
     3852,
     1738,
     6690,
     4686,
     2255,
     592,
     3793,
     5275,
     4942,
     4921,
     4687,
     6693,
     4688,
     6715,
     2726,
     102,
     103,
     104,
     1129,
     2413,
     4728,
     127]
    with db_connection() as connection:
        for effect in connection.execute('select effectID, preExpression, modifierInfo from dogma.effects').fetchall():
            if effect.modifierInfo or effect.effectID not in effect_ids:
                continue
            pre_expression = effect.preExpression
            expression = get_expression_row_from_db(pre_expression)
            if expression.operandID in MODIFIER_INFO_BY_OPERAND or expression.operandID == dgmconst.operandCOMBINE:
                try:
                    modifier_info_by_effect[effect.effectID] = get_db_expression_as_yaml_expression(pre_expression)
                except InvalidExpression:
                    continue
                except Exception:
                    raise RuntimeError('Failed on effect %s' % effect.effectID)

    if path is None:
        with open('modifier_data33.yaml', 'w') as f:
            yaml.dump(modifier_info_by_effect, f, default_flow_style=False)
    else:
        with open(path, 'w') as f:
            yaml.dump(modifier_info_by_effect, f, default_flow_style=False)


if __name__ == '__main__':
    get_data_for_conversion()
