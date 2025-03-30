#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\form_sounds.py
import json
from collections import defaultdict
import blue
import audio2
from carbonui import fontconst, uiconst, Align
from carbonui.control.combo import Combo
from carbonui.control.tabGroup import TabGroup
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from eve.client.script.ui.control.entries.generic import Generic
from carbonui.control.window import Window
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.common.lib import appConst as const
BTNSIZE = 16

def get_events_by_bank():
    eventsByBank = defaultdict(list)
    data = json.load(open('res/audio/SoundBanksInfo.json'))
    for bank in data['SoundBanksInfo']['SoundBanks']:
        for event in bank.get('IncludedEvents', []):
            eventsByBank[bank['ShortName']].append(event)

    return eventsByBank


def get_events_by_category():
    events_by_bank = get_events_by_bank()
    events_by_category = defaultdict(list)
    for events in events_by_bank.values():
        for event in events:
            category_name, _ = get_category_name_event_name(event)
            events_by_category[category_name].append(event)

    return events_by_category


def get_category_name_event_name(event):
    _, category_name, event_name = event['ObjectPath'].strip('\\').split('\\', 2)
    return (category_name, event_name)


class InsiderSoundPlayer(Window):
    __guid__ = 'form.InsiderSoundPlayer'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        w, h = (200, 300)
        self.SetMinSize([w, h])
        self.SetHeight(h)
        self.SetCaption('Sound Player')
        margin = const.defaultPadding
        self.sr.innermain = Container(name='inner', left=margin, top=margin, parent=self.sr.main, pos=(0, 0, 0, 0))
        self.sr.bottomframe = Container(name='bottom', align=uiconst.TOBOTTOM, parent=self.sr.innermain, height=BTNSIZE, left=margin, top=margin, clipChildren=1)
        self.sr.main = Container(name='main', align=uiconst.TOALL, parent=self.sr.innermain, pos=(margin,
         margin,
         margin,
         margin))
        self.node = None
        self.InitButtons()
        self.eventsByCategoryName = get_events_by_category()
        options = [ ('{} ({})'.format(name, len(events)), name) for name, events in self.eventsByCategoryName.iteritems() ]
        options = sorted(options)
        self.categoryCombo = Combo(parent=self.content, align=Align.TOTOP, callback=self.OnCategoryCombo, options=options)
        self.scroll = eveScroll.Scroll(parent=self.content)

    def OnCategoryCombo(self, *args):
        self.PopulateScroll(self.categoryCombo.GetValue())

    def InitButtons(self):
        buttons = [['Play', self.SoundPlay, 'ui_38_16_228'], ['Stop', self.StopAllSounds, 'ui_38_16_111']]
        for button in buttons:
            hint, function, iconID = button
            btn = Container(name=hint, align=uiconst.TOLEFT, width=BTNSIZE, left=const.defaultPadding, parent=self.sr.bottomframe)
            Frame(parent=btn, color=(1.0, 1.0, 1.0, 0.125))
            icon = eveIcon.Icon(icon=iconID, parent=btn, size=BTNSIZE, align=uiconst.CENTER)
            icon.OnClick = function
            icon.hint = hint
            icon.OnMouseEnter = (self.ShowSelected, icon, 1)
            icon.OnMouseExit = (self.ShowSelected, icon, 0)
            icon.sr.hilite = Fill(parent=btn, name='hilite', state=uiconst.UI_HIDDEN)

        textWidth = 353
        self.textBlock = Container(parent=self.sr.bottomframe, align=uiconst.TOLEFT, width=textWidth, left=const.defaultPadding)
        self.textTop = eveLabel.Label(text='', parent=self.textBlock, align=uiconst.TOALL, left=int(textWidth * 0.2) + const.defaultPadding, top=1, height=0, fontsize=fontconst.EVE_SMALL_FONTSIZE, letterspace=1, linespace=9, uppercase=1, state=uiconst.UI_NORMAL)
        self.textBtm = eveLabel.Label(text='', parent=self.textBlock, align=uiconst.TOALL, left=const.defaultPadding, height=0, top=1, fontsize=fontconst.EVE_SMALL_FONTSIZE, letterspace=1, linespace=9, uppercase=1, state=uiconst.UI_NORMAL)

    def ShowSelected(self, btn, toggle, *args):
        btn.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][toggle]

    def SoundPlay(self, *args):
        if self.node != None:
            sm.StartService('audio').SendUIEvent(self.node.filename)

    def StopAllSounds(self, *args):
        audio2.StopAll()

    def ParseTxtFile(self, file, soundUrlList):
        bf = blue.classes.CreateInstance('blue.ResFile')
        if not bf.Open(file):
            raise RuntimeError('Unable to open sound file %s' % file)
        myData = bf.Read()
        bf.Close()
        lines = myData.split('\r\n')
        if lines == None:
            return
        lines = lines[1:]
        for line in lines:
            if len(line) <= 0:
                break
            entries = line.split('\t')
            if len(entries) < 3:
                continue
            entry = entries[2].strip()
            if entry.startswith('music_') == False:
                soundUrlList.append((entry, file))

    def PopulateScroll(self, category_name):
        sounds = []
        for event in self.eventsByCategoryName[category_name]:
            _, eventNameLong = get_category_name_event_name(event)
            sounds.append(GetFromClass(GenericNoSound, {'label': eventNameLong,
             'hint': event.get('ID', 'No ID Assigned') + ': ' + event['ObjectPath'],
             'filename': event['Name'],
             'OnClick': self.ScrollClick,
             'OnDblClick': self.ScrollDblClick}))

        self.scroll.Load(contentList=sounds, headers=['Filename'], fixedEntryHeight=18)
        self.scroll.Confirm = self.OnScrollConfirm

    def OnScrollConfirm(self, *args):
        self.node = self.scroll.GetSelected()[0]
        self.SoundPlay()

    def ScrollClick(self, node, *args):
        self.node = node.sr.node

    def ScrollDblClick(self, node, *args):
        self.node = node.sr.node
        self.SoundPlay()


class GenericNoSound(Generic):
    sound_hover = None
    sound_select = None
