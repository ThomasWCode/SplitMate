import sys
import os
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)

from Database.dbSyncManager import DbSyncManager
import Database.dbGlobal as dbGlobal

import time
import sqlite3
import json
#from jnius import autoclass

internetAvailable = False
timeBetweenSyncing = 300 #secs

class OfflineDbSyncer:
    '''
    def checkInternet(self): #function for android
        global internetAvailable

        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        connectivity_service = activity.getSystemService(Context.CONNECTIVITY_SERVICE)
        
        NetworkInfo = connectivity_service.getActiveNetworkInfo()

        if NetworkInfo and NetworkInfo.isConnected():
            internetAvailable = True
            
        internetAvailable = False
    '''
    
    def testCheckInternet(self): #for testing on comp
        global internetAvailable
        
        internetAvailable = True
        
    def pullDownFromOnlineDb(self):
        db = dbGlobal.db
        
        offlineDbPath = dbGlobal.offlineDbPath
        tempOfflineDbPath = dbGlobal.tempOfflineDbPath
        
        try:
            if os.path.exists(tempOfflineDbPath):
                os.remove(tempOfflineDbPath)
            
            conn = sqlite3.connect(tempOfflineDbPath)
            cursor = conn.cursor()
            
            cursor.execute("CREATE TABLE Groups (groupId, groupName, membersDict, expensesDict)")
            cursor.execute("CREATE TABLE JoinCodes (joinCode, groupId)")
            cursor.execute("CREATE TABLE Users (userId, email, password, username, groupsDict)")
            cursor.execute("CREATE TABLE Changes (changesDict)")
            
            conn.commit()
            
            groupsRef = db.reference("Groups/Groups")
            if groupsRef.get():
                for groupId in (groupsRef.get()).keys():
                    groupName = db.reference(f"Groups/Groups/{groupId}/name").get()
                    unformattedExpensesDict = db.reference(f"Groups/Groups/{groupId}/Expenses").get()
                    membersDict = db.reference(f"Groups/Groups/{groupId}/Members").get()
                    
                    if not unformattedExpensesDict:
                        expensesDict = {}
                    
                    if not membersDict:
                        membersDict = {}
                    
                    if unformattedExpensesDict:
                        for expenseId in unformattedExpensesDict.keys():
                            expensesDict[expenseId] = {"Paid By": unformattedExpensesDict[expenseId]["Paid By"], "Amount": unformattedExpensesDict[expenseId]["Amount"], "Reference": unformattedExpensesDict[expenseId]["Reference"], "Time": unformattedExpensesDict[expenseId]["Time"]}
                    
                    cursor.execute("INSERT INTO Groups (groupId, groupName, membersDict, expensesDict) VALUES (?, ?, ?, ?)", (groupId, groupName, json.dumps(membersDict), json.dumps(expensesDict)))
                    conn.commit()
                    
            joinCodesRef = db.reference("Groups/Join Codes")
            
            if joinCodesRef.get():
                for joinCode in (joinCodesRef.get()).keys():
                    
                    groupId = db.reference(f"Groups/Join Codes/{joinCode}").get()
                    
                    cursor.execute("INSERT INTO JoinCodes (joinCode, groupId) VALUES (?, ?)", (joinCode, groupId))
                    conn.commit()
            
            usersRef = db.reference("Users/Users")
            if usersRef.get():
                for userId in (usersRef.get()).keys():
                    email = db.reference(f"Users/Users/{userId}/email").get()
                    password = db.reference(f"Users/Users/{userId}/password").get()
                    username = db.reference(f"Users/Users/{userId}/username").get()
                    userGroups = db.reference(f"Users/Users/{userId}/Groups").get()
                    
                    cursor.execute("INSERT INTO Users (userId, email, password, username, groupsDict) VALUES (?, ?, ?, ?, ?)", (userId, email, password, username, json.dumps(userGroups)))
                    conn.commit()
            
            conn.commit()
            
        except Exception as e:
            print("pullDownFromOnlineDb", e)
            
        finally:
            if conn:
                conn.close()
        
        if os.path.exists(offlineDbPath):
            os.remove(offlineDbPath)
        
        os.rename(tempOfflineDbPath, offlineDbPath)
        
        
    def syncLocalDb(self):
        with DbSyncManager() as dbSyncManager:
            try:
                userChanges = dbSyncManager.getChangesInOnlineDb()
                if userChanges:
                    for change in userChanges.keys():
                        splitChange = change.split("_")
                        
                        if splitChange[0] == "Groups":
                            groupId = splitChange[1]
                            
                            if splitChange[2] == "Expenses":
                                expenseId = splitChange[3]
                                
                                expensePaidBy = dbSyncManager.getExpensePaidByFromOnlineDb(groupId, expenseId)
                                expenseAmount = dbSyncManager.getExpenseAmountFromOnlineDb(groupId, expenseId)
                                expenseReference = dbSyncManager.getExpenseReferenceFromOnlineDb(groupId, expenseId)
                                expenseTime = dbSyncManager.getExpenseTimeFromOnlineDb(groupId, expenseId)
                                
                                dbSyncManager.addExpenseInOfflineDb(groupId, expenseId, expensePaidBy, expenseAmount, expenseReference, expenseTime)
                                
                            elif splitChange[2] == "Members":
                                memberId = splitChange[3]
                                
                                if splitChange[4] == "Add":
                                    dbSyncManager.addUserToGroupMembersInOfflineDb(memberId, groupId)
                                    
                                elif splitChange[4] == "Remove":
                                    dbSyncManager.removeUserFromGroupMembersInOfflineDb(memberId, groupId)
                        
                            elif splitChange[2] == "Join Codes":
                                joinCode = splitChange[3]
                                
                                dbSyncManager.addJoinCodeInOfflineDb(groupId, joinCode)
                            
                            elif splitChange[2] == "Groups":
                                dbSyncManager.addGroupInOfflineDb(groupId)
                        
                        elif splitChange[0] == "Users":
                            userId = splitChange[1]
                            
                            if splitChange[2] == "Groups":
                                groupId = splitChange[3]
                                
                                if splitChange[4] == "Add":
                                    dbSyncManager.addGroupToUserGroupsInOfflineDb(userId, groupId)
                                    
                                elif splitChange[4] == "Remove":
                                    dbSyncManager.removeGroupFromUserGroupsInOfflineDb(userId, groupId)
                                
                            elif splitChange[2] == "Users":
                                dbSyncManager.addUserInOfflineDb(userId)
                                
                    dbSyncManager.deleteChangesInOnlineDb()
            
            except Exception as e:
                print("syncLocalDb", e)
                
    def syncOnlineDb(self):
        with DbSyncManager() as dbSyncManager:
            try:
                changes = dbSyncManager.getChangesInOfflineDb()
                if changes:
                    for change in changes.keys():
                        print(change)
                        splitChange = change.split("_")
                    
                        if splitChange[0] == "Groups":
                            groupId = splitChange[1]
                            
                            if splitChange[2] == "Expenses":
                                expenseId = splitChange[3]
                                
                                expensePaidBy = dbSyncManager.getExpensePaidByFromOfflineDb(groupId, expenseId)
                                expenseAmount = dbSyncManager.getExpenseAmountFromOfflineDb(groupId, expenseId)
                                expenseReference = dbSyncManager.getExpenseReferenceFromOfflineDb(groupId, expenseId)
                                expenseTime = dbSyncManager.getExpenseTimeFromOfflineDb(groupId, expenseId)
                                
                                dbSyncManager.addExpenseInOnlineDb(groupId, expenseId, expensePaidBy, expenseAmount, expenseReference, expenseTime)
                                
                            elif splitChange[2] == "Members":
                                memberId = splitChange[3]
                                
                                if splitChange[4] == "Add":
                                    dbSyncManager.addUserToGroupMembersInOnlineDb(memberId, groupId)
                                    
                                elif splitChange[4] == "Remove":
                                    dbSyncManager.removeUserFromGroupMembersInOnlineDb(memberId, groupId)
                        
                            elif splitChange[2] == "Join Codes":
                                joinCode = splitChange[1]
                                
                                dbSyncManager.addJoinCodeInOnlineDb(groupId, joinCode)
                            
                            elif splitChange[2] == "Groups":
                                dbSyncManager.addGroupInOnlineDb(groupId)
                        
                        elif splitChange[0] == "Users":
                            userId = splitChange[1]
                            
                            if splitChange[2] == "Groups":
                                groupId = splitChange[3]
                                
                                if splitChange[4] == "Add":
                                    dbSyncManager.addGroupToUserGroupsInOnlineDb(userId, groupId)
                                
                                elif splitChange[4] == "Remove":
                                    dbSyncManager.removeGroupFromUserGroupsInOnlineDb(userId, groupId)
                            
                            elif splitChange[2] == "Users":
                                dbSyncManager.addUserInOnlineDb(userId)
                                
                    dbSyncManager.deleteChangesInOfflineDb()
                
            except Exception as e:
                print("syncOnlineDb", e)
                
    def syncDatabases(self):
        global currentUser
        
        currentUser = dbGlobal.currentUser
            
        if currentUser:
            self.syncLocalDb()
            self.syncOnlineDb()
            
        else:
            self.pullDownFromOnlineDb()
            
        print("COMPLETE syncDatabases")
        
'''
def mainSyncingLoop(self):
    offlineDbSyncer = OfflineDbSyncer()
    while True:
        offlineDbSyncer.testCheckInternet() #change to proper func before apk convert
        
        time.sleep(1)
        
        if internetAvailable:
            offlineDbSyncer.syncDatabases()
        
        time.sleep(timeBetweenSyncing)
'''