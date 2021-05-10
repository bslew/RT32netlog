'''
Created on Jan 20, 2020

@author: blew
'''
import datetime
from RT32logging.common import commons
from RT32logging.communication import config_file
import re
import smtplib

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

def convert_UDP_datagram(data,required_keys, output_keys, input_resub=None):
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
        input_resub = [] list of [pattern,replacement] strings used to feed to re.sub(pattern, replacement, data) function
            before processing
        
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

    data=data.decode() if isinstance(data,bytes) else data

    if input_resub!=None:
        for p,r in input_resub:
            data=re.sub(r'%s' % p,r'%s' % r,data)

    data=commons.strip_white_spaces(data)

    for param in data.split(','):
#     for param in data.decode().split(','):
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


class alarmCheck():
    def __init__(self,d,cfg,moduleName):
        '''
        
        '''
        self.dgramdict=d
        self.cfg=cfg
        self.modulename=moduleName
        self.alarmcfg=config_file.getOption('alarm_on',cfg,moduleName,None)
        self.alarmemail=config_file.getOption('alarm_email',cfg,moduleName,None)
        self.offendingKey=None
        self.offendingValue=None
        self.alarm_thres=None
        self.raise_alarm=False
#         if alarmcfg==None:
        
        
    def execute(self):
        '''
        check if alarm should be raised and raise if needed
        '''
        if self.check():
            self.raiseAlarm()
    
    def check(self):
        '''
        check alarm conditions
        '''
        for al in self.alarmcfg:
            key,cond,thres_val=al
            
            if cond=='>':
                if float(self.dgramdict[key])>float(thres_val):
                    self.raise_alarm=True
                    self.offendingKey=key
                    self.offendingValue=self.dgramdict[key]
                    self.alarm_thres=thres_val
                    return True
            elif cond=='<':
                if float(self.dgramdict[key])<float(thres_val):
                    self.raise_alarm=True
                    self.offendingKey=key
                    self.offendingValue=self.dgramdict[key]
                    self.alarm_thres=thres_val
                    return True

        return False
        
    def raiseAlarm(self):
        '''
        alarm
        '''
        print('RISING ALARM')
        
        


        fromaddr = "RT32netlog@astro.umk.pl"
        toaddrs  = self.alarmemail
        subject= '[RT32netlog] ALARM in module: %s due to key %s=%s (thres. %s)' % (
            self.modulename, self.offendingKey, self.offendingValue, self.alarm_thres)

        # Add the From: and To: headers at the start!
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
               % (fromaddr, ", ".join(toaddrs),subject))
        msg=msg+'This e-mails is sent automatically from RT32netlog module: "{}" '.format(self.modulename)
        msg+='working on galaxy. Do not reply to this message.'

        print("Message length is", len(msg))

        server = smtplib.SMTP('localhost')
#         server.set_debuglevel(1)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()        
        