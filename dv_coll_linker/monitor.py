'''
Database creation for study level links in a Dataverse installation.

Required because collection level links were apparently broken in v5.? +

This module creates the database and, if running on the server with a Dataverse
installation, can automatically add any detected linked collections for use with the
linker and search modules.

This module basically acts as a singleton object on import.

'''
import json
import logging
import sqlite3
#import sys
import pkg_resources

LOGGER = logging.getLogger(__name__)

#if sys.version_info[1] >= 7:
#    import importlib.resources as ilib
#    try:
#        from . import data
#    except ImportError:
#        import data
#else:
#    LOGGER.warning('Using Python 3.6 or below')
#    #import importlib_resources as ilib
#    import pkg_resources

try:
    import psycopg2
    NOPG = False
except (ModuleNotFoundError, ImportError):
    NOPG = True

def init(dbname:str) -> sqlite3.Connection:
    '''Intialize database with {dbname}.'''
    #sqlite3.IntegrityError

    #if sys.version_info[1] >= 7:
    #    create = ilib.read_text(data, 'create_tables.sql').split('\n\n')
    #    #create = [x.replace('\n', ' ') for x in create]
    #else:
    #    #pkg_resources.resource_filename('dv_coll_linker', 'data/create_tables.sql')
    #    with open(pkg_resources.resource_filename('dv_coll_linker',
    #                                              'data/create_tables.sql'),
    #            'r', encoding='utf-8') as fil:
    #        create = fil.read().split('\n\n')
    with open(pkg_resources.resource_filename('dv_coll_linker',
                                              'data/create_tables.sql'),
            'r', encoding='utf-8') as fil:
        create = fil.read().split('\n\n')
        LOGGER.info('Read database initialization SQL')
        LOGGER.info('%s', create)
    conn = sqlite3.Connection(dbname)
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    for table in create:
        cursor.execute(table)
        conn.commit()
    LOGGER.info('Initialized database')
    return conn

def get_pg_data(dbname:str, user:str, password:str,
                host:str='localhost', port:int=5432) -> (list, list):
    '''
    Grabs linking data from postgres database. Returns two lists used
    to populate the collections and children tables
    '''
    #pconn=psycopg2.connect(dbname='dvndb', user='dvnapp', password='')
    if NOPG:
        LOGGER.warning('Did not connect to PostgreSQL database; no psycopg2')
        return None, None

    try:
        pconn=psycopg2.connect(dbname=dbname, user=user,
                               password=password,
                               host=host, port=port)
        pcursor = pconn.cursor()
        pcursor.execute('SELECT id, alias, name FROM dataverse;')
        collections = pcursor.fetchall()
        pcursor.execute(('SELECT  dl.linkingdataverse_id AS parent_id, '
                         'parent.alias AS parent_alias, '
                         'dl.dataverse_id AS child_id, dataverse.alias AS child_alias '
                         'FROM dataverselinkingdataverse AS dl '
                         'INNER JOIN dataverse ON dataverse.id=dl.dataverse_id '
                         'INNER JOIN dataverse AS parent '
                         'ON parent.id = dl.linkingdataverse_id ORDER BY parent_id;'))
        children = pcursor.fetchall()
        pconn.close()
        LOGGER.info('Successfully parsed PostgreSQL database')
        return collections, children

    except psycopg2.OperationalError:
        LOGGER.exception('Postgres Error')
        LOGGER.critical(('Params – dbname: %s, user: %s, password: %s, '
                         'host:%s, port: %s'), dbname, user, '[redacted]',
                         host, port)
        return None, None

def populate_db(conn:sqlite3.Connection,
                collections:list, children:list)-> bool:
    '''
    Updates the database with linking dataverse info
    '''
    cursor = conn.cursor()
    orig_coll = set(cursor.execute('SELECT * FROM collections;').fetchall())
    orig_children = set(cursor.execute('SELECT * FROM children').fetchall())
    for rec in collections:
        try:
            cursor.execute('INSERT INTO collections VALUES (?, ?, ?)', rec)
        except sqlite3.IntegrityError:
            cursor.execute(('UPDATE collections SET id=?, alias=? , name=? '
                                'WHERE alias = ?'), list(rec) +[rec[1]])
        conn.commit()
    for rec in children:
        try:
            cursor.execute('INSERT INTO children VALUES (?, ?, ?, ?)', rec)
        except sqlite3.IntegrityError:
            cursor.execute(('UPDATE children SET '
                            'parent_id=?, parent_alias=?, '
                            'child_id=?, child_alias=? '
                            'WHERE parent_alias=? AND child_alias=?'),
                            list(rec) + [rec[1], rec[3]])
        conn.commit()
    #set theory
    cursor.executemany(('DELETE FROM children WHERE parent_id=? AND parent_alias=?'
                        'AND child_id=? AND child_alias=?;'),
                        orig_children - {tuple(x) for x in children})
    cursor.executemany(('DELETE from collections WHERE id=? AND alias=? '
                        'AND name=?'), orig_coll-{tuple(x) for x in collections})
    conn.commit()

def fetch_parent_child_collections(conn:sqlite3.Connection)->list:
    '''
    Returns a list of (parent, child) collection pairs
    '''
    cursor = conn.cursor()
    cursor.execute('SELECT parent_alias, child_alias FROM children;')
    return cursor.fetchall()

