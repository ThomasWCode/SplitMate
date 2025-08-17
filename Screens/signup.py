import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

from Database.offlineDbManager import OfflineDbManager
from Database.offlineDbSyncer import OfflineDbSyncer

import re

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window

class SignupScreen(GridLayout):
    def __init__(self, switchToLogin, autoLogin, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20

        self.switchToLogin = switchToLogin
        self.autoLogin = autoLogin
        
        textInputHeight = Window.height * 0.1

        splitmateLogo = Image(source="Images\\splitmatePresplash.png",
                              size_hint=(1, None),
                              height=Window.height * 0.1)
        self.add_widget(splitmateLogo)
        
        self.add_widget(Label(size_hint_y=0.1))
        
########################################
        secondGrid = GridLayout(cols=2)
        
        secondGrid.add_widget(Label(text="Username:", size_hint_y=None, height=textInputHeight))
        self.username = TextInput(multiline=False, size_hint_y=None, height=textInputHeight)
        secondGrid.add_widget(self.username)

        thirdGrid = GridLayout(cols=1)
        thirdGrid.add_widget(Label(size_hint_y=0.1))
        secondGrid.add_widget(thirdGrid)

        self.add_widget(secondGrid)

########################################
        forthGrid = GridLayout(cols=2)

        forthGrid.add_widget(Label(text="Email:", size_hint_y=None, height=textInputHeight))
        self.email = TextInput(multiline=False, size_hint_y=None, height=textInputHeight)
        forthGrid.add_widget(self.email)

        fifthGrid = GridLayout(cols=1)
        fifthGrid.add_widget(Label(size_hint_y=0.1))
        forthGrid.add_widget(fifthGrid)

        self.add_widget(forthGrid)

########################################
        sixthGrid = GridLayout(cols=2)

        sixthGrid.add_widget(Label(text="Password:", size_hint_y=None, height=textInputHeight))
        self.password = TextInput(password=True, multiline=False, size_hint_y=None, height=textInputHeight)
        sixthGrid.add_widget(self.password)
        
        self.add_widget(sixthGrid)

########################################
        self.add_widget(Label())
        self.signupButton = Button(text="Sign Up", size_hint_y=0.5)
        self.signupButton.bind(on_press=self.signup)
        self.add_widget(self.signupButton)

        self.add_widget(Label())
        self.loginButton = Button(text="Go to Login", size_hint_y=0.4)
        self.loginButton.bind(on_press=self.switchToLogin)
        self.add_widget(self.loginButton)
        
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
        
    def signup(self, instance):
        offlineDbSyncer = OfflineDbSyncer()
        offlineDbSyncer.pullDownFromOnlineDb()
        
        with OfflineDbManager() as dbManager:
            alreadyUser, error = dbManager.checkAlreadyUser(self.email.text)
            if alreadyUser:
                self.showPopup("Email already in use", "That email is already in use. Please login instead.")
                self.switchToLogin()
            elif error:
                self.showPopup("Error", "There was an error while trying to sign you up. Please try again later.")
            else:
                emailValid = self.checkEmailValidity(self.email.text)
                if emailValid:
                    signupSuccess = dbManager.signupNewUser(self.username.text, self.email.text, self.password.text)
                    if signupSuccess:
                        self.showPopup("Signup Succesful", "You have been signup successfully.")
                        
                        self.switchToLogin()
                        self.autoLogin(self.email.text, self.password.text)
                        
                elif not emailValid:
                    self.showPopup("Invalid Email", "Given email is not valid.")
                else:
                    self.showPopup("Invalid Password", "Given password is not valid. Password must be 8 characters long and contain at least 1 special character and number.")
                    
    def checkEmailValidity(self, email):
        emailPattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
        validEmail = re.match(emailPattern, email)
        if validEmail:
            return True
        else:
            return False