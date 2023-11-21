import time

import kivy
from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput

from kivy_garden.graph import Graph, MeshLinePlot

from kivy.storage.jsonstore import JsonStore

kivy.require('2.1.0')

UPath = JsonStore('UserPath.json')
if not UPath:
    UPath['0'] = {'path':'UserData.json'}
    UPath.store_sync()
print(UPath['0']['path'])
UD = JsonStore(UPath['0']['path'])

if not UD:
    UD['UP'] = {'t000': time.time(), 'Manager':'Graph', 'Wellbeing': {'Parameters':{}}}
    UD['USP'] = {'Wellbeing':{'Parameters':{}, 'Events':[]}}
UP = UD['UP']
USP = UD['USP']


def cycler(n, i, max):
    if i == 1:
        n += 1
        if n == max: n = 0
    if i == -1:
        n -= 1
        if n == -1: n = max-1
    return n

def SaveData():
    UD['UP'] = UP
    UD['USP'] = USP
    UD.store_sync()
# GUI --------------------------------------------------------------------------
class GUI(ScreenManager):
    def __init__(self):
        super().__init__()




        self.GMs = Screen(name='GMs')
        self.Glist = [self.GMs]
        self.Gs = 0
        self.add_widget(self.GMs)

        self.EMs = Screen(name='EMs')
        self.EEs = Screen(name='EEs')
        self.Elist = [self.EMs, self.EEs]
        self.Es = 0
        self.add_widget(self.EMs)
        self.add_widget(self.EEs)


        self.EM = EventMenu()
        self.EMs.add_widget(self.EM)
        self.EE = EventEditor()
        self.EEs.add_widget(self.EE)
        self.GM = GraphMenu()
        self.GMs.add_widget(self.GM)

        #for event in UE: print(event)

        self.bind(on_touch_down=self.TouchDown)
        self.bind(on_touch_up=self.TouchUp)


    def TouchDown(self, instance, touch):
        self.downpos=touch.pos
        self.direction=touch.pos
    def TouchUp(self, instance, touch):
        self.direction = (touch.pos[0] - self.direction[0], touch.pos[1] - self.direction[1])
        if 250 < abs(self.direction[0]) or 250 < abs(self.direction[1]):
            self.Drag()


    def Drag(self):
        self.GM.Drag(self.downpos, self.direction)
        self.EM.Drag(self.downpos, self.direction)
        self.EE.Drag(self.downpos, self.direction)
        # UP
        if self.direction[1] > 250 and self.current_screen in self.Glist:
            self.Gs = self.Glist.index(self.current_screen)
            self.switch_to(self.Elist[self.Es], direction='up')
        # DOWN
        if self.direction[1] < -250 and self.current_screen in self.Elist:
            self.Es = self.Elist.index(self.current_screen)
            self.switch_to(self.Glist[self.Gs], direction='down')

        # RIGHT
        if self.direction[0] > 150:
            self.SwitchPageRight()

        if self.direction[0] < -150:
            self.SwitchPageLeft()

    def SwitchPageRight(self):
        if self.downpos[0] < Window.size[0] * 0.1:
            if self.current_screen in self.Elist:
                self.Es = self.Elist.index(self.current_screen)
                self.switch_to(self.Elist[cycler(self.Es, -1, len(self.Elist))], direction='right')
            else:
                self.Gs = self.Glist.index(self.current_screen)
                self.switch_to(self.Glist[cycler(self.Gs, -1, len(self.Glist))], direction='right')

    def SwitchPageLeft(self):
        if self.downpos[0] > Window.size[0] * 0.9:
            if self.current_screen in self.Elist:
                self.Es = self.Elist.index(self.current_screen)
                self.switch_to(self.Elist[cycler(self.Es, 1, len(self.Elist))], direction='left')
            else:
                self.Gs = self.Glist.index(self.current_screen)
                self.switch_to(self.Glist[cycler(self.Gs, 1, len(self.Glist))], direction='left')

