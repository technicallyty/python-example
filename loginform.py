from tkinter import *
from tkinter.messagebox import showinfo

loginSuccess = False

class LogInForm(Frame):
    # Constructor//Globals
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        #User Variables
        self.username = StringVar()
        self.password = StringVar()
        self.credentials={'Verisurf':'Admin'}
        self.LogInForm()


    # main window objects
    def LogInForm(self):
        self.master.title("Log In Form")
        Label(text="Username:").grid(row=0, column=0, sticky=W, pady=20)
        Entry(textvariable = self.username).grid(row = 0, column=1, sticky=W, pady=20, padx=5)
        Label(text="Password: ").grid(row=1, column=0, sticky=W, pady=20)
        Entry(textvariable = self.password, show="*").grid(row=1, column=1, sticky=W, pady=20, padx=5)
        Button(text="Log In", command = self.login).grid(row=3, column=0, sticky=W, pady=20)


    def login(self):
        try:
            if(self.password.get() == self.credentials[self.username.get()]):
                global loginSuccess
                loginSuccess = True
                self.destroyz()
            else:
                showinfo("Error", "Username or Password is incorrect!")
        except KeyError:
            showinfo("Error", "User does not exist!")


    def destroyz(self):
        self.master.destroy()

def runLogin():
    foo = Tk()
    foo.geometry("600x500")
    foo.resizable(False, False)

    application = LogInForm(foo)
    foo.mainloop()
    return loginSuccess