from tkinter import *
from tkinter import filedialog
from tkinter import font
import socket
from pathlib import Path
from xml.dom import minidom
import os
#dsdfasdf#sdf

class Window(Frame):
    # Constructor//Globals
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.window()
        self.MainFile = None
        self.SOCK = None
        self.PlanInfo = []
        self.resultX = None

    # window objects
    def window(self):
        self.master.title("Tyler's App")
        self.pack(fill=BOTH, expand=1)

        # SAVE
        saveButton = Button(self, text="Save As", command=self.saveas)
        saveButton.place(x=0, y=50)
        self.lbl = Label(text="File path: ")
        self.lbl.place(x=0, y=0)

        # CONNECTION BUTTON
        self.connection = StringVar()
        self.connection.set("Not Connected")
        self.lbl2 = Label(text=self.connection.get())
        self.lbl2.place(x=245, y=375)
        connectButton = Button(self, text="Connect", command=self.Connect)
        connectButton.place(x=250, y=400)

        # PLAN ID INFO
        getPlanInfo = Button(self, text="Retrieve Verisurf Info", command=self.getPlans)
        getPlanInfo.place(x=0, y=150)

        # Steps
        steps = Label(text="1. Connect \n 2. SaveAs \n 3. Get Verisurf Info")
        steps.place(x=300, y=25)

    # Creates XML file to write Verisurf Responses
    def saveas(self):
        files = [('XML Files', '*.xml')]
        file = filedialog.asksaveasfile(mode='a', filetypes=files, defaultextension=files)
        self.lbl.configure(text="File path: " + file.name)
        fileName = Path(file.name).stem
        fileName = (fileName + ".xml")
        myFile = open(file.name, "w+")
        myFile.write(self.tm)
        self.MainFile = myFile

    # Connects to Verisurf.
    def Connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        port = 33666
        try:
            s.connect((host, port))
            self.SOCK = s
            tm = s.recv(1024)
            self.tm = tm.decode('ascii')
            self.lbl2.configure(text="Connected!")
        except:
            self.lbl2.configure(text="Unable to Connect")

    #testsdfsdf
    # Asks verisurf for plan names. Creates drop down box to select each plan
    def getPlans(self):
        sender = "<Inspect_Plan_List />\n"
        received = self.sendCommand(sender)
        self.writeFiles(received)
        self.Plans = self.ParseXML(received, "plan", "id")

        ##CREATE DROP DOWN##
        var = StringVar()
        var.set("Select Plan")
        menu = OptionMenu(self, var, *self.Plans, command=self.Working)
        menu.config(width=10)
        menu.place(x=0, y=200)

    # Updates plan selection
    def Working(self, planNum):
        self.planDetails(self.Plans.index(planNum))

    # Gets plan details - objects in plan
    def planDetails(self, planNumber):
        send = ("<Inspect_Plan_Load id=\"" + str(planNumber) + "\" />\n")
        self.SOCK.send(send.encode('ascii'))
        temp = self.SOCK.recv(10000)
        send = "<Inspect_Plan_Info id = \"" + str(planNumber) + "\" />\n"
        received = self.sendCommand(send)
        self.writeFiles(received)
        self.parsedList = self.ParseXML(received, "plan_object", "object_id")
        ##CREATE DROP DOWN##
        var = StringVar()
        var.set("Select Object")
        menu = OptionMenu(self, var, *self.parsedList, command=self.ObjectSelect)
        menu.config(width=10)
        menu.place(x=0, y=250)

    # Tkinter function needed to detect when dropdown has changed
    def ObjectSelect(self, num):
        self.objectDetails(self.parsedList.index(num))

    def objectDetails(self, num):
        sender = "<Inspect_Object_Info id=\"" + str(num) + "\" />\n"
        received = self.sendCommand(sender)
        self.writeFiles(received)
        self.objectList = self.ParseXML(received, "property", "none")
        resultsbtn = Button(self, text="Results", command=self.showResults)
        resultsbtn.place(x=0, y=300)
        print(self.objectList)

    def showResults(self):
        self.font = font.Font(self.master, family="Helvetica", size=20, weight="bold")
        self.top = Toplevel(master=None, height=750, width=750, relief="sunken")
        self.top.title("Results")

        self.actual = Label(self.top, text="Act", font=self.font)
        self.actual.grid(row=0, column=1)
        self.meas = Label(self.top, text="Meas", font=self.font)
        self.meas.grid(row=0, column=2)
        self.dev = Label(self.top, text="Dev", font=self.font)
        self.dev.grid(row=0, column=3)

        inTol = "blue"
        outTol = "red"

        rows = 1
        for items in self.objectList:
            nameLabel = Label(self.top, text=items['name'], font=self.font)
            nameLabel.grid(row=rows, column=0, padx=100, pady=20, sticky=W)
            nomLabel = Label(self.top, text="{:.3f}".format(items['nominal']), font=self.font, fg=inTol)
            nomLabel.grid(row=rows, column=1, padx=100, pady=20, sticky=W)
            devLabel = Label(self.top, text="{:.3f}".format(items['deviation']), font=self.font, fg=inTol)
            devLabel.grid(row=rows, column=3, padx=100, pady=20, sticky=W)

            if items['deviation'] > items['tolmax'] or items['deviation'] < items['tolmin']:
                measLabel = Label(self.top, text="{:.3f}".format(items['measured']), font=self.font, fg=outTol)
                measLabel.grid(row=rows, column=2, padx=100, pady=20, sticky=W)
            else:
                measLabel = Label(self.top, text="{:.3f}".format(items['measured']), font=self.font, fg=inTol)
                measLabel.grid(row=rows, column=2, padx=100, pady=20, sticky=W)

            rows += 1

        self.update()
        self.top.bind('<Configure>', self.resize)

    # event that detects when window has changed. Adjusts font size to fit to window
    def resize(self, event):
        size = len(self.objectList) * 13

        self.font['size'] = int(((self.top.winfo_height() + self.top.winfo_width()) / size))

    # Sends commands to Verisurf, returns message
    def sendCommand(self, msg):
        self.SOCK.send(msg.encode('ascii'))
        newmsg = self.SOCK.recv(10000)
        newmsg = self.SOCK.recv(10000)
        newmsg = newmsg.decode('ascii')
        self.MainFile.write(newmsg)
        return (newmsg)

    # Writes Verisurf responses to global file
    def writeFiles(self, st):
        self.MainFile.write(st)

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
        os.remove('temp.xml')
        return list


def runWindow():
    root = Tk()
    root.geometry("600x500")
    for x in range(0, 3):
        root.grid_rowconfigure(x, minsize=800)
        root.grid_columnconfigure(x, minsize=800)
    app = Window(root)
    root.mainloop()