class GraphMenu(ScreenManager):
    def __init__(self):
        super(GraphMenu, self).__init__()

        self.LoadGM()

    def LoadGM(self):
        self.clear_widgets()
        self.Screens = []
        self.Graphs = []
        for section in list(USP):
            self.Screens += [Screen(name=section)]

            if UD['UP']['Manager'] == 'Graph':
                self.Graphs += [GraphManager(section)]
            if UD['UP']['Manager'] == 'Log':
                self.Graphs += [LogManager(section)]

            self.add_widget(self.Screens[-1])


            ScreenBox = BoxLayout(orientation='vertical')
            self.Screens[-1].add_widget(ScreenBox)
            OptionBox = BoxLayout(size_hint=(1,0.1))
            ScreenBox.add_widget(OptionBox)

            OptionBox.add_widget(BoxLayout(size_hint=(0.7, 1)))
            OptionBox.add_widget(LogButton())
            OptionBox.add_widget(GraphButton())
            OptionBox.add_widget(FileSelector(self))

            ScreenBox.add_widget(Label(text=section, size_hint=(1, 0.1)))
            ScreenBox.add_widget(self.Graphs[-1])

            #ParScroll = ScrollView(size_hint=(1, 0.8))
            #ScreenBox.add_widget(ParScroll)

            #ParBox = GridLayout(cols=1, size_hint=(1, None))
            #ParBox.bind(minimum_height=ParBox.setter('height'))
            #ParScroll.add_widget(ParBox)

            #ParBox.add_widget(Evaluator(section))



    def Drag(self, downpos, direction):
        GMscreen = self.Screens.index(self.current_screen)
        # RIGHT
        if direction[0] > 150:
            if downpos[0] > Window.size[0] * 0.1:
                self.switch_to(
                    self.Screens[cycler(GMscreen, -1, len(self.Screens))],
                    direction='right')
        # LEFT
        if direction[0] < -150:
            if downpos[0] < Window.size[0] * 0.9:
                self.switch_to(
                    self.Screens[cycler(GMscreen, 1, len(self.Screens))],
                    direction='left')


class EventEditor(ScreenManager):
    def __init__(self):
        super(EventEditor, self).__init__()

        self.EEscreen = 0
        self.LoadEE()

    def LoadEE(self):
        self.clear_widgets()
        self.Screens = []
        for section in list(USP):
            self.LoadSection(section)

    def LoadSection(self, section):
        global G
        self.Screens += [Screen(name=section[0])]
        self.add_widget(self.Screens[-1])

        ScreenBox = BoxLayout(orientation='vertical')
        self.Screens[-1].add_widget(ScreenBox)

        New = NewSectPar(section, (1, 0.6))
        ScreenBox.add_widget(New)

        ParScroll = ScrollView(size_hint=(1, 0.4))
        ScreenBox.add_widget(ParScroll)

        ParBox = GridLayout(cols=1, size_hint=(1, None))
        ParBox.bind(minimum_height=ParBox.setter('height'))
        ParScroll.add_widget(ParBox)

        for parameter in list(USP[section]['Parameters']):
            self.LoadPar(ParBox, section, parameter)


    def LoadPar(self, ParBox, section, parameter):
        Par = TrashBox(section, parameter)
        ParBox.add_widget(Par)

    def Drag(self, downpos, direction):
        EEscreen = self.Screens.index(self.current_screen)
        # RIGHT
        if direction[0] > 150:
            if downpos[0] > Window.size[0]*0.1:
                self.switch_to(self.Screens[cycler(EEscreen, -1, len(self.Screens))], direction='right')
        # LEFT
        if direction[0] < -150:
            if downpos[0] < Window.size[0]*0.9:
                self.switch_to(self.Screens[cycler(EEscreen, 1, len(self.Screens))], direction='left')


class EventMenu(ScreenManager):
    def __init__(self):
        super(EventMenu, self).__init__()

        self.LoadEM()

    def LoadEM(self):
        self.clear_widgets()
        self.Screens = []
        for section in list(USP):
            self.Screens += [Screen(name=section)]
            self.add_widget(self.Screens[-1])

            ScreenBox = BoxLayout(orientation='vertical')
            self.Screens[-1].add_widget(ScreenBox)
            ScreenBox.add_widget(Label(text=section, size_hint=(1,0.1)))

            ParScroll = ScrollView(size_hint=(1, 0.8))
            ScreenBox.add_widget(ParScroll)

            ParBox = GridLayout(cols=1, size_hint=(1, None))
            ParBox.bind(minimum_height=ParBox.setter('height'))
            ParScroll.add_widget(ParBox)

            ParameterList = []

            for par in list(USP[section]['Parameters']):

                if USP[section]['Parameters'][par]['type'] == 'OFive':
                    ParameterList += [OFive(section, par)]
                    ParBox.add_widget(ParameterList[-1])
                if USP[section]['Parameters'][par]['type'] == 'text':
                    ParameterList += [TextPar(section, par)]
                    ParBox.add_widget(ParameterList[-1])
                if USP[section]['Parameters'][par]['type'] == 'number':
                    ParameterList += [NumberPar(section, par)]
                    ParBox.add_widget(ParameterList[-1])

            ConcludeButton = EventConclude(section, ParameterList)
            ScreenBox.add_widget(ConcludeButton)


    def Drag(self, downpos, direction):
        EMscreen = self.Screens.index(self.current_screen)
        # RIGHT
        if direction[0] > 150:
            if downpos[0] > Window.size[0]*0.1:
                self.switch_to(self.Screens[cycler(EMscreen, -1, len(self.Screens))], direction='right')

        # LEFT
        if direction[0] < -150:
            if downpos[0] < Window.size[0]*0.9:
                self.switch_to(self.Screens[cycler(EMscreen, 1, len(self.Screens))], direction='left')


