# Command Line Usage

Unless the Dataverse installation has an unusual use case or setup, most users will just need to run the included command line utilty, called, unsurprisingly, `dv_coll_linker`.

**Notes on running the software outside the Dataverse server environment**

While it is *technically* not required to run the collection linker from the server which hosts a Dataverse installation, it may be desirable to do so. If the user running the program has sufficient privileges, if run on the server the `dv_coll_linker` utility will automatically detect linked collections and populate the resultant [sqlite3](https://sqlite.org) database with the appropriate data, allowing the software to run more-or-less automatically.

If the database is *not* automatically populated, the `children` table in the tracking database must be populated manually. It's quite straightforward:

* parent_id: Database id number of parent
* parent_alias: Dataverse short name for collection
* child_id: Database id number of child (ie, the collection which is linked to the parent)
* child_alias: Dataverse short name for the child collection.

For those not comfortable using sqlite3 from the command line, there is a very nice free and open source piece of software with a well-designed UI: [DB Browser for SQLite](https://sqlitebrowser.org).

It may be possible to have the utility automatically populate the tables if you have the PostgreSQL port open to outside, but that seems unlikely and inadvisable.

## Using the command line tool:

To use the tool on the server and automatically harvest data from PostgreSQL, you will need:

* The Dataverse installation's PostgreSQL database name
* The password to access the database
* The port for accessing the database
* A superuser API key

**Superuser keys are required because links may only be produced by superusers.** Some defaults are already in place as listed below.

### dv_coll_linker

```nohighlight
usage: dv_coll_linker [-h] [-u URL] [-d DVDBNAME] [-y USER] [-w PASSWORD] [-p PORT] [-r DBHOST] [-k KEY] [-b DBNAME] [-l LOG] [-v--version]
   
Study level linker for Dataverse installations. Finds collection level links and automatically adds study-level links for each found collection. Addresses issues as noted here
https://groups.google.com/g/dataverse-community/c/DDmVelt3Zfk
  
optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL to base Dataverse installation. Default https://abacus.library.ubc.ca
  -d DVDBNAME, --dvdbname DVDBNAME
                        Dataverse PostgreSQL Database name. Defaults to dvndb. If not run on the server hosting a Dataverse installation, the program will attempt to connect to
                        PostgreSQL. It will likely fail if your security is good and you will need to populate the collection and children database manually.
  -y USER, --user USER  PostgreSQL database username. Defaults to dvnapp
  -w PASSWORD, --password PASSWORD
                        PostgreSQL database password for --user.Defaults to 123456. No, of course it doesn't. There is no default password.
  -p PORT, --port PORT  PostgreSQL port. Defaults to 5432
  -r DBHOST, --dbhost DBHOST
                        Database host. Defaults to localhost. If using another host use *just* the hostname.
  -k KEY, --key KEY     Dataverse installation API key. This *must* be a superuser API key. Non-superuser keys will fail. If you don't know if you have superuser keys, you are probably
                        not a superuser.
  -b DBNAME, --dbname DBNAME
                        Local sqlite3 link database. Defaults to ~/dv_links.sqlite3
  -l LOG, --log LOG     Log directory. Defaults to ~/logs. Log is saved as dv_coll_linker.log
  -v--version           Show version number and exit
```

## Continual updating 

There are a few options for ensuring automatic updates to your dataverse installation.

* Run at intervals with `cron`
	* This is probably advisable with large or multi-user Dataverse installations. As the utility only obtains new or changed studies, it does not place excessive server load and can be run at fairly frequent intervals, such as 10 minutes. Note that the *first* time the software runs, the whole Dataverse installation will be crawled for metadata, so if server load is an issue, you should be aware of this

* Manually running
	* For smaller installations or those with few linked collections, it may be easier to just run the utility on an *ad_hoc* basis.

* Windows scheduler
	* If, for some reason, you are not running the software on the server and are using a Windows computer, you can use the Windows Task Scheduler to run the application at your desired interval.
