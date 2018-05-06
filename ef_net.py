#! /usr/bin/env python
#
# Network functions for ESPFinder
#
from subprocess import getoutput
import urllib.request
import json
import re
import os
import itertools
from contextlib import closing
import socket

macesp = [
'18-FE-34',
'24-0A-C4',
'24-B2-DE',
'2C-3A-E8',
'30-AE-A4',
'54-5A-A6',
'5C-CF-7F',
'60-01-94',
'68-C6-3A',
'84-0D-8E',
'84-F3-EB',
'90-97-D5',
'A0-20-A6',
'A4-7B-9D',
'AC-D0-74',
'B4-E6-2D',
'BC-DD-C2',
'CC-50-E3',
'D8-A0-1D',
'DC-4F-22',
'EC-FA-BC']


def parseTable(html):
    #Each "row" of the HTML table will be a list, and the items
    #in that list will be the TD data items.
    ourTable = []

    #We keep these set to NONE when not actively building a
    #row of data or a data item.
    ourTD = None    #Stores one table data item
    ourTR = None    #List to store each of the TD items in.


    #State we keep track of
    inTable = False
    inTR = False
    inTD = False

    #Start looking for a start tag at the beginning!
    tagStart = html.find("<", 0)

    while( tagStart != -1):
        tagEnd = html.find(">", tagStart)

        if tagEnd == -1:    #We are done, return the data!
            return ourTable

        tagText = html[tagStart+1:tagEnd]

        #only look at the text immediately following the <
        tagList = tagText.split()
        tag = tagList[0]
        tag = tag.lower()

        #Watch out for TABLE (start/stop) tags!
        if tag == "table":      #We entered the table!
            inTable = True
        if tag == "/table":     #We exited a table.
            inTable = False

        #Detect/Handle Table Rows (TR's)
        if tag == "tr":
            inTR = True
            ourTR = []      #Started a new Table Row!

        #If we are at the end of a row, add the data we collected
        #so far to the main list of table data.
        if tag == "/tr":
            inTR = False
            ourTable.append(ourTR)
            ourTR = None

        #We are starting a Data item!
        if tag== "td":
            inTD = True
            ourTD = ""      #Start with an empty item!

        #We are ending a data item!
        if tag == "/td":
            inTD = False
            if ourTD != None and ourTR != None:
                cleanedTD = ourTD.strip()   #Remove extra spaces
                ourTR.append( ourTD.strip() )
            ourTD = None


        #Look for the NEXT start tag. Anything between the current
        #end tag and the next Start Tag is potential data!
        tagStart = html.find("<", tagEnd+1)

        #If we are in a Table, and in a Row and also in a TD,
        # Save anything that's not a tag! (between tags)
        #
        #Note that this may happen multiple times if the table
        #data has tags inside of it!
        #e.g. <td>some <b>bold</b> text</td>
        #
        #Because of this, we need to be sure to put a space between each
        #item that may have tags separating them. We remove any extra
        #spaces (above) before we append the ourTD data to the ourTR list.
        if inTable and inTR and inTD:
            ourTD = ourTD + html[tagEnd+1:tagStart] + " "
            #print("td:", ourTD)   #for debugging


    #If we end the while loop looking for the next start tag, we
    #are done, return ourTable of data.
    return(ourTable)


def get_ip():
   print("OS =", os.name, "found.")
   if os.name == "posix":
    f = os.popen('ifconfig')
    for iface in [' '.join(i) for i in iter(lambda: list(itertools.takewhile(lambda l: not l.isspace(),f)), [])]:
        #print('  -> ',iface)
        if re.findall('^(eth|wlan|enp|ens|enx|wlp|wls|wlx)[0-9]',iface) and re.findall('RUNNING',iface):
            ip = re.findall('(?<=inet\saddr:)[0-9\.]+',iface)
            if ip and ip[0]!='127.0.0.1':
                return ip[0]
            else:
                ip = re.findall('(?<=inet\sAdresse:)[0-9\.]+',iface)
                if ip:
                    return ip[0]
   elif os.name == "nt":
    f = getoutput("ipconfig")
    ipconfig = f.split('\n')
    for line in ipconfig:
        if 'IPv4' in line:
            ip = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',line)
            if ip:
                return ip[0]
   return False

def check_port(host, port):
    opened = False
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(2)
        if sock.connect_ex((host, port)) == 0:
            #print("Port ",port," is open")
            opened = True
    return opened

