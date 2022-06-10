'''
Collection level linker for Dataverse data repository software.

As the current (June 2022) version of [Dataverse](https://dataverse.org) v5.10
has a bug which has apparently disabled collection level linking.
For more information on this bug, please see the Dataverse User's Community
Google group at:
<https://groups.google.com/g/dataverse-community/c/DDmVelt3Zfk>:

This part of the dv_coll_linker package will automate *per-study* linking for
collections which are listed as being linked, restoring the functionality found
in Dataverse v4+.

This involves *no* changes to the underlying code. Links are tracked in a
user specified SQLite database, and linking is performed via the Dataverse API.

There are several caveats to this software:

1. Link tables can only be populated automatically if the software has
access to the Dataverse PostgreSQL database which usually means that the
software will run on the server which hosts the database. This is not techincally
required, though, and if the collection and children tables are populated manually,
either by importing a PostgreSQL dump or by entering them labouriously by hand,
the software will function.

 This means, however, that new collection links will not be discovered automatically
 and will need to be added by hand or by reimporting the tables.

2. The software requires superuser Dataverse API keys, as linking is a superuser
function. It's theoretically possible that a superuser does not have direct server
access, so if that is the case, please re-read number 1 and speak to the administrator
of the Datavese server to obtain the initial data with which to populate your
salite database.

3. The software can be run repeatedly to include new links or remove old ones (although
old links should automatically be removed if a study is deleted anyway, as it should
be purged from the PostgreSQL database. The easiest way to do this is to schedule it
to run at regular intervals, such as by using crontab or the windows scheduler.

 There are other ways to daemonize, but this is supposed to be a stopgap and not a
 permanent solution, so they have not been implemented.

4. Unlinking code is commented out in the code below. See also linker.unlink.
'''

import argparse
import datetime
import logging
import logging.handlers
import os

import dv_coll_linker
from dv_coll_linker import linker
from dv_coll_linker import monitor
from dv_coll_linker import search

#FORMATTER = logging.Formatter(('%(asctime)s - %(levelname)s - %(name)s - '
#                               '%(funcName)s - %(message)s'))
#I like this formatting better
FORMATTER = logging.Formatter(('{asctime} - {levelname} - {name} - '
                               '{funcName} - {message}'), style='{')
LEVEL = logging.INFO
TIMEFMT = '%Y-%m-%dT%H:%M:%SZ'
DEFAULTDATE = '0001-01-01T00:00:00Z' #publishing predating this is unlikely

def argument_parser() -> argparse.ArgumentParser:
    '''
    Argument parser for command line script.
    '''
    parser = argparse.ArgumentParser(description=('Study level linker for Dataverse '
                                     'installations. Finds collection level links and '
                                     'automatically adds study-level links for each '
                                     'found collection. Addresses issues as noted here '
                                     'https://groups.google.com/g/dataverse-community/'
                                     'c/DDmVelt3Zfk'))
    parser.add_argument('-u', '--url',
                        help=('URL to base Dataverse installation. '
                              'Default https://abacus.library.ubc.ca'),
                        default='https://abacus.library.ubc.ca'
                        )
    parser.add_argument('-d', '--dvdbname',
                        help=('Dataverse PostgreSQL Database name. '
                              'Defaults to dvndb. If not run on the '
                              'server hosting a Dataverse installation, the program '
                              'will attempt to connect to PostgreSQL. It will likely '
                              'fail if your security is good and you will need to '
                              'populate the collection and children database manually.'),
                        default='dvndb')
    parser.add_argument('-y', '--user',
                        help=('PostgreSQL database username. Defaults to dvnapp'),
                        default='dvnapp')
    parser.add_argument('-w', '--password',
                        help=('PostgreSQL database password for --user.'
                              'Defaults to 123456. No, of course it doesn\'t. '
                              'There is no default password.'),
                        default=None)
    parser.add_argument('-p', '--port',
                        help=('PostgreSQL port. Defaults to 5432'),
                        type=int,
                        default=5432)
    parser.add_argument('-r', '--dbhost',
                        help=('Database host. Defaults to localhost. If using another host '
                              'use *just* the hostname.'),
                        default='localhost')
    parser.add_argument('-k', '--key',
                        help=('Dataverse installation API key. This *must* be a '
                              'superuser API key. Non-superuser keys will fail. '
                              'If you don\'t know if you have superuser keys, you '
                              'are probably not a superuser.')
                        )
    parser.add_argument('-b','--dbname',
                        help=('Local sqlite3 link database. Defaults to ~/dv_links.sqlite3'),
                        default=os.path.expanduser('~/dv_links.sqlite3'))
    parser.add_argument('-l', '--log',
                        help=('Log directory. Defaults to ~/logs. Log is saved '
                              'as dv_coll_linker.log'),
                        default=os.path.expanduser('~/logs'))
    ##Do I really want to do it this way, or do I just add it to crontab? No
    #parser.add_argument('-z', '--daemonize',
    #                    help=('Run as daemon'),
    #                    action='store_true')
    #parser.add_argument('-t', '--interval',
    #                    help=('Update check interval in minutes if daemonized. '
    #                          'Default: 10'),
    #                    default=10)
    parser.add_argument('-v''--version', action='version',
                        version='%(prog)s '+dv_coll_linker.__version__,
                        help='Show version number and exit')
    return parser

def console_logger(level:int) -> logging.getLogger:
    '''
    Logging to console only.
    '''
    logger = logging.getLogger()#Use root logger to format submodule logs
    console_out = logging.StreamHandler()
    console_out.setFormatter(FORMATTER)
    logger.addHandler(console_out)
    logger.setLevel(level)
    return logger

