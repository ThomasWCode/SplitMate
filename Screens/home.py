import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.window import Window

class HomeScreen(GridLayout):
    def __init__(self, switchToHome, switchToGroups, switchToTotals, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20

        splitmateLogo = Image(source="Images\\splitmatePresplash.png",
                              size_hint=(1, None),
                              height=Window.height * 0.1)
        self.add_widget(splitmateLogo)
        
        self.add_widget(Label(size_hint_y=0.1))
        
########################################
        navGrid = GridLayout(cols=3, size_hint_y=None, height=Window.height * 0.1)
        
        homeButton = Button(text="Home", size_hint=(0.2, None))
        homeButton.bind(on_press=switchToHome)
        navGrid.add_widget(homeButton)
        
        groupsButton = Button(text="Groups", size_hint=(0.2, None))
        groupsButton.bind(on_press=switchToGroups)
        navGrid.add_widget(groupsButton)
        
        totalsButton = Button(text="Totals", size_hint=(0.2, None))
        totalsButton.bind(on_press=switchToTotals)
        navGrid.add_widget(totalsButton)
        
        self.add_widget(navGrid)
        
########################################
        activityLabel=Label(size_hint_y=1)
        self.add_widget(activityLabel)