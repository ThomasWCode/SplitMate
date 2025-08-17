import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

from Database.offlineDbManager import OfflineDbManager
from Database.offlineDbSyncer import OfflineDbSyncer
import Database.dbGlobal as dbGlobal

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.image import Image

class LoginScreen(GridLayout):
    def __init__(self, switchToSignup, switchToHome, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20
        
        self.switchToHome = switchToHome
        textInputHeight = Window.height * 0.1
        
        splitmateLogo = Image(source="Images\\splitmatePresplash.png",
                              size_hint=(1, None),
                              height=Window.height * 0.1)
        self.add_widget(splitmateLogo)
        
        self.add_widget(Label(size_hint_y=0.1))

########################################    
        secondGrid = GridLayout(cols=2)

        secondGrid.add_widget(Label(text="Email:", size_hint_y=None, height=textInputHeight))
        self.email = TextInput(multiline=False, size_hint_y=None, height=textInputHeight)
        secondGrid.add_widget(self.email)

        thirdGrid = GridLayout(cols=1)
        thirdGrid.add_widget(Label(size_hint_y=0.1))
        secondGrid.add_widget(thirdGrid)

        self.add_widget(secondGrid)

########################################
        forthGrid = GridLayout(cols=2)
        
        forthGrid.add_widget(Label(text="Password:", size_hint_y=None, height=textInputHeight))
        self.password = TextInput(password=True, multiline=False, size_hint_y=None, height=textInputHeight)
        forthGrid.add_widget(self.password)

        self.add_widget(forthGrid)
        
########################################
        self.add_widget(Label(size_hint_y=0.1))
        self.loginButton = Button(text="Login", size_hint_y=0.3)
        self.loginButton.bind(on_press=self.login)
        self.add_widget(self.loginButton)

        self.add_widget(Label(size_hint_y=0.3))
        self.signupButton = Button(text="Go to Signup", size_hint_y=0.2)
        self.signupButton.bind(on_press=switchToSignup)
        self.add_widget(self.signupButton)

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

    def login(self, instance):
        offlineDbSyncer = OfflineDbSyncer()
        offlineDbSyncer.pullDownFromOnlineDb()
        
        with OfflineDbManager() as dbManager:
            loginSuccess, error = dbManager.checkEmailAndPassword(self.email.text, self.password.text)

            if loginSuccess:
                setCurrentUserSuccess = dbManager.setCurrentUser(self.email.text)
                if setCurrentUserSuccess:
                    self.switchToHome()
                else:
                    self.showPopup("Error", "An error occurred while trying to sign you in. Please try again later.")
            elif error:
                self.showPopup("Error", "An error occurred while trying to sign you in. Please try again later.")
            else:
                self.showPopup("Username or password incorrect", "Your username or password is incorrect. Please try again.")
                
    def autoLogin(self, email, password):
        with OfflineDbManager() as dbManager:
            dbGlobal.currentUser = dbManager.getUserIdFromEmail(email)
            
        offlineDbSyncer = OfflineDbSyncer()
        offlineDbSyncer.syncDatabases()
        
        dbGlobal.currentUser = None
        
        with OfflineDbManager() as dbManager:
            loginSuccess, error = dbManager.checkEmailAndPassword(email, password)

            if loginSuccess:
                setCurrentUserSuccess = dbManager.setCurrentUser(email)
                if setCurrentUserSuccess:
                    self.switchToHome()
                else:
                    self.showPopup("Error", "An error occurred while trying to sign you in. Please try again later.")
            else:
                self.showPopup("Error", "An error occurred while trying to sign you in. Please try again later.")