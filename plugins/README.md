# Plugins
Once dark magic has been used to extract the log information, there is usually the need
to process it to extract conclusions. Each user needs different functionalities: plotting 
error/accuracy curves, confusion matrices, and much more. Thus we provide a plugin system
so that it is easy to add a new isolated function.

New plugins have to be created in plugins/plugin_name/plugin.py. They have to be derived from the 
``AbstractPlugin`` class, which receives an instance to the dark magic API and a configuration
dictionary read from plugins/plugin_name/config.py. The programmer only has to implement the
``update`` function, which uses the API to do the magic.

Currently available plugins:

Plugin Name | Description | Depends
------------|-------------|--------
``plot`` | Uses matplotlib to generate a plot comparing multiple logs. The title, axis and legend are
configurable. | numpy, pylab, matplotlib, [seaborn].
``max`` | Gets the max score, argmax, and log id of multiple logs and returns/print them in the desired format. | numpy