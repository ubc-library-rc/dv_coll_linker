<a name="dv_coll_linker"></a>
# Complete API Reference

## dv\_coll\_linker

Dataverse collection linker for Dataverse 5.6+ to emulate the
functionality of the collection linking in which functioned
correctly in Dataverse 4.20

In essence, this software can create individual item links
where collection links were. That is, for a collection containing
10 files, this product will create individual links to the
10 files instead of just using the (non-functioning) link
to the collection.

search: institutes date level searching via Dataverse's
search API

linker: Python implementation of linking and unlinking
data sets

monitor: SQLite monitor of collection level linking.

app: Implementation of a standalone application which can
run at intervals to emulate the collection linking feature.

If run on the server hosting a Dataverse instance, it can
read the collection level linking from the `datverselinkingdataverse`
table if supplied the proper credentials for the PostreSQL database
underlying Dataverse.

If connections fail or the product is run on a platform with no
access to the PostgreSQL database, the product will still function
but the underlying SQLite database holding dataverse and link information
will need to be populated manually. That is, the tables
`collections` and `children` will need to be manually populated.

Similarly, if changes are made to the collection structure, such
as an unlinked collection, if the PostgreSQL database cannot be read then
the changes must be added to the SQLite database manually.

<a name="dv_coll_linker.monitor"></a>

## dv\_coll\_linker.monitor

Database creation for study level links in a Dataverse installation.

Required because collection level links were apparently broken in v5.? +

This module creates the database and, if running on the server with a Dataverse
installation, can automatically add any detected linked collections for use with the
linker and search modules.

This module basically acts as a singleton object on import.

<a name="dv_coll_linker.monitor.init"></a>

##### init

```python
init(dbname: str) -> sqlite3.Connection
```

Intialize database with {dbname}.

<a name="dv_coll_linker.monitor.get_pg_data"></a>

##### get\_pg\_data

```python
get_pg_data(dbname: str, user: str, password: str, host: str = 'localhost', port: int = 5432) -> (list, list)
```

Grabs linking data from postgres database. Returns two lists used
to populate the collections and children tables

<a name="dv_coll_linker.monitor.populate_db"></a>

##### populate\_db

```python
populate_db(conn: sqlite3.Connection, collections: list, children: list) -> bool
```

Updates the database with linking dataverse info

<a name="dv_coll_linker.monitor.fetch_parent_child_collections"></a>

##### fetch\_parent\_child\_collections

```python
fetch_parent_child_collections(conn: sqlite3.Connection) -> list
```

Returns a list of (parent, child) collection pairs

<a name="dv_coll_linker.monitor.add_single_study"></a>

##### add\_single\_study

```python
add_single_study(conn: sqlite3.Connection, **kwargs) -> None
```

Writes metadata from a single study to the database. Supply the
JSON from the record as keyword arguments.

<a name="dv_coll_linker.monitor.purge_nonexistent"></a>

##### purge\_nonexistent

```python
purge_nonexistent(conn: sqlite3.Connection, allrecs: dict) -> None
```

Removes PIDS that don't appear in allrecs['data']['items']

<a name="dv_coll_linker.monitor.check_link_old"></a>

##### check\_link\_old

```python
check_link_old(conn: sqlite3.Connection, pid: str) -> bool
```

Check for existence of link. Returns True if link exists, else False:

<a name="dv_coll_linker.monitor.check_link"></a>

##### check\_link

```python
check_link(conn: sqlite3.Connection, pid: str, parent: str, child: str) -> bool
```

Check for existence of link. Returns True if link exists, else False:

<a name="dv_coll_linker.monitor.add_link"></a>

##### add\_link

```python
add_link(conn: sqlite3.Connection, pid: str, parent: str, child: str) -> None
```

desc

<a name="dv_coll_linker.monitor.check_unlink"></a>

##### check\_unlink

```python
check_unlink(conn: sqlite3.Connection) -> tuple
```

Returns persistent IDs where a link exists but a parent/child relationship
does not. That is, it detects the items in a collection that has been unlinked
from a parent

