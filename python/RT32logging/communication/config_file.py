'''
Created on Jan 23, 2019

@author: blew
'''
import configparser
import os,sys
import json

configFile=os.environ['HOME']+os.sep+'.RT32netlog.ini'

def writeConfigFile(configFile):
    config = configparser.ConfigParser()
    print('Generating config file')
    config['ELECTRIC_CABIN_DATA'] = {
        'udp_port' : 33051, 
        'udp_ip' : '192.168.1.255',
        'required_keys' : json.dumps('["T_electric", "RH_electric"]'),
        'db_keys' : json.dumps('["T", "RH"]'),
        'table' : 'electric_cabin',
        'saveToDB' : True,
    }

    config['FOCUS_CABIN_DATA'] = {
        'udp_port' : 33060, 
        'udp_ip' : '192.168.1.255',
        'required_keys' : json.dumps('["T_focB", "P_focB", "RH_focB"]'),
        'db_keys' : json.dumps('["T", "P", "RH"]'),
        'table' : 'focus_cabin',
        'saveToDB' : True,
    }
    
    config['DB'] = {'host' : '192.168.1.8',
                    'port' : 3306,
                    'user' : 'kra', 
                    'passwd' : 'passwd',
                    'db' : 'kra',
                 }
    
    config['CONFIG_FILE']=configFile


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


def getOption(optName,cfg,cfgSection,valueIfNotExists):
    '''
    check if optName exists in the ConfigParser object
    and if it does retuns its value.
    Otherwise returns valueIfNotExists
    
    
    '''
    if cfgSection in cfg.keys():
        if optName in cfg[cfgSection].keys():
            return cfg[cfgSection][optName]
    
    return valueIfNotExists

def eprint(*args):
#         print(*args, file=sys.stderr, **kwargs)
    sys.stderr.write(''.join(*args))
#     sys.stderr.write(''.join(**kwargs))
    sys.stderr.write('\n')
