#! /usr/bin/env python
#
# Pings for active host on *this* sub network.
# The current sub network address and
# the host numbers 1-254 will be pinged
#

from subprocess import getoutput
from multiprocessing import Process, Array
from sys import exit, argv
import ctypes
import time
import signal
from ef_net import *
import tkinter# sudo apt-get install python3-tk 
from tkinter import ttk

PROG_NAME= "ESP Finder"
PROG_VER="0.1b"

# ---------- MULTIPROCESSING PART

shared_array = Array(ctypes.c_ubyte,255)  # multiprocessing ping results

class PING_SWEEP(object):

  def __init__(self,callback,ownip):
    self.callback = callback
    self.ownip = ownip
    self.ping_sweeper.__init__(self)
    self.ping_sweeper()

  def pinger(self, host_num, resarray):
    """thread pinger function"""
    hostadrr = self.ownip.split('.')[:-1]
    hostadrr = '.'.join(hostadrr) + '.' + repr(host_num)
    try:
     line = getoutput("ping -n -c 1 -W 0.2 %s 2> /dev/null" % hostadrr)
    except:
     line = ""
     exit(0)
#    self.callback(1,0)
    if line.find(hostadrr) and line.find("bytes from") > -1:  # Host Active
#        self.callback(0,hostadrr)
        resarray[host_num] = host_num
    else:
        exit(0)

  def ping_sweeper(self):
    global shared_array
    self.maxnum = 255
    procarr = []
    for host_num in range(1, self.maxnum):
      ping = Process(target=self.pinger, args=(host_num,shared_array))
      ping.start()
      procarr.append(ping.pid)
    time.sleep(3)
    for process in procarr: # Cleanup
     try:
      os.kill(process,signal.SIGTERM)
     except:
      pass 

#  def __del__(self):
#   self.callback(2,0) 

def cb_stationsearch(func, par1):
 global ownip, scanlist, UseGUI, progress1
 if (func == 0) or (func == 1):
  if UseGUI:
   progress1.step()
 elif (func == 2):
  if UseGUI:
   progress1["value"] = 254


def pingscan():
 global shared_array, ownip
 shared_array = Array(ctypes.c_ubyte,255)  # multiprocessing ping results
 PING_SWEEP(cb_stationsearch,ownip)

def analyzerange():
 global shared_array, ownip, UseGUI, tree
 hostaddr = ownip.split('.')[:-1]

 if UseGUI:
  for i in tree.get_children(): # clear tree
    tree.delete(i)

 for i in range(1,255):
  if shared_array[i] > 0:
   hostadr = '.'.join(hostaddr) + '.' + repr(shared_array[i])
   if (hostadr == ownip):
    tline = "THIS DEVICE"
    if UseGUI==False:
     print(hostadr.ljust(14)+tline)
    else:
     tree.insert("","end",text=hostadr, values=(tline))   
   else:
    analyzeip(hostadr)

def analyzeip(par1):
  global UseGUI, tree    
  # 0:mac,1:netname,2:mactype, 3: ptype
  attribs = ["","","",""]
  
  infoarr = getMACfromIP(par1)
  if (infoarr[0] != ""):
    attribs[0] = str(infoarr[0])
    attribs[1] = str(infoarr[1])
    attribs[2] = checkMACManuf(infoarr[0])          
  if (check_port(par1,80)):
    attribs[3] = check80(par1)
  if (str(attribs[2]) != str("Espressif")) and (str(attribs[3]) == str("ESPurna")):
    attribs[3] = "" # its only a wild guess, delete if surely not!
  tline = attribs[0] + ", "+ attribs[1] + ", "+ attribs[2] +" "+ attribs[3]
  if UseGUI==False:
   print(par1.ljust(14) + tline)
  else:
   tpid= tree.insert("","end",text=par1.ljust(14),values=(tline))
  if attribs[3] == "Tasmota":
   tinfos = get_tasmota(par1)
   tline = tinfos[2] + ", " + tinfos[3] + ", "+ tinfos[4] +", "+ tinfos[5] +", "+ tinfos[6]+", "+ tinfos[7]+", "+ tinfos[8]
   if UseGUI==False:
    print(" -"+tline)
   else:
    tree.insert(tpid,"end",values=(tinfos[2],tinfos[3],tinfos[4],tinfos[5],tinfos[6],tinfos[7],tinfos[8]))
  elif attribs[3] == "ESPEasy":
   tinfos = get_espeasy(par1)
   tline = tinfos[2] + ", " + tinfos[3] + ", "+ tinfos[4] +", "+ tinfos[5] +", "+ tinfos[6]+", "+ tinfos[7]
   if UseGUI==False:       
    print(" -"+tline)     
   else:
    tree.insert(tpid,"end",values=(tinfos[2],tinfos[3],tinfos[4],tinfos[5],tinfos[6],tinfos[7]))

def searchdevices():
  global UseGUI, progress1    
  if UseGUI==False:
   print("Starting pingscan...")
  pingscan()
  if UseGUI==False:
   print("Analyzing online targets...")
  analyzerange()

UseGUI = True
  
if __name__ == '__main__':

  if len(argv)>1:
   if argv[1] == '-t':
    UseGUI = False   
  
  if UseGUI:
   window = tkinter.Tk()
   window.title(PROG_NAME)
   window.geometry('1000x700')
   
  ownip = get_ip()
  if UseGUI:
 
   tree = ttk.Treeview(window)

   tree["columns"]=("A","B","C","D","E","F","G")
   tree.column("A", width=250)
   tree.column("B", width=150)
   tree.column("C", width=100)
   tree.column("D", width=120)
   tree.column("E", width=105)
   tree.column("F", width=38)
   tree.column("G", width=50)
   tree.heading("A", text="Version")
   tree.heading("B", text="Unit num/name")
   tree.heading("C", text="Uptime")
   tree.heading("D", text="Prog/Flash size")
   tree.heading("E", text="Free RAM")
   tree.heading("F", text="Wifi")
   tree.heading("G", text="Vcc")

   tree.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP)

   refreshbutton = ttk.Button(window, text='Refresh', command=searchdevices)
   refreshbutton.pack()
   refreshbutton.focus_set()

   #draw the window, and start the 'application'
   window.mainloop()      
      
  else:
   searchdevices()
   
