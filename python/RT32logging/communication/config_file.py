'''
Created on Jan 23, 2019

@author: blew
'''
import configparser
import os,sys


configFile=os.environ['HOME']+os.sep+'.RT32netlog.ini'

def writeConfigFile(configFile):
    config = configparser.ConfigParser()
    print('Generating config file')
    config['ELECTRIC_CABIN_DATA'] = {
        'udp_port' : 33051, 
        'udp_ip' : '192.168.1.255',
    }

    
    config['DB'] = {'host' : '192.168.1.8',
                    'port' : 3306,
                    'user' : 'kra', 
                    'passwd' : 'passwd',
                    'db' : 'kra',
                    'table' : 'electric_cabin',
                 }


    with open(configFile,"w") as f:
        config.write(f)
        
    return config

def readConfigFile():
    config = configparser.ConfigParser()
    configFile=os.environ['HOME']+os.sep+'.RT32netlog.ini'
    if os.path.isfile(configFile):
        print('Found configuration file: {}'.format(configFile))
        config.read(configFile)
    else:
        print('Cound not find config file: {}'.format(configFile))
        configFile='/etc/RT32netlog/RT32netlog.ini'
        if os.path.isfile(configFile):
            print('Found configuration file: {}'.format(configFile))
            config.read(configFile)
        else:
            print('Cound not find config file: {}'.format(configFile))
            configFile=os.environ['HOME']+os.sep+'.RT32netlog.ini'
            config=writeConfigFile(configFile)
            print("Generated config file in: {}".format(configFile))
    return config

def eprint(*args):
#         print(*args, file=sys.stderr, **kwargs)
    sys.stderr.write(''.join(*args))
#     sys.stderr.write(''.join(**kwargs))
    sys.stderr.write('\n')