class EventConclude(BoxLayout):
    def __init__(self, Section, ParameterList):
        super(EventConclude, self).__init__(size_hint=(1,0.1))

        Conclude = Button(text='Conclude')
        Conclude.bind(on_press=self.ConcludeF)
        Trash = Button(text='Trash')
        Trash.bind(on_press=self.TrashF)
        self.add_widget(Conclude)
        self.add_widget(Trash)

        self.sect = Section
        self.ParList = ParameterList

    def ConcludeF(self, instance):
        event = ['-']*(len(list(USP[self.sect]['Parameters']))+1)
        event[0] = Time()
        for ParWidget in self.ParList:
            index = USP[self.sect]['Parameters'][ParWidget.par]['i']

            if USP[self.sect]['Parameters'][ParWidget.par]['type'] == 'OFive' and ParWidget.n != 0:
                    event[index] = ParWidget.n
            if USP[self.sect]['Parameters'][ParWidget.par]['type'] == 'text' and ParWidget.text_input.text != '':
                    event[index] = ParWidget.text_input.text
            if USP[self.sect]['Parameters'][ParWidget.par]['type'] == 'number' and ParWidget.number_input.text != '':
                    event[index] = float(ParWidget.number_input.text)

        USP[self.sect]['Events'] += [event]
        SaveData()
        G.GM.LoadGM()

    def TrashF(self, instance):
        for ParWidget in self.ParList:
            if USP[self.sect]['Parameters'][ParWidget.par]['type'] == 'OFive':
                ParWidget.n = 0
                ParWidget.LabelValue.text = str(ParWidget.n)
            if USP[self.sect]['Parameters'][ParWidget.par]['type'] == 'text':
                ParWidget.text_input.text = ''
            if USP[self.sect]['Parameters'][ParWidget.par]['type'] == 'number':
                ParWidget.number_input.text = ''

