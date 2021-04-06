'''
Created on Jan 23, 2019

@author: blew
'''

import os,sys
import numpy as np
from scipy.stats import binned_statistic
import datetime
import MySQLdb
from RT32logging.communication import config_file
from RT32logging import logger
from RT32logging.common import commons


def save_to_redis(rcon, data_dict,logger=None):
    '''
    save dictionary key and values to redis server
    
    parameters
    ----------
        rcon - dictionary {
            'con' : instance of redis.Redis class, 
            'pref' : prefix used to access the required namespace,
            'maxelem' : maximal number of elements in lists} 
        data_dict - dict to be saved
    '''
    N=rcon['maxelem']
    for k,v in data_dict.items():
#         print(rcon['pref']+'::'+k)
#         rcon['con'].set(rcon['pref']+'::last::'+k,v)
        rcon['con'].lpush(rcon['pref']+'::last::'+k,v)
        rcon['con'].ltrim(rcon['pref']+'::last::'+k,0,int(N)-1)
        
    # store the whole thing
    rcon['con'].lpush(rcon['pref']+'::last::_raw',commons.dict2str(data_dict))
    rcon['con'].ltrim(rcon['pref']+'::last::_raw',0,int(N)-1)


def fetch_from_redis(rcon, key='_raw',from_idx=0,to_idx=-1):
    '''
        returns
        -------
            list of bytes containing serialized datagram dictionary
    '''
    return rcon['con'].lrange(rcon['pref']+'::last::'+key,from_idx,to_idx-1)


class redissrv:
    def __init__(self, rcon=None):
        '''
        '''
        self.rcon=rcon
        
    def fetchLast(self):
        '''
        fetch last entry stored in redis and return as dictionary.
        This intends to recover the UDP datagram structure temperarily stored
        in redis. The namespace is defined by the connection name at 
        initialization time.
        
        returns
        -------
            dictionary 
        '''
        raw=fetch_from_redis(self.rcon,'_raw',0,1)
        print(raw)
        raw=[x.decode() for x in raw]
        if len(raw)==0:
            return {}
        
        s2l=lambda s,sep: s.split(sep)
    
        raw=[ [s2l(y,'=') for y in s2l(x,',') if y!=''] for x in raw][0]
        d={}
        for k,v in raw:
            d[k]=v
            
#         print(d)
        return d
    
    
    def fetchLastNhours(self, Nhours,step=6,json_serializable=False, **kwargs):
        '''
        
        Keywords
        --------
        
            avgdt - interval in seconds over which to average the redis data
        '''
        dt2=datetime.datetime.utcnow()
        dt1=dt2 - datetime.timedelta(hours=Nhours)
        return self.fetch(dt1, dt2, step, json_serializable, **kwargs)

    
    def fetch(self,dt1,dt2,step=6,json_serializable=False, **kwargs):
        '''
        Fetch data from redis storage
        
        
        parameters
        ----------
            dt1, dt2 - datetimes objects defining UTC date and time (space separated) 
            
            step - select every this row
            json_serializable- if True, then datatime objects are converted back to strings
                before returning.Default (False)

        Keywords
        --------
        
            dtavg - interval in seconds over which to average the redis data
            
        returns:
            tuple: a list with column names, data
        
        '''
        raw=fetch_from_redis(self.rcon)
        raw=[x.decode() for x in raw]
        
        '''
        convert to list of strings
        '''
        s2l=lambda s,sep: s.split(sep)
        
        raw=[ [s2l(y,'=') for y in s2l(x,',') if y!=''] for x in raw]
#         print(raw[0])
        d={}
        keys=[]
        for entry in raw[0]:
            try:
                k,_=entry
                d[k]=[]
            except:
                print(entry)
                raise
        for row in raw:
            for k,v in row:
                if k=='dt':
                    d[k].append(datetime.datetime.strptime(v,'%Y-%m-%d %H:%M:%S'))
                else:
                    d[k].append(float(v))                        


        
        '''
        select data by dates
        '''
        mask=np.logical_and(np.array(d['dt'])>=dt1,np.array(d['dt'])<=dt2)
