import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

from datetime import datetime

from Database.offlineDbManager import OfflineDbManager

from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

class GroupTotalsScreen(GridLayout):
    def __init__(self, switchToGroupPage, switchToAddExpense, **kwargs):
        super(GroupTotalsScreen, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.padding = 20
        
        self.switchToGroupPage = switchToGroupPage
        self.switchToAddExpense = switchToAddExpense
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
        self.groupTotalsGrid = GridLayout(cols=1)
        
        self.add_widget(self.groupTotalsGrid)

    def refreshGrid(self):
        with OfflineDbManager() as dbManager:
            self.groupTotalsGrid.clear_widgets()
            
            infoGrid = GridLayout(cols=2)
            self.groupTotalsGrid.add_widget(infoGrid)
            
            recentExpensesGrid = GridLayout(cols=1)
            infoGrid.add_widget(recentExpensesGrid)
            
            overallTotalsGrid = GridLayout(cols=1)
            infoGrid.add_widget(overallTotalsGrid)
            
            recentExpensesGrid.add_widget(Label(text="Recent Expenses", size_hint_y=None, height=self.textInputHeight/2, underline=True))
            
            groupExpenseIds, error = dbManager.getGroupExpenseIds(self.currentGroupId)
            groupExpenseInfo = {}
            if groupExpenseIds:
                for expenseId in groupExpenseIds:
                    expenseAmount = dbManager.getExpenseAmount(self.currentGroupId, expenseId)
                    expenseRef = dbManager.getExpenseReference(self.currentGroupId, expenseId)
                    expenseTime = dbManager.getExpenseTime(self.currentGroupId, expenseId)
                    expensePaidBy = dbManager.getUsername((dbManager.getExpensePaidBy(self.currentGroupId, expenseId)))
                    
                    groupExpenseInfo[expenseId] = [expenseAmount, expenseTime, expenseRef, expensePaidBy]
                    
            elif error:
                recentExpensesGrid.add_widget(Label(text="Error while loading recent expenses."))
            else:
                recentExpensesGrid.add_widget(Label(text="No recent expenses."))
                self.addExpenseButton = Button(text="Add Expense", size_hint_y=None, height=self.textInputHeight/2)
                self.addExpenseButton.bind(on_press=lambda instance: self.switchToAddExpense(self.currentGroupId))
                recentExpensesGrid.add_widget(self.addExpenseButton)
                
            if groupExpenseInfo:
                timeSortedGroupExpenseInfo = dict(sorted(groupExpenseInfo.items(), key=lambda item: datetime.strptime(item[1][1], '%d_%m_%Y:%H_%M_%S'), reverse=True))
                
                expensesOnScreen = 0
                for expenseId in timeSortedGroupExpenseInfo:
                    if expensesOnScreen < 5:
                        expenseInfo = timeSortedGroupExpenseInfo[expenseId]
                        
                        expenseAmount = expenseInfo[0]
                        expenseTime = expenseInfo[1]
                        expenseRef = expenseInfo[2]
                        expensePaidBy = expenseInfo[3]
                        
                        dateText = "/".join((expenseTime.split(":")[0]).split("_"))
                        timeText = f"{expenseTime.split(':')[1].split('_')[0]}:{expenseTime.split(':')[1].split('_')[1]}"
                        formattedExpenseTime = f"{dateText} at {timeText}"
                        
                        recentExpensesGrid.add_widget(Label(text=f"{expenseAmount}\n  - {formattedExpenseTime}\n  - {expenseRef}\n  - {expensePaidBy}"))
                        expensesOnScreen += 1
                    else:
                        break
                
########################################
            overallTotalsGrid.add_widget(Label(text="Totals", size_hint_y=None, height=self.textInputHeight/2, underline=True))
            
            groupExpenseIds, error = dbManager.getGroupExpenseIds(self.currentGroupId)
            if groupExpenseIds:
                
                groupTotalExpenseAmount = 0
                for expenseId in groupExpenseIds:
                    groupTotalExpenseAmount += float(dbManager.getExpenseAmount(self.currentGroupId, expenseId))
                
                memberAmountsPaid = {}
                for memberId in dbManager.getGroupMembers(self.currentGroupId):
                    memberAmountsPaid[memberId] = 0
                    
                    for expenseId in groupExpenseIds:
                        expensePaidBy = dbManager.getExpensePaidBy(self.currentGroupId, expenseId)
                        
                        if expensePaidBy == memberId:
                            expenseAmount = float(dbManager.getExpenseAmount(self.currentGroupId, expenseId))
                            
                            memberAmountsPaid[memberId] += expenseAmount
                            
                for memberId in memberAmountsPaid:
                    memberName = dbManager.getUsername(memberId)
                    
                    amountOwed = -(memberAmountsPaid[memberId] - (groupTotalExpenseAmount / len(memberAmountsPaid)))
                    
                    if amountOwed > 0:
                        for secondMemberId in memberAmountsPaid:
                            secondMemberName = dbManager.getUsername(secondMemberId)
                            
                            if memberAmountsPaid[secondMemberId] > (groupTotalExpenseAmount / len(memberAmountsPaid)):
                                overallTotalsGrid.add_widget(Label(text=f"{memberName} owes {secondMemberName} {amountOwed}", size_hint_y=None, height=self.textInputHeight/2))
                                break
                    else:
                        overallTotalsGrid.add_widget(Label(text=f"{memberName} owes nothing", size_hint_y=None, height=self.textInputHeight/2))
                        
                overallTotalsGrid.add_widget(Label(text=f"Total Expense Amount: {groupTotalExpenseAmount}"))


                    
                overallTotalsGrid.add_widget(Label(text=f"Total Expense Amount: {groupTotalExpenseAmount}"))
            elif error:
                overallTotalsGrid.add_widget(Label(text="Error while loading group totals."))
            else:
                overallTotalsGrid.add_widget(Label(text=f"Total Expense Amount: 0"))
    
    def setCurrentGroupId(self, groupId):
        self.currentGroupId = groupId
        
        self.backButton.bind(on_press=lambda instance=None:self.switchToGroupPage(self.currentGroupId))
        
        self.refreshGrid()