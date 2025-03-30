#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\entitlements\corporation\structure\qa.py
from eve.devtools.script.structureCosmetics import StructurePaintsTable
from cosmetics.client.messengers.entitlements.corporation.structure.qaconst import *

def get_insider_qa_menu():
    menu = ('Structure Cosmetics', (('Structure Cosmetics Tool', StructurePaintsTable.Open),
      ('Clear License & Catalogue Cache', flush_cache()),
      ('Force Structure Issue License Errors', (('On', lambda : set_force_structure_issue_license_errors(True)), ('Off', lambda : set_force_structure_issue_license_errors(False)))),
      ('Force Structure Issue License Delay', (('0', lambda : set_force_structure_issue_license_delay(0)), ('5', lambda : set_force_structure_issue_license_delay(5)), ('30', lambda : set_force_structure_issue_license_delay(30)))),
      ('Force Structure Get License Errors', (('On', lambda : set_force_structure_get_license_errors(True)), ('Off', lambda : set_force_structure_get_license_errors(False)))),
      ('Force Structure Get License Random Errors', (('On', lambda : set_force_structure_get_license_random_errors(True)), ('Off', lambda : set_force_structure_get_license_random_errors(False)))),
      ('Force Structure Get License Delay', (('0', lambda : set_force_structure_get_license_delay(0)), ('5', lambda : set_force_structure_get_license_delay(5)))),
      ('Force Structure Revoke License Errors', (('On', lambda : set_force_structure_revoke_license_errors(True)), ('Off', lambda : set_force_structure_revoke_license_errors(False)))),
      ('Force Structure Revoke License Delay', (('0', lambda : set_force_structure_revoke_license_delay(0)), ('10', lambda : set_force_structure_revoke_license_delay(5)))),
      ('Force Structure Get License Catalogue Errors', (('On', lambda : set_force_structure_get_license_catalogue_errors(True)), ('Off', lambda : set_force_structure_get_license_catalogue_errors(False)))),
      ('Force Structure Get License Catalogue Delay', (('0', lambda : set_force_structure_get_license_catalogue_delay(0)), ('10', lambda : set_force_structure_get_license_catalogue_delay(10)))),
      ('Force Structure Get Cosmetic State Errors', (('On', lambda : set_force_structure_get_cosmetic_state_errors(True)), ('Off', lambda : set_force_structure_get_cosmetic_state_errors(False)))),
      ('Force Structure Get Cosmetic State Delay', (('0', lambda : set_force_structure_get_cosmetic_state_delay(0)), ('10', lambda : set_force_structure_get_cosmetic_state_delay(5))))))
    return menu
