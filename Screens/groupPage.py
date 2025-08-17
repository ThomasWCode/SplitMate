import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

import pyperclip

from Database.offlineDbManager import OfflineDbManager

from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

class GroupPageScreen(GridLayout):
    def __init__(self, switchToGroups, switchToAddExpense, switchToGroupTotals, **kwargs):
        super(GroupPageScreen, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20
        
        self.switchToGroups = switchToGroups
        self.switchToAddExpense = switchToAddExpense
        self.switchToGroupTotals = switchToGroupTotals
        self.textInputHeight = Window.height * 0.1
        
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
        self.groupGrid = GridLayout(cols=2)
        self.add_widget(self.groupGrid)
        
########################################
        bottomGrid = GridLayout(cols=1)
        self.add_widget(bottomGrid)
        
        bottomGrid.add_widget(Label(size_hint_y=None, height=self.textInputHeight))
        
        self.groupTotalsButton = Button(text="Group Totals")
        bottomGrid.add_widget(self.groupTotalsButton)
        
        bottomGrid.add_widget(Label(size_hint_y=None, height=self.textInputHeight/4))
        
        self.addExpenseButton = Button(text="Add Expense", size_hint_y=None, height=self.textInputHeight/2)
        bottomGrid.add_widget(self.addExpenseButton)
        
        logPaymentButton = Button(text="Log Payment", size_hint_y=None, height=self.textInputHeight/2)
        bottomGrid.add_widget(logPaymentButton)
        
    def refreshPageInfo(self):
        with OfflineDbManager() as dbManager:
            self.groupGrid.clear_widgets()
            
            membersGrid = GridLayout(cols=1)
            self.groupGrid.add_widget(membersGrid)
            
            infoGrid = GridLayout(cols=1)
            self.groupGrid.add_widget(infoGrid)
        
########################################
            groupMemberIds = dbManager.getGroupMembers(self.groupId)
            
            membersGrid.add_widget(Label(text=f"Group Members", size_hint_y=None, height=self.textInputHeight, underline=True))
            membersGrid.add_widget(Label(size_hint_y=None, height=self.textInputHeight/4))
            
            if groupMemberIds:
                
                groupMemberUsernames = []
                for userId in groupMemberIds:
                    username = dbManager.getUsername(userId)
                    
                    if username:
                        groupMemberUsernames.append(username)
                    else:
                        membersGrid.add_widget(Label(text="Could not load group memebers.", size_hint_y=None, height=self.textInputHeight))
            else:
                membersGrid.add_widget(Label(text="Could not load group memebers.", size_hint_y=None, height=self.textInputHeight))
            
            for username in groupMemberUsernames:
                membersGrid.add_widget(Label(text=username, size_hint_y=None, height=self.textInputHeight/2))
        
########################################       
            groupName = dbManager.getGroupName(self.groupId)
            joinCode = dbManager.getJoinCode(self.groupId)
            
            infoGrid.add_widget(Label(text=f"Group Info", size_hint_y=None, height=self.textInputHeight, underline=True))
            infoGrid.add_widget(Label(size_hint_y=None, height=self.textInputHeight/4))
            
            infoGrid.add_widget(Label(text=f"Group Name: {groupName}", size_hint_y=None, height=self.textInputHeight/2))
            
            infoGrid.add_widget(Label(size_hint_y=None, height=self.textInputHeight/4))
            
            if joinCode:
                infoGrid.add_widget(Label(text=f"Join Code: {joinCode}", size_hint_y=None, height=self.textInputHeight/2))
                
                infoGrid.add_widget(Label(size_hint_y=None, height=self.textInputHeight/4))
                copyJoinCodeButton = Button(text="Copy Join Code", size_hint_y=None, height=self.textInputHeight/1.5)
                infoGrid.add_widget(copyJoinCodeButton)
                copyJoinCodeButton.bind(on_press=lambda instance: pyperclip.copy(joinCode))
            else:
                infoGrid.add_widget(Label(text=f"Join Code: Failed to access join code.", size_hint_y=None, height=self.textInputHeight/2))
            
    def setGroupId(self, groupId):
        self.groupId = groupId
        
        self.addExpenseButton.bind(on_press=lambda instance: self.switchToAddExpense(self.groupId))
        self.groupTotalsButton.bind(on_press=lambda instance: self.switchToGroupTotals(self.groupId))
        
        self.refreshPageInfo()