def getMACfromIP(ipaddr):
  resarr = []
  if os.name == "posix": 
   line = getoutput("arp -a %s 2> /dev/null" % ipaddr)
   try:
    mac = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", line).groups()[0]
    resarr.append(mac.strip())
   except:
    resarr.append("")
   strname = line.split(' ')[0]
   resarr.append(strname.strip())
  elif os.name == "nt":
   aout = getoutput("arp -a %s" % ipaddr)
   mstr = ""
   arpout = aout.split('\n')
   for line in arpout:
      if ipaddr in line:
       try:
        mstr = re.search(r"(([a-f\d]{1,2}\-){5}[a-f\d]{1,2})", line).groups()[0]
       except:
        mstr = ""
   resarr.append(mstr.strip()) 
   resarr.append("") 
  return resarr

def check80(purl):
 tipus = "Unknown"
 rescode = 0
 try:
  content = urllib.request.urlopen("http://"+purl, None, 2)
 except:
  rescode = -1
  if check_espurna(purl):
   tipus = "ESPurna"     
 if rescode == 0: 
  try:
   rescode = content.getcode()
  except:
   rescode = -1
  if (rescode == 200):
   tipus2 = content.info()['Server']
   try:
    retdata = content.read()
   except:
    retdata = ""
   if str(retdata).find("Sonoff-Tasmota")>-1:
    tipus = "Tasmota"
   elif str(retdata).find("www.letscontrolit.com")>-1: 
    tipus = "ESPEasy"
   elif str(retdata).find("/cgi-bin/luci")>-1:
    tipus = "OpenWRT"
   elif tipus2 != "" and tipus2 != None:
    tipus = tipus2
  else:
   tipus = "HTTP Err:"+str(rescode)
 return tipus
 
def get_tasmota(purl):
    
#0:IP, 1:MAC, 
#3:FriendlyName, 2:Tasmota FW_Ver + Core_Ver, 4:Uptime, 5:ProgramSize/FlashSize, 6: Heap, 7:RSSI, (%), 8:Vcc
 resarr = ['','','','','','','','','']
 rescode = 0
 try:
  content = urllib.request.urlopen("http://"+purl+"/cm?cmnd=status%209", None, 2)
 except:
  rescode = -1
 if rescode == 0: 
  try:
   rescode = content.getcode()
  except:
   rescode = -1
  if (rescode == 200):
   try:
    retdata = content.read()
   except:
    retdata = ""
   msg2 = retdata.decode('utf-8')
   if ('{' in msg2):
    list = []
    try:
     list = json.loads(msg2)
    except Exception as e:
     print("JSON decode error:",e,"'",msg2,"'")
     list = []
    if (list):
     if list['Status']:
      resarr[3] = str(list['Status']['FriendlyName'])
 rescode = 0
 try:
  content = urllib.request.urlopen("http://"+purl+"/cm?cmnd=status%202", None, 2)
 except:
  rescode = -1
 if rescode == 0: 
  try:
   rescode = content.getcode()
  except:
   rescode = -1
  if (rescode == 200):
   try:   
    retdata = content.read()
   except:
    retdata = ""    
   msg2 = retdata.decode('utf-8')
   if ('{' in msg2):
    list = []
    try:
     list = json.loads(msg2)
    except Exception as e:
     print("JSON decode error:",e,"'",msg2,"'")
     list = []
    if (list):
     if list['StatusFWR']:
      resarr[2] = "Tasmota "+str(list['StatusFWR']['Version']) + " (core " +str(list['StatusFWR']['Core']) + ")"
 rescode = 0
 try:
  content = urllib.request.urlopen("http://"+purl+"/cm?cmnd=status%204", None, 2)
 except:
  rescode = -1
 if rescode == 0: 
  try:
   rescode = content.getcode()
  except:
   rescode = -1
  if (rescode == 200):
   try:
    retdata = content.read()
   except:
    retdata = ""    
   msg2 = retdata.decode('utf-8')
   if ('{' in msg2):
    list = []
    try:
     list = json.loads(msg2)
    except Exception as e:
     print("JSON decode error:",e,"'",msg2,"'")
     list = []
    if (list):
     if list['StatusMEM']:
      resarr[5] = str(list['StatusMEM']['ProgramSize']) + "kB /" + str(list['StatusMEM']['FlashSize'])+" kB"
      resarr[6] = str(list['StatusMEM']['Heap'])+" kB"
 rescode = 0
 try:
  content = urllib.request.urlopen("http://"+purl+"/cm?cmnd=status%2011", None, 2)
 except:
  rescode = -1
 if rescode == 0: 
  try:
   rescode = content.getcode()
  except:
   rescode = -1
  if (rescode == 200):
   try:
    retdata = content.read()
   except:
    retdata = ""    
   msg2 = retdata.decode('utf-8')
   if ('{' in msg2):
    list = []
    try:
     list = json.loads(msg2)
    except Exception as e:
     print("JSON decode error:",e,"'",msg2,"'")
     list = []
    if (list):
     if list['StatusSTS']:
      resarr[4] = str(list['StatusSTS']['Uptime'])
      if len(resarr[4]) < 8:
        resarr[4] += "h"
      resarr[8] = str(list['StatusSTS']['Vcc'])+"V"
      resarr[7] = str(list['StatusSTS']['Wifi']['RSSI'])+"%"
 return resarr

