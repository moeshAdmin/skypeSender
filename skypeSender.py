import os, sys
from skpy import Skype
from datetime import datetime, datetime

def main(argvConfig):
    #組態設定
    config = {
          'sysAccount':'',
          'sysPassword':'',
          'sysToken':''      
        }

    #參數     
    userID = argvConfig["userID"]
    mode = argvConfig["mode"]
    isAuthChk = argvConfig["isAuthChk"]
    msgContent = argvConfig["msgContent"]

    #系統帳號登入
    print("tokenChk")
    sk = tokenChk(config)
    print(isAuthChk)
    #如果身分確認功能有開啟才確認
    #身分確認關閉->直接發送訊息
    if(isAuthChk=="True"):
        #針對使用者身分確認 確定EP帳號可以正常與帳號溝通
        userAuth = userAuthChk(userID,mode,sk)
        if userAuth==True:
            sendMessage(sk,userID,msgContent)
        else:#可能尚未加好友，或為測試/請求驗證等模式
            print("userAuth:"+str(userAuth))
    elif(isAuthChk=="False"):
        #z發送正式訊息
        sendMessage(sk,userID,msgContent)


def tokenChk(config):
    try:
        #token登入 如果token已失效，重新以帳密登入取得新token
        sk = Skype(tokenFile=config["sysToken"])
        tokenExpiry = sk.conn.tokenExpiry["skype"]
        now = datetime.now()
        if tokenExpiry>now:
            loginMode = "token"
        else:
            sk = Skype(config["sysAccount"], config["sysPassword"], config["sysToken"])
            tokenExpiry = sk.conn.tokenExpiry["skype"]
            loginMode = "password"
        print("tokenChkSuccess:"+loginMode)
        return sk        
    except Exception as e:
        #沒有token存在 建立新token
        if "No username or password" in str(e):
            sk = Skype(config["sysAccount"], config["sysPassword"], config["sysToken"])
            tokenExpiry = sk.conn.tokenExpiry["skype"]
            loginMode = "password"
            print("tokenChkSuccess:"+loginMode)
            return sk
        else:
            print ("tokenChkError:"+str(e))
            sys.exit()

def userAuthChk(userID,mode,sk):
    userName = sk.contacts[userID].name.first
    userStatus = sk.contacts[userID].authorised
    userBlock = sk.contacts[userID].blocked
    if userStatus == False or userBlock == True:
        if mode=="test":
            print("此帳號尚未允許發送通知訊息，請確認一下帳號是否為您所有，若正確無誤，請按下[發送好友邀請]")
            print("帳號:"+userID)
            print("使用者名稱:"+userName+", 允許狀態:"+str(userStatus))
        elif mode=="auth":
            print("好友訊息已發送，請至Skype確認")
            ch = sk.chats["8:"+userID]
            ch.sendMsg("請先將此帳號加為好友，往後訊息才能正常接收!")
        else:
            print("此帳號尚未允許發送通知訊息，請先加入好友")
            print("帳號:"+userID)
        return False
    else:
        if (mode=="test" or mode=="auth"):
            print("帳號狀態檢測成功，您已可在Skype正常接收訊息!")
            ch = sk.chats["8:"+userID]
            ch.sendMsg("測試訊息發送完成，可以正常接收訊息!")
        else:
            return True

def sendMessage(sk,userID,msgContent):
    ch = sk.chats["8:"+userID]
    ch.sendMsg(msgContent)
    print("sendMsgSuccess")

if __name__ == "__main__":
    #argv1_使用者目標帳號

    #argv2_運作模式 
        #非好友狀態:test=測試是否允許發送 auth=請求允許
        #已加好友:test/auth=確認訊息均可正常發送

    #argv3_是否檢查使用者授權狀態
    if len(sys.argv) != 5:
        print("ERROR Argv: skypeSender <account> <type> <authChk> <msg>")
    else:
        argvConfig = {
              'userID':sys.argv[1],
              'mode':sys.argv[2],
              'isAuthChk':sys.argv[3],
              'msgContent':sys.argv[4],
            }
        print("mainStart")
        main(argvConfig)