def add_single_study(conn:sqlite3.Connection, **kwargs) -> None:
    '''
    Writes metadata from a single study to the database. Supply the
    JSON from the record as keyword arguments.
    '''
    values = (kwargs.get('global_id'),
              kwargs.get('identifier_of_dataverse'),
              kwargs.get('name'),
              kwargs.get('createdAt'),
              kwargs.get('updatedAt'))
    cursor = conn.cursor()
    cursor.execute('SELECT pid, updated_time FROM studies WHERE pid =?;',
                   (values[0],))
    out = cursor.fetchone()
    if out and out[1] == values[4]:#record exists
        LOGGER.debug('Existing study record: %s', values[0])
        return
    if out and out[1] != values[4]:#record updated
        LOGGER.debug('Updated study record: %s', values[0])
        cursor.execute(('UPDATE studies SET pid=?, dv_alias=?, title=?, '
                        'created_time=?, updated_time=? WHERE pid=?;'),
                        list(values) + [values[0]])
        conn.commit()
        return
    #new record
    cursor.execute('INSERT INTO studies VALUES (?, ?, ?, ?, ?);',
                   values)

    LOGGER.info('Added record to studies: %s', values)
    conn.commit()
    LOGGER.debug('Committed transaction')
    return

def purge_nonexistent(conn:sqlite3.Connection, allrecs:dict) -> None:
    '''
    Removes PIDS that don't appear in allrecs['data']['items']
    '''
    newpids = {x['global_id'] for x in allrecs['data']['items']}
    cursor = conn.cursor()
    #oldpids = set(cursor.execute('SELECT DISTINCT pid FROM studies;').fetchall())

    oldpids = {x[0] for x in cursor.execute('SELECT DISTINCT pid FROM studies;').fetchall()}
    if not oldpids:
        return
    #remove the difference of sets
    diff = oldpids - newpids
    LOGGER.debug('oldpids: %s', oldpids)
    LOGGER.debug('newpids: %s', newpids)
    LOGGER.warning('PIDs to purge: %s', diff)
    if diff:
        LOGGER.info('Purging %s old records', len(diff))
        cursor.executemany('DELETE FROM studies WHERE pid=?;', diff)
        LOGGER.info('Records purged from *studies*: %s', diff)
        cursor.executemany('DELETE FROM links WHERE pid=?;', diff)
        LOGGER.info('Records purged from *links*: %s', diff)
    conn.commit()

def check_link_old(conn:sqlite3.Connection, pid:str) -> bool:
    '''
    Check for existence of link. Returns True if link exists, else False:
    '''
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM links WHERE pid=?;', (pid,))
    if cursor.fetchone():
        return True
    return False

def check_link(conn:sqlite3.Connection, pid:str, parent:str, child:str) -> bool:
    '''
    Check for existence of link. Returns True if link exists, else False:
    '''
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM links WHERE pid=? AND parent=? AND child=?;',
                   (pid, parent, child))
    if cursor.fetchone():
        return True
    return False

def add_link(conn:sqlite3.Connection, pid:str, parent: str, child: str) -> None:
    '''
    desc
    '''
    cursor = conn.cursor()
    cursor.execute('INSERT INTO links VALUES(?, ?, ?);',
                   (pid, parent, child))
    conn.commit()

def check_unlink(conn:sqlite3.Connection)-> tuple:
    '''
    Returns persistent IDs where a link exists but a parent/child relationship
    does not. That is, it detects the items in a collection that has been unlinked
    from a parent
    '''
    cursor = conn.cursor()
    children = set(cursor.execute('SELECT parent_alias, child_alias FROM children').fetchall())
    checkme = set(cursor.execute('SELECT parent, child FROM links').fetchall())
    diff = checkme - children
    LOGGER.debug('children: %s',children)
    LOGGER.debug('Current links: %s', checkme)
    LOGGER.debug('Diff:%s', diff)
    pids = []
    for coll in diff:
        cursor.execute('SELECT * FROM links WHERE parent=? AND child=?', coll)
        pids += list(cursor.fetchall())
    LOGGER.info('PIDs to unlink and delete from table: %s', pids)
    return tuple(pids)

def remove_link(conn:sqlite3.Connection, pid:str, parent: str, child: str) -> None:
    '''
    desc
    '''
    cursor = conn.cursor()
    cursor.execute('DELETE FROM links WHERE pid=? AND parent=? AND child=?;',
                   (pid, parent, child))
    conn.commit()

def write_status(conn:sqlite3.Connection, last_check:str, last_count: int)->None:
    '''
    Writes timestamp and total file count to database
    '''
    cursor = conn.cursor()
    cursor.execute('INSERT INTO status VALUES (?, ?)', (last_check, last_count))
    conn.commit()

def get_last_count(conn:sqlite3.Connection) -> (str, int):
    '''
    Returns the last count of studies in a Dataverse installation
    '''
    cursor = conn.cursor()
    cursor.execute('SELECT last_check, last_count FROM status ORDER BY last_check DESC LIMIT 1')
    last_count = cursor.fetchone()
    if not last_count:
        return None, 0
    return last_count

def get_search_data(conn:sqlite3.Connection)->dict:
    '''
    Retrieves last harvested search results
    '''
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM raw_data ORDER BY last_check DESC LIMIT 1')
    outdata = cursor.fetchone()
    if outdata:
        return json.loads(outdata[1])
    return None

def write_search_data(conn:sqlite3.Connection, last_check:str, search_json:dict)->None:
    '''
    Writes the current study search JSON to the database
    '''
    cursor = conn.cursor()
    cursor.execute('INSERT INTO raw_data VALUES (?, ?)',
                   (last_check, json.dumps(search_json)))
    conn.commit()

##based on time.now() - 1d/1h/10min if no time provided

if __name__ == '__main__':
    pass
