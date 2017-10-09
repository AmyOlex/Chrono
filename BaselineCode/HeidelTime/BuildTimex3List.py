def find_all(a_str,sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def getList(output):
    str = output
    first = []
    second = []

    first = list(find_all(str,"<TIMEX3 "))
    second = list(find_all(str,"/TIMEX3>"))
    strList = []
    for i in range(len(first)):
        tempStr = str[str.find('<TIMEX3')+1 : str.find('</TIMEX3')]       
        tempStr ="<{0}</TIMEX3>".format(tempStr)
        strList.append(tempStr)
        str = str.split('</TIMEX3',1)[1]               
    
    return strList, first, second


    