class NewSectPar(BoxLayout):
    def __init__(self,section, size):
        super(NewSectPar, self).__init__(orientation='vertical',size_hint=size, padding=(0,20))

        self.sect = section

        self.add_widget(Label(text=section, size_hint=(1, 0.1)))

        SectionDelete = Button(text="Delete Section", size_hint=(1, 0.15))
        SectionDelete.bind(on_press=self.DeleteSectionF)
        self.add_widget(SectionDelete)

        NewSectBox = BoxLayout(size_hint=(1, 0.2))
        NewParBox = BoxLayout(size_hint=(1, 0.2))
        ParType = GridLayout(cols=2, size_hint=(1, 0.35))
        self.add_widget(NewSectBox)
        self.add_widget(NewParBox)
        self.add_widget(ParType)

        NewSect = Button(text='New Section')
        NewSect.bind(on_press=self.NewSectF)
        self.SectName = TextInput()
        NewSectBox.add_widget(NewSect)
        NewSectBox.add_widget(self.SectName)

        NewPar = Button(text='New Parameter')
        NewPar.bind(on_press=self.NewParF)
        self.ParName = TextInput()
        NewParBox.add_widget(NewPar)
        NewParBox.add_widget(self.ParName)


        OFiveL = Label(text='0 to 5 selector')
        self.OFive = CheckBox(group='datatype')
        NumberL = Label(text='Number')
        self.Number = CheckBox(group='datatype')
        TextL = Label(text='Text')
        self.Text = CheckBox(group='datatype')

        ParType.add_widget(OFiveL)
        ParType.add_widget(self.OFive)
        ParType.add_widget(NumberL)
        ParType.add_widget(self.Number)
        ParType.add_widget(TextL)
        ParType.add_widget(self.Text)

    def DeleteSectionF(self, instance):
        global G
        if len(USP) > 1:
            section = G.EE.current
            Screen = G.EE.current_screen
            i = G.EE.Screens.index(Screen)
            if i == 0:
                G.EE.switch_to(G.EE.Screens[1], direction='left')
            else:
                G.EE.switch_to(G.EE.Screens[i - 1], direction='right')
            G.EE.Screens.remove(Screen)
            USP.delete(section)
            SaveData()

    def NewSectF(self, instance):
        if self.SectName.text not in list(USP) and self.SectName.text:
            UP[self.SectName.text] = {'Parameters':{}}
            USP[self.SectName.text] = {'Parameters':{}, 'Events':[]}

            SaveData()
            G.GM.LoadGM()

            G.EE.LoadSection(list(USP)[-1])
            G.EE.switch_to(G.EE.Screens[-1], direction='left')

            self.SectName.text = ''

    def ParIndex(self):
        index = 1
        if len(list(USP[self.sect]['Parameters']))>0:
            indexes = [USP[self.sect]['Parameters'][parameter]['i'] for parameter in list(USP[self.sect]['Parameters'])]
            while True:
                if index in indexes:
                    index += 1
                else: break
        return index



    def NewParF(self, instance):

        if self.ParName.text not in list(USP[self.sect]['Parameters']) and self.ParName.text:
            type = ""
            if self.OFive.active: type = 'OFive'
            if self.Number.active: type = 'number'
            if self.Text.active: type = 'text'
            if type:
                UP[self.sect]['Parameters'][self.ParName.text] = False

                USP[self.sect]['Parameters'][self.ParName.text] = {'type': type, 'i':self.ParIndex()}
                SaveData()

                n = G.EE.Screens.index(G.EE.current_screen)
                G.EE.LoadPar(G.EE.Screens[n].children[0].children[0].children[0], self.sect, self.ParName.text)

                G.EM.LoadEM()
                G.GM.LoadGM()

                self.ParName.text = ''

    def on_touch_down(self, touch):
        time.sleep(0)
    def on_touch_up(self, touch):
        super(NewSectPar, self).on_touch_down(touch)
        super(NewSectPar, self).on_touch_up(touch)


class Evaluator(BoxLayout):
    def __init__(self, section):
        super(Evaluator, self).__init__(size_hint=(1, None))

        self.sect = section[0]

        #self.add_widget(Label(text=self.par))
        #for event in UE.find():
            #print(event)


class TrashBox(BoxLayout):
    def __init__(self, section, par):
        super(TrashBox, self).__init__(size_hint=(1, None))

        self.sect = section
        self.par = par

        self.add_widget(Label(text=par))

        TrashButton = Button(text='Delete')
        TrashButton.bind(on_press=self.TrashF)
        self.add_widget(TrashButton)

    def TrashF(self, instance):
        self.parent.remove_widget(self)
        index = USP[self.sect]['Parameters'][self.par]['i']
        USP[self.sect]['Parameters'].pop(self.par)
        parameters = list(USP[self.sect]['Parameters'])
        print(USP[self.sect]['Events'])
        RemoveIndex = lambda l,i: l[:i]+l[i+1:]
        USP[self.sect]['Events'] = [RemoveIndex(event,index) for event in USP[self.sect]['Events'] if len(RemoveIndex(event,index))>1]

        print(USP[self.sect]['Events'])
        for parameter in parameters:
            if index < USP[self.sect]['Parameters'][parameter]['i']:
                USP[self.sect]['Parameters'][parameter]['i'] -= 1

        SaveData()
        G.EM.LoadEM()
        G.GM.LoadGM()




class OFive(BoxLayout):
    def __init__(self, section, par):
        super(OFive, self).__init__(size_hint=(1, None))

        self.sect = section
        self.par = par

        self.n = 0

        self.add_widget(Label(text=par))
        plusb = Button(text='+')
        minusb = Button(text='-')

        plusb.bind(on_press=self.Plus)
        minusb.bind(on_press=self.Minus)

        self.add_widget(plusb)
        self.add_widget(minusb)

        self.LabelValue = Label(text='0')
        self.add_widget(self.LabelValue)
    def Plus(self, instance):
        if self.n < 5:
            self.n += 1
            self.LabelValue.text = str(self.n)
        else:
            self.n = 0
            self.LabelValue.text = str(self.n)

    def Minus(self, instance):
        if self.n > 0:
            self.n -= 1
            self.LabelValue.text = str(self.n)
        else:
            self.n = 5
            self.LabelValue.text = str(self.n)

