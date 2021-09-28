# GENERAL

This package implements capturing UDP datagrams, parsing,
and saving to mySQL database and/or other storages.
The package is meant to process UDP datagrams that contain data
in a form of serialized dictionaries e.g.:

key1=value1,key2=value2,...

where values should generally be floating point values, but it can 
also be used with arbitrary datagram formats by employing regular
expressions.

# Suported output backend storages:

 * mySQL
 * redis
 * text files
 * MLflow (planned)

# Download

```sh
git clone https://github.com/bslew/RT32netlog.git
```

# Build & Install
```sh
cd RT32netlog
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python3 setup.py build
python3 setup.py install
```


# Configuration

The operation of the package programs relay config files, 
so the package should be configured before usage.



## Config file
The config file is by default sought for in (but can be located anywhere in the system) 

`$HOME/.RT32netlog.ini`

and has the following structure

	# this file should be placed at $HOME and renamed to
	# .RT32netlog.ini

	##############################################################
	##############################################################
	##############################################################
	[EXAMPLE1]
	
	# listen on port
	udp_port = 33051
	# and interface
	udp_ip = 0.0.0.0
	
	# search for the required keys in the incoming UDP datagram
	required_keys = ["T_electric", "H_electric", "P_electric"]
	
	# If the keys are found and values correctly extracted and 
	# if saving to mysql database is requested then
	saveToDB = True
	
	# name of mysql table
	table = electric_cabin
	
	# The datagram keys are mapped to mysql table column names as
	# (these names are also used for redis)
	db_keys = ["T","RH", "P"]
	
	# If output to redis database is also requested then
	saveToRedis = True
	
	# The key names can be prefixed using namespace 
	redisNamespace = electric_cabin
	
	
	# logger prefix (used only in log file)
	logPrefix = 'Electric cabin'
	
	
	##############################################################
	##############################################################
	##############################################################
	#
	# COMMON BLOCKS
	#
	#
	# The names of these blocks are reserved so individual module blocks should
	# not be named after COMMON BLOCKS 
	#
	##############################################################
	##############################################################
	##############################################################
	
	# mysql database block
	[DB]
	host = 127.0.0.1
	port = 3306
	user = kra
	passwd = xxxxxxxxx
	db = kra
	
	##############################################################
	##############################################################
	##############################################################
	# redis database block
	[REDIS]
	host = 127.0.0.1
	port = 6379
	db = 0
	#namespace = 'rt32meteo'
	list_max_elem = 10000

	`
	
Of course the password needs to be set, and file access rights set to 600

`chmod 600 ~/.RT32netlog.ini`


### Other examples
Check [etc/netlog.ini](etc/netlog.ini) for more examples, showing how to save to redis, files,
resend data to other ports or average datagrams on selected time scales,
or even apply regular expressions.


# Initialization
One time databse initialization is needed before saving data to it.
This applies to blocks that use tables that do not yet exist:

```sh
python python/services/save-UDPdata-generic-module.py -m EXAMPLE1 --setup -c examples/RT32netlog.ini
```


# Start server to capture udp datagrams

A generic module suitable for saving any type of UDP datagrams can be used instead
of dedicated programs. For example to run service that will use block
[EXAMPLE1] from the configuration file use

```sh
python python/services/save-UDPdata-generic-module.py -m EXAMPLE1 --serverUDP -c examples/RT32netlog.ini
```

This will start and configure server as defined in the EXAMPLE1 block in the 
configuration file (by default .RT32netlog.ini). The name of the config file 
can be specified on the command line.

See, 
```sh
python python/services/save-UDPdata-generic-module.py --help
```
for details.


# Installation of shipped script examples as system services

The data acquisition daemon can work as a system service controlled via systemctl.
The package is shipped with example scripts
(e.g. save-electric_cabin-data.service) file which should be placed in the correct
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



# AUTHOR
Bartosz Lew [<bartosz.lew@protonmail.pl>](bartosz.lew@protonmail.pl)

