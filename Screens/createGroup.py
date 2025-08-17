import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

from Database.offlineDbManager import OfflineDbManager

from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.popup import Popup

class CreateGroupScreen(GridLayout):
    def __init__(self, switchToGroups, **kwargs):
        super(CreateGroupScreen, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20
        
        self.switchToGroups = switchToGroups
        textInputHeight = Window.height * 0.1
        
        splitmateLogo = Image(source="Images\\splitmatePresplash.png",
                              size_hint=(1, None),
                              height=Window.height * 0.1)
        self.add_widget(splitmateLogo)
        
        self.add_widget(Label(size_hint_y=0.1))
        
########################################
        navGrid = GridLayout(cols=3, size_hint_y=None, height=Window.height * 0.1)
        
        backButton = Button(text="Back", size_hint=(0.2, None))
        backButton.bind(on_press=switchToGroups)
        navGrid.add_widget(backButton)
        
        self.add_widget(navGrid)
        
########################################
        groupInfoGrid = GridLayout(cols=2)
        
        groupInfoGrid.add_widget(Label(text="Group Name: ", size_hint_y=None, height=textInputHeight))
        self.groupName = TextInput(multiline=False, size_hint_y=None, height=textInputHeight)
        groupInfoGrid.add_widget(self.groupName)
    
        self.add_widget(groupInfoGrid)
    
########################################
        secondGrid = GridLayout(cols=1)
        createGroupButton = Button(text="Create Group", size_hint_y=0.4)
        createGroupButton.bind(on_press=self.createGroup)
        secondGrid.add_widget(createGroupButton)
        
        self.add_widget(secondGrid)
        
    def showPopup(self, title, message):
        layout = GridLayout(cols=1, spacing=10, padding=10)

        label = Label(
            text=message,
            size_hint=(0.8, 0.3)
        )
        labelWidth, labelHeight = label.size
        label.text_size = (labelWidth*4, None)

        closeButton = Button(text="Close", size_hint=(1, 0.3))

        layout.add_widget(label)
        layout.add_widget(closeButton)

        popup = Popup(
            title=title,
            content=layout,
            size_hint=(0.7, 0.5)
        )

        closeButton.bind(on_press=popup.dismiss)
        
        popup.open()
        
    def createGroup(self, instance=None):
        with OfflineDbManager() as dbManager:
            groupName = self.groupName.text
            
            creationSuccess, groupId, joinCode = dbManager.createGroup(groupName)
                
            currentUserId = dbManager.getCurrentUser()
            
            if creationSuccess:
                addUserSuccess = dbManager.addUserToGroup(currentUserId, groupId)
                
                if addUserSuccess:
                    self.showPopup("Success", "Group created successfully.")
                    self.switchToGroups()
                else:
                    self.showPopup("Error", "There was an error creating group. Please try again later.")
            else:
                self.showPopup("Error", "There was an error creating group. Please try again later.")