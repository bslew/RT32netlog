'''
Created on Jan 20, 2020

@author: blew
'''
from socket import *
import datetime
import sys,os
import threading
import json
import redis
'''
FOR EXTRA MODULES LOCATED IN LOCAL DIRECTORIES 
for runs started without installing the package
'''
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1]))  

from common import commons
from database import storage
from communication import UDPdatagrams
from communication import config_file



def UDPserver(host,port,log,dgram_converter,**kwargs):
    log.info("Listening on udp {}:{}".format(host, port))

    keys=kwargs['keys']
    moduleName=kwargs['moduleName']
    cfg=kwargs['cfg']
    args=kwargs['args']
#     resend_input_to_host=host
    resend_input_to_host=cfg[moduleName].get('resend_input_to_host','localhost')
    resend_input_to_port=cfg[moduleName].getint('resend_input_to_port',None)
    input_resub=config_file.getOption('input_resub',cfg,moduleName,None)
#     print(input_resub)
    resend_output_to_host=cfg[moduleName].get('resend_output_to_host','localhost')
    resend_output_to_port=cfg[moduleName].getint('resend_output_to_port',None)

    resend_output=True
#     print('averaging_interval',cfg[moduleName].getint('averaging_interval',None))
    # if cfg[moduleName].getint('averaging_interval',None)==None:
    #     resend_output=False
    if resend_output_to_port==None:
        resend_output=False
    
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.bind((host, int(port)))
    while 1:
        (data, addr) = s.recvfrom(128*1024)
        if args.verbose>2:
            print('datagram:',data)
        readout,status=dgram_converter(data,keys['required'],keys['target'],input_resub=input_resub,
                                       **kwargs)
#        s.sendto(data, (host, int(port)))
    


        yield readout,status

        if resend_input_to_port!=None:
            s.sendto(data, (resend_input_to_host, int(resend_input_to_port)))
            if args.verbose>1:
                log.debug('resending input data')
        
        if resend_output:
            s.sendto(commons.dict2str(readout).encode(), (resend_output_to_host, int(resend_output_to_port)))
            if args.verbose>1:
                log.debug('resending output data')


def UDPserver_time_avg(host,port,log,dgram_converter,**kwargs):
    '''
    UDP generator that can average stuff over time
    '''
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    keys=kwargs['keys']
    moduleName=kwargs['moduleName']
    args=kwargs['args']
    cfg=kwargs['cfg']
    avg_int=cfg[moduleName].getint('averaging_interval',60)
    delta=datetime.timedelta(seconds=avg_int)

    resend_output_to_host=cfg[moduleName].get('resend_output_to_host','localhost')
    resend_output_to_port=cfg[moduleName].getint('resend_output_to_port',None)
    
    dt0=datetime.datetime.utcnow()
    dgrams=[]
    for readout,status in UDPserver(host,port,log,dgram_converter,**kwargs):
        if status['result']:
            dgrams.append(readout)
            dt=datetime.datetime.utcnow()
#             print(dt)
#             print(dt0+delta)
            if dt>dt0+delta:
                avg_readout=storage.bin_list_dict_vals(dgrams,avg_int)
                dt0=dt0+delta
                status['time_avg_samples']=len(dgrams)
                dgrams=[]
                yield avg_readout,status

                if resend_output_to_port!=None:
                    s.sendto(commons.dict2str(avg_readout).encode(), (resend_output_to_host, int(resend_output_to_port)))
                    if args.verbose>1:
                        log.debug('resending output data')


# def startServerUDP(cfg,moduleName,args,sqldbProxy,datagramConverter,keys,log):
def startServerUDP(cfg,moduleName,args,datagramConverter,log,**kwargs):
    '''
    kwargs
    ------
    '''
    try:
        host=cfg[moduleName]['udp_ip'].split(',')[0]
        port=cfg[moduleName]['udp_port'].split(',')[0]
    except KeyError:
        log.error('There is no {} block in the configuration file {} or some of its entries are missing.'.format(moduleName,cfg['CONFIG_FILE']))
        log.info('This program will not work without the information from that block.')
        sys.exit(1)
    db=None

    keys={}
#     if cfg[moduleName]['required_keys']=='raw':
#         keys['required']='_raw'
#     else:
    keys['required']=json.loads(cfg[moduleName]['required_keys'])
    keys['target']=None
#     if cfg[moduleName].getboolean('saveToDB') or \
#         cfg[moduleName].getboolean('saveToRedis') or cfg[moduleName].getboolean('saveToFile'):
    keys['target']=json.loads(cfg[moduleName]['db_keys'])
#     keys={'required' : json.loads(cfg[moduleName]['required_keys']), 
#           'target' : json.loads(cfg[moduleName]['db_keys'])
#           }
    assert(len(keys['required'])==len(keys['target']))

    if args.saveToDB:
        
        db = storage.sqldb(host=cfg['DB']['host'], port=cfg['DB']['port'],
                         db=cfg['DB']['db'],table=cfg[moduleName]['table'],
                         user=cfg['DB']['user'], 
                         passwd=cfg['DB']['passwd'],
                         logger=log)
        db.connect()

    rcon=None
    if args.saveToRedis:
#         from redis_namespace import StrictRedis
# 
#         rcon = redis.StrictRedis()
#         redis = StrictRedis(namespace=cfg['STRUCT_TEMP']['redisNamespace'])
        rcon=redis.Redis(host=cfg['REDIS']['host'], port=cfg['REDIS']['port'],
                         db=cfg['REDIS']['db'])
        redis_con={'con' : rcon, 
                   'pref' : cfg[moduleName].get('redisNamespace',moduleName),
                   'maxelem' : cfg['REDIS']['list_max_elem']}
    
    UDPgenerator=UDPserver
    if cfg.has_option(moduleName,'averaging_interval'):
        if args.verbose:
            log.debug('time averaging generator')
#             print('time averaging generator')
        UDPgenerator=UDPserver_time_avg
        
    
    for readout,status in UDPgenerator(host,port,log, 
                                       dgram_converter=datagramConverter,
                                       keys=keys,
                                       cfg=cfg,
                                       args=args,
                                       moduleName=moduleName):
        
#         readout,status=datagramConverter(data,keys['required'],keys['target'])
        
        if args.test1:
            dataRef={}
        if args.verbose:
            log.debug('New datagram')
            log.debug('{}'.format(commons.dict2str(readout)))
            log.debug('{}'.format(commons.dict2str(status)))

        if len(status['comments'])>0:
            log.debug(';'.join(x for x in status['comments']))


            
        if status['result']:
            
            '''
            check values if needed
            '''
            if args.verbose>2:
                print(readout)
            UDPdatagrams.alarmCheck(readout,cfg,moduleName).execute()
            
            
            '''
            The below "saving" part should be done in sub-processes
            in case some storage operation takes long time, or cannot
            be finished quickly (e.g. mysql backups that block db).
            '''
            
            if args.saveToFile:
                storage.save_to_file(args.outfile,readout,log)
            if args.saveToRedis:
                storage.save_to_redis(redis_con,readout,log)
            if args.saveToDB:
                # db.store(readout)
                # print(readout)
                try:
                    threading.Thread(target=db.store,args=[readout]).start()
                except:
                    raise
        else:
            if args.verbose>2:
                log.error('Bad datagram: ')
                log.error(','.join(x for x in status['comments']))
    

# if __name__ == '__main__':
#     pass
