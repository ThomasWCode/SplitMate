import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

from Database.offlineDbManager import OfflineDbManager

import re

from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup

LabelBase.register(name='ArrowFont', fn_regular='Fonts/ZeroCool-MVD9B.ttf')

class AddExpenseScreen(GridLayout):
    def __init__(self, switchToGroupPage, **kwargs):
        super(AddExpenseScreen, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20
        
        self.switchToGroupPage = switchToGroupPage
        self.textInputHeight = Window.height * 0.1
        
        splitmateLogo = Image(source="Images\\splitmatePresplash.png",
                              size_hint=(1, None),
                              height=Window.height * 0.1)
        self.add_widget(splitmateLogo)
        
        self.add_widget(Label(size_hint_y=0.1))
        
########################################
        navGrid = GridLayout(cols=3, size_hint_y=None, height=Window.height * 0.1)
        
        self.backButton = Button(text="Back", size_hint=(0.2, None))
        
        navGrid.add_widget(self.backButton)
        
        self.add_widget(navGrid)
        
########################################
        self.addExpenseGrid = GridLayout(cols=1)
        
        self.add_widget(self.addExpenseGrid)
        
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
        with OfflineDbManager() as dbManager:
            self.addExpenseGrid.clear_widgets()

            self.groupMemberIds = dbManager.getGroupMembers(self.currentGroupId)
            self.groupMemberNames = [dbManager.getUsername(memberId) for memberId in self.groupMemberIds]
            
            self.paidByDropdown = DropDown()
            self.paidByDropdownSelected = None
            
            for memberName in self.groupMemberNames:
                dropdownButton = Button(text=memberName, size_hint_y=None, height=self.textInputHeight)
                dropdownButton.bind(on_press=lambda instance, name=memberName: self.paidByDropdown.select(name))
                self.paidByDropdown.add_widget(dropdownButton)
            
            openDropdownGrid = GridLayout(cols=2)
            
            openDropdownGrid.add_widget(Label(text="Paid by: ", size_hint_y=None, height=self.textInputHeight))
            openDropdownButton = Button(text="\u25BC", font_name="ArrowFont", size_hint_y=None, height=self.textInputHeight)
            openDropdownButton.bind(on_press=lambda instance: self.paidByDropdown.open(instance))
            self.paidByDropdown.bind(on_select=lambda instance, x: [
                setattr(openDropdownButton, 'text', x),
                setattr(openDropdownButton, 'font_name', 'data/fonts/Roboto-Regular.ttf'),
                setattr(openDropdownButton, 'font_size', '14sp')
            ])
            self.paidByDropdown.bind(on_select=self.dropdownValueSelected)
            openDropdownGrid.add_widget(openDropdownButton)
            
            self.addExpenseGrid.add_widget(openDropdownGrid)
        
########################################
            self.addExpenseGrid.add_widget(Label(size_hint_y=None, height=self.textInputHeight))

            secondGrid = GridLayout(cols=2)
            self.addExpenseGrid.add_widget(secondGrid)
            
            secondGrid.add_widget(Label(text="Amount: ", size_hint_y=None, height=self.textInputHeight))
            self.amountInput = TextInput(size_hint_y=None, height=self.textInputHeight)
            secondGrid.add_widget(self.amountInput)
            
            self.addExpenseGrid.add_widget(Label(size_hint_y=None, height=self.textInputHeight/4))
            
            thirdGrid = GridLayout(cols=2)
            self.addExpenseGrid.add_widget(thirdGrid)
            
            thirdGrid.add_widget(Label(text="Reference: ", size_hint_y=None, height=self.textInputHeight))
            self.referenceInput = TextInput(size_hint_y=None, height=self.textInputHeight)
            thirdGrid.add_widget(self.referenceInput)
            
            addExpenseButton = Button(text="Add Expense", size_hint_y=None, height=self.textInputHeight)
            addExpenseButton.bind(on_press=self.addExpense)
            self.addExpenseGrid.add_widget(addExpenseButton)
    
    def dropdownValueSelected(self, instance, selected):
        self.paidByDropdownSelected = selected
    
    def addExpense(self, inctance=None):
        with OfflineDbManager() as dbManager:
            expenseAmount = self.amountInput.text
            expenseReference = self.referenceInput.text
            
            pattern = r'^\d+(\.\d{1,2})?$'
            validAmount = bool(re.match(pattern, expenseAmount))
            
            if validAmount:
                if "." in list(expenseAmount):
                    if len(expenseAmount.split(".")[1]) == 1:
                        expenseAmount += "0"
                else:
                    expenseAmount += ".00"
            else:
                self.showPopup("Invalid Amount", "The amount you enetered is invalid. You do not need to include the currency symbol.")
                return
        
            if not expenseReference:
                self.showPopup("Enter Reference", "Please enter a reference for this expense.")
                return
                
            if not self.paidByDropdownSelected:
                self.showPopup("Select Who Paid", "Please select who paid this expense.")
                return
            
            paidById = self.groupMemberIds[self.groupMemberNames.index(self.paidByDropdownSelected)]
            
            expenseAdded = dbManager.addExpense(self.currentGroupId, paidById, expenseAmount, expenseReference)
            if expenseAdded:
                self.showPopup("Expense Added", "Expense added successfully.")
                self.switchToGroupPage(self.currentGroupId)
            else:
                self.showPopup("Error", "An error occurred while trying to add this expense. Please try again later.")
    
    def setCurrentGroupId(self, groupId):
        self.currentGroupId = groupId
        
        self.backButton.bind(on_press=lambda instance=None:self.switchToGroupPage(self.currentGroupId))
        
        self.refreshGrid()