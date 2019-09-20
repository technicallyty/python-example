from tkinter import filedialog
from tkinter import font
from tkinter import ttk
from tkinter.tix import *
from tkinter.messagebox import showinfo
import socket
import xmlParser
import os
from shutil import copyfile
import DRO
import handleCommand
import threading

# --------------------------
# Main GUI code
# Handles placement of front end objects
# handles resizing events for
# scaling the widgets to their respective window
# handles saving functionalities,
# connecting, and data placement
# --------------------------

# constructor
class Window(Frame):
    # Constructor//Globals
    def __init__(self, master=None):
        Frame.__init__(self, master) # /FRAMES
        self.listboxFrame = Frame(self, width=200, height=400)
        self.listboxFrame.pack(side=LEFT)
        self.dataFrame = Frame(self, width=590, height=400)
        self.dataFrame.pack(pady=125)
        self.msmtFrame = Frame(self, width=100, height=100, relief='groove')
        self.msmtFrame.place(x=600, y=550) # FRAMES\
        self.master = master
        self.window()
        self.myFile = None                              # temp save xml
        self.tempFile = open("xmltempdata.xml", 'w')    # temporary pre-save XML dump
        self.SOCK = None        # socket object. initialized upon connect()
        self.Connected = False  # Sets during connection/disconnection
        self.isSaved = False    # helper bool to see if file has been saved yet
        self.runstate = False   # helps determine if something was measured
        self.measuring = False  # ^
        self.currentObject = [] # list of labels containing the currently placed data
        self.selectedObject = None
        self.objectList = []
        self.current_RRO = []
        self.top = None

    # main window objects
    def window(self):
        self.master.title("Tyler's App")
        self.pack(fill=BOTH, expand=True)

        global machineName
        Label(text=("Machine: " + machineName)).place(x=650)

        # connect button, triggers Connect function
        self.connectButton = Button(self, text="Connect", command=self.connect, height=2, width=10)
        self.connectButton.place(x=340, y=640)

        # menu bar
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu)
        file.add_command(label="Export XML", command=self.saveas)
        file.add_command(label="Quit", command=self.exit_client)
        menu.add_cascade(label="File", menu=file)
        #Button(self, text="test", command= lambda: print(handleCommand.sendCommand(self, "<Object_List />\n"))).place(x=300,y=300)

    def exit_client(self):
        self.master.destroy()

    # Creates XML file to write Verisurf Responses
    def saveas(self):
        fileTypes = [('XML Files', '*.xml')]
        file = filedialog.asksaveasfile(mode='a', filetypes=fileTypes, defaultextension=fileTypes)
        if file == None:
            return
        if self.isSaved == False:
            self.myFile = open(file.name, "w+")
            self.tempFile.close()
            self.myFile.close()
            copyfile('xmltempdata.xml', file.name)
            self.isSaved = True
            # os.remove(self.tempFile)
            self.myFile = open(file.name, "a")
            base = os.path.basename(self.tempFile.name)
            os.remove(base)
        else:
            self.myFile.close()
            tempcopy = open(file.name, "w+")
            tempcopy.close()
            copyfile(self.myFile.name, file.name)
            self.myFile = open(file.name, "a")

    # Connects to Verisurf.
    def connect(self):
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
                handleCommand.writeFiles(self, self.tm)
                self.Connected = True
                self.connectButton.configure(text="Disconnect")
                self.layOut()
            else:
                self.Connected = False
                self.SOCK.close()
                self.connectButton.configure(text="Connect")
                for widget in self.listboxFrame.winfo_children():
                    widget.destroy()
                for widget in self.dataFrame.winfo_children():
                    widget.destroy()
        except ConnectionError:
            self.Connected = False

    def layOut(self):
        self.getPlans()
        self.objType = StringVar()
        self.msmtFrameLayout()
        Button(self, text="DRO", command=lambda: DRO.dispDevice(self)).place(x=50, y=575)

        t2 = threading.Thread(target=self.checkMeasure)
        self.dataFrame.after(0, t2.start())
        self.img = PhotoImage(file="sizeicon.png")

        resultsbtn = Button(self, command=self.showResults, image=self.img, height=20, width=20)
        resultsbtn.image = self.img
        resultsbtn.place(x=5, y=580)
        resultsTip = Balloon()
        resultsTip.bind_widget(resultsbtn, balloonmsg="Expand Results")


    def msmtFrameLayout(self):
        menu = ttk.Combobox(self.msmtFrame, values=['Point', 'Line', 'Circle', 'Ellipse',
                                                    'Slot', 'Plane', 'Sphere', 'Cylinder', 'Spline',
                                                    'Cone'],
                            textvariable=self.objType)
        menu.pack()
        menu.current(0)
        menu.bind("<<ComboboxSelected>>", self.selection)

        modes = [("Single Point", "0"), ("Continuous", "1"), ("Average Point", "2")]
        ptMode = handleCommand.sendCommand(self, "<Measure_Get_Point_Mode />\n", True)
        nolist = []
        ptMode = xmlParser.ParseXML(ptMode, "data", "data", nolist)
        self.v = StringVar()
        self.v.set(ptMode[0])

        for text, mode in modes:
            b = Radiobutton(self.msmtFrame, text=text, variable=self.v, value=mode, justify=LEFT, command=self.ptMode, indicatoron=0)
            b.pack(anchor=W)

        msmtBtn = Button(self.msmtFrame, text="Measure",
                         command=lambda: handleCommand.sendCommand(self, "<Measure_Trigger />\n", True), height=1, width=15)

        msmtBtn.pack()

    def ptMode(self):
        modes = ["<Measure_Set_Single />\n", "<Measure_Set_Cloud />\n", "<Measure_Set_Average />\n"]
        handleCommand.sendCommand(self, modes[int(self.v.get())], True)


    def selection(self, event):
        handleCommand.sendCommand(self, "<Measure_" + self.objType.get() + " />\n", True)



    def resize_top(self, event):
        size = self.topwin.winfo_height()
        self.font1['size'] = int(size / 20)

    # Asks verisurf for plan names. Creates drop down box to select each plan
    def getPlans(self):
        Label(text="Active Plan").place(x=0, y=50)
        sender = "<Inspect_Plan_List />\n"
        received = handleCommand.sendCommand(self, sender, True)
        try:
            self.Plans = xmlParser.ParseXML(received, "plan", "id", None)
        except:
            self.Plans = ['No Plans']

        # CREATE DROP DOWN
        self.selected = StringVar()
        menu = ttk.Combobox(self, values=[*self.Plans], textvariable=self.selected)
        menu.current(0)
        menu.place(x=0, y=80)
        menu.bind("<<ComboboxSelected>>", self.userSelection)
        self.planDetails(0)

    # Required tkinter function to detect selection
    def userSelection(self, event):
        for widget in self.listboxFrame.winfo_children():
            widget.destroy()
        for widget in self.dataFrame.winfo_children():
            widget.destroy()
        self.planDetails(self.Plans.index(self.selected.get()))

    # Gets plan details - objects in plan
    def planDetails(self, planNumber):
        try:
            send = "<Inspect_Plan_Load id=\"" + str(planNumber) + "\" />\n"
            received = handleCommand.sendCommand(self, send, True)
            send = "<Inspect_Plan_Info id = \"" + str(planNumber) + "\" />\n"
            received = handleCommand.sendCommand(self, send, True)
            self.parsedList = xmlParser.ParseXML(received, "plan_object", "object_id", None)

            # CREATE DROP DOWN

            self.listboxFrame.scrollbar = Scrollbar(self.listboxFrame, orient="vertical")
            self.listboxFrame.scrollbar.pack(side=RIGHT, fill=Y)

            self.listboxFrame.objects = Listbox(self.listboxFrame, height=20)
            self.listboxFrame.objects.pack(side=LEFT, expand=True, fill=Y)
            self.listboxFrame.objects.config(yscrollcommand=self.listboxFrame.scrollbar.set)
            self.listboxFrame.objects.bind("<<ListboxSelect>>", self.ObjectSelect)
            self.listboxFrame.scrollbar.config(command=self.listboxFrame.objects.yview)

            x = 1
            for items in self.parsedList:
                self.listboxFrame.objects.insert(END, items)
                x += 1
            ranger = len(self.parsedList)
            isOOT = self.checkOOT(ranger)
            x = 0
            for i in isOOT:
                if i == True:
                    self.listboxFrame.objects.itemconfig(x, bg="red")
                elif i == None:
                    self.listboxFrame.objects.itemconfig(x, bg="white")
                else:
                    self.listboxFrame.objects.itemconfig(x, bg="green")
                x += 1
        except:
            showinfo("No data", "Selected plan has no objects.")




    def checkOOT(self, num):
        indexOOT = []
        for i in range(0, num):
            isOOT = False
            sender = "<Inspect_Object_Info id=\"" + str(i) + "\" />\n"
            received = handleCommand.sendCommand(self, sender, False)
            taglist = ["name", "nominal", "measured", "deviation", "tolmin", "tolmax"]
            list = xmlParser.ParseXML(received, "property", "none", taglist)
            for items in list:
                if items['measured'] == 0:
                    isOOT = None
                    break
                elif items['deviation'] > items['tolmax'] or items['deviation'] < items['tolmin']:
                    isOOT = True
                    break
            indexOOT.insert(i, isOOT)
        return indexOOT

    # Tkinter function needed to detect when dropdown has changed
    def ObjectSelect(self, event):
        for widget in self.dataFrame.winfo_children():
            widget.destroy()
        widget = event.widget
        selection = widget.curselection()
        self.selectedObject = widget.get(selection)
        self.objectDetails(self.parsedList.index(self.selectedObject))

    def objectDetails(self, num):
        sender = "<Inspect_Object_Info id=\"" + str(num) + "\" />\n"
        received = handleCommand.sendCommand(self, sender, False)
        taglist = ["name", "nominal", "measured", "deviation", "tolmin", "tolmax"]
        self.objectList = xmlParser.ParseXML(received, "property", "none", taglist)
        self.placeResults(num)

    def checkMeasure(self):
        if self.Connected == True:
            planid = str(self.Plans.index(self.selected.get()))
            send = "<Inspect_Plan_Info id=\"" + planid + "\"/>\n"
            receive = handleCommand.sendCommand(self, send, False)
            if "run_state=\"1\"" in receive:
                self.runstate = True
                self.measuring = True
            else:
                self.runstate = False
                if self.measuring == True:
                    t1 = threading.Thread(target=self.refresh_dataFrame)
                    t1.start()
            self.dataFrame.after(1000, self.checkMeasure)

    def refresh_dataFrame(self):
        self.measuring = False
        send = "<Object_List />\n"
        rec = handleCommand.sendCommand(self, send, True)
        names = []
        objinfo = xmlParser.ParseXML(rec, "object", "object", names)
        for widget in self.dataFrame.winfo_children():
            widget.destroy()
        objectIndex = self.parsedList.index(objinfo[-1])
        self.objectDetails(objectIndex)
        if self.isOOT == True:
            self.listboxFrame.objects.itemconfig(objectIndex, bg="red")
        else:
            self.listboxFrame.objects.itemconfig(objectIndex, bg="green")

        self.listboxFrame.objects.selection_clear(0, END)
        self.listboxFrame.objects.selection_set(objectIndex)
        self.listboxFrame.objects.activate(objectIndex)

        try:
            if self.top.winfo_exists():
                if objinfo[-1] != objinfo[-2]:
                    for widget in self.top.winfo_children():
                        widget.destroy()
                    self.showResults()
                else:
                    self.update_rro()
        except AttributeError:
            #do nothing, no window
            None

    def update_rro(self):
        i = 0
        j = 1
        item = 0
        while item != len(self.objectList):
            meas = self.current_RRO[i]
            dev = self.current_RRO[j]
            obj = self.objectList[item]

            meas.configure(text="{:.3f}".format(obj['measured']))
            dev.configure(text="{:.3f}".format(obj['deviation']))

            i += 2
            j += 2
            item += 1



    def placeResults(self, num):

        frameName = self.dataFrame
        xpad = 40
        ypad = 5
        fontsize = 10


        self.font1 = font.Font(self.master, family="Helvetica", size=fontsize, weight="bold")
        name = Label(frameName, text=self.parsedList[num], font=self.font1)
        name.grid(row=0,column=0, padx=xpad, sticky=W)
        actual = Label(frameName, text="Nom", font=self.font1)
        actual.grid(row=0, column=1, padx=xpad)
        meas = Label(frameName, text="Meas", font=self.font1)
        meas.grid(row=0, column=2, padx=xpad)
        dev = Label(frameName, text="Dev", font=self.font1)
        dev.grid(row=0, column=3, padx=xpad)

        inTol = "green"
        outTol = "red"
        self.isOOT = False
        rows = 1
        # generates values to display
        labels={}
        for items in self.objectList:
            nameLabel = Label(frameName, text=items['name'], font=self.font1)
            nameLabel.grid(row=rows, column=0, padx=xpad, pady=ypad, sticky=W)
            nomLabel = Label(frameName, text="{:.3f}".format(items['nominal']), font=self.font1, fg=inTol)
            nomLabel.grid(row=rows, column=1, padx=xpad, pady=ypad, sticky=W)
            devLabel = Label(frameName, text="{:.3f}".format(items['deviation']), font=self.font1, fg=inTol)
            devLabel.grid(row=rows, column=3, padx=xpad, pady=ypad, sticky=W)

            # Logic to determine if OOT. changes to red if so
            if items['deviation'] > items['tolmax'] or items['deviation'] < items['tolmin']:
                measLabel = Label(frameName, text="{:.3f}".format(items['measured']), font=self.font1,
                                            fg=outTol)
                self.isOOT = True
            else:
                measLabel = Label(frameName, text="{:.3f}".format(items['measured']), font=self.font1,
                                            fg=inTol)
            measLabel.grid(row=rows, column=2, padx=xpad, pady=ypad, sticky=W)

            labelList=[]
            labelList.append(measLabel)
            labelList.append(devLabel)
            labels.update({items['name']: labelList})
            rows += 1
        self.currentObject = labels


    def showResults(self):
        self.font = font.Font(self.master, family="Helvetica", size=20, weight="bold")
        if self.top == None or self.top.winfo_exists() == False:
            self.top = Toplevel(master=None, height=750, width=750, relief="sunken")
            self.top.title("Report Read-Out")

        for x in range(0, len(self.objectList)):
            self.top.grid_rowconfigure(x, weight=1)
            self.top.grid_columnconfigure(x, weight=1)
        # Default headers for information
        actual = Label(self.top, text="Nom", font=self.font)
        actual.grid(row=0, column=1, padx=100, sticky=W)
        meas = Label(self.top, text="Meas", font=self.font)
        meas.grid(row=0, column=2, padx=100, sticky=W)
        dev = Label(self.top, text="Dev", font=self.font)
        dev.grid(row=0, column=3, padx=100, sticky=W)

        inTol = "green"
        outTol = "red"

        rows = 1
        # generates values to display
        label_list=[]
        for items in self.objectList:
            nameLabel = Label(self.top, text=items['name'], font=self.font)
            nameLabel.grid(row=rows, column=0, padx=40, pady=20, sticky=W)
            nomLabel = Label(self.top, text="{:.3f}".format(items['nominal']), font=self.font, fg=inTol)
            nomLabel.grid(row=rows, column=1, padx=100, pady=20, sticky=W)
            devLabel = Label(self.top, text="{:.3f}".format(items['deviation']), font=self.font, fg=inTol)
            devLabel.grid(row=rows, column=3, padx=100, pady=20, sticky=W)

            # Logic to determine if OOT. changes to red if so
            if items['deviation'] > items['tolmax'] or items['deviation'] < items['tolmin']:
                measLabel = Label(self.top, text="{:.3f}".format(items['measured']), font=self.font, fg=outTol)
            else:
                measLabel = Label(self.top, text="{:.3f}".format(items['measured']), font=self.font, fg=inTol)
            measLabel.grid(row=rows, column=2, padx=100, pady=20, sticky=W)
            rows += 1
            label_list.append(measLabel)
            label_list.append(devLabel)

        self.current_RRO = label_list

        self.update()
        self.top.bind('<Configure>', self.resize)

    # handles window resizing event. adjusts font size accordingly.
    def resize(self, event):
        try:
            size = len(self.objectList) * 14
            if size == 0:
                size = 30
            self.font['size'] = int(((self.top.winfo_height() + self.top.winfo_width()) / size))
        except TclError:
            # do nothing
            None


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
