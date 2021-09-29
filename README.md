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

# Use Examples
## Example 1 - data averaging and forwarding

Suppose the incoming datagrams have format:
```sh
2021 9 28 10 31 41 888523 2000.000 2459485.938679 271 44139.483510 -24.9975 0.0007 183.9150 53.0948 0 1 -0.0100 0.0100 0.0000 0.0000 -0 -0 -0 0 70 0 0 0 0 0 0 -25.0000 0.0000 344.2920 62.1476 13415
```
and arrive several times per second.
We wish to extract julian day (the 9'th word), ammed it with
apropriate key - "JD" and average the incoming UDP stream
in timescales of 2 seconds and redistribute it to another port.
This can be done using the following configuration block:

```sh
.netlog.ini file
# Datagram average and forward example
[TEST_FWD]
# listen on port
udp_port = 3493
# and interface
udp_ip = 192.168.1.255

# First let's pre-process the input datagram using regular expressions.
# We use input_resub option which should specify a list of lists of length
# two. The first element should specify regular expression for 
# the pattern to be sought in the input datagram string and 
# the second element should specify regex for its replacement.
# Escape characters '\' should be used for back-references e.g. \1
input_resub=[ ["^(?:\\S+ ){8}(\\S+).*", "JD=\\1"] ]

# After pre-processing the incoming UDP datagram, 
# search for the required keys
required_keys = ["JD"]

# Define how these keys should be mapped - i.e. specify their
# target names
# (these names are also used for mySQL and redis if used)
db_keys = ["JD"]

# If output to redis database is also requested then uncomment
#saveToRedis = True

# Finally, perform 2-s averaging of the preprocessed input and 
# resubmit the input to a different host and port
averaging_interval=2
resend_output_to_host=127.0.0.1
resend_output_to_port=10000


# The output datagram sent to port 10000 will look something 
# like this:
#
# JD=2459485.962054424,dt=2021-09-28 11:05:21.717967,
# 
# and will be emitted roughly every two seconds as requested.
# Each datagram of the package is ammended with additional
# dt key that contains UTC date and time of the UDP datagram
# arrival (or as in this case the mean date and time calculated
# over dates and times of all datagrams that came within the 
# averaging time scale (here 2 seconds).


```

In order to use this configuration we need to run:

```sh
python3 python/services/save-UDPdata-generic-module.py -m TEST_FWD --serverUDP -c path/to/configuration/file.ini
```

## Example 2 - regular expressions
We assume the same input datagrams format as in example 1.
This time we are interested in two values in the datagrams:
the one on position 11 and 12 counting from 0.

```sh
.netlog.ini file
[TEST_RTAZ]

# listen on port
udp_port = 3493
# and interface
udp_ip = 192.168.1.255

# We pre-process the input datagram using the below list of patterns
# and replacements,
# and name the selected columns with keys "AZtrue" and "ZDtrue".
# The input_resub option is a list of [PATTERN,REPL]
# where PATTERN,REPL are fed directly to re.sub python function as
# re.sub(PATTERN, REPL, udp_string)
input_resub=[ ["^(?:\\S+ ){11}(\\S+) (\\S+).*", "AZtrue=\\1,ZDtrue=\\2"] ]

# search for the required keys in the incoming UDP datagram
required_keys = ["AZtrue","ZDtrue"]

# The datagram keys are mapped to mysql table column names as
# (these names are also used for redis)
db_keys = ["AZtrue","ZDtrue"]

# The key names can be prefixed using namespace 
# redisNamespace = rt4_control
# If output to redis database is also requested then
#saveToRedis = True


# averaging interval in seconds
# If this is not given then resend_output* options can still be used
# and in this case the non-averaged version of the output datagram
# is sent. Note that saveToRedis and saveToDB options store
# the output version of the data (here, pre-processed and averaged).
averaging_interval=1
resend_output_to_host=127.0.0.1
resend_output_to_port=10000
```

Similarly to example 1 this configuration is run with:

```sh
python3 python/services/save-UDPdata-generic-module.py -m TEST_RTAZ --serverUDP -c path/to/configuration/file.ini
```

## Example 3 - alarms (experimentall)

One can set email notifications if given value crosses specified
thresholds. E.g.


```sh
.netlog.ini file
##############################################################
##############################################################
##############################################################
[TEST_ALARM]

# listen on port
udp_port = 10000
# and interface
udp_ip = 127.0.0.1

# search for the required keys in the incoming UDP datagram
required_keys = ["T"]

# The datagram keys are mapped to mysql table column names as
# (these names are also used for redis)
db_keys = ["T"]

alarm_on = [ ["T", ">", "30" ], ["T", "<", "15" ] ]
alarm_email= ["xxx@yyy.zzz"]
```



### Other examples
Check [etc/netlog.ini](etc/netlog.ini) for more examples, 
or use cases showing how to save to redis, files,
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

