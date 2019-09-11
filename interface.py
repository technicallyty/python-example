from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import ttk
from tkinter.messagebox import showinfo
import socket
from xml.dom import minidom
import os
from shutil import copyfile


 # constructor
class Window(Frame):
    # Constructor//Globals
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.window()
        self.myFile = None
        self.tempFile = open("xmltempdata.xml", 'w')
        self.SOCK = None
        self.PlanInfo = []
        self.resultX = None
        self.Connected = False
        self.isSaved = False

    # main window objects
    def window(self):
        self.master.title("Tyler's App")
        self.pack(fill=BOTH, expand=True)

        global machineName
        Label(text=("Connected to: " + machineName)).place(x=650)

        # connect button, triggers Connect function
        self.connectedLabel = Label(text="Status: Not Connected")
        self.connectedLabel.place(x=5, y=660)
        self.connectButton = Button(self, text="Connect", command=self.Connect, height=2, width=10)
        self.connectButton.place(x=340, y=600)

        # menu bar
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu)
        file.add_command(label="Export XML", command=self.saveas)
        file.add_command(label="Quit", command=self.exit_client)
        menu.add_cascade(label="File", menu=file)

    def exit_client(self):
        self.master.destroy()


    # Creates XML file to write Verisurf Responses
    def saveas(self):
        fileTypes = [('XML Files', '*.xml')]
        file = filedialog.asksaveasfile(mode='a', filetypes=fileTypes, defaultextension=fileTypes)
        try:
            self.lbl.configure(text="File path: " + file.name)

            if self.isSaved == False:
                self.myFile = open(file.name, "w+")
                self.tempFile.close()
                self.myFile.close()
                copyfile('xmltempdata.xml', file.name)
                self.isSaved = True
                #os.remove(self.tempFile)
                self.myFile = open(file.name, "a")
                base = os.path.basename(self.tempFile.name)
                os.remove(base)
            else:
                self.myFile.close()
                tempcopy = open(file.name, "w+")
                tempcopy.close()
                copyfile(self.myFile.name, file.name)
                self.myFile = open(file.name, "a")



        except AttributeError:
            None
            # do nothing, file was not saved.

    # Connects to Verisurf.
    def Connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global ipnum
        host = ipnum
        port = 33666
        try:
            if self.Connected == False:
                s.connect((host, port))
                self.SOCK = s
                tm = s.recv(1024)
                self.tm = tm.decode('ascii')
                self.connectedLabel.configure(text="Status: Connected")
                self.writeFiles(self.tm)
                self.Connected = True
                self.connectButton.configure(text="Disconnect")
                self.getPlans()
            else:
                self.Connected = False
                self.SOCK.close()
                self.connectButton.configure(text="Connect")
                self.connectedLabel.configure(text="Status: Not Connected")
        except ConnectionError:
            self.connectedLabel.configure(text="Unable to Connect")
            self.Connected = False

    # Asks verisurf for plan names. Creates drop down box to select each plan
    def getPlans(self):
        Label(text="Active Plan").place(x=15,y=100)

        #try:
        sender = "<Inspect_Plan_List />\n"
        received = self.sendCommand(sender)
        self.writeFiles(received)
        self.Plans = self.ParseXML(received, "plan", "id")

        # CREATE DROP DOWN
        self.selected = StringVar()
        menu = ttk.Combobox(self, values=[*self.Plans], textvariable=self.selected)
        menu.current(0)
        menu.place(x=15, y=140)
        menu.bind("<<ComboboxSelected>>", self.userSelection)
        self.planDetails(0)
        #except:
            # checks if connection error, or if project empty
            #if self.Connected == False:
                #showinfo("Connection Error", "You are not connected to Verisurf!")
            #else:
                #showinfo("No data", "Your verisurf project is empty!")

    # Required tkinter function to detect selection
    def userSelection(self, event):
        self.planDetails(self.Plans.index(self.selected.get()))

    # Gets plan details - objects in plan
    def planDetails(self, planNumber):
        try:
            send = ("<Inspect_Plan_Load id=\"" + str(planNumber) + "\" />\n")
            self.SOCK.send(send.encode('ascii'))
            temp = self.SOCK.recv(10000)
            send = "<Inspect_Plan_Info id = \"" + str(planNumber) + "\" />\n"
            received = self.sendCommand(send)
            self.writeFiles(received)
            self.parsedList = self.ParseXML(received, "plan_object", "object_id")

            # CREATE DROP DOWN
            objects = Listbox(self)
            for items in self.parsedList:
                objects.insert(1, items)
            objects.place(x=15,y=200)
            objects.bind("<<ListboxSelect>>", self.ObjectSelect)
        except:
            showinfo("No data", "Selected plan has no objects.")

    # Tkinter function needed to detect when dropdown has changed
    def ObjectSelect(self, event):
        widget = event.widget
        selection = widget.curselection()
        value = widget.get(selection[0])
        self.objectDetails(self.parsedList.index(value))
        #self.objectDetails(self.parsedList.index(self.objectSelect))

    def objectDetails(self, num):
        sender = "<Inspect_Object_Info id=\"" + str(num) + "\" />\n"
        received = self.sendCommand(sender)
        self.writeFiles(received)
        self.objectList = self.ParseXML(received, "property", "none")
        resultsbtn = Button(self, text="Results", command=self.showResults)
        resultsbtn.place(x=600, y=600)
        print(self.objectList)

    def showResults(self):
        self.font = font.Font(self.master, family="Helvetica", size=20, weight="bold")
        self.top = Toplevel(master=None, height=750, width=750, relief="sunken")
        self.top.title("Results")

        # Default headers for information
        self.actual = Label(self.top, text="Act", font=self.font)
        self.actual.grid(row=0, column=1)
        self.meas = Label(self.top, text="Meas", font=self.font)
        self.meas.grid(row=0, column=2)
        self.dev = Label(self.top, text="Dev", font=self.font)
        self.dev.grid(row=0, column=3)

        inTol = "blue"
        outTol = "red"

        rows = 1
        # generates values to display
        for items in self.objectList:
            nameLabel = Label(self.top, text=items['name'], font=self.font)
            nameLabel.grid(row=rows, column=0, padx=40, pady=20, sticky=W)
            nomLabel = Label(self.top, text="{:.3f}".format(items['nominal']), font=self.font, fg=inTol)
            nomLabel.grid(row=rows, column=1, padx=100, pady=20, sticky=W)
            devLabel = Label(self.top, text="{:.3f}".format(items['deviation']), font=self.font, fg=inTol)
            devLabel.grid(row=rows, column=3, padx=100, pady=20, sticky=W)

            #Logic to determine if OOT. changes to red if so
            if items['deviation'] > items['tolmax'] or items['deviation'] < items['tolmin']:
                measLabel = Label(self.top, text="{:.3f}".format(items['measured']), font=self.font, fg=outTol)
            else:
                measLabel = Label(self.top, text="{:.3f}".format(items['measured']), font=self.font, fg=inTol)
            measLabel.grid(row=rows, column=2, padx=100, pady=20, sticky=W)

            rows += 1

        self.update()
        self.top.bind('<Configure>', self.resize)

    # handles window resizing event. adjusts font size accordingly.
    def resize(self, event):
        try:
            size = len(self.objectList) * 14
            self.font['size'] = int(((self.top.winfo_height() + self.top.winfo_width()) / size))
        except TclError:
            # do nothing
            None

    # Sends commands to Verisurf, returns message
    def sendCommand(self, msg):
        self.SOCK.send(msg.encode('ascii'))
        newmsg = self.SOCK.recv(10000)
        newmsg = self.SOCK.recv(10000)
        newmsg = newmsg.decode('ascii')
        self.writeFiles(newmsg)
        return (newmsg)

    # Writes Verisurf responses to global file
    def writeFiles(self, st):
        # Try to write to the saveas file, otherwise, temp file.
        try:
            self.myFile.write(st)
        except:
            self.tempFile.write(st)

    # Parses XML response from Verisurf
    def ParseXML(self, data, tagname, id):
        # set up temp doc to parse with minidom
        tempFile = open("temp.xml", "w+")
        tempFile.write(data)
        tempFile.close()
        mydoc = minidom.parse('temp.xml')
        list = []

        # handles tags that have a closing tag such as <\tagname>
        if (id != "none"):
            items = mydoc.getElementsByTagName(tagname)

            for elem in items:
                list.append(elem.firstChild.data)
        else:
            property = mydoc.getElementsByTagName(tagname)
            for items in property:
                dict = {}
                dict.update({"name": items.getAttribute("name")})

                # list of properties to extract from object
                names = ["nominal", "measured", "deviation", "tolmin", "tolmax"]
                for x in names:
                    if len(items.getAttribute(x)) == 0:
                        dict.update({x: 0.0})
                    else:
                        dict.update({x: float(items.getAttribute(x))})
                list.append(dict)

        tempFile.close()
        #Removes temporary file used to parse XML
        os.remove('temp.xml')
        return list


def runWindow(ip, name):
    global ipnum
    global machineName
    machineName = name
    ipnum = ip
    root = Tk()
    root.geometry("800x700")
    root.resizable(False, False)
    app = Window(root)
    root.mainloop()

ipnum = None
machineName = None

runWindow("127.0.0.1", "Tyler")