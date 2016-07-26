```
           ______ ___  ___   ___  _     
           |  _  \|  \/  |  /   || |    
 /__/\__\  | | | || .  . | / /| || |     /__/\__\ 
(`-/__\-') | | | || |\/| |/ /_| || |    (`-/__\-')
 \/,'`.\/  | |/ / | |  | |\___  || |____ \/,'`.\/
           |___/  \_|  |_/    |_/\_____/
```

*Dark magic for machine learning log files.*


# What is it?

DM4L is a tool thought to **avoid rewritting full codes** each time one wants to extract information from machine learning logs. For instance, when a neural network is trained in caffe, we cannot expect the logs to be comparable to torch or even to another caffe branch. Thus, if we want to plot train vs test error, we usually have to create a parser and to add matplotlib calls etc. each time. DM4L reduces all this effort to the creation of a simple shareable implementation of the concrete parser, the rest is just done by magic (and a nice and easy plugin system which makes easy to add new reusable functions like plotting, early-stopping, reporting, etc.). Basically **it allows you to do everything you can do from a log file** and do it with any kind of log file with **minimal effort**.

## Features
- Plugin system
- [x] Core
- [x] Plot Plugin
- [x] Max Plugin
- [ ] Webserver interface with bottle (**under development**)
- [ ] Early stopping pluggin.
- [ ] E-mail on event.
- Handler System
- [x] Core 
- [x] Accuracy list parser
- [x] Torch-json parser
- [ ] Caffe Parser
- [ ] Tensorflow Parser
- [ ] Chainer Parser
- [ ] Tiny CNN Parser

# Install
clone this repository and install:
- numpy
- Your [plugin dependences](https://github.com/prlz77/dm4l/tree/master/plugins)
- Your [handler dependences](https://github.com/prlz77/dm4l/tree/master/handlers)

# Add a new [plugin](https://github.com/prlz77/dm4l/tree/master/plugins)
I encourage anyone to add his own features and to share them with the rest.

1. Create a folder with your plugin name.
2. Copy the abstract_plugin.py inside the folder.
3. Write your own update function.
4. Test and document it.
5. Pull Request

# Add a new [handler](https://github.com/prlz77/dm4l/tree/master/handlers)
You can add your own handlers with a similar procedure. We encourage the community to
add handlers since sharing them will eliminate the need of rewriting them every time.

1. Create a folder with your handler name.
2. Copy the abstract_log_handler.py inside the folder.
3. Write your own parse function.
4. Test and document it.
5. Pull Request

# Usage
Dark magic can be used as a simple commandline tool or directly importing dm4l.py to use the dark [API](https://prlz77.github.io/dm4l/).

## Commandline
The commandline script basically takes the following structure:
``[options] [input] plugin1 plugin2...``

Let's say we want to create a plot comparing all the accuracies (in list format) of the logs in a path:

![](https://raw.githubusercontent.com/prlz77/dm4l/gh-pages/snapshots/folders.jpg)

Then we can run:

```pyhon
python main.py --path logs/*/test.log misc.acc_list plot
```

And obtain:

<img src="https://raw.githubusercontent.com/prlz77/dm4l/gh-pages/snapshots/example_plot.png" width="512" />

That easy? Yes :)

If we want them to update in real time (every 1sec for instance):

```pyhon
python main.py --refresh 1 --path logs/*/test.log misc.acc_list plot
```

# Author
prlz77 at ISELAB

Any problem, please e-mail me.