class TextPar(BoxLayout):
    def __init__(self, section, par):
        super(TextPar, self).__init__(size_hint=(1, None))

        self.sect = section
        self.par = par

        self.add_widget(Label(text=par))

        self.text_input = TextInput(text='', font_size=16, multiline=True)
        self.add_widget(self.text_input)

class NumberPar(BoxLayout):
    def __init__(self, section, par):
        super(NumberPar, self).__init__(size_hint=(1, None))

        self.sect = section
        self.par = par

        self.add_widget(Label(text=par))
        self.number_input = TextInput(text='', font_size=16, multiline=False)
        self.add_widget(self.number_input)

class LogButton(Button):
    def __init__(self):
        super(LogButton, self).__init__(text='Log')
        self.bind(on_press=self.press)
    def press(self, touch):
        UP['Manager'] = 'Log'
        SaveData()
        G.GM.LoadGM()

class LogManager(ScrollView):
    def __init__(self, section):
        super(LogManager, self).__init__()
        self.section = section

        EventBox = GridLayout(cols=1, size_hint=(1, None))
        self.add_widget(EventBox)

        if len(USP[self.section]['Parameters']) != 0:
            for event in USP[self.section]['Events']:
                EventBox.add_widget(LogBlock(self.section,event))

class LogBlock(BoxLayout):
    def __init__(self,section, event):
        super(LogBlock, self).__init__(orientation='vertical')
        self.section = section

        ParBox = BoxLayout()
        ParBox.add_widget(Label(text='time'))
        ParBox.add_widget(Label(text=str(event[0])))
        self.add_widget(ParBox)

        for par in list(USP[self.section]['Parameters']):
            try:
                val = str(event[USP[self.section]['Parameters'][par]['i']])
                ParBox = BoxLayout()
                ParBox.add_widget(Label(text=par))
                ParBox.add_widget(Label(text=val))
                self.add_widget(ParBox)
            except: print()


class GraphButton(Button):
    def __init__(self):
        super(GraphButton, self).__init__(text='Graph')
        self.bind(on_press=self.press)

    def press(self, touch):
        UP['Manager'] = 'Graph'
        SaveData()
        G.GM.LoadGM()

