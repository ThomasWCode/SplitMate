import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

import sqlite3
import uuid
from datetime import datetime
import json

import Database.dbGlobal as dbGlobal

changesDict = {}

class OfflineDbManager:
    def __enter__(self):
        self.conn = sqlite3.connect(dbGlobal.offlineDbPath)
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type or exc_value or traceback:
            self.conn.rollback()
        else:
            self.conn.commit()
            
            self.setChanges()
            self.conn.commit()
            
        self.conn.close()
        
    ###GENERAL###
    def getCurrentUser(self):
        return dbGlobal.currentUser
    
    def setCurrentUser(self, email):
        try:
            self.cursor.execute("SELECT userId FROM Users WHERE email = ?", (email,))
            userId = self.cursor.fetchone()[0]
            
            dbGlobal.currentUser = userId
            
            return True
        except Exception:
            return False
    
    def getUsername(self, userId):
        try:
            self.cursor.execute("SELECT username FROM Users WHERE userId = ?", (userId,))
            
            username = self.cursor.fetchone()[0]
            
            return username
        except Exception:
            return None
        
    def getUserIdFromEmail(self, email):
        try:
            self.cursor.execute("SELECT userId FROM Users WHERE email = ?", (email,))
            userId = self.cursor.fetchone()[0]
            
            return userId
        except Exception:
            return None
        
    def setChanges(self):
        global changesDict
        
        try:
            db = dbGlobal.db
            currentUser = dbGlobal.currentUser
            
            allUserIds = []
            if db.reference("Users/Users").get():
                for userId in (db.reference("Users/Users").get()).keys():
                    allUserIds.append(userId)
            
            for change in changesDict.keys():
                self.cursor.execute("SELECT changesDict FROM Changes")
                userChangesDict = self.cursor.fetchone()
                
                try:
                    userChangesDict = json.loads(userChangesDict[0])
                except Exception:
                    userChangesDict = {}
                
                userChangesDict[change] = self.getUsername(currentUser)
                
                self.cursor.execute("DELETE FROM Changes")
                self.conn.commit()
                
                self.cursor.execute("INSERT INTO Changes (changesDict) VALUES (?)", (json.dumps(userChangesDict),))
                
                for userId in allUserIds:
                    if userId != currentUser:
                        changeRef = db.reference(f"Changes/{userId}/{change}")
                        changeRef.set(self.getUsername(currentUser))
                        
            changesDict = {}
                        
        except Exception as e:
            print(f"Error while setting changes: {e}")
            
    ###LOGIN###
    def checkEmailAndPassword(self, email, password):
        try:
            self.cursor.execute("SELECT userId FROM Users WHERE email = ?", (email,))
            userId = self.cursor.fetchone()
            
            if userId:
                userId = userId[0]
                
                self.cursor.execute("SELECT password FROM Users WHERE userId = ?", (userId,))
                passwordInDb = self.cursor.fetchone()[0]
                
                if passwordInDb == password:
                    return True, False
                
        except Exception:
            return False, True
        
        return False, False
    
    ###SIGNUP##
    def checkAlreadyUser(self, email):
        try:
            self.cursor.execute("SELECT userId FROM Users WHERE email = ?", (email,))
            userId = self.cursor.fetchone()

            if userId:
                return True, False
            
        except Exception:
            return False, True
            
        return False, False
    
    def signupNewUser(self, username, email, password):
        global changesDict
        
        try:
            userId = str(uuid.uuid4())
            
            self.cursor.execute("INSERT INTO Users (userId, email, password, username, groupsDict) VALUES (?, ?, ?, ?, ?)", (userId, email, password, username, json.dumps({})))
            
            changesDict[f"Users_{userId}_Users"] = self.getUsername(userId)
            
            self.conn.commit()
            
            return True
        except Exception:
            return False
        
    ###GROUPS###
    def getGroupName(self, groupId):
        self.cursor.execute("SELECT groupName FROM Groups WHERE groupId = ?", (groupId,))
        groupName = self.cursor.fetchone()[0]
        
        return groupName
                
    def createGroup(self, groupName):
        global changesDict
        
        try:
            groupId = str(uuid.uuid4())
            
            self.cursor.execute("INSERT INTO Groups (groupId, groupName, membersDict, expensesDict) VALUES (?, ?, ?, ?)", (groupId, groupName, json.dumps({}), json.dumps({})))
            
            changesDict[f"Groups_{groupId}_Groups"] = self.getUsername(groupId)
            
            generationSuccess, joinCode = self.generateJoinCode(groupId)
            if generationSuccess:
                return True, groupId, joinCode
            else:
                raise Exception
        except Exception:
            return False, None, None
        
    ###GROUPS//JOIN CODES###
    def generateJoinCode(self, groupId):
        global changesDict
        
        try:
            joinCode = str(uuid.uuid4())[:8]
            
            self.cursor.execute("INSERT INTO JoinCodes (joinCode, groupId) VALUES (?, ?)", (joinCode, groupId))
            
            changesDict[f"Groups_{groupId}_Join Codes_{joinCode}"] = joinCode
            
            return True, joinCode
        except Exception:
            return False, None
        
    def checkJoinCode(self, joinCode):
        try:
            self.cursor.execute("SELECT groupId FROM JoinCodes WHERE joinCode = ?", (joinCode,))
            groupId = self.cursor.fetchone()[0]
            
            if groupId:
                groupId = groupId[0]
                return True, False, groupId
            else:
                return False, False, None
        except Exception:
            return False, True, None
        
    def getJoinCode(self, groupId):
        try:
            self.cursor.execute("SELECT joinCode FROM JoinCodes WHERE groupId = ?", (groupId,))
            joinCode = self.cursor.fetchone()[0]
            
            return joinCode
        except Exception:
            return None
        
    ###GROUPS//MEMBERS###
    def getUserGroups(self, userId):
        self.cursor.execute("SELECT groupsDict FROM Users WHERE userId = ?", (userId,))
        groupsDict = json.loads(self.cursor.fetchone()[0])
        
        userGroups = []
        for groupId in groupsDict.keys():
            userGroups.append(groupId)
        
        return userGroups
    
    def addUserToGroup(self, userId, groupId):
        global changesDict
        
        try:
            groupName = self.getGroupName(groupId)
            username = self.getUsername(userId)
            
            if not groupName or not username:
                raise Exception
            
            self.cursor.execute("SELECT groupsDict FROM Users WHERE userId = ?", (userId,))
            groupsDict = json.loads(self.cursor.fetchone()[0])
            
            groupsDict[groupId] = groupName
            
            self.cursor.execute("UPDATE Users SET groupsDict = ? WHERE userId = ?", (json.dumps(groupsDict), userId))
            
            changesDict[f"Users_{userId}_Groups_{groupId}_Add"] = self.getGroupName(groupId)
            
        
            self.cursor.execute("SELECT membersDict FROM Groups WHERE groupId = ?", (groupId,))
            membersDict = json.loads(self.cursor.fetchone()[0])
            
            membersDict[userId] = username
            
            self.cursor.execute("UPDATE Groups SET membersDict = ? WHERE groupId = ?", (json.dumps(membersDict), groupId))
            
            changesDict[f"Groups_{groupId}_Members_{userId}_Add"] = self.getUsername(userId)
                
            return True
        except Exception:
            return False
    
    def getGroupMembers(self, groupId):
        try:
            self.cursor.execute("SELECT membersDict FROM Groups WHERE groupId = ?", (groupId,))
            membersDict = json.loads(self.cursor.fetchone()[0])
            
            groupMemberIds = []
            for memberId in membersDict.keys():
                groupMemberIds.append(memberId)
            
            if not groupMemberIds:
                return None
            
            return groupMemberIds
        except Exception:
            return None
        
    def checkAlreadyMember(self, userId, groupId):
        try:
            self.cursor.execute("SELECT membersDict FROM Groups WHERE groupId = ?", (groupId,))
            membersDict = json.loads(self.cursor.fetchone()[0])
            
            groupMemberIds = []
            for memberId in membersDict.keys():
                groupMemberIds.append(memberId)
            
            if not groupMemberIds:
                return False, True
                
            if userId in groupMemberIds:
                return True, False
            
            return False, False
        
        except Exception:
            return False, True
    
    def removeUserFromGroup(self, userId, groupId):
        global changesDict
        
        try:
            self.cursor.execute("SELECT groupsDict FROM Users WHERE userId = ?", (userId,))
            groupsDict = json.loads(self.cursor.fetchone()[0])
            
            groupsDict.pop(groupId)
            
            self.cursor.execute("UPDATE Users SET groupsDict = ? WHERE userId = ?", (json.dumps(groupsDict), userId))
            
            changesDict[f"Users_{userId}_Groups_{groupId}_Remove"] = self.getGroupName(groupId)
            
        
            self.cursor.execute("SELECT membersDict FROM Groups WHERE groupId = ?", (groupId,))
            membersDict = json.loads(self.cursor.fetchone()[0])
            
            membersDict.pop(userId)
            
            self.cursor.execute("UPDATE Groups SET membersDict = ? WHERE groupId = ?", (json.dumps(membersDict), groupId))
            
            changesDict[f"Groups_{groupId}_Members_{userId}_Remove"] = self.getUsername(userId)
            
            return True
        except Exception:
            return False
        
    ###GROUPS//EXPENSES###
    def addExpense(self, groupId, paidById, amount, reference):
        global changesDict
        
        try:
            currentTime = datetime.now()
            currentDay, currentMonth, currentYear, currentHour, currentMin, currentSec, currentMicrosec = str(currentTime.day), str(currentTime.month), str(currentTime.year), str(currentTime.hour), str(currentTime.minute), str(currentTime.second), str(currentTime.microsecond)
            if len(currentDay) == 1:
                currentDay = f"0{currentDay}"
            if len(currentMonth) == 1:
                currentMonth = f"0{currentMonth}"
            if len(currentYear) == 1:
                currentYear = f"0{currentYear}"
            if len(currentHour) == 1:
                currentHour = f"0{currentHour}"
            if len(currentMin) == 1:
                currentMin = f"0{currentMin}"
            if len(currentSec) == 1:
                currentSec = f"0{currentSec}"
                
            currentTime = f"{currentDay}_{currentMonth}_{currentYear}:{currentHour}_{currentMin}_{currentSec}"
            
            expenseId = str(uuid.uuid4())
            
            
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expensesDict[expenseId] = {"Paid By": paidById, "Amount": amount, "Reference": reference, "Time": currentTime}
            
            self.cursor.execute("UPDATE Groups SET expensesDict = ? WHERE groupId = ?", (json.dumps(expensesDict), groupId))
            
            changesDict[f"Groups_{groupId}_Expenses_{expenseId}"] = expenseId
            
            return True
        except Exception:
            return False
        
    def getGroupExpenseIds(self, groupId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            groupExpenseIds = []
            for expenseId in expensesDict.keys():
                groupExpenseIds.append(expenseId)
            
            if not groupExpenseIds:
                return None, False

            return groupExpenseIds, False
        except Exception:
            return None, True
        
    def getExpenseAmount(self, groupId, expenseId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expenseAmount = expensesDict[expenseId]["Amount"]
            
            return expenseAmount
        
        except Exception:
            return None
        
    def getExpenseReference(self, groupId, expenseId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expenseReference = expensesDict[expenseId]["Reference"]
            
            return expenseReference
        
        except Exception:
            return None
        
    def getExpenseTime(self, groupId, expenseId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expenseTime = expensesDict[expenseId]["Time"]
            
            return expenseTime
        
        except Exception:
            return None
    
    def getExpensePaidBy(self, groupId, expenseId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expensePaidBy = expensesDict[expenseId]["Paid By"]
            
            return expensePaidBy
        
        except Exception:
            return None