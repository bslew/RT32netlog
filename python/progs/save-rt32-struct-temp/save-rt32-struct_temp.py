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
import json
from distutils import util 

'''
FOR EXTRA MODULES LOCATED IN LOCAL DIRECTORIES 
for runs started without installing the package
'''
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))  
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1]))  

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

# from RT32logging.communication import config_file
# from RT32logging.communication import UDPdatagrams
# 
# from RT32logging.database import storage
# from RT32logging import logger, server
# from RT32logging.common import commons

import RT32logging
        
__all__ = []
__version__ = 0.1
__date__ = '2020-01-20'
__updated__ = '2020-01-20'

DEBUG = 1
TESTRUN = 0
PROFILE = 0


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

    program_log_title='StructTempMonitor'
    
    program_module_name='STRUCT_TEMP'


    try:
        # Setup argument parser
        parser=RT32logging.common.commons.getParser(program_license,program_epilog,program_version_message)
        # Process arguments
        args = parser.parse_args()
        verbose = args.verbose

        logfile=os.environ['HOME']+os.path.sep+__file__+'.log'
        lvl=RT32logging.logger.logging.INFO
        if verbose>1:
            lvl=RT32logging.logger.logging.DEBUG
        log = RT32logging.logger.get_logging(program_log_title,logfile,lvl=lvl)
        log.info(__file__+": === NEW RUN ===")

        configSection=program_module_name
        cfg=RT32logging.communication.config_file.readConfigFile()
        args.saveToDB=RT32logging.common.commons.str2bool(RT32logging.communication.config_file.getOption('saveToDB', cfg,configSection,args.saveToDB))

        if verbose > 1:
            log.debug("Verbose mode on")
            log.debug("args.saveToDB: {}".format(args.saveToDB))
#             log.debug("will save to DB: {}".format(saveToDB))
            log.debug("args.saveToFile: {}".format(args.saveToFile))
            log.debug('Log file: {}'.format(logfile))
#             for x in json.loads(cfg[program_module_name]['required_keys']):
#                 print(x)



        if args.setup:
            cfg=None
            if os.path.isfile(RT32logging.communication.config_file.configFile):
                log.warning('Config file ({}) already exists. Will not overwrite.'.format(RT32logging.communication.config_file.configFile))
                log.warning('Remove config file manually and run this program again if you want to start a fresh config file.')
                cfg=RT32logging.communication.config_file.readConfigFile()

                log.info("Configuring DB table")
                db = RT32logging.database.storage.FocusBoxMeteo_sqldb(
                    host=cfg['DB']['host'], port=cfg['DB']['port'],
                    db=cfg['DB']['db'],table=cfg[configSection]['table'],
                    user=cfg['DB']['user'],
                    passwd=cfg['DB']['passwd'],
                    logger=log,
                    )
                db.connect()
                if verbose>0:
                    log.info("DB connected: {}".format(db.connected()))
                db.create_table()
            
            else:
                cfg=RT32logging.communication.config_file.writeConfigFile(config_file.configFile)
                log.info("Configuration done. ")
                log.info("Now you need to edit the db password in config file ({}) and run the setup again to create DB table.".format(config_file.configFile))
                log.info("Remember to chmod 600 {}* after you edit the file.".format(config_file.configFile))
            
                        
        if args.serverUDP:
            keys={'required' : json.loads(cfg[program_module_name]['required_keys']), 
                  'target' : json.loads(cfg[program_module_name]['db_keys'])}
#             server.startServerUDP(cfg, configSection, args, storage.FocusBoxMeteo_sqldb,UDPdatagrams.convert_UDP_datagram_focus_cabin,keys,log)
            RT32logging.server.startServerUDP(cfg, configSection, args, 
                                              RT32logging.database.storage.FocusBoxMeteo_sqldb,
                                              RT32logging.communication.UDPdatagrams.convert_UDP_datagram,
                                              keys,log)

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