import socket


# ---------------------------
# Handles sending and receiving commands.
# Requires self, and the message.
# Writes the responses to XML file as they
# are received.
# Returns the string.
# -----------------------------

def sendCommand(object, msg):
    object.SOCK.send(msg.encode('ascii'))
    newmsg = object.SOCK.recv(10000)
    if "acknowledgement" in (newmsg.decode('ascii')):
        newmsg = object.SOCK.recv(10000)
        newmsg = newmsg.decode('ascii')
    else:
        newmsg = newmsg.decode('ascii')

    writeFiles(object, newmsg)
    return newmsg



def writeFiles(object, msg):
    try:
        object.myFile.write(msg)
    except:
        object.tempFile.write(msg)
    return

