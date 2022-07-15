# Installation

## Prequisites

* Python  >= v.3.6
* For automatic database population, Dataverse server access and access to Dataverse's PostgreSQL database


## Installation
Generally, installation is performed using `pip`:

`pip install git+https://github.com/ubc-library-rc/dv_coll_linker@master`

Alternately, it is possible to install using one of the many other ways to [install Python packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)

`dv_coll_linker` is not on [PyPi](https://pypi.org); installing from git or downloading from source is the only option at this time.

## Post-install

After installation, most users will us the command line script, invoked by `dv_coll_linker`. See the [usage](usage.md) page for more details.

Using the package within Python is the same as any other. Importing `dv_coll_linker` on its own does nothing, however. Each module must be imported on its own. For example:

`import dv_coll_linker.search` or
`from dv_coll_linker import search`

If using `dv_coll_linker` as Python package, you may wish to consult the [API reference](api_reference.md).
