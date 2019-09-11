from interface import runWindow
import loginform
import time



logindata = loginform.runLogin()



loginsuccess = logindata[0]
machineip = logindata[1]
machineName = logindata[2]


if loginsuccess == True:
    print("Login Successful")
    runWindow(machineip, name)

