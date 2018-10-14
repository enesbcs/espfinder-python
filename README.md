# espfinder-python
Find ESP8266 modules in the /24 network neighborhood, and collect infos about them. (ESPEasy,Tasmota,ESPurna,Tuya,Shelly)

Requirements:
- Linux
- Python3

Install prerequisite libraries (Debian/Ubuntu):
  sudo apt-get install python3-tk

(*)Debian Stretch specific prerequisite: (ifconfig required)
  suto apt-get install net-tools

Install prerequisite libraries (Arch):
  sudo pacman -S tk  

Run GUI:
  python3 espfinder.py

Run plain console:
  python3 espfinder.py -t

Update:

0.4
- (enesbcs) added Tuya and Shelly detection support

0.3
- (bollitec) german language linux (ifconfig) support + some extended progress informations
- (enesbcs) Arch linux ifconfig output support

0.2
- (enesbcs) warning when ifconfig output can not be parsed + introduced some windows ipconfig support, but multiprocessing on windows seems slow as hell

0.1
First version
