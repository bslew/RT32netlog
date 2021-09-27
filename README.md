# GENERAL

This package implements capturing UDP datagrams and saving to
mySQL database and/or other storages.

# Suported storages:

 * mySQL
 * redis
 * files


# DOWNLOAD

```sh
git clone https://github.com/bslew/RT32netlog.git
```

# BUILD
```sh
python3 setup.py build
```

# INSTALL

## Installation general

```sh
sudo python3 setup.py install
```


To install without sources

```sh
python3 setup.py bdist_egg --exclude-source-files
```

```sh
sudo python3 setup.py install
```

The data acquisition daemon can work as a system service controlled via systemctl.
The package is shipped with save-electric_cabin-data.service file which should be placed in the correct
directory depending on the system. For ubuntu it should be 
/etc/systemd/system/save-electric_cabin-data.service and the soft link to this file should be in
/etc/systemd/system/multi-user.target.wants/save-electric_cabin-data.service.


###### To install all services run provided `install_service_ubuntu.sh` script or run 

`sudo ./install_services_ubuntu.sh`

###### To install a service manually run

`cp WS800UMB/save-electric_cabin-data.service /lib/systemd/`

and

`systemctl enable save-electric_cabin-data`

Now you can use:

`systemctl start/stop/restart/status save-electric_cabin-data`



## Installation on galaxy (install UDP datagram reader)

On galaxy we need a service to capture the UDP datagrams and store them to mySQL 
database.

	* Follow download, build and install general
	* Add meteo user
	* Initialize (see below)
	* Add enable the service (see below)
	* To install as a service

`cp RT32netlog/save-electric_cabin-data.service /lib/systemd/`

and

`systemctl enable save-electric_cabin-data`




#Configuration

The packages uses config files, so before usage the program should be configured.


## Config file
The config file is located in 

`$HOME/.RT32netlog.ini`

and has the following structure

	`
	#
	# each section describes one network service 
	#
	
	
	[ELECTRIC_CABIN_DATA]
	# required options
	udp_port = 33051
	udp_ip = 192.168.1.255
	required_keys = ["T_electric", "RH_electric"]
	db_keys = ["T","RH"]
	table = electric_cabin
	# optional options
	saveToDB = True
	
	[FOCUS_CABIN_DATA]
	# required options
	udp_port = 33060
	udp_ip = 192.168.1.255
	required_keys = ["T_focB", "P_focB", "RH_focB"]
	db_keys = ["T","P","RH"]
	table = focus_cabin
	# optional options
	saveToDB = True

	# 
	# Common section for all services.
	# section that describes the location and access to mySQL database
	#
	[DB]
	# required options
	host = 192.168.1.8
	port = 3306
	user = kra
	passwd = password
	db = kra`
	
Of course the password needs to be set, and file access rights set to 600

`chmod 600 ~/.RT32netlog.ini`

## Initialization
One time databse initialization is needed for each service:

`save-electric_cabin-data.py --setup`

`save-focus-box-meteo.py --setup`


#Use

	* To run as a daemon use e.g.

`save-electric_cabin-data.py --serverUDP`

or use

`systemctl start save-electric_cabin-data`


This script makes sure that the data collecting program called 

`/usr/local/bin/save-electric_cabin-data.py`

is up and running.

## More generally

A generic module suitable for saving any type of UDP datagrams can be used instead
of dedicated programs. For example to run service that will use block
[my_block] from the configuration file use

```sh
python python/services/save-UDPdata-generic-module.py -m my_block --serverUDP
```

This will start and configure server as defined in the my_block block in the 
configuration file (by default .RT32netlog.ini). The name of the config file 
can be specified on the command line.

See, 
```sh
python python/services/save-UDPdata-generic-module.py --help
```
for details.


# MISSING DATA AND ANOMALY DETECTION

TBD


#AUTHOR
Bartosz Lew [<bartosz.lew@protonmail.pl>](bartosz.lew@protonmail.pl)

