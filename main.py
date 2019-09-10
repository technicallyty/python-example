from interface import runWindow
import loginform
import time



bll = loginform.runLogin()

if bll == True:
    print("Login Successful")
    runWindow()

