'''
Created on Jan 20, 2020

@author: blew
'''
import datetime
from RT32logging.common import commons

def convert_UDP_datagram_electric_cabin(data):
    '''
    Converts UDP datagram to dictionary with keys that 
    represent names in the mySQL database.
    
    '''
    d={}
    for param in data.decode().split(','):
        kv=param.split('=')
        k=kv[0]
        v=kv[1]
        if k=='T_electric':
            d['T']=v
        if k=='H_electric':
#             d[k]=v
            d['RH']=v
        if k=='RH_electric':
#             d[k]=v
            d['RH']=v
        
    if 'T' not in d.keys():
        d=None
    if 'RH' not in d.keys():
        d=None
    
    
    dtstr=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    d['dt']=dtstr
    
    return d

def convert_UDP_datagram_focus_cabin(data):
    '''
    Converts UDP datagram to dictionary with keys that 
    represent names in the mySQL database.
    
    '''
    d={}
    for param in data.decode().split(','):
        kv=param.split('=')
        k=kv[0]
        v=kv[1]
        if k=='T_focB':
            d['T']=v
        if k=='P_focB':
            d['P']=v
        if k=='RH_focB':
#             d[k]=v
            d['RH']=v
        
    if 'T' not in d.keys():
        d['T']=None
    if 'RH' not in d.keys():
        d['RH']=None
    if 'P' not in d.keys():
        d['P']=None
    
    
    dtstr=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    d['dt']=dtstr
    
    return d

def convert_UDP_datagram(data,required_keys, output_keys):
    '''
    convert data string to key value dictionary
    The function checks if all required keys are present
    
    require data format:
    k1=v1,k2=v2,...
    
    parameter
    ---------
        data - string with required data format
        required_keys - list of required keys that should be present
        output_keys - list of corresponding output keys (should have the same length as required_keys
        
    returns
    -------
        kv,status tuple where kv is a dictionary and status is a dictionary containing
        operation status and comments
    '''
    d={}
    extra_keys=[]
    present_keys=[]
    missing_keys=[]
    status={'result': True, 'comments' :[] }

    data=commons.strip_white_spaces(data)

    for param in data.decode().split(','):
        kv=param.split('=')

        if len(kv)==2:
            k=kv[0]
            v=kv[1]
            if k in required_keys:
                d[output_keys[required_keys.index(k)]]=v
                present_keys.append(k)
            else:
                extra_keys.append(k)

    for k in required_keys:
        if k not in present_keys:
            missing_keys.append(k)

    for k in output_keys:
        if k not in d.keys():
            d[k]=None
    
    if 'dt' not in d.keys():
        dtstr=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        d['dt']=dtstr
#     status=verify_UDP_datagram_dict(d)

    if len(extra_keys)>0:
        status['comments'].append('Extra keys: '+','.join(x for x in extra_keys))
    if len(missing_keys)>0:
        status['comments'].append('Missing keys: '+','.join(x for x in missing_keys))
        status['result']=False
    
    
    return d,status

def verify_UDP_datagram_dict(d):
    '''
    '''
    status={'result': True, 'comments' :[] }
    
    
    for k,v in d.items():
        if v==None:
            status['comments'].append('Missing key {}'.format(k))
            status['result']=False
        
    return status
