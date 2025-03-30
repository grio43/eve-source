#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\qa\skin_licenses_table.py
import evetypes
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import uiconst
from carbonui.control.scroll import Scroll
from carbonui.control.window import Window
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from cosmetics.client.ships.ship_skin_signals import on_skin_license_added, on_skin_license_updated, on_skin_license_deleted
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass

class SkinLicensesTableWindow(Window):
    __guid__ = 'SkinLicensesTableWindow'
    default_width = 600
    default_height = 600
    default_windowID = 'skinLicensesTableWindow'
    default_minSize = [default_width, default_height]

    def __init__(self, *args):
        super(SkinLicensesTableWindow, self).__init__(*args)
        self.SetCaption('Ship 3P SKIN Licenses')
        self._rebuilding = False
        self.scroll = Scroll(name='scroll', parent=self.sr.maincontainer, align=uiconst.TOALL)
        self.populate()
        on_skin_license_added.connect(self._on_skin_license_added)
        on_skin_license_updated.connect(self._on_skin_license_updated)
        on_skin_license_deleted.connect(self._on_skin_license_deleted)

    def _OnClose(self, *args, **kw):
        on_skin_license_added.disconnect(self._on_skin_license_added)
        on_skin_license_updated.disconnect(self._on_skin_license_updated)
        on_skin_license_deleted.disconnect(self._on_skin_license_deleted)
        super(SkinLicensesTableWindow, self)._OnClose(*args, **kw)

    def populate(self):
        self._rebuilding = True
        licenses = get_ship_skin_license_svc().get_my_licenses(force_refresh=True)
        entries = []
        for skin_hex, license in licenses.iteritems():
            data = [ u'{}'.format(x) or '' for x in [license.owner_character_id,
             evetypes.GetName(license.skin_design.ship_type_id),
             license.skin_design.name,
             1 if license.activated else 0,
             license.nb_unactivated,
             license.nb_escrowed,
             license.skin_hex] ]
            entries.append(GetFromClass(SkinLicenseTableEntry, {'label': '<t>'.join(data),
             'skin_license': license}))

        self.scroll.Load(contentList=entries, headers=self._get_headers())
        self._rebuilding = False

    def _get_headers(self):
        return ['char id',
         'ship type',
         'design name',
         'nb activated',
         'nb unactivated',
         'nb escrowed',
         'skin hex']

    def _on_skin_license_added(self, _skin_hex, _license):
        if not self._rebuilding:
            self.scroll.Clear()
            self.populate()

    def _on_skin_license_updated(self, _skin_hex, _license):
        if not self._rebuilding:
            self.scroll.Clear()
            self.populate()

    def _on_skin_license_deleted(self, _license):
        if not self._rebuilding:
            self.scroll.Clear()
            self.populate()


class SkinLicenseTableEntry(Generic):
    __guid__ = 'listentry.SkinLicenseTableEntry'
    __nonpersistvars__ = []

    def GetMenu(self):
        if session and session.role & ROLE_GML:
            menu = [('Revoke', lambda : revoke_license(self.sr.node.skin_license.skin_hex), ())]
            return menu


def grant_license_from_design(skin_design_id, nb_licenses):
    skin_hex = get_ship_skin_design_svc().admin_get_skin_design_cached_hex(skin_design_id)
    if skin_hex:
        get_ship_skin_license_svc().admin_grant_license(skin_hex, nb_licenses)


def revoke_license(skin_hex):
    get_ship_skin_license_svc().admin_revoke_license(skin_hex)
