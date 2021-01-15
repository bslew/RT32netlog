'''
Created on Jan 20, 2020

@author: blew
'''
from socket import *
import datetime
import sys,os
'''
FOR EXTRA MODULES LOCATED IN LOCAL DIRECTORIES 
for runs started without installing the package
'''
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1]))  

from common import commons
from database import storage
from communication import UDPdatagrams



def UDPserver(host,port,log):
    log.info("Listening on udp {}:{}".format(host, port))
    
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.bind((host, int(port)))
    while 1:
        (data, addr) = s.recvfrom(128*1024)
        yield data


def startServerUDP(cfg,moduleName,args,sqldbProxy,datagramConverter,keys,log):
    try:
        host=cfg[moduleName]['udp_ip'].split(',')[0]
        port=cfg[moduleName]['udp_port'].split(',')[0]
    except KeyError:
        log.error('There is no {} block in the configuration file {} or some of its entries are missing.'.format(moduleName,cfg['CONFIG_FILE']))
        log.info('This program will not work without the information from that block.')
        sys.exit(1)
    db=None


    if args.saveToDB:
        db = sqldbProxy(host=cfg['DB']['host'], port=cfg['DB']['port'],
                         db=cfg['DB']['db'],table=cfg[moduleName]['table'],
                         user=cfg['DB']['user'], 
                         passwd=cfg['DB']['passwd'],
                         logger=log)
        db.connect()

    rcon=None
    if args.saveToRedis:
        import redis
#         from redis_namespace import StrictRedis
# 
#         rcon = redis.StrictRedis()
#         redis = StrictRedis(namespace=cfg['STRUCT_TEMP']['redisNamespace'])
        rcon=redis.Redis(host=cfg['REDIS']['host'], port=cfg['REDIS']['port'],
                         db=cfg['REDIS']['db'])
        redis_con={'con' : rcon, 
                   'pref' : cfg[moduleName]['redisNamespace'],
                   'maxelem' : cfg['REDIS']['list_max_elem']}
        
    for data in UDPserver(host,port,log):
        
        readout,status=datagramConverter(data,keys['required'],keys['target'])
        
        if args.test1:
            dataRef={}
        if args.verbose:
            log.debug('New datagram')
            log.debug('{}'.format(commons.dict2str(readout)))

        if len(status['comments'])>0:
            log.info(';'.join(x for x in status['comments']))


            
        if status['result']:
            if args.saveToFile:
                storage.save_to_file(args.outfile,readout,log)
            if args.saveToRedis:
                storage.save_to_redis(redis_con,readout,log)
            if args.saveToDB:
                db.store(readout)
        else:
            log.error('Bad datagram: ')
            log.error(','.join(x for x in status['comments']))
    

# if __name__ == '__main__':
#     pass