#         print(mask)
        
        dsel={}
        for k,v in d.items():
            dsel[k]=list(np.array(d[k])[mask][::step])
        
        
        '''
        average in time domain
        '''
        if 'dtavg' in kwargs.keys():
            dsel=bin_dict_list_vals(dsel, kwargs['dtavg'], 'mean')
        
        '''
        convert datetime objects back to strings
        '''
        if json_serializable:
            dsel['dt']=[datetime.datetime.strftime(x,'%Y-%m-%d %H:%M:%S') for x in dsel['dt'] ]
        return dsel


def bin_list_dict_vals(data,dtavg,how='mean'):
    '''
    bin list of dictionaries containing 'dt' key datetime objects 
        that are used for averaging over time
        of all other keys that must be float lists of the same length
        
    parameter
    ---------
        data - list of dict(). All keys in each list element dictionary must be consistent.
        
    returns
    -------
        binned version of dictionary containing a given statistic (mean by default)
    '''
    
    '''
    convert list of dict to dict containing lists
    '''
    if len(data)==0:
        return None
    
    d={}
    for k,v in data[0].items():
        d[k] = list()
    for entry in data:
        for k,v in entry.items():
            if k=='dt':
                d[k].append(datetime.datetime.strptime(v,"%Y-%m-%d %H:%M:%S"))
#                 print(v)
#                 print(d[k])
            else:
                d[k].append(float(v))

#     print(d)        
    dstat=bin_dict_list_vals(d, dtavg, how)
    for k,v in dstat.items():
        dstat[k]=v[0]

    return dstat
    

def bin_dict_list_vals(data, dtavg, how='mean',nmin=1):
    '''
    data - dict containing 'dt' key with datetime objects that are used for averaging over time
        of all other keys that must be float lists of the same length
        
    '''
#     def binned(X):
#         return binned_statistic(X,X,how,dtavg)[0]
    
    X=[ x.timestamp() for x in data['dt'] ]
    n=nmin if np.abs(X[-1]-X[0])//dtavg < nmin else np.abs(X[-1]-X[0])//dtavg
