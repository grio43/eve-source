#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\insuranceConst.py
from functools import total_ordering
INSURANCE_ICON = 'res:/ui/Texture/WindowIcons/insurance.png'
BASE_INSURANCE_FRACTION = 0.4
INSURANCE_FRACTION_INCREMENT = 0.5

@total_ordering

class InsurancePackage(object):
    __slots__ = ('payout_ratio', 'name')

    def __init__(self, payout_ratio, name):
        self.payout_ratio = payout_ratio
        self.name = name

    def __eq__(self, other):
        return (self.payout_ratio, self.name) == (other.payout_ratio, other.name)

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if isinstance(other, InsurancePackage):
            return self.payout_ratio < other.payout_ratio
        if isinstance(other, (int, long, float)):
            return self.payout_ratio < other
        return super(InsurancePackage, self).__lt__(other)


INSURANCE_PACKAGES = sorted([InsurancePackage(0.5, 'Basic'),
 InsurancePackage(0.6, 'Standard'),
 InsurancePackage(0.7, 'Bronze'),
 InsurancePackage(0.8, 'Silver'),
 InsurancePackage(0.9, 'Gold'),
 InsurancePackage(1.0, 'Platinum')])

def get_insurance_fractions_and_prices(full_insurance_price):
    return [ (insurance_fraction, _get_insurance_price_by_fraction(full_insurance_price, insurance_fraction)) for insurance_fraction in [ package.payout_ratio for package in INSURANCE_PACKAGES ] ]


def get_insurance_package_by_fraction(insurance_fraction):
    insurance_fraction = float('%.1f' % insurance_fraction)
    package_name = None
    for package in INSURANCE_PACKAGES:
        if insurance_fraction < package.payout_ratio:
            break
        package_name = package.name

    return package_name


def get_insurance_price_by_package(full_insurance_price, insurance_package):
    for package in INSURANCE_PACKAGES:
        if package.name == insurance_package:
            return _get_insurance_price_by_fraction(full_insurance_price, package.payout_ratio)

    raise ValueError('Insurance package not supported: %s' % insurance_package)


def _get_insurance_price_by_fraction(full_insurance_price, insurance_fraction):
    return float(full_insurance_price) * _get_insurance_increment_by_fraction(insurance_fraction)


def _get_insurance_increment_by_fraction(insurance_fraction):
    return (insurance_fraction - BASE_INSURANCE_FRACTION) * INSURANCE_FRACTION_INCREMENT
