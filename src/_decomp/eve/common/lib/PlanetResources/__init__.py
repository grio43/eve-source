#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\lib\PlanetResources\__init__.py
import blue
import sys
_planetresources = blue.LoadExtension('_eveplanetresources')
PR_LUT_RESULUTION = 2048
_planetresources.builder = _planetresources.SHBuilder()
_planetresources.builder.GenerateLookUpTables(PR_LUT_RESULUTION)
sys.modules[__name__] = _planetresources