#     print(X)
#     print(data.keys())
    for k in data.keys():
        if k=='dt':
            data[k]=list([datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") for ts in binned_statistic(X,X,how,n)[0]])
            
        else:
            Y=data[k]
            data[k]=list(binned_statistic(X,Y,how,n)[0])
    return data

def save_to_file(fname,data_dict, logger=None):
    '''
    save a dictionary to CSV file
    
    we import pandas here because it conflicts with pyqt5 via io.clipboards that import 
    QtCore4 from PyQt4.QtGui import QApplication
    '''
    import pandas as pd
    
    data_dict_tmp=data_dict.copy()
    for k,v in data_dict.items(): # what's the reason behind this ? - we need backward compatibility check here
        if isinstance(data_dict[k],list):
            data_dict_tmp[k]=list([v])
        else:
            data_dict_tmp[k]=list([v])
    
#     print(data_dict)
    header=True
    if os.path.isfile(fname):
        header=False

    try:
    
        with open(fname,"a") as f:
            df=pd.DataFrame.from_dict(data=data_dict_tmp, orient='columns')
#             print(df)
            df.to_csv(f, sep='\t', encoding='utf-8',header=header, index=False)
    except:
        sys.stderr.write(str(sys.exc_info()[1])+'\n')
        if logger!=None:
            logger.error('Cannot write to file {}'.format(fname))
            logger.error(str(sys.exc_info()[1]))


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z




class sqldb:
    def __init__(self,host,port,dbname,table,user,passwd, cols=[], **kwargs):
        self.host=host
        self.port=port
        self.dbname=dbname
        self.table=table
        self.user=user
        self.passwd=passwd
        self.db=None
        self.cur=None
        self.logger=None
        
        if 'logger' in kwargs:
            self.logger=kwargs['logger']
        else:
            self.logger=logger.get_logging("RT32netlog", fname=None)

#         self.connect()

        '''
        Column names in mySQL database 
        '''
        self.cols=cols


    def connect(self):
        try:
            self.db = MySQLdb.connect(self.host, self.user, self.passwd, self.dbname)
            self.cur = self.db.cursor()
        except MySQLdb.Error as e:
            self.logger.error("Cannot connect to mySQL db (host: {}, user: {}, db: {})".format(self.host, self.user,self.dbname))
            self.logger.error(e)
        
    def connected(self):
        if self.db==None:
            return False
    
        return True


    def create_table(self):
        '''
        create DB table
        '''
        sql="CREATE TABLE if not exists %s (id integer UNSIGNED AUTO_INCREMENT, " % self.table
        sql+="dt datetime COMMENT 'UTC DATE AND TIME',"
        for col in self.cols:
            sql+="{} float COMMENT 'TBD',".format(col)
        sql+="PRIMARY KEY (`id`))"
#         print(sql)
        try:
#             self.db.query(sql)
            self.cur.execute(sql)
            self.db.commit()
            self.logger.info("Created mysql table")
        except:
            self.db.rollback()
            sys.stderr.write(str(sys.exc_info()[1])+'\n')

            
        
#         sql="CREATE TABLE %s (id integer UNSIGNED AUTO_INCREMENT, " % self.table
#         sql+="date date COMMENT 'UTC DATE',"
#         sql+="time time COMMENT 'UTC TIME', "
#         sql+="AH_ac float COMMENT 'actual absolute humidity [g/m3]',"
#         sql+="AH_av float COMMENT 'average absolute humidity [g/m3]',"
#         sql+="PRIMARY KEY (`id`))"
# #         print(sql)
#         try:
# #             self.db.query(sql)
#             self.cur.execute(sql)
#             self.db.commit()
#             print("Created mysql table")
#         except:
#             self.db.rollback()
#             sys.stderr.write(str(sys.exc_info()[1])+'\n')

    def fetch(self,dt1,dt2,step=6):
        '''
        Fetch data from mySQL database
        
        dt1, dt2 - datetimes objects defining UTC date and time (space separated) 
            that are passed directly to SQL query
            
        returns:
            tuple: a list with column names, data
        
        '''
        d1=dt1.strftime('%Y-%m-%d')
        d2=dt2.strftime('%Y-%m-%d')
        sql='SELECT '
        for col in self.cols:
            sql+=col+','
        sql=sql[:-1]
        sql+=' FROM %s WHERE datetime>="%s" AND datetime<"%s" ' % (self.table,d1,d2)
        sql+=' AND id%%%i=0 ' % step
#         print(sql)
        data=None
        try:
            self.cur.execute(sql)
            data=self.cur.fetchall()
#             for row in self.cur.fetchall():
#                 print(row)
                
        except:
            sys.stderr.write(str(sys.exc_info()[1])+'\n')
            self.logger.error(str(sys.exc_info()[1]))

        return self.cols,data
    

    def store(self,data):
        '''
        store data to mySQL database

        input:
            data - dictionary with data to be stored. Must be consistent with database
                mySQL database columns
        '''
        try:
            kstr=''
            vstr=''
            for k,v in data.items():
                kstr+='%s,' % k
                vstr+='"%s",' % v
#                 print(v)
                
            sql ='INSERT INTO %s ' % self.table
            sql+='('+kstr[0:-1]+') VALUES ('+vstr[0:-1]+')'
#             print(sql)
        
            self.cur.execute(sql)
            self.db.commit()
                    
        except:
            sys.stderr.write(str(sys.exc_info()[1])+'\n')
            self.logger.error('Cannot store to mySQL db')
            self.logger.error(str(sys.exc_info()[1]))

            if self.connected():
                self.db.rollback()
            else:
                self.logger.error('Not connected to mySQL db')
#             pass
            raise
        


class Telectric_sqldb(sqldb):
    '''
    Class for mySQL database communication to manipulate electric cabin meteo data.
    
    '''
    def __init__(self,host,port,db,table,user,passwd, **kwargs):
        super().__init__(host,port,db,table,user,passwd, **kwargs)
        self.host=host
        self.port=port
        self.dbname=db
        self.table=table
        self.user=user
        self.passwd=passwd
        self.db=None
        self.cur=None
        
        self.cols=[]
        self.cols.append('datetime')
        self.cols.append('T')
        self.cols.append("RH")
        self.cols.append('P')
        
    def create_table(self):
        '''
        '''
        
        
        sql="CREATE TABLE if not exists %s (id integer UNSIGNED AUTO_INCREMENT, " % self.table
        sql+="dt datetime COMMENT 'UTC DATE AND TIME',"
        sql+="RH float COMMENT 'relative humidity [%]',"
        sql+="T float COMMENT 'temperature [degC]',"
        sql+="P float COMMENT 'pressure [mbar]',"
        sql+="PRIMARY KEY (`id`))"
#         print(sql)
        try:
#             self.db.query(sql)
            self.cur.execute(sql)
            self.db.commit()
            self.logger.info("Created mysql table")
        except:
            self.db.rollback()
            sys.stderr.write(str(sys.exc_info()[1])+'\n')

    def fetch(self,dt1,dt2,step=6):
        '''
        Fetch data from mySQL database
        
        dt1, dt2 - datetimes objects defining UTC date and time (space separated) 
            that are passed directly to SQL query
        
            Only the date part is currently used 
            
        returns:
            tuple: a list with column names, data
            
            
        
        '''
        
        d1=dt1.strftime('%Y-%m-%d')
        d2=dt2.strftime('%Y-%m-%d')
        sql='SELECT '
        for col in self.cols:
            sql+=col+','
        sql=sql[:-1]
        sql+=' FROM %s WHERE datetime>="%s" AND datetime<"%s" ' % (self.table,d1,d2)
        sql+=' AND id%%%i=0 ' % step
#         print(sql)
        data=None
        try:
            self.cur.execute(sql)
            data=self.cur.fetchall()
#             for row in self.cur.fetchall():
#                 print(row)
                
        except:
            sys.stderr.write(str(sys.exc_info()[1])+'\n')
            self.logger.error(str(sys.exc_info()[1]))

        return self.cols,data
            

class FocusBoxMeteo_sqldb(Telectric_sqldb):
    '''
    Class for mySQL database communication to manipulate focus box cabin meteo data.
    
    '''
    def __init__(self,host,port,db,table,user,passwd, **kwargs):
        super().__init__(host,port,db,table,user,passwd, **kwargs)
        self.host=host
        self.port=port
        self.dbname=db
        self.table=table
        self.user=user
        self.passwd=passwd
        self.db=None
        self.cur=None
        
        self.cols=[]
        self.cols.append('datetime')
        self.cols.append('T')
        self.cols.append('P')
        self.cols.append("RH")
        
    def create_table(self):
        '''
        '''
        
        sql="CREATE TABLE if not exists %s (id integer UNSIGNED AUTO_INCREMENT, " % self.table
        sql+="dt datetime COMMENT 'UTC DATE AND TIME',"
        sql+="RH float COMMENT 'relative humidity [%]',"
        sql+="T float COMMENT 'temperature [degC]',"
        sql+="P float COMMENT 'pressure [mbar]',"
        sql+="PRIMARY KEY (`id`))"
#         print(sql)
        try:
#             self.db.query(sql)
            self.cur.execute(sql)
            self.db.commit()
            self.logger.info("Created mysql table")
        except:
            self.db.rollback()
            sys.stderr.write(str(sys.exc_info()[1])+'\n')

            