def rotating_logger(path:str, level:int, fname='dv_coll_linker.log') -> logging.getLogger:
    '''
    Rotating log called called logname, where logname is the full
    path (ie, /path/to/
    '''
    #logger = logging.getLogger(__name__)#if you don't want formatting for submodules
    logger = logging.getLogger()#root logger
    for name in ['linker', 'monitor', 'search']:
        logging.getLogger(name).setLevel(LEVEL)

    rotator = logging.handlers.RotatingFileHandler(filename=os.path.join(path,fname),
                                                   maxBytes=10*1024**2,
                                                   backupCount=10)
    logger.addHandler(rotator)
    rotator.setFormatter(FORMATTER)
    logger.setLevel(level)
    return logger

def main():
    '''
    Primary
    '''
    args = argument_parser().parse_args()
    os.makedirs(os.path.split(os.path.expanduser(args.dbname))[0], exist_ok=True)
    os.makedirs(os.path.expanduser(args.log), exist_ok=True)
    mainlog = rotating_logger(args.log, LEVEL)
    #mainlog = console_logger(LEVEL)

    #create database if if doesn't exist
    conn = monitor.init(os.path.expanduser(args.dbname))

    #is debugging
    #cursor = conn.cursor()
    #cursor.execute('DELETE FROM raw_data')
    #cursor.execute('DELETE FROM status')

    #Populate with data if running on server, otherwise nothing
    collections, children = monitor.get_pg_data(args.dvdbname, args.user,
                                                args.password, args.dbhost,
                                                args.port)
    if collections:
        monitor.populate_db(conn, collections, children)

    #get link relationships
    family_tree = monitor.fetch_parent_child_collections(conn)

    #Get last count
    date, count = monitor.get_last_count(conn)
    mainlog.info('Last count: %s', count)
    if not date:
        date = DEFAULTDATE

    #Check to see if we need to update
    newcount = search.get_total_records(args.url)
    newdate = datetime.datetime.now().strftime(TIMEFMT)
    mainlog.debug('count: %s,  newdate: %s, date: %s',
                 count, newdate, date)

    if newcount != count: #!= or >? I suppose it's possible that it can shrink
        mainlog.info('Total number of new records: %s', newcount)
        allrecs = search.get_all_recs(args.url)
        #if we had to download, we should save the data set
        #status has to come first because it has the primary key
        monitor.write_status(conn, newdate, newcount)
        monitor.write_search_data(conn, newdate, allrecs)
        #Update the list of all studies in the Dataverse installation
        for rec in allrecs['data']['items']:
            monitor.add_single_study(conn, **rec)
        #Strip nonexistent studies out just to keep things current
    else:
        allrecs = monitor.get_search_data(conn)

    monitor.purge_nonexistent(conn, allrecs)

    #And now the magic happens
    for branch in family_tree:
        #Checking by time example
        #new = [x for x in allrecs['data']['items'] if
        #      datetime.datetime.strptime(x['updatedAt'], TIMEFMT) >
        #      datetime.datetime.strptime(date, TIMEFMT) and
        #      x['identifier_of_dataverse'] == branch[1]]
        #However . . .
        #Checking by time doesn't work if collections are deleted
        #Link must not currently exist
        #new = [x for x in allrecs['data']['items'] if
        #       x['identifier_of_dataverse'] == branch[1]
        #       and not monitor.check_link(conn, x['global_id'])]

        #for item in new:
        for item in [x for x in allrecs['data']['items'] if
                     x['identifier_of_dataverse'] == branch[1]
                     and not monitor.check_link(conn, x['global_id'],
                                                branch[0], branch[1])]:

            mainlog.debug('%s\t%s\t%s\t%s',
                         item['global_id'], branch[0],
                         branch[1], item['identifier_of_dataverse'])
            mainlog.info('Creating link %s to %s', item["global_id"], branch[0])
            if linker.create_link(item['global_id'], branch[0], args.url, args.key):
                monitor.add_link(conn, item['global_id'], branch[0], branch[1])

    #Unlink and remove old links from deleted collections
    for gone in monitor.check_unlink(conn):
        #mainlog.info('Removing link for %s', gone)
        if linker.unlink(gone[0], gone[1], args.url, args.key):
            mainlog.info('Removed link for %s', gone)
            monitor.remove_link(conn, *gone)
            mainlog.info('Removed %s from links table', gone[0])
    conn.commit()
    conn.close()

def testme():
    '''
    This is just a test to see if the hook worked
    '''
    parser = argument_parser()
    args = parser.parse_args()
    print(args.dbname)
    print('I have been sorely tested')
    logger = console_logger(logging.DEBUG)
    #logger = rotating_logger('/Users/paul/tmp/testme.log', logging.DEBUG)
    #logger.debug('DEBUG')
    #logger.info('INFO')
    #logger.warning('WARNING')
    #logger.error('ERROR')
    #logger.critical('CRITICAL')
    #logger.info('Not printing exception')
    logger.info('here is a representation of set length %s',len({1,3,9}))
    logger.info('view set: %s',{1,32,389,32})
    logger.info('multiple values %s, %s', 'paul', {2,3,798})
    #import sqlite3
    #conn = sqlite3.Connection(('/Users/paul/Documents/Work'
    #                           '/Projects/dv_coll_linker/tmp/testme_del.db'))
    #for gone in monitor.check_unlink(conn):
    #    if linker.unlink(gone[0], gone[1], args.url, args.key):
    #        monitor.remove_link(conn, *gone)
    #logger.info(monitor.check_unlink(conn))

if __name__ == '__main__':
    main()
