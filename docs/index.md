---
layout: default
title: Main
nav_order: 1
---

# dv_coll_linker

### Automated study linking for [Dataverse](https://dataverse.org) installations

## Introduction

Some time in the history of Dataverse 5.x, probably around version 5.6, collection level links in a Dataverse installation ceased to function correctly.

More specifically, if collection level links were present,the collection title was linked, but the _contents_ did not appear.

For example, given Collections A and B, and Collection B is linked to Collection A:

**Expected behaviour:**

- Collection A
	- Collection A studies
  	- Collection B linked collection entry
    	- Collection B studies

That is, the studies from Collection B will appear while looking at Collection A. At the very least, this was the behaviour with v4.20.

**Actual behaviour:**

- Collection A
    - Collection A studies
    - Collection B linked collection entry

Further details and links to Github/issues are available  [here](https://groups.google.com/g/dataverse-community/c/DDmVelt3Zfk/m/upo7XoIJBgAJ).

---

### Quick install, or I hate reading

`pip install git+https://github.com/ubc-library-rc/dv_coll_linker@master`

---

## The collection linker

This software rectifies this issue externally by creating individual links to studies where formerly there was only a collection link. The software exists as both a Python 3 module and a command line application. Most users will just need the command line application, but the module is present in case the application does not meet user needs.

The collection linker:

* tracks changes over time
* links newly added items
* links applicable items when collections are newly linked
* unlinks items when collections are unlinked

It's designed to be a drop-in replacement returning the former functionality *without* touching the existing Dataverse code base. It is a standalone product and does not (necessarily) have to be run from the server which hosts a Dataverse installation.


