from tkinter import *
import xmlParser
from tkinter import font
from tkinter import ttk
import handleCommand
# ------------------------------------------
# This sets up the display for the DRO
# All functionality exist in this file
# except for resize_top
# the event param would not pass in
# this file for some reason.
# ------------------------------------------

taglist = ['X', 'Y', 'Z', 'PX', 'PY', 'PZ', 'DX', 'DY', 'DZ', 'D3']

def dispDevice(object):
    # get data
    msg = "<Build />\n"
    rmsg = handleCommand.sendCommand(object, msg, True)
    msg = "<Device_Info id=\"1\" />\n"
    rmsg = handleCommand.sendCommand(object, msg, True)

    global taglist
    data = xmlParser.ParseXML(rmsg, "device_info", "none", taglist)
    print(data)
    # set up interface
    object.font1 = font.Font(object.master, family="Helvetica", size=10, weight="bold")
    object.topwin = Toplevel(master=None, relief="sunken")
    for x in range(0, 5):
        object.topwin.grid_rowconfigure(x, weight=1)
        object.topwin.grid_columnconfigure(x, weight=1)

    xpads = 10
    ypads = 10
    widthnum = 5
    items = data[0]
    setup = ["X", "Y", "Z", "3D"]
    rownum=1
    for labels in setup:
        lbl = Label(object.topwin, text=labels, font=object.font1)
        lbl.grid(row=rownum, column=0)
        lbl.grid_configure(sticky="nsew")
        lbl.grid_rowconfigure(0, weight=1)
        lbl.grid_columnconfigure(0, weight=1)
        rownum += 1

    setup = ["Nom", "Meas", "Dev"]
    colnum = 1
    for labels in setup:
        lbl = Label(object.topwin, text=labels, font=object.font1, anchor=E)
        lbl.grid(row=0, column=colnum)
        lbl.grid_configure(sticky="nsew")
        lbl.grid_rowconfigure(0, weight=1)
        lbl.grid_columnconfigure(0, weight=1)
        colnum += 1



    format = ['PX', 'PY', 'PZ', 'X','Y','Z', 'DX', 'DY', 'DZ']
    rownum=1
    colnum=1
    label_list = []
    for names in format:
        if rownum == 4:
            colnum +=1
            rownum=1
        object.newLabel = Label(object.topwin, text="{:.3f}".format(items[names]), font=object.font1, anchor=E, width=widthnum)
        object.newLabel.grid(row=rownum, column=colnum, padx=xpads, pady=ypads, sticky="nsew")
        label_list.append(object.newLabel)
        rownum +=1

    object.dev3D = Label(object.topwin, text="{:.3f}".format(items['D3']), font=object.font1, anchor=E, width=widthnum)
    object.dev3D.grid(row=4, column=3, padx=xpads, pady=ypads, sticky="nsew")
    object.dev3D.grid_columnconfigure(1, weight=1)
    object.dev3D.grid_rowconfigure(0, weight=1)

    object.update()
    object.topwin.bind('<Configure>', object.resize_top)
    print(data)
    placeValues(object, data, format, label_list)
    object.topwin.after(5, lambda: refresh_window(object, format, label_list))



def refresh_window(object, format, label_list):
    msg = "<Device_Info id=\"1\" />\n"
    newmsg = handleCommand.sendCommand(object, msg, True)
    global taglist
    data = xmlParser.ParseXML(newmsg, "device_info", "none", taglist)
    placeValues(object, data, format, label_list)
    object.topwin.after(5, lambda: refresh_window(object, format, label_list))


def placeValues(object, values, format, label_list):
    items = values[0]
    i=0
    for label in label_list:
        label.configure(text="{:.3f}".format(items[format[i]]))
        i +=1

