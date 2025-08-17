import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

from Database.offlineDbManager import OfflineDbManager

from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.popup import Popup

class GroupsScreen(GridLayout):
    def __init__(self, switchToHome, switchToGroups, switchToTotals, switchToCreateGroup, switchToJoinGroup, switchToGroupPage, **kwargs):
        super(GroupsScreen, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20
        
        self.switchToGroupPage = switchToGroupPage
        self.main = self
        
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
        createGroupButton = Button(text="Create New Group", size_hint=(0.2, None))
        createGroupButton.bind(on_press=switchToCreateGroup)
        self.add_widget(createGroupButton)
        
        joinGroupButton = Button(text="Join Group", size_hint=(0.2, None))
        joinGroupButton.bind(on_press=switchToJoinGroup)
        self.add_widget(joinGroupButton)
        
########################################
        self.groupsGrid = GridLayout(cols=2)
        
        self.main.add_widget(self.groupsGrid)
        
    def showLeaveGroupPopup(self, groupName):
        layout = GridLayout(cols=1, spacing=10, padding=10)

        label = Label(
            text=f"Are you sure you want to leave group: {groupName}?",
            size_hint=(0.8, 0.3)
        )
        labelWidth, labelHeight = label.size
        label.text_size = (labelWidth*4, None)

        yes = Button(text="Leave Group", size_hint=(1, 0.3))
        no = Button(text="Cancel", size_hint=(1, 0.3))

        layout.add_widget(label)
        layout.add_widget(yes)
        layout.add_widget(no)

        popup = Popup(
            title=f"Leave {groupName}?",
            content=layout,
            size_hint=(0.7, 0.5)
        )

        yes.bind(on_press=self.leaveGroup)
        yes.bind(on_press=popup.dismiss)
        
        no.bind(on_press=popup.dismiss)
        
        popup.open()
        
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
        
    def refreshGrid(self):
        self.groupsGrid.clear_widgets()
        
        userGroupIds, userGroupNames = self.getGroupNames()
        
        for i in range(len(userGroupIds)):
            groupGrid = GridLayout(cols=1)
            
            groupButton = Button(text=userGroupNames[i], size_hint_y=0.4)
            groupButton.bind(on_press=lambda instance, groupId=userGroupIds[i]: self.switchToGroupPage(groupId))
            
            groupGrid.add_widget(groupButton)
            
            leaveGroupButton = Button(text="Leave Group", size_hint_y=0.1)
            leaveGroupButton.bind(on_press=lambda instance, groupId=userGroupIds[i]: self.askLeaveGroup(groupId))
            
            groupGrid.add_widget(leaveGroupButton)
            
            self.groupsGrid.add_widget(groupGrid)
        
    def getGroupNames(self):
        with OfflineDbManager() as dbManager:
            currentUserId = dbManager.getCurrentUser()
            userGroupIds = dbManager.getUserGroups(currentUserId)
            
            userGroupNames = []
            for groupId in userGroupIds:
                groupName = dbManager.getGroupName(groupId)
                userGroupNames.append(groupName)
            
            return userGroupIds, userGroupNames
    
    def askLeaveGroup(self, groupId):
        with OfflineDbManager() as dbManager:
            groupName = dbManager.getGroupName(groupId)
            
            self.groupToLeave = groupId
            
            self.showLeaveGroupPopup(groupName)
        
    def leaveGroup(self, instance=None):
        with OfflineDbManager() as dbManager:
            currentUserId = dbManager.getCurrentUser()
            
            groupName = dbManager.getGroupName(self.groupToLeave)
            
            leaveSuccess = dbManager.removeUserFromGroup(currentUserId, self.groupToLeave)
            
            if leaveSuccess:
                self.showPopup("Left Group", f"You have left {groupName}")
                self.refreshGrid()
            else:
                self.showPopup("Error", f"An error occured while trying to remove you from {groupName}. Please try again later.")