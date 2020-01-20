# GENERAL

This package implements saving UDP datagrams from localnetwork to mySQL database.

#CONTENTS:

	* RT32netlog package contains daemons working as ubuntu service at galaxy. 
	  They read UDP datagrams and stores them to mySQL database on galaxy
		


# DOWNLOAD

`git ssh://gitolite@galaxy.astro.uni.torun.pl/RT32netlog`

# BUILD
`python3 setup.py build`

# INSTALL

## Installation general

`sudo python3 setup.py install`


To install without sources

`python3 setup.py bdist_egg --exclude-source-files`

`sudo python3 setup.py install`

The data acquisition daemon can work as a system service controlled via systemctl.
The package is shipped with save-electric_cabin-data.service file which should be placed in the correct
directory depending on the system. For ubuntu it should be 
/etc/systemd/system/save-electric_cabin-data.service and the soft link to this file should be in
/etc/systemd/system/multi-user.target.wants/save-electric_cabin-data.service.


###### To install as a service run provided `install_service_ubuntu.sh` script or run 

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



## Installation

#INITIALIZE

The packages uses config files, so before usage the program should be configured.
This is a one time initialization:

`save-electric_cabin-data.py --setup`



#USE


	* To run as a daemon use

`save-electric_cabin-data.py --serverUDP`

or use

`systemctl start save-electric_cabin-data`


This script makes sure that the data collecting program called 

`/usr/local/bin/save-electric_cabin-data.py`

is up and running.


#AUTHOR
Bartosz Lew [<bartosz.lew@umk.pl>](bartosz.lew@umk.pl)

#BUGS
Send info to author or to [rt4-dev@cosmo.torun.pl](rt4-dev@cosmo.torun.pl)
