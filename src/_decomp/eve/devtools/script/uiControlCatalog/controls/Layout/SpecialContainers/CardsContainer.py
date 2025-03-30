#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\CardsContainer.py
import carbonui.const as uiconst
from carbonui.primitives.cardsContainer import CardsContainer
from carbonui.primitives.container import Container
from eve.devtools.script.uiControlCatalog.sample import Sample
from eve.devtools.script.uiControlCatalog.sampleUtil import GetCollapsableCont

class Sample1(Sample):
    name = 'Basic sample'
    description = CardsContainer.__doc__

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent, width=400, height=400)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.cardsContainer import CardsContainer
        myGridCont = CardsContainer(name='myGridCont', parent=parent, align=uiconst.TOTOP, cardHeight=60, cardMaxWidth=180, contentSpacing=(4, 4))
        for i in xrange(9):
            alpha = 0.2 + i * 0.1
            Container(parent=myGridCont, bgColor=(0.8,
             0.2,
             0.4,
             alpha), state=uiconst.UI_NORMAL)


class Sample2(Sample):
    name = 'allow_stretch attribute'
    description = 'The allow_stretch attribute can be passed into the container. What this will do is cause the container to try to fill any empty space by stretching the cards horizontally.'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent, width=400, height=400)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.cardsContainer import CardsContainer
        myGridCont = CardsContainer(name='myGridCont', parent=parent, align=uiconst.TOTOP, cardHeight=60, cardMaxWidth=180, contentSpacing=(4, 4), allow_stretch=True)
        for i in xrange(5):
            alpha = 0.2 + i * 0.1
            Container(parent=myGridCont, bgColor=(0.8,
             0.2,
             0.4,
             alpha), state=uiconst.UI_NORMAL)


class Sample3(Sample):
    name = 'Grouping'
    description = 'Cards in the container can be grouped together. \nYou do this by calling the CreateGroup method on the container. This returns a new container which you then use as the parent of the items you want grouped together. \nDoing this will make sure that the members of the group always appear together in a line'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent, width=400, height=420)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.cardsContainer import CardsContainer
        cardCont = CardsContainer(name='myGridCont', parent=parent, align=uiconst.TOTOP, cardHeight=60, cardMaxWidth=180, contentSpacing=(4, 4))
        group = cardCont.CreateGroup()
        for i in xrange(4):
            alpha = 0.2 + i * 0.1
            Container(parent=group, state=uiconst.UI_NORMAL, bgColor=(0.8,
             0.2,
             0.4,
             alpha), hint='This group has 4 members that will always be in the same line')

        for i in xrange(4):
            alpha = 0.2 + i * 0.1
            Container(parent=cardCont, bgColor=(0.2,
             0.8,
             0.4,
             alpha), state=uiconst.UI_NORMAL)

        group2 = cardCont.CreateGroup()
        for i in xrange(2):
            alpha = 0.2 + i * 0.1
            Container(parent=group2, bgColor=(0.8,
             0.2,
             0.4,
             alpha), state=uiconst.UI_NORMAL, hint='This group has two members and thus fits in a line with 3 columns')

        for i in xrange(4):
            alpha = 0.2 + i * 0.1
            Container(parent=cardCont, bgColor=(0.2,
             0.8,
             0.4,
             alpha), state=uiconst.UI_NORMAL)


class Sample4(Sample):
    name = 'fill_always attribute'
    description = 'Individual cards can also be set to fill a line. This will cause them to always take a whole line for themselves. Groups can also be configured this way this way'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent, width=400, height=800)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.cardsContainer import CardsContainer
        cardCont = CardsContainer(name='myGridCont', parent=parent, align=uiconst.TOTOP, cardHeight=60, cardMaxWidth=180, contentSpacing=(4, 4))
        group = cardCont.CreateGroup()
        for i in xrange(4):
            alpha = 0.2 + i * 0.1
            Container(parent=group, bgColor=(0.8,
             0.2,
             0.4,
             alpha), state=uiconst.UI_NORMAL)

        stretchGroup1 = cardCont.CreateGroup(fill_always=True)
        Container(parent=stretchGroup1, bgColor=(0.4, 0.2, 0.8, 0.6), state=uiconst.UI_NORMAL, hint='This item is set to fill')
        for i in xrange(4):
            alpha = 0.2 + i * 0.1
            Container(parent=cardCont, bgColor=(0.2,
             0.8,
             0.4,
             alpha), state=uiconst.UI_NORMAL)

        group2 = cardCont.CreateGroup(fill_always=True)
        for i in xrange(2):
            alpha = 0.2 + i * 0.1
            Container(parent=group2, bgColor=(0.8,
             0.2,
             0.4,
             alpha), state=uiconst.UI_NORMAL, hint='This group is set to fill')

        stretchGroup2 = cardCont.CreateGroup(fill_always=True)
        Container(parent=stretchGroup2, bgColor=(0.4, 0.2, 0.8, 0.6), state=uiconst.UI_NORMAL, hint='This item is set to fill')
