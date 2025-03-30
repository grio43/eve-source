#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\Windows\DockablePanel.py
from carbonui import uiconst
from carbonui.control.button import Button
from eve.client.script.ui.control import eveLabel
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    description = 'Dockable panels are windows that open up in fullscreen by default, but can be configured to be floating or left/right aligned'

    def sample_code(self, parent):
        from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel

        class MyDockablePanel(DockablePanel):
            panelID = 'MyDockablePanel'
            default_caption = 'My Dockable Panel'

            def ApplyAttributes(self, attributes):
                super(MyDockablePanel, self).ApplyAttributes(attributes)
                eveLabel.EveCaptionLarge(parent=self.content, text="I'm open to anything!", align=uiconst.CENTER)

        def OpenPanel(*args):
            return MyDockablePanel.Open()

        Button(name='openButton', parent=parent, label='Open Dockable Panel', func=OpenPanel)
