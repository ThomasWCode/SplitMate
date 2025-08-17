import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

import sqlite3
import json

import Database.dbGlobal as dbGlobal

class DbSyncManager:
    def __enter__(self):
        self.conn = sqlite3.connect(dbGlobal.offlineDbPath)
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type or exc_value or traceback:
            self.conn.rollback()
        else:
            self.conn.commit()
            
        self.conn.close()
        
    ###GENERAL###
    def getUsername(self, userId):
        try:
            self.cursor.execute("SELECT username FROM Users WHERE userId = ?", (userId,))
            
            username = self.cursor.fetchone()[0]
            
            return username
        except Exception:
            return None
        
    def getGroupName(self, groupId):
        self.cursor.execute("SELECT groupName FROM Groups WHERE groupId = ?", (groupId,))
        groupName = self.cursor.fetchone()[0]
        
        return groupName
    
    ###EXPENSES###
    def getExpenseAmountFromOnlineDb(self, groupId, expenseId):
        db = dbGlobal.db
        
        try:
            expenseAmountRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Amount")
            
            expenseAmount = expenseAmountRef.get()
            
            return expenseAmount
        
        except Exception:
            return None
        
    def getExpenseReferenceFromOnlineDb(self, groupId, expenseId):
        db = dbGlobal.db
        
        try:
            expenseReferenceRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Reference")
            
            expenseReference = expenseReferenceRef.get()
            
            return expenseReference
        
        except Exception:
            return None
    
    def getExpensePaidByFromOnlineDb(self, groupId, expenseId):
        db = dbGlobal.db
        
        try:
            expensePaidByRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Paid By")
            
            expensePaidBy = expensePaidByRef.get()
            
            return expensePaidBy
        
        except Exception:
            return None
        
    def getExpenseTimeFromOnlineDb(self, groupId, expenseId):
        db = dbGlobal.db
        
        try:
            expenseTimeRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Time")
            
            expenseTime = expenseTimeRef.get()
            
            return expenseTime
        
        except Exception:
            return None
        
    def addExpenseInOfflineDb(self, groupId, expenseId, paidById, amount, reference, time):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expensesDict[expenseId] = {"Paid By": paidById, "Amount": amount, "Reference": reference, "Time": time}
            
            self.cursor.execute("UPDATE Groups SET expensesDict = ? WHERE groupId = ?", (json.dumps(expensesDict), groupId))
            
            return True
        except Exception:
            return False
        
