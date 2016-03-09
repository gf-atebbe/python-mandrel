# Mandrel (python-mandrel) #

Mandrel provides bootstrapping and configuration tools for consistent,
straightforward project config management.

Use Mandrel to:

* bootstrap your python project configuration
* manage configuration file location/access
* manage logging configuration and Logger retrieval

Separate projects can rely on Mandrel for these purposes, and when they're
brought together (as eggs, for instance) to a single application, their
configuration can be managed simply in an easily-configurable way.

## Why and how? ##

Suppose you want to be able to look for configuration files across
several directories, in order of precedence:

* `./`
* `~/.whizzies/`
* `/etc/whizzies/`

Suppose further that you have one aspect of your app that deals with
storage, and another that deals with analysis.  You configure them
separately.

So at the root of your project, you would add a file named `Mandrel.py`,
and in it you would say:

    bootstrap.SEARCH_PATHS.extend(['~/.whizzies', '/etc/whizzies'])

Now name your YAML configuration files for the subsections of your app:

* `storage.yaml`
* `analysis.yaml`

You can easily load configuration dictionaries from YAML files if those
files exist on the bootstrap.SEARCH_PATH:

    analysis_config = mandrel.config.get_configuration('analysis')
    storage_config = mandrel.config.get_configuration('storage')

If you want a standard configuration system-wide, put it in /etc/whizzies.

But then if you want a configuration for a particular user, put it in
~user/.whizzies.  That will completely override the system-wide one when
present.

And of course, the SEARCH_PATH just looks in the current working directory,
so the most-specific config can go there, again completely overruling the
lower-precedence config.

Similarly, a `logging.cfg` file can be placed somewhere in the search
path, and you can use `mandrel.bootstrap.get_logger(logger_name)` to
get loggers.  The bootstrapper will ensure that logging config is
properly applied.

### Configuration classes ###

Take it farther:

    class StorageConfig(mandrel.config.Configuration):
        NAME = 'storage'

Now the `StorageConfig` class easily wraps the lookup of "storage.yaml",
and makes the key/value pairs therein available as attributes on a
`StorageConfig` instance.

Add functionality to your class to enforce particular defaults,
ensure values are properly formatted, constrained, etc.

You can fetch a logger named "storage" from it, too:

    logger = StorageConfig.get_logger()

### Bootstrap Configuration ###

By default, mandrel looks for a bootstrap file named 'Mandrel.py' in the search path, as described above.
In most cases this works well and the default behaviour is exactly what you need.
There are rare exceptions though where you don't want Mandrel to throw an exception if the
bootstrap file isn't found or don't want to the default search path to be the current working directory.

Mandrel supports two environment variables for these specific cases:
`MANDREL_ROOT = The root directory from which to start looking for the bootstrap file`
`MANDREL_BOOTSTRAP_NAME = The name of the bootstrap file to look for in the search path`

These environment variables can be set independently of each other and do not have to both be set.

# License #

Mandrel is free software and is released under the terms
of the MIT license (<http://opensource.org/licenses/mit-license.php>),
as specified in the accompanying LICENSE.txt file.
