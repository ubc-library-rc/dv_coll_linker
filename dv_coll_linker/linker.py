'''
Implementation of Dataverse study linking as Python functions.

Nothing fancy, but it does add log messages on failures.
'''

import logging
import requests

LOGGER = logging.getLogger(__name__)

def create_link(pid:str, parent:str, url:str, key:str, timeout:int=100) -> bool:
    '''
    Create a dataverse link of pid to collection parent.
    Returns true on successful (new) link.

    pid: str
        Dataverse persistent ID (handle or DOI)
    parent: str
        Parent (target) collection short name
    url: str
        Base url to Dataverse installation
    key: str
        API key for Dataverse installation. Note: linking requires superuser privileges.
    timeout: int
        Timeout in seconds
    '''
    try:
        linky = requests.put(f'{url}/api/datasets/:persistentId/link/{parent}',
                             headers={'X-Dataverse-key': key},
                             params={'persistentId':pid},
                             timeout=timeout)
        linky.raise_for_status()
        if linky.json().get('status') == 'ERROR':
            LOGGER.warning(linky.json().get('message'))
            return False
    except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError):
        LOGGER.exception('Requests Error')
        return False
    LOGGER.info('%s linked to %s', pid, parent)
    return True

def unlink(pid:str, parent:str, url:str, key:str, timeout:int=100) -> bool:
    '''
    Removes a Dataverse link of pid to collection parent.
    Returns true on successful removal.
    pid: str
        Dataverse persistent ID (handle or DOI)
    parent: str
        Parent (target) collection short name
    url: str
        Base url to Dataverse installation
    key: str
        API key for Dataverse installation. Note: linking requires superuser privileges.
    timeout: int
        Timeout in seconds
    '''
    try:
        unlinky = requests.delete(f'{url}/api/datasets/:persistentId/deleteLink/{parent}',
                                  headers={'X-Dataverse-key': key},
                                  params={'persistentId':pid},
                                  timeout=timeout)
        unlinky.raise_for_status()
        if unlinky.json().get('status') == 'ERROR':
            LOGGER.warning(unlinky.json().get('message'))
            return False
    except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError):
        LOGGER.exception(('Requests Error. 404 errors (usually) indicate '
            '              that the link did not exist in the first place.'))
        LOGGER.debug(unlinky.json())
        return False
    LOGGER.info('%s unlinked from %s', pid, parent)
    return True
