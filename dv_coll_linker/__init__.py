'''
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
'''
VERSION = (0, 4, 2)
__version__ = '.'.join([str(x) for x in VERSION])
