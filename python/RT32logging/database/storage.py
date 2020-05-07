'''
Created on Jan 23, 2019

@author: blew
'''

import os,sys
# import _mysql
import datetime
import MySQLdb
from RT32logging.communication import config_file
from RT32logging import logger

def save_to_file(fname,data_dict, logger=None):
    '''
    save a dictionary to CSV file
    
    we import pandas here because it conflicts with pyqt5 via io.clipboards that import 
    QtCore4 from PyQt4.QtGui import QApplication
    '''
    import pandas as pd
    
    data_dict_tmp={}
    for k,v in data_dict.items():
        if isinstance(data_dict[k],list):
            data_dict_tmp[k]=list([v])
    
#     print(data_dict)
    header=True
    if os.path.isfile(fname):
        header=False
    
    try:
    
        with open(fname,"a") as f:
            df=pd.DataFrame.from_dict(data=data_dict_tmp, orient='columns')
            df.to_csv(f, sep='\t', encoding='utf-8',header=header)
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
    def __init__(self,host,port,dbname,table,user,passwd, **kwargs):
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
        self.cols=[]


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
        pass
        
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
        pass
    

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
        
    def create_table(self):
        '''
        '''
        
        
        sql="CREATE TABLE if not exists %s (id integer UNSIGNED AUTO_INCREMENT, " % self.table
        sql+="dt datetime COMMENT 'UTC DATE AND TIME',"
        sql+="RH float COMMENT 'relative humidity [%]',"
        sql+="T float COMMENT 'temperature [degC]',"
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

            
