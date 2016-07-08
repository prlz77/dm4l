# Handlers
To minimize the amount of code to rewrite each time one wants to extract/use 
logging information from a machine learning system, a simple log-handler class
is provided.

The user only has to implement the ``parse`` function of a ``LogHandler`` 
derived from the abstract class ``AbstractLogHandler``, which uses the provided
log file pointer to update the ``log_data`` with the last log file changes.

New handlers should be created in handlers/MLframework/handler_name/handler.py. A configuration
file config.py can also be provided.


Currently available handlers:

Plugin Name | Description | Depends
------------|-------------|--------
``misc.acc_list`` | Reads data from an accuracy list. | 
``torch.wide_resnet`` | Reads data in json format. | json