<a name="dv_coll_linker.monitor.remove_link"></a>

##### remove\_link

```python
remove_link(conn: sqlite3.Connection, pid: str, parent: str, child: str) -> None
```

desc

<a name="dv_coll_linker.monitor.write_status"></a>

##### write\_status

```python
write_status(conn: sqlite3.Connection, last_check: str, last_count: int) -> None
```

Writes timestamp and total file count to database

<a name="dv_coll_linker.monitor.get_last_count"></a>

##### get\_last\_count

```python
get_last_count(conn: sqlite3.Connection) -> (str, int)
```

Returns the last count of studies in a Dataverse installation

<a name="dv_coll_linker.monitor.get_search_data"></a>

##### get\_search\_data

```python
get_search_data(conn: sqlite3.Connection) -> dict
```

Retrieves last harvested search results

<a name="dv_coll_linker.monitor.write_search_data"></a>

##### write\_search\_data

```python
write_search_data(conn: sqlite3.Connection, last_check: str, search_json: dict) -> None
```

Writes the current study search JSON to the database

<a name="dv_coll_linker.linker"></a>

## dv\_coll\_linker.linker

Implementation of Dataverse study linking as Python functions.

Nothing fancy, but it does add log messages on failures.

<a name="dv_coll_linker.linker.create_link"></a>

##### create\_link

```python
create_link(pid: str, parent: str, url: str, key: str, timeout: int = 100) -> bool
```

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

<a name="dv_coll_linker.linker.unlink"></a>

##### unlink

```python
unlink(pid: str, parent: str, url: str, key: str, timeout: int = 100) -> bool
```

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

<a name="dv_coll_linker.app"></a>

## dv\_coll\_linker.app

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

<a name="dv_coll_linker.app.argument_parser"></a>

##### argument\_parser

```python
argument_parser() -> argparse.ArgumentParser
```

Argument parser for command line script.

<a name="dv_coll_linker.app.console_logger"></a>

##### console\_logger

```python
console_logger(level: int) -> logging.getLogger
```

Logging to console only.

<a name="dv_coll_linker.app.rotating_logger"></a>

##### rotating\_logger

```python
rotating_logger(path: str, level: int, fname='dv_coll_linker.log') -> logging.getLogger
```

Rotating log called called logname, where logname is the full
path (ie, /path/to/

<a name="dv_coll_linker.app.main"></a>

##### main

```python
main()
```

Primary

<a name="dv_coll_linker.app.testme"></a>

##### testme

```python
testme()
```

This is just a test to see if the hook worked

<a name="dv_coll_linker.search"></a>

## dv\_coll\_linker.search

A theoretical date search for Dataverse installations.
Inelegant.

<a name="dv_coll_linker.search.get_total_records"></a>

##### get\_total\_records

```python
get_total_records(baseurl: str = 'https://abacus.library.ubc.ca') -> int
```

Returns the total number of datasets in the root collection of a
Dataverse installation (ie, total number of data sets)

<a name="dv_coll_linker.search.get_all_recs"></a>

##### get\_all\_recs

```python
get_all_recs(baseurl: str = 'https://abacus.library.ubc.ca', per_page: int = 100, timeout: int = 100) -> dict
```

Returns a single, non-paginated json from the Dataverse search API
including all datasets (only).

baseurl : str
    Base url of Dataverse installation
per_page : int
    Number of results per page
timeout  : int
    Request timeout in second

<a name="dv_coll_linker.search.get_new_recs"></a>

##### get\_new\_recs

```python
get_new_recs(allrecs: dict, last_check=str) -> list
```

Returns a list of records (ie, individual items from allrecs['data']['items']
that are newer than last_check. Note that "newer" in this case is to the second,
so searching for "2022" will pull up all records for 2022, as 2022 will be
automatically encoded to 2022-01-01T00:00:00Z.

last_check is a time string in '%Y-%m-%dT%H:%M:%SZ', or portions thereof. When including the
time, make sure to use/include T.

<a name="dv_coll_linker.data"></a>

## dv\_coll\_linker.data

