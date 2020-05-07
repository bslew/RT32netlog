'''
Created on May 7, 2020

@author: blew
'''
import sys
import os
import datetime
from distutils import util 

'''
FOR EXTRA MODULES LOCATED IN LOCAL DIRECTORIES 
for runs started without installing the package
'''
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1]))  

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from RT32logging.communication import config_file
from RT32logging.communication import UDPdatagrams

from RT32logging.database import storage
from RT32logging import logger, server

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg



def dict2str(d):
    if d==None:
        return 'None'
    s=''
    for key,val in sorted(d.items()):
        s=s+'{}={},'.format(key,val)
    return s
    
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


def getParser(program_license,program_epilog,program_version_message):
    parser = ArgumentParser(description=program_license, epilog=program_epilog, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]", default=0)
#         parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
#         parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
    parser.add_argument('-V', '--version', action='version', version=program_version_message)
#         parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')

    parser.add_argument("--serverUDP", dest="serverUDP", action='store_true', help='''
    run in server mode -- starts collecting data from UDP packages and storing them to mysql db.
    ''')
    parser.add_argument("--test1", dest="test1", action='store_true', help="test run 1")
    parser.add_argument("--saveToDB", help='True or False [default: %(default)s]', metavar="VALUE", type=str2bool, default='True')
    parser.add_argument("--saveToFile", help='True or False [default: %(default)s]', metavar="VALUE", type=str2bool, default='False')
#         parser.add_argument("--test", dest="test", action='store_true', help="test run")
    parser.add_argument("--setup", dest="setup", action='store_true', help="initialize configuration file")
    parser.add_argument("-o", "--outfile", dest="outfile", help='Output file name [default: %(default)s]', metavar="VALUE", type=str, nargs='?', default='WS800UMB.dat')
    

    return parser