class GraphManager(BoxLayout):
    def __init__(self, section):
        super(GraphManager, self).__init__(orientation='vertical')

        self.section = section

        Hours = 24
        if len(UP) != 0:
            Hours = Time()

        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph = Graph(xlabel='X', ylabel='Y', x_ticks_minor=1, x_ticks_major=6,
                      y_ticks_minor=1,
                      y_ticks_major=5, y_grid_label=True, x_grid_label=True,
                      padding=5,
                      x_grid=True, y_grid=True, xmin=(Hours-24)//1, xmax=(Hours+24)//1, ymin=0,
                      ymax=6)
        self.add_widget(self.graph)

        self.ParScroll = ScrollView(size_hint=(1, 0.8))
        self.add_widget(self.ParScroll)

        self.update_pars()
        self.update()

    def update_pars(self):
        self.ParScroll.clear_widgets()

        ParBox = GridLayout(cols=1, size_hint=(1, None))
        ParBox.bind(minimum_height=ParBox.setter('height'))
        self.ParScroll.add_widget(ParBox)
        self.DataSelectors = []

        for par in list(USP[self.section]['Parameters']):
            if USP[self.section]['Parameters'][par]['type'] == ('OFive' or 'number'):
                self.DataSelectors += [DataSelector(self, par)]
                ParBox.add_widget(self.DataSelectors[-1])

    def update(self):
        print(f"Update {self.section}")
        for plot in self.graph.plots[:]:  # Use [:] to create a copy of the list for iteration
            self.graph.remove_plot(plot)
        plot_par_index = []
        for par in list(USP[self.section]['Parameters']):
            if UP[self.section]['Parameters'][par] == True:
                plot_par_index += [USP[self.section]['Parameters'][par]['i']]
        points = []
        print(plot_par_index)
        for event in USP[self.section]['Events']:
            for plotpar in plot_par_index:
                if event[plotpar] != '-':
                    points += [(event[0],event[plotpar])]
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        if len(points) != 0:
            plot.points = points
        print(points)
        self.graph.add_plot(plot)

    def on_touch_down(self, touch):
        if self.graph.collide_point(*touch.pos):
            touch.grab(self)
        return super(GraphManager, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            scale_factor = 0.1  # Adjust this value based on your preference
            self.graph.xmin -= touch.dx * scale_factor
            self.graph.xmax -= touch.dx * scale_factor
            #self.update_label()
        return super(GraphManager, self).on_touch_move(touch)

class DataSelector(BoxLayout):
    def __init__(self, GMinst, par):
        super(DataSelector, self).__init__(size_hint=(1, None))
        self.GMinst = GMinst
        self.sect = GMinst.section
        self.par = par
        self.add_widget(Label(text=self.par))
        self.check = CheckBox(active=UP[self.sect]['Parameters'][self.par])
        self.check.bind(on_press=self.SelectorUpdate)
        self.add_widget(self.check)

    def SelectorUpdate(self, instance):
        UP[self.sect]['Parameters'][self.par] = self.check.active
        SaveData()
        self.GMinst.update()

class FileSelector(Button):
    def __init__(self, screen_manager, **kwargs):
        super(FileSelector, self).__init__(text='Data',size_hint=(0.1,1))
        self.screen_manager = screen_manager
        self.bind(on_press=self.open_file_selection)


    def open_file_selection(self, instance):
        file_selector_screen = FileSelectorScreen(self.screen_manager.current,name='file_selector_screen')
        file_selector_screen.file_selector.bind(on_submit=self.selected)
        self.screen_manager.add_widget(file_selector_screen)
        self.screen_manager.transition.direction = 'down'
        self.screen_manager.current = 'file_selector_screen'

    def selected(self, chooser, selected, touch):
        if selected:
            if selected[0].endswith('.json'):
                print('ends in .json')
                SelectUD = JsonStore(selected[0])
                print(list(SelectUD))
                if list(SelectUD) == ['UP','USP']:
                    print('New Path')
                    UPath['0'] = {'path':selected[0]}
                    UPath.store_sync()
                    print(UPath['0']['path'])
                    E.stop()
            else:
                print('Does not end in .json')

            print(f"Selected file: {selected[0]}")
            #self.screen_manager.remove_widget(chooser.parent)  # Remove file selector screen

class FileSelectorScreen(Screen):
    def __init__(self, previous_screen, **kwargs):
        super(FileSelectorScreen, self).__init__(**kwargs)
        self.file_selector = FileChooserListView()
        self.previous_screen = previous_screen
        self.add_widget(self.file_selector)

        # Button to go back to the previous screen
        back_button = Button(text='Go Back',size_hint=(0.1,0.1))
        back_button.bind(on_press=self.go_back)
        self.add_widget(back_button)

    def go_back(self, instance):
         # Set the transition direction
        self.manager.transition.direction = 'up'
        self.manager.current = self.previous_screen  # Switch to the previous screen


def Time():
    return float((time.time() - UP['t000'])/3600)




# GUI --------------------------------------------------------------------------



def ShowUSP():
    for section in list(USP):
        print(f"---{section}---")
        if 0:
            print(list(USP[section]['Parameters']))
        else:
            for par in list(USP[section]['Parameters']):
                print(f"{par} - {USP[section][par]['type']} - {USP[section][par]['Events']}")

def Sections():
    sections = list(USP)
    print(sections)

def Parameters(section):
    for par in list(USP[section]):
        print(par)

def Events(section, parameter):
    print(USP[section][parameter]['Events'])

def Clear():
    UD.clear()

class Emotion(App):
    def build(self):
        global G
        global E
        return G


#print(UD['Wellbeing']['xaxa'])
#ShowUSP()
#print(USP['Wellbeing']['Events'])
if 1:
    G = GUI()
    E = Emotion()
    E.run()
else:
    Clear()


while False:
    inp = input('-')
    print(inp[11:-1])
    if inp == "Sections":
        Sections()
    if inp[:11] == "Parameters(" and inp[-1] == ")":
        Parameters(inp[11:-1])
    if inp[:7] == "Events(" and inp[-1] == ")":
        section, parameter = inp[7:-1].split(', ')
        print(USP[section][parameter]['Events'])



