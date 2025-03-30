#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\qa\component_licenses_table.py
import blue
import eveicon
from carbonui import uiconst
from carbonui.control.forms import formComponent
from carbonui.control.forms.form import Form, FormActionSubmit, FormActionCancel
from carbonui.control.forms.formWindow import FormWindow
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui.control.scroll import Scroll
from carbonui.control.window import Window
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.ships.ship_skin_signals import on_component_license_granted, on_component_license_cache_invalidated
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass

class ComponentLicensesTableWindow(Window):
    __guid__ = 'ComponentLicensesTableWindow'
    default_width = 600
    default_height = 600
    default_windowID = 'componentLicensesTableWindow'
    default_minSize = [default_width, default_height]

    def __init__(self, *args):
        super(ComponentLicensesTableWindow, self).__init__(*args)
        self.SetCaption('Ship SKIN Component Licenses')
        self._rebuilding = False
        self.scroll = Scroll(name='scroll', parent=self.sr.maincontainer, align=uiconst.TOALL)
        self.populate()
        on_component_license_granted.connect(self._on_component_license_granted)
        on_component_license_cache_invalidated.connect(self._on_cache_invalidated)

    def _OnClose(self, *args, **kw):
        on_component_license_granted.disconnect(self._on_component_license_granted)
        on_component_license_cache_invalidated.disconnect(self._on_cache_invalidated)
        super(ComponentLicensesTableWindow, self)._OnClose(*args, **kw)

    def populate(self):
        self._rebuilding = True
        components = ComponentsDataLoader.get_components_data()
        entries = []
        for component_id, component in components.iteritems():
            infinite_license = get_ship_skin_component_svc().get_unbound_license(component_id, component.category)
            finite_license = get_ship_skin_component_svc().get_bound_license(component_id, component.category)
            data = [ str(x) or '' for x in [component_id,
             component.name,
             'Yes' if infinite_license else 'No',
             finite_license.remaining_license_uses if finite_license else '-'] ]
            entries.append(GetFromClass(ComponentLicenseTableEntry, {'label': '<t>'.join(data),
             'component': component}))

        self.scroll.Load(contentList=entries, headers=self._get_headers())
        self._rebuilding = False

    def _get_headers(self):
        return ['component id',
         'component name',
         'infinite license',
         'finite license uses']

    def _on_component_license_granted(self, *args):
        if not self._rebuilding:
            self.scroll.Clear()
            self.populate()

    def _on_cache_invalidated(self, _licenses):
        if not self._rebuilding:
            self.scroll.Clear()
            self.populate()


class ComponentLicenseTableEntry(Generic):
    __guid__ = 'listentry.ComponentLicenseTableEntry'
    __nonpersistvars__ = []

    def GetMenu(self):
        if session and session.role & ROLE_GML:
            menu = [('Grant Infinite', self._grant_infinite_license, ()),
             ('Grant Finite', self._grant_finite_license, ()),
             ('Revoke Infinite', self._revoke_infinite_license, ()),
             ('Revoke Finite', self._revoke_finite_license, ()),
             ('Copy Type ID Infinite', self._copy_type_id_for_license_type, (ComponentLicenseType.UNLIMITED,)),
             ('Copy Type ID Finite', self._copy_type_id_for_license_type, (ComponentLicenseType.LIMITED,))]
            return menu

    def _grant_infinite_license(self):
        get_ship_skin_component_svc().admin_grant_license(self.sr.node.component.component_id, ComponentLicenseType.UNLIMITED, self.sr.node.component.category)

    def _revoke_infinite_license(self):
        get_ship_skin_component_svc().admin_revoke_license(self.sr.node.component.component_id, ComponentLicenseType.UNLIMITED, self.sr.node.component.category)

    def _grant_finite_license(self):
        dialogue = QAGrantLicenseCountDialogue(component_id=self.sr.node.component.component_id, component_category=self.sr.node.component.category)
        dialogue.ShowModal()

    def _revoke_finite_license(self):
        get_ship_skin_component_svc().admin_revoke_license(self.sr.node.component.component_id, ComponentLicenseType.LIMITED, self.sr.node.component.category)

    def _copy_type_id_for_license_type(self, license_type):
        component_type_id = '?'
        for type_id, data in self.sr.node.component.component_item_data_by_type_id.iteritems():
            if data.license_type == license_type:
                component_type_id = type_id
                break

        blue.pyos.SetClipboardData(str(component_type_id))


class QAGrantLicenseCountDialogue(FormWindow):
    default_windowID = 'QAGrantLicenseCountDialogue'

    def ApplyAttributes(self, attributes):
        super(FormWindow, self).ApplyAttributes(attributes)
        self.window_name = 'Grant Finite Licenses'
        self._component_id = attributes.component_id
        self._component_category = attributes.component_category
        components = [formComponent.Integer(name='Licenses to grant', label='Licenses to grant', value=1)]
        self.form = Form(name=self.window_name, icon=eveicon.load, components=components, actions=[FormActionSubmit(label='OK', func=self.on_form_submit), FormActionCancel()])
        self.SetCaption(self.form.name)
        if self.form.icon:
            self.icon = self.form.icon
        self.formCont = ContainerAutoSize(name='formCont', parent=self.content, align=uiconst.TOTOP, callback=self.OnFormContHeightChanged)
        self.ConstructLayout()
        self.ConnectSignals()

    def on_form_submit(self, form):
        get_ship_skin_component_svc().admin_grant_license(self._component_id, ComponentLicenseType.LIMITED, self._component_category, form.get_component('Licenses to grant').get_value())
