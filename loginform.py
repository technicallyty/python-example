from tkinter import *
from tkinter.messagebox import showinfo

loginSuccess = False
machineIP = None
machineName = None
class LogInForm(Frame):
    # Constructor//Globals
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        #User Variables
        self.username = StringVar()
        self.password = StringVar()
        self.machine = StringVar()
        self.credentials={'Verisurf':'Admin'}
        self.machineNames={'Tyler':'127.0.0.1', 'Sean':'192.168.2.134'}
        self.LogInForm()


    # main window objects
    def LogInForm(self):
        self.master.title("Log In Form")
        Label(text="Machine:").pack()
        Entry(textvariable = self.machine).pack()
        Label(text="Username:").pack()
        Entry(textvariable = self.username).pack()
        Label(text="Password: ").pack()
        Entry(textvariable = self.password, show="*").pack()
        Button(text="Log In", command = self.login).pack()


    def login(self):
        try:
            machine = self.machine.get()
            user = self.username.get()
            password = self.password.get()
            if(password == self.credentials[user]):
                if(machine == 'Tyler' or 'Sean'):
                    global loginSuccess
                    global machineIP
                    loginSuccess = True
                    machineIP = self.machineNames[machine]
                    self.destroyz()
                else:
                    showinfo("Cannot Login", "Machine not found on network.")
            else:
                showinfo("Error", "Username or Password is incorrect!")
        except KeyError:
            showinfo("Error", "One or more credentials incorrect")




    def destroyz(self):
        self.master.destroy()

def runLogin():
    foo = Tk()
    foo.geometry("500x200")
    foo.resizable(False, False)

    application = LogInForm(foo)
    foo.mainloop()
    global machineName
    return (loginSuccess, machineIP, machineName)