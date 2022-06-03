'''
A theoretical date search for Dataverse installations.
Inelegant.
'''
import datetime
import logging

import requests

TIMEFMT ='%Y-%m-%dT%H:%M:%SZ'

LOGGER = logging.getLogger(__name__)

LOGGER.setLevel(logging.DEBUG)
#FORMATTER = logging.Formatter(('%(asctime)s - %(levelname)s - %(name)s - '
#                               '%(funcName)s - %(message)s'))

FORMATTER = logging.Formatter(('{asctime} - {levelname} - {name} - '
                               '{funcName} - {message}'), style='{')

CONSOLE_OUT = logging.StreamHandler()
CONSOLE_OUT.setFormatter(FORMATTER)
LOGGER.addHandler(CONSOLE_OUT)

def get_total_records(baseurl:str = 'https://abacus.library.ubc.ca') -> int:
    '''
    Returns the total number of datasets in the root collection of a
    Dataverse installation (ie, total number of data sets)
    '''
    #just getting count, minimum is 1, which is the fastest
    req = requests.get(f'{baseurl}/api/search?q=*&type=dataset&per_page=1')
    req.raise_for_status()
    return req.json()['data']['total_count']

def get_all_recs(baseurl : str='https://abacus.library.ubc.ca',
                 per_page : int=100,
                 timeout : int=100) -> dict:
    '''
    Returns a single, non-paginated json from the Dataverse search API
    including all datasets (only).

    baseurl : str
        Base url of Dataverse installation
    per_page : int
        Number of results per page
    timeout  : int
        Request timeout in second
    '''
    recs = get_total_records(baseurl)
    if recs % per_page:
        npage = int(recs/per_page+1)
    else:
        npage = int(recs/per_page)

    #first page will be added to
    base = requests.get(f'{baseurl}/api/search?q=*&type=dataset&per_page={per_page}',
                        timeout=timeout)
    base.raise_for_status()
    out = base.json().copy()

    for page in range(1, npage):
    #for page in range(1, 3):
        LOGGER.info('Reading page %s of %s', page, npage)
        url = (f'{baseurl}/api/search?q=*&type=dataset&per_page={per_page}'
               f'&start={page*per_page}')
        base_add = requests.get(url, timeout=timeout)
        base_add.raise_for_status()
        out['data']['items'] += base_add.json()['data']['items'].copy()
    LOGGER.info('There are %s records', len(out["data"]["items"]))
    return out

def get_new_recs(allrecs:dict, last_check=str) -> list:
    '''
    Returns a list of records (ie, individual items from allrecs['data']['items']
    that are newer than last_check. Note that "newer" in this case is to the second,
    so searching for "2022" will pull up all records for 2022, as 2022 will be
    automatically encoded to 2022-01-01T00:00:00Z.

    last_check is a time string in '%Y-%m-%dT%H:%M:%SZ', or portions thereof. When including the
    time, make sure to use T.
    '''
    time_string = '0000-01-01T00:00:00Z'
    if len(last_check) < 4:
        LOGGER.error('Insufficient date information')
        raise ValueError('Insufficient date information')
    if len(last_check) < 20:
        last_check = last_check + time_string[len(last_check):]

    last = datetime.datetime.strptime(last_check, TIMEFMT)
    return [x for x in allrecs['data']['items'] if
            datetime.datetime.strptime(x.get('updatedAt'), TIMEFMT) > last]

if __name__ == '__main__':
    import pickle
    with open(('/Users/paul/Documents/Work/Projects'
               '/link_dv_studies/tmp/alldata.pickle'), 'wb') as fil:
        pickle.dump(get_all_recs(), fil)

    with open(('/Users/paul/Documents/Work/Projects'
               '/link_dv_studies/tmp/alldata.pickle'), 'rb') as fil:
        mallrecs = pickle.load(fil)
    #print(get_new_recs(mallrecs, '2022-04-01T10:00:23Z'))
    print([x['updatedAt'] for x in mallrecs['data']['items']
           if x['updatedAt'].startswith('2022-04')])
