'''
Created on Jan 20, 2020

@author: blew
'''
import datetime

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