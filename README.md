```
           ______ ___  ___   ___  _     
           |  _  \|  \/  |  /   || |    
 /__/\__\  | | | || .  . | / /| || |     /__/\__\ 
(`-/__\-') | | | || |\/| |/ /_| || |    (`-/__\-')
 \/,'`.\/  | |/ / | |  | |\___  || |____ \/,'`.\/
           |___/  \_|  |_/    |_/\_____/
```

**Dark magic for machine learning log files.**

DM4L is a tool though to **avoid rewritting full codes** each time one wants to extract information from machine learning logs. For instance, when a neural network is trained in caffe, we cannot expect the logs to be comparable to torch or even to another caffe branch. Thus, if we want to plot train vs test error, we usually have to create a parser and to add matplotlib calls etc. each time. DM4L reduces all this effort to the creation of a simple shareable implementation of the concrete parser, the rest is just done by magic (and a nice and easy plugin system which makes easy to add new reusable functions like plotting, early-stopping, reporting, etc.). Basically **it allows you to do everything you can do from a log file** and do it with any kind of log file with **minimal effort**.



