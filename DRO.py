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

def dispDevice(object):
    # get data
    msg = "<Build />\n"
    rmsg = handleCommand.sendCommand(object, msg)
    msg = "<Device_Info id=\"1\" />\n"
    rmsg = handleCommand.sendCommand(object, msg)

    taglist = ['X', 'Y', 'Z', 'PX', 'PY', 'PZ', 'DX', 'DY', 'DZ']
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

    setup = ["Act", "Meas", "Dev"]
    colnum = 1
    for labels in setup:
        lbl = Label(object.topwin, text=labels, font=object.font1, anchor=E)
        lbl.grid(row=0, column=colnum)
        lbl.grid_configure(sticky="nsew")
        lbl.grid_rowconfigure(0, weight=1)
        lbl.grid_columnconfigure(0, weight=1)
        colnum += 1

    object.xAct = Label(object.topwin, text="{:.3f}".format(items['PX']), font=object.font1, anchor=E, width=10)
    object.xAct.grid(row=1, column=1, padx=xpads, pady=ypads, sticky="nsew")
    object.xAct.grid_columnconfigure(1, weight=1)
    object.xAct.grid_rowconfigure(0, weight=1)

    object.yAct = Label(object.topwin, text="{:.3f}".format(items['PY']), font=object.font1, anchor=E, width=10)
    object.yAct.grid(row=2, column=1, padx=xpads, pady=ypads, sticky="nsew")
    object.yAct.grid_columnconfigure(1, weight=1)
    object.yAct.grid_rowconfigure(0, weight=1)

    object.zAct = Label(object.topwin, text="{:.3f}".format(items['PZ']), font=object.font1, anchor=E, width=10)
    object.zAct.grid(row=3, column=1, padx=xpads, pady=ypads, sticky="nsew")
    object.zAct.grid_columnconfigure(1, weight=1)
    object.zAct.grid_rowconfigure(0, weight=1)

    object.xDev = Label(object.topwin, text="{:.3f}".format(items['DX']), font=object.font1, anchor=E, width=10)
    object.xDev.grid(row=1, column=3, padx=xpads, pady=ypads, sticky="nsew")
    object.xDev.grid_columnconfigure(1, weight=1)
    object.xDev.grid_rowconfigure(0, weight=1)

    object.yDev = Label(object.topwin, text="{:.3f}".format(items['DY']), font=object.font1, anchor=E, width=10)
    object.yDev.grid(row=2, column=3, padx=xpads, pady=ypads, sticky="nsew")
    object.yDev.grid_columnconfigure(1, weight=1)
    object.yDev.grid_rowconfigure(0, weight=1)

    object.zDev = Label(object.topwin, text="{:.3f}".format(items['DZ']), font=object.font1, anchor=E, width=10)
    object.zDev.grid(row=3, column=3, padx=xpads, pady=ypads, sticky="nsew")
    object.zDev.grid_columnconfigure(1, weight=1)
    object.zDev.grid_rowconfigure(0, weight=1)


    object.xlbl = Label(object.topwin, text="{:.3f}".format(items['X']), font=object.font1, anchor=E, width=10)
    object.xlbl.grid(row=1, column=2, padx=xpads, pady=ypads, sticky="nsew")
    object.xlbl.grid_columnconfigure(1, weight=1)
    object.xlbl.grid_rowconfigure(0, weight=1)

    object.ylbl = Label(object.topwin, text="{:.3f}".format(items['Y']), font=object.font1, anchor=E, width=10)
    object.ylbl.grid(row=2, column=2, padx=xpads, pady=ypads, sticky="nsew")
    object.ylbl.grid_columnconfigure(1, weight=1)
    object.ylbl.grid_rowconfigure(0, weight=1)

    object.zlbl = Label(object.topwin, text="{:.3f}".format(items['Z']), font=object.font1, anchor=E, width=10)
    object.zlbl.grid(row=3, column=2, padx=xpads, pady=ypads, sticky="nsew")
    object.zlbl.grid_columnconfigure(1, weight=1)
    object.zlbl.grid_rowconfigure(0, weight=1)



    object.update()
    object.topwin.bind('<Configure>', object.resize_top)
    print(data)
    placeValues(object, data)
    object.topwin.after(5, lambda: refresh_window(object))



def refresh_window(object):
    msg = "<Device_Info id=\"1\" />\n"
    newmsg = handleCommand.sendCommand(object, msg)
    taglist = ['X', 'Y', 'Z', 'PX', 'PY', 'PZ', 'DX', 'DY', 'DZ']
    data = xmlParser.ParseXML(newmsg, "device_info", "none", taglist)
    placeValues(object, data)
    object.topwin.after(5, lambda: refresh_window(object))


def placeValues(object, values):
    items = values[0]
    object.xlbl.configure(text="{:.3f}".format(items['X']))
    object.ylbl.configure(text="{:.3f}".format(items['Y']))
    object.zlbl.configure(text="{:.3f}".format(items['Z']))
    object.xAct.configure(text="{:.3f}".format(items['PX']))
    object.yAct.configure(text="{:.3f}".format(items['PY']))
    object.zAct.configure(text="{:.3f}".format(items['PZ']))
    object.xDev.configure(text="{:.3f}".format(items['DX']))
    object.yDev.configure(text="{:.3f}".format(items['DY']))
    object.zDev.configure(text="{:.3f}".format(items['DZ']))
