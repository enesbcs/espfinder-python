Be a patron at [Patreon](https://www.patreon.com/enesbcs)

# espfinder-python
Find ESP8266 modules in the /24 network neighborhood, and collect infos about them. (ESPEasy, Tasmota, ESPurna, Tuya,Shelly, RPIEasy)

## Installation

Requirements:
- Linux
- Python3

Install prerequisite libraries (Debian/Ubuntu):
```sh
sudo apt-get install python3-tk
```

(*)Debian Stretch specific prerequisite: (ifconfig required)
```sh
sudo apt-get install net-tools
```

Install prerequisite libraries (Arch):
```sh
sudo pacman -S tk
```



## Usage

Run GUI:
```sh
python3 espfinder.py
```

Run plain console:
```sh
python3 espfinder.py -t
```


## Release notes

0.5
- (enesbcs) added RPIEasy detection support

0.4
- (enesbcs) added Tuya and Shelly detection support

0.3
- (bollitec) german language linux (ifconfig) support + some extended progress informations
- (enesbcs) Arch linux ifconfig output support

0.2
- (enesbcs) warning when ifconfig output can not be parsed + introduced some windows ipconfig support, but multiprocessing on windows seems slow as hell

0.1
First version