########################################
    def getExpenseAmountFromOfflineDb(self, groupId, expenseId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expenseAmount = expensesDict[expenseId]["Amount"]
            
            return expenseAmount
        
        except Exception:
            return None
        
    def getExpenseReferenceFromOfflineDb(self, groupId, expenseId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expenseReference = expensesDict[expenseId]["Reference"]
            
            return expenseReference
        
        except Exception:
            return None
    
    def getExpensePaidByFromOfflineDb(self, groupId, expenseId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expensePaidBy = expensesDict[expenseId]["Paid By"]
            
            return expensePaidBy
        
        except Exception:
            return None
        
    def getExpenseTimeFromOfflineDb(self, groupId, expenseId):
        try:
            self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
            
            expensesDict = json.loads(self.cursor.fetchone()[0])
            
            expenseTime = expensesDict[expenseId]["Time"]
            
            return expenseTime
        
        except Exception:
            return None
        
    def addExpenseInOnlineDb(self, groupId, expenseId, paidById, amount, reference, time):
        db = dbGlobal.db
        
        try:
            expensePaidByRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Paid By")
            expenseAmountRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Amount")
            expenseReferenceRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Reference")
            expenseTimeRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Time")
            
            expensePaidByRef.set(paidById)
            expenseAmountRef.set(amount)
            expenseReferenceRef.set(reference)
            expenseTimeRef.set(time)
            
            return True
        except Exception:
            return False
        
    ###GROUPS###
    def addGroupInOfflineDb(self, groupId):
        db = dbGlobal.db
        
        groupName = db.reference(f"Groups/Groups/{groupId}/name").get()
        membersDict = db.reference(f"Groups/Groups/{groupId}/Members").get()
        expensesDict = db.reference(f"Groups/Groups/{groupId}/Expenses").get()
        
        self.cursor.execute("INSERT INTO Groups (groupId, groupName, membersDict, expensesDict) VALUES (?, ?, ?, ?)", (groupId, groupName, json.dumps(membersDict), json.dumps(expensesDict)))
    
    def addGroupInOnlineDb(self, groupId):
        db = dbGlobal.db
        
        self.cursor.execute("SELECT groupName FROM Groups WHERE groupId = ?", (groupId,))
        groupName = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT membersDict FROM Groups WHERE groupId = ?", (groupId,))
        membersDict = json.loads(self.cursor.fetchone()[0])

        self.cursor.execute("SELECT expensesDict FROM Groups WHERE groupId = ?", (groupId,))
        expensesDict = json.loads(self.cursor.fetchone()[0])
        
        
        groupNameRef = db.reference(f"Groups/Groups/{groupId}/name")
        groupNameRef.set(groupName)
        
        for memberId in membersDict.keys():
            memberRef = db.reference(f"Groups/Groups/{groupId}/Members/{memberId}")
            memberRef.set(self.getUsername(memberId))
            
        for expenseId in expensesDict.keys():
            expenseAmountRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Amount")
            expensePaidByRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Paid By")
            expenseReferenceRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Reference")
            expenseTimeRef = db.reference(f"Groups/Groups/{groupId}/Expenses/{expenseId}/Time")
            
            expenseAmountRef.set(expensesDict[expenseId]["Amount"])
            expensePaidByRef.set(expensesDict[expenseId]["Paid By"])
            expenseReferenceRef.set(expensesDict[expenseId]["Reference"])
            expenseTimeRef.set(expensesDict[expenseId]["Time"])

########################################
    def addUserToGroupMembersInOfflineDb(self, userId, groupId):
        try:
            username = self.getUsername(userId)
            
            if not username:
                raise Exception
        
            self.cursor.execute("SELECT membersDict FROM Groups WHERE groupId = ?", (groupId,))
            membersDict = json.loads(self.cursor.fetchone()[0])
            
            membersDict[userId] = username
            
            self.cursor.execute("UPDATE Groups SET membersDict = ? WHERE groupId = ?", (json.dumps(membersDict), groupId))
                
            return True
        except Exception:
            return False
        
    def removeUserFromGroupMembersInOfflineDb(self, userId, groupId):
        try:
            username = self.getUsername(userId)
            
            if not username:
                raise Exception
        
            self.cursor.execute("SELECT membersDict FROM Groups WHERE groupId = ?", (groupId,))
            membersDict = json.loads(self.cursor.fetchone()[0])
            
            membersDict.pop(userId)
            
            self.cursor.execute("UPDATE Groups SET membersDict = ? WHERE groupId = ?", (json.dumps(membersDict), groupId))
                
            return True
        except Exception:
            return False
        
    def addGroupToUserGroupsInOfflineDb(self, userId, groupId):
        try:
            groupName = self.getGroupName(groupId)
            
            if not groupName:
                raise Exception
            
            self.cursor.execute("SELECT groupsDict FROM Users WHERE userId = ?", (userId,))
            groupsDict = json.loads(self.cursor.fetchone()[0])
            
            groupsDict[groupId] = groupName
            
            self.cursor.execute("UPDATE Users SET groupsDict = ? WHERE userId = ?", (json.dumps(groupsDict), userId))
                
            return True
        except Exception:
            return False
        
    def removeGroupFromUserGroupsInOfflineDb(self, userId, groupId):
        try:
            groupName = self.getGroupName(groupId)
            
            if not groupName:
                raise Exception
            
            self.cursor.execute("SELECT groupsDict FROM Users WHERE userId = ?", (userId,))
            groupsDict = json.loads(self.cursor.fetchone()[0])
            
            groupsDict.pop(groupId)
            
            self.cursor.execute("UPDATE Users SET groupsDict = ? WHERE userId = ?", (json.dumps(groupsDict), userId))
                
            return True
        except Exception:
            return False
        
########################################
    def addUserToGroupMembersInOnlineDb(self, userId, groupId):
        db = dbGlobal.db
        
        try:
            username = self.getUsername(userId)
            
            if not username:
                raise Exception
                
            memberRef = db.reference(f"Groups/Groups/{groupId}/Members/{userId}")
            memberRef.set(username)
                
            return True
        except Exception:
            return False
    
    def removeUserFromGroupMembersInOnlineDb(self, userId, groupId):
        db = dbGlobal.db
        
        try:
            memberRef = db.reference(f"Groups/Groups/{groupId}/Members/{userId}")
            memberRef.delete()
                
            return True
        except Exception:
            return False
        
    def addGroupToUserGroupsInOnlineDb(self, userId, groupId):
        db = dbGlobal.db
        
        try:
            groupName = self.getGroupName(groupId)
            
            if not groupName:
                raise Exception
            
            userGroupRef = db.reference(f"Users/Users/{userId}/Groups/{groupId}")
            userGroupRef.set(groupName)
                
            return True
        except Exception:
            return False
    
    def removeGroupFromUserGroupsInOnlineDb(self, userId, groupId):
        db = dbGlobal.db
        
        try:
            userGroupRef = db.reference(f"Users/Users/{userId}/Groups/{groupId}")
            userGroupRef.delete()
                
            return True
        except Exception:
            return False
        
    #JOIN CODES###
    def addJoinCodeInOfflineDb(self, groupId, joinCode):
        try:
            self.cursor.execute("INSERT INTO JoinCodes (joinCode, groupId) VALUES (?, ?)", (joinCode, groupId))
            
            return True
        except Exception:
            return False
        
    def addJoinCodeInOnlineDb(self, groupId, joinCode):
        db = dbGlobal.db
        
        try:
            groupJoinCodeRef = db.reference(f"Groups/Join Codes/{joinCode}")
            groupJoinCodeLookupRef = db.reference(f"Groups/Join Code Lookup/{groupId}")
            
            groupJoinCodeRef.set(groupId)
            groupJoinCodeLookupRef.set(joinCode)
            
            return True
        except Exception as e:
            print("addJoinCodeInOnlineDb", e)
            return False
        
    ###CHANGES###
    def deleteChangesInOfflineDb(self):
        try:
            self.cursor.execute("DELETE FROM Changes")
            
            return True
        except Exception:
            return False
        
    def getChangesInOfflineDb(self):
        try:
            self.cursor.execute("SELECT changesDict FROM Changes")
            changes = json.loads(self.cursor.fetchone()[0])
            
            return changes
        except Exception:
            return None
        
    def deleteChangesInOnlineDb(self):
        db = dbGlobal.db
        
        try:
            currentUser = dbGlobal.currentUser
            db.reference(f"Changes/{currentUser}").delete()
            
            return True
        except Exception:
            return False
        
    def getChangesInOnlineDb(self):
        db = dbGlobal.db
        
        try:
            currentUser = dbGlobal.currentUser
            userChanges = db.reference(f"Changes/{currentUser}").get()
            
            return userChanges
        except Exception:
            return None
        
    ###USERS###
    def addUserInOfflineDb(self, userId):
        db = dbGlobal.db
        
        try:
            email = db.reference(f"Users/Users/{userId}/email").get()
            password = db.reference(f"Users/Users/{userId}/password").get()
            username = db.reference(f"Users/Users/{userId}/username").get()
            groupsDict = db.reference(f"Users/Users/{userId}/Groups").get()
            
            self.cursor.execute("INSERT INTO Users (userId, email, password, username, groupsDict) VALUES (?, ?, ?, ?, ?)", (userId, email, password, username, json.dumps(groupsDict)))
            
            return True
        except Exception:
            return False
        
    def addUserInOnlineDb(self, userId):
        db = dbGlobal.db
        
        try:
            username = self.getUsername(userId)
            
            self.cursor.execute("SELECT email FROM Users WHERE userId = ?", (userId,))
            email = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT password FROM Users WHERE userId = ?", (userId,))
            password = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT groupsDict FROM Users WHERE userId = ?", (userId,))
            groupsDict = self.cursor.fetchone()[0]
            
            
            usernameRef = db.reference(f"Users/Users/{userId}/username")
            usernameRef.set(username)
            
            emailRef = db.reference(f"Users/Users/{userId}/email")
            emailRef.set(email)
            
            passwordRef = db.reference(f"Users/Users/{userId}/password")
            passwordRef.set(password)
            
            for groupId in groupsDict:
                userGroupRef = db.reference(f"Users/Users/{userId}/Groups/{groupId}")
                userGroupRef.set(groupsDict[groupId])
            
            return True
        except Exception:
            return False