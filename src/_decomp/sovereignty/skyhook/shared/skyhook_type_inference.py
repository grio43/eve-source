#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\skyhook\shared\skyhook_type_inference.py
import numbers
POWER = 'power'
WORKFORCE = 'workforce'

def get_skyhook_type_and_amount(reagent_type_id, reagent_amounts_info, power, workforce):
    if reagent_type_id:
        product_type = reagent_type_id
        amountPerPeriod, period = reagent_amounts_info
        secsInHour = 3600
        amountPerHour = round(float(amountPerPeriod) / (float(period) / secsInHour), 1)
        product_amount = amountPerHour
        return (product_type, product_amount)
    if power:
        product_type = POWER
        product_amount = power
        return (product_type, product_amount)
    if workforce:
        product_type = WORKFORCE
        product_amount = workforce
        return (product_type, product_amount)


def get_skyhook_product_type(reagent_type_id, power, workforce):
    if reagent_type_id:
        return reagent_type_id
    if power:
        return POWER
    if workforce:
        return WORKFORCE


def is_reagent_skyhook(product_type):
    return isinstance(product_type, numbers.Number)


def is_non_reagent_skyhook(product_type):
    return not is_reagent_skyhook(product_type)
