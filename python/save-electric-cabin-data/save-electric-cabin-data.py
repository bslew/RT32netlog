#!/usr/bin/env python
'''
 -- save UDP data from local network to DB on galaxy

 is a description

It defines classes_and_methods

@author:     Bartosz Lew

@copyright:  2020 UMK-IA. All rights reserved.

@license:    GPL

@contact:    blew@astro.uni.torun.pl
@deffield    updated: Updated
'''

import sys
import os
import datetime

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from RT32logging.communication import config_file
from RT32logging.communication import UDPdatagrams

from RT32logging.database import storage
from RT32logging import logger, server
        
__all__ = []
__version__ = 0.1
__date__ = '2020-01-20'
__updated__ = '2020-01-20'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

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

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_epilog ='''
    
Examples:

show examples how to use the program... 
'''
    program_license = '''%s

  Created by Bartosz Lew on %s.
  Copyright 2020 UMK-IA. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
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
        parser.add_argument("--storeDB", help='True or False [default: %(default)s]', metavar="VALUE", type=str2bool, default='True')
        parser.add_argument("--storeFile", help='True or False [default: %(default)s]', metavar="VALUE", type=str2bool, default='False')
#         parser.add_argument("--test", dest="test", action='store_true', help="test run")
        parser.add_argument("--setup", dest="setup", action='store_true', help="initialize configuration file")
        parser.add_argument("-o", "--outfile", dest="outfile", help='Output file name [default: %(default)s]', metavar="VALUE", type=str, nargs='?', default='WS800UMB.dat')

        # Process arguments
        args = parser.parse_args()

#         paths = args.paths
        verbose = args.verbose
#         recurse = args.recurse
#         inpat = args.include
#         expat = args.exclude

        logfile=os.environ['HOME']+os.path.sep+__file__+'.log'
        log = logger.get_logging('Electric cabin',logfile)
        log.info(__file__+": === NEW RUN ===")

        if verbose > 0:
            log.debug("Verbose mode on")
            log.debug("args.storeDB: {}".format(args.storeDB))
            log.debug("args.storeFile: {}".format(args.storeFile))
            log.debug('Log file: {}'.format(logfile))



        if args.setup:
            cfg=None
            if os.path.isfile(config_file.configFile):
                log.warning('Config file ({}) already exists. Will not overwrite.')
                log.warning('Remove config file manually and run this program again if you want to start a fresh config file.')
                cfg=config_file.readConfigFile()
            else:
                cfg=config_file.writeConfigFile(config_file.configFile)
                log.info("Configuration done. ")
            db = storage.Telectric_sqldb(host=cfg['DB']['host'], port=cfg['DB']['port'],
                                 db=cfg['DB']['db'],table=cfg['DB']['table'],
                                 user=cfg['DB']['user'],
                                 passwd=cfg['DB']['passwd'],
                                 )
            db.connect()
            if verbose>0:
                log.info("DB connected: {}".format(db.connected()))
            db.create_table()
            

        if args.serverUDP:
            cfg=config_file.readConfigFile()
            host=cfg['ELECTRIC_CABIN_DATA']['udp_ip'].split(',')[0]
            port=cfg['ELECTRIC_CABIN_DATA']['udp_port'].split(',')[0]
            db=None

            if args.storeDB:
                db = storage.Telectric_sqldb(host=cfg['DB']['host'], port=cfg['DB']['port'],
                                     db=cfg['DB']['db'],table=cfg['DB']['table'],
                                     user=cfg['DB']['user'], 
                                     passwd=cfg['DB']['passwd'],
                                     logger=log)
                db.connect()

            for data in server.UDPserver(host,port,log):
                readout=UDPdatagrams.convert_UDP_datagram_electric_cabin(data)
                
                if args.test1:
                    dataRef={}
                if args.verbose:
                    log.debug('New datagram')
                    log.debug('{}'.format(dict2str(readout)))
                if args.storeFile:
                    storage.save_to_file(args.outfile,readout)
                if args.storeDB:
                    db.store(readout)


        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = '_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())