def get_espeasy(purl):
#0:IP, 1:MAC, 
#3:Unit num, 2:ESPEasy build + Git build, 4:Uptime, 6: Free RAM,
#Core_Ver into 2, 5:ProgramSize/FlashSize, 7:RSSI, (%)
 resarr = ['','','','','','','','','']
 rescode = 0
 try:
  content = urllib.request.urlopen("http://"+purl+"/json", None, 2)
 except:
  rescode = -1
 if rescode == 0: 
  try:
   rescode = content.getcode()
  except:
   rescode = -1
  if (rescode == 200):
   try:
    retdata = content.read()
   except:
    retdata = ""
   msg2 = retdata.decode('utf-8')
   if ('{' in msg2):
    list = []
    try:
     list = json.loads(msg2)
    except Exception as e:
     print("JSON decode error:",e,"'",msg2,"'")
     list = []
    if (list):
     if list['System']:
      try:   
       resarr[2] = "ESPEasy "+str(list['System']['Build'])+" "+str(list['System']['Git Build'])
       resarr[3] = str(list['System']['Unit'])
       upmin = int(list['System']['Uptime'])
       resarr[4] = str(round(upmin/60,2))+"h"
       heapfree = list['System']['Free RAM']
       resarr[6] = str(round(heapfree/1024,2))+" kB"
       wifistren = list['WiFi']['RSSI']
       if wifistren != "" or int(wifistren) < 0:
        wifistren = 2 * (int(wifistren) + 100)
        if wifistren > 100:
         wifistren = 100
        resarr[7] = str(wifistren) + "%"

      except:
       pass   
 rescode = 0
 try:
  content = urllib.request.urlopen("http://"+purl+"/sysinfo", None, 2)
 except:
  rescode = -1
 if rescode == 0: 
  try:
   rescode = content.getcode()
  except:
   rescode = -1
  if (rescode == 200):
   try:
    readinfos = str(content.read())
   except:
    readinfos = ""
   readinfos2 = readinfos.replace("<TR><TD>","</TD></TR><TR><TD>") # correct missing html markers
   readinfos2 = readinfos2.replace("</TD></TR></TD></TR><TR><TD>","</TD></TR><TR><TD>")
   readinfos2 = readinfos2.replace("<TD>","</TD><TD>")
   readinfos2 = readinfos2.replace("<TR></TD>","<TR>")
   readinfos2 = readinfos2.replace("</TD></TD><TD>","</TD><TD>")
   readinfos2 = readinfos2.replace("</table>","</TD></TR></TABLE>")   
   dataTable = parseTable(readinfos2)
   for item in dataTable:
    tarr = str(item)
    if (tarr.find("Wifi")>0 and tarr.find("802.")>0) or tarr.find("Wifi RSSI")>0:
        try:
         wifistren = int(re.findall(r'-\d\d',item[1])[0])
        except:
         wifistren = 0
        if wifistren < 0:
         wifistren = 2 * (wifistren + 100)
        if wifistren > 100:
         wifistren = 100
        resarr[7] = str(wifistren) + "%"
    
    if (tarr.find("Build")>0 and ((tarr.find("core")>0) or (tarr.find("Core")>0))) or tarr.find("Build:")>0:
       resarr[2] = "ESPEasy " + item[1]
        
    if tarr.find("Flash Chip Real Size")>0 or tarr.find("Flash Size:")>0:
       resarr[5] = item[1]
            
    if tarr.find("Flash IDE mode")>0:
       resarr[5] += " ("+item[1]+")"

    if tarr.find("Core Version:")>0:
       resarr[2] += " "+item[1]
                
    if tarr.find("Sketch Size")>0:
       resarr[5] = re.findall(r'\d\d\d kB',item[1])[0] + "/" + resarr[5]
        
 return resarr

def check_espurna(purl): # 23 & 80 open
 wildguess = 0
 if check_port(purl, 80):
  try:
   content = urllib.request.urlopen("http://"+purl+"/index.html", None, 2)
  except Exception as e:
   if str(e).find("Error 401:")>0:
    wildguess += 1
 if check_port(purl, 23):
    wildguess += 1
 return (wildguess==2)   

def checkMACManuf(macaddr):
 retstr = ""   
 normmac = str(macaddr).upper().replace(":","-").strip()
 normmac = normmac[:8]
 if normmac in macesp:
  retstr = "Espressif"
 elif normmac == "B8-27-EB":
  retstr = "Raspberry"
 return retstr 
