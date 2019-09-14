from xml.dom import minidom

# -------------------------------------------------
# Handles the parsing of XML strings
# Data = string of XML
# tagname = where to start looking.
# id = what to look for inside the tagname
# if have multiple things to look for within tagname
# pass as string 'none'
# pass list of id's to look for in names.
# --------------------------------------------------


def ParseXML(data, tagname, id, names):
    mydoc = minidom.parseString(data)
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
            # list of properties to extract from object
            for x in names:
                if len(items.getAttribute(x)) == 0:
                    dict.update({x: 0.0})
                else:
                    try:
                        dict.update({x: float(items.getAttribute(x))})
                    except:
                        dict.update({x:items.getAttribute(x)})
            list.append(dict)

    return list
