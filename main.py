from interface import runWindow
import loginform
import time

# ------------------------
# Main logic -
# Runs login form, which will
# return a tuple of information/results.
# Gives bool success, int IP, and string name
# associated with the IP.
# -------------------------

logindata = loginform.runLogin()



loginsuccess = logindata[0]
machineip = logindata[1]
machineName = logindata[2]

if loginsuccess == True:
    print("Login Successful")
    runWindow(machineip, machineName)

