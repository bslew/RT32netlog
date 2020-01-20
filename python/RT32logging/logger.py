'''
Created on Jul 17, 2019

@author: blew
'''
import os,sys
import logging
import datetime

def get_logging(name,fname,mode='a', lvl=logging.DEBUG):
    print("Starting logger {} with level {} (log file: {})".format(name,lvl,fname))
    
    # create logger with 'spam_application'
    logger = logging.getLogger(name)
    logger.setLevel(lvl)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    
    # create file handler which logs even debug messages
    if fname!=None:
        if os.path.dirname(fname)!='':
            os.makedirs(os.path.dirname(fname),exist_ok=True)
        fh = logging.FileHandler(fname,mode=mode)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(lvl)
    ch.setFormatter(formatter)
    
    # add the handlers to the logger
    logger.addHandler(ch)

    
    return logger
