'''
Created on Jan 23, 2019

@author: blew
'''
import configparser
import os,sys
import json
# import csv
# from io import StringIO
import re

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


class RT32netlogParser(configparser.ConfigParser):
    def __init__(self):
        super().__init__()
#         list_keys=['db_keys']
        self.set('DEFAULT','db_keys',json.dumps('[]'))
        self.set('DEFAULT','saveToRedis','False')
        self.set('DEFAULT','saveToDB','False')
        self.set('DEFAULT','saveToFile','False')
        self.set("DEFAULT",'alarm_email','["blew@astro.umk.pl"]')
#         self['DEFAULT']['resend_input_to_port']=None
        
    def getlist(self, section_name,option_name):
#         for lk in list_keys:
#             for s in config.sections():
#                 if lk in config[s].keys():
#                     print(config[s][lk])
#                     print(type(config[s][lk]))
#                     config[s][lk]=csv.reader(config[s][lk], delimiter=',')
        val=self.get(section_name,option_name)
        if not val.startswith('['):
            raise "List should start with ["
        if not val.endswith(']'):
            raise "List should end with ]"
#         print(val[1:-1])
#         f=StringIO(val[1:-1])
#         reader = csv.reader([val[1:-1]], delimiter=',')
#         for r in reader:
#             print('----')
#             print(r)
#         print('----')
#         print('----')
        chars_to_remove=['"']
        rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
        l=[ re.sub(rx,'',x.strip()) for x in val[1:-1].split(',')]
#         for it in l:
#             print(it)
        return l

def readConfigFile(cf_name='RT32netlog.ini'):
#     config = configparser.ConfigParser()
    config = RT32netlogParser()
    configFile=cf_name
    if os.path.isfile(cf_name):
        print('Found configuration file: {}'.format(configFile))
        config.read(configFile)
    else:
        configFile=os.environ['HOME']+os.sep+'.'+cf_name
        if os.path.isfile(configFile):
            print('Found configuration file: {}'.format(configFile))
            config.read(configFile)
        else:
            print('Cound not find config file: {}'.format(configFile))
            configFile='/etc/RT32netlog/'+cf_name
            if os.path.isfile(configFile):
                print('Found configuration file: {}'.format(configFile))
                config.read(configFile)
            else:
                print('Cound not find config file: {}'.format(configFile))
#                 configFile=os.environ['HOME']+os.sep+'.'+cf_name
#                 config=writeConfigFile(configFile)
#                 print("Generated config file in: {}".format(configFile))
                raise 'Cound not find config file'

    return config


def getOption(optName,cfg,cfgSection,valueIfNotExists):
    '''
    check if optName exists in the ConfigParser object
    and if it does retuns its value.
    Otherwise returns valueIfNotExists
    
    
    '''
    if cfgSection in cfg.keys():
        if optName in cfg[cfgSection].keys():
            if cfg[cfgSection][optName].startswith('['):
                return json.loads(cfg[cfgSection][optName])
            else:
                return cfg[cfgSection][optName]
    
    return valueIfNotExists

def eprint(*args):
#         print(*args, file=sys.stderr, **kwargs)
    sys.stderr.write(''.join(*args))
#     sys.stderr.write(''.join(**kwargs))
    sys.stderr.write('\n')
