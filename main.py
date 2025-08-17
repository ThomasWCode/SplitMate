import sys
import os
currentDir = os.getcwd()
sys.path.append(currentDir)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from Screens.login import LoginScreen
from Screens.signup import SignupScreen
from Screens.home import HomeScreen
from Screens.groups import GroupsScreen
from Screens.createGroup import CreateGroupScreen
from Screens.groupPage import GroupPageScreen
from Screens.joinGroup import JoinGroupScreen
from Screens.addExpense import AddExpenseScreen
from Screens.groupTotals import GroupTotalsScreen

class LoginScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(LoginScreenWindow, self).__init__(**kwargs)
        self.loginScreen = LoginScreen(
            switchToSignup=self.switchToSignup,
            switchToHome=self.switchToHome
        )
        self.add_widget(self.loginScreen)

    def switchToSignup(self, instance):
        self.manager.current = "signup"

    def switchToHome(self, instance=None):
        self.manager.current = "home"
        
    def autoLogin(self, email, password):
        self.loginScreen.autoLogin(email, password)

class SignupScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(SignupScreenWindow, self).__init__(**kwargs)
        self.add_widget(SignupScreen(
            switchToLogin=self.switchToLogin,
            autoLogin = self.autoLogin
        ))

    def switchToLogin(self, instance=None):
        self.manager.current = "login"
        
    def autoLogin(self, email, password):
        self.manager.get_screen("login").autoLogin(email, password)

class HomeScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(HomeScreenWindow, self).__init__(**kwargs)
        self.add_widget(HomeScreen(switchToHome=self.switchToHome, switchToGroups=self.switchToGroups, switchToTotals=self.switchToTotals))
        
    def switchToHome(self, instance=None):
        self.manager.current = "home"
        
    def switchToGroups(self, instance=None):
        if not self.manager.has_screen("groups"):
            self.manager.add_widget(GroupsScreenWindow(name="groups"))
            
        self.manager.current = "groups"
        self.manager.get_screen("groups").refreshGrid()
        
    def switchToTotals(self, instance=None):
        self.manager.current = "totals"
        
class GroupsScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(GroupsScreenWindow, self).__init__(**kwargs)
        
        self.groupsScreen = GroupsScreen(
            switchToHome=self.switchToHome,
            switchToGroups=self.switchToGroups,
            switchToTotals=self.switchToTotals,
            switchToCreateGroup=self.switchToCreateGroup,
            switchToGroupPage=self.switchToGroupPage,
            switchToJoinGroup=self.switchToJoinGroup
        )
        self.add_widget(self.groupsScreen)
        
    def refreshGrid(self, instance=None):
        self.groupsScreen.refreshGrid()
        
    def switchToHome(self, instance=None):
        self.manager.current = "home"
        
    def switchToGroups(self, instance=None):
        self.manager.current = "groups"
        self.manager.get_screen("groups").refreshGrid()
        
    def switchToTotals(self, instance=None):
        self.manager.current = "totals"
    
    def switchToCreateGroup(self, instance=None):
        self.manager.current = "createGroup"
        
    def switchToJoinGroup(self, instance=None):
        self.manager.current = "joinGroup"
    
    def switchToGroupPage(self, groupId, instance=None):
        self.manager.get_screen("groupPage").loadGroupPage(groupId)
        
class CreateGroupScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(CreateGroupScreenWindow, self).__init__(**kwargs)
        self.add_widget(CreateGroupScreen(switchToGroups=self.switchToGroups))
        
    def switchToGroups(self, instance=None):
        self.manager.current = "groups"
        self.manager.get_screen("groups").refreshGrid()
        
class GroupPageScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(GroupPageScreenWindow, self).__init__(**kwargs)
        self.groupPageScreen = GroupPageScreen(switchToGroups=self.switchToGroups, switchToAddExpense=self.switchToAddExpense, switchToGroupTotals=self.switchToGroupTotals)
        self.add_widget(self.groupPageScreen)
        
    def switchToGroups(self, instance=None):
        self.manager.current = "groups"
        self.manager.get_screen("groups").refreshGrid()
        
    def switchToAddExpense(self, groupId):
        self.manager.current = "addExpense"
        self.manager.get_screen("addExpense").setCurrentGroupId(groupId)
        
    def loadGroupPage(self, groupId):
        self.groupPageScreen.setGroupId(groupId)
        self.manager.current = "groupPage"
        
    def switchToGroupTotals(self, groupId):
        self.manager.current = "groupTotals"
        self.manager.get_screen("groupTotals").setCurrentGroupId(groupId)
    
class JoinGroupScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(JoinGroupScreenWindow, self).__init__(**kwargs)
        self.add_widget(JoinGroupScreen(switchToGroups=self.switchToGroups))
        
    def switchToGroups(self, instance=None):
        self.manager.current = "groups"
        self.manager.get_screen("groups").refreshGrid()
        
class AddExpenseScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(AddExpenseScreenWindow, self).__init__(**kwargs)
        
        self.addExpenseScreen = AddExpenseScreen(
            switchToGroupPage=self.switchToGroupPage
        )
        self.add_widget(self.addExpenseScreen)
        
    def setCurrentGroupId(self, groupId):
        self.addExpenseScreen.setCurrentGroupId(groupId)
        
    def switchToGroupPage(self, groupId):
        self.manager.get_screen("groupPage").loadGroupPage(groupId)
        
class GroupTotalsScreenWindow(Screen):
    def __init__(self, **kwargs):
        super(GroupTotalsScreenWindow, self).__init__(**kwargs)
        
        self.groupTotalsScreen = GroupTotalsScreen(
            switchToGroupPage=self.switchToGroupPage,
            switchToAddExpense=self.switchToAddExpense
        )
        self.add_widget(self.groupTotalsScreen)
        
    def setCurrentGroupId(self, groupId):
        self.groupTotalsScreen.setCurrentGroupId(groupId)
        
    def switchToGroupPage(self, groupId):
        self.manager.get_screen("groupPage").loadGroupPage(groupId)
    
    def switchToAddExpense(self, groupId):
        self.manager.current = "addExpense"
        self.manager.get_screen("addExpense").setCurrentGroupId(groupId)

class MyApp(App):
    def build(self):
        screenManager = ScreenManager()
        
        screenManager.add_widget(LoginScreenWindow(name="login"))
        screenManager.add_widget(SignupScreenWindow(name="signup"))
        screenManager.add_widget(HomeScreenWindow(name="home"))
        screenManager.add_widget(CreateGroupScreenWindow(name="createGroup"))
        screenManager.add_widget(GroupPageScreenWindow(name="groupPage"))
        screenManager.add_widget(JoinGroupScreenWindow(name="joinGroup"))
        screenManager.add_widget(AddExpenseScreenWindow(name="addExpense"))
        screenManager.add_widget(GroupTotalsScreenWindow(name="groupTotals"))

        screenManager.current = "login"
        return screenManager

if __name__ == '__main__':
    MyApp().run()