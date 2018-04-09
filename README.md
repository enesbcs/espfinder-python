# espfinder-python
Find ESP8266 modules in the /24 network neighborhood, and collect infos about them. (ESPEasy,Tasmota,ESPurna)

Requirements:
- Linux
- Python3

Install prerequisite libraries:
  sudo apt-get install python3-tk
  
  sudo pip3 install multiprocessing ctypes itertools contextlib

Run GUI:
  python3 espfinder.py

Run plain console:
  python3 espfinder.py -t
