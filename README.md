# Webmixer: local-only personal webserver with dynamic mapping

Webmixer has wx-based user interface.
Use of Webmixer is described in the `docs/manual.html` file.
Webmixer is developed and tested under Linux.

#### Installation of Webmixer from the package directory can be done as:

- `python -m pip install .` when it is run within *venv* environments,
- `python -m pip install --prefix /usr .` wehn it is run outside *venv* environments.

Notice that under many Linux distributions, incl. Debian/Ubuntu, the */usr* prefix is auto-translated into the actual */usr/local* location.
And making *venv* environments is suggested with the *--system-site-packages* option so that system-wide wxPython packages (if present) can be reused.

#### Webmixer can present multiple directories within single web source.
The served directories can be mapped both statically and dynamically.
The mapping is kept in configuration files in form of pairs of lines:

- the first lines are URL paths for the mappings,
- the second lines are the local directories mapped to the URLs.

Webmixer uses two files for the mapping of the served directories.
They are supposed to be at `~/.webmixer` directory by default on Linux
and alike operating systems, and at home directory under Windows.
The location of these two files can be set by startup options,
see the `docs/options.txt` file.

Static mapping is set by the user before Webmixer is run;
file with the dynamic mapping is filled by Webmixer.

The dynamic mapping is done according to MAP/1.0 protocol
that is described in the `docs/protocol.txt` file,
and a client implementation is at `client/setmap.py` script.

Webmixer uses two ports: for the dynamic mapping (12001 by default)
and for the web serving (12000 by default).
It can be set by startup options too.

**The project site is at [Tangloid](https://webmixer.tangloid.net) and its repository is hosted at [GitHub](https://github.com/queuine/webmixer